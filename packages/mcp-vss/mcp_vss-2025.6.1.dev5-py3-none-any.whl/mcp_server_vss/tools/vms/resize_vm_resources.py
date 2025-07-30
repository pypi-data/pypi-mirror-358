"""Resize VM tool."""
import asyncio
from typing import Any, Dict, Optional

from fastmcp import Context, FastMCP
from loguru import logger

from mcp_server_vss.client import VssApiClient
from mcp_server_vss.exceptions import VssError
from mcp_server_vss.models import VmResizeRequest
from mcp_server_vss.models.vms import VMInfo, VmOsInfo
from mcp_server_vss.tools.common import BaseVmTool


class ResizeVmTool(BaseVmTool):
    """Resize VM tool."""

    def __init__(self, mcp: FastMCP, auth_token: str, api_endpoint: str):
        """Initialize class."""
        super().__init__(auth_token, api_endpoint)
        mcp.tool(name='resize_vm_resources')(self.resize_vm_resources)

    async def resize_vm_resources(
        self,
        ctx: Context,
        request: VmResizeRequest,
    ) -> str:
        """Modify VM CPU, memory, or storage allocation.

        Use this tool when you need to:
        - Scale up VM resources for increased workload
        - Scale down to optimize costs
        - Adjust VM configuration for new requirements
        - Optimize resource allocation based on usage patterns

        Important limitations:
        - CPU/Memory can be hot-added only if VM supports it
        - CPU/Memory can only be decreased when VM is powered off
        - Memory hot-add restrictions apply to certain Linux/Windows guests
        - CPU topology changes require careful core-per-socket planning

        Hot-add support depends on VM configuration and guest OS compatibility.
        """
        await ctx.info(f'Updating vm {request.vm_id_or_uuid_or_name}')
        try:
            # Validate that at least one resource change is requested
            if request.new_cpu_count is None and request.new_memory_gb is None:
                raise VssError(
                    "At least one resource change (CPU or memory) "
                    "must be specified"
                )

            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                # Resolve VM identifier to ID and get current VM info
                vm_data = await self.handle_vm_info(
                    api_client, request.vm_id_or_uuid_or_name, ctx
                )
                # Get OS information for memory hot-add validation
                os_info = await self.handle_get_vm_os_info(
                    api_client, vm_data, ctx
                )
                # Analyze resize feasibility
                resize_plan = await self._analyze_resize_feasibility(
                    api_client, vm_data, request, os_info, ctx
                )
                await ctx.info(f'Resize plan: {resize_plan}')
                # Execute the resize operations
                resize_results = await self._execute_vm_resize(
                    api_client, vm_data, request, resize_plan, ctx
                )
                # Format comprehensive response
                response = self._format_resize_response(
                    vm_data, request, resize_plan, resize_results
                )
                return response
        except VssError as e:
            logger.error(f"VSS error in resize_vm_resources: {str(e)}")
            raise Exception(f"VSS API error: {str(e)}")
        except ValueError as e:
            logger.error(f"Validation error in resize_vm_resources: {str(e)}")
            raise Exception(f"Validation error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in resize_vm_resources: {e}")
            raise Exception(f"Internal error: {str(e)}")

    async def _analyze_resize_feasibility(
        self,
        api_client: VssApiClient,
        vm_data: VMInfo,
        request: VmResizeRequest,
        os_info: VmOsInfo,
        ctx: Context,
    ) -> Dict[str, Any]:
        """Analyze if the requested resize operation is feasible."""

        plan = {
            'cpu_change': None,
            'memory_change': None,
            'requires_power_off': False,
            'warnings': [],
            'errors': [],
            'hot_add_supported': {
                'cpu': getattr(vm_data, 'cpu_hotadd', False),
                'memory': getattr(vm_data, 'memory_hotadd', False),
            },
        }

        current_cpu = vm_data.cpu_count
        current_memory_gb = vm_data.memory_gb
        vm_powered_on = vm_data.power_state == 'poweredOn'
        await ctx.info(
            f"Analyzing resize feasibility considering {current_memory_gb=}, "
            f"{current_cpu=}, {vm_powered_on=}."
        )
        # Analyze CPU changes
        if request.new_cpu_count is not None:
            if request.new_cpu_count == current_cpu:
                plan['warnings'].append(
                    f"CPU count unchanged ({current_cpu} vCPUs)"
                )
            else:
                cpu_increase = request.new_cpu_count > current_cpu

                plan['cpu_change'] = {
                    'from': current_cpu,
                    'to': request.new_cpu_count,
                    'increase': cpu_increase,
                    'cores_per_socket': request.new_cores_per_socket,
                }

                if cpu_increase:
                    if vm_powered_on and not plan['hot_add_supported']['cpu']:
                        plan['errors'].append(
                            "CPU hot-add not supported - "
                            "VM must be powered off"
                        )
                        plan['requires_power_off'] = True
                    elif vm_powered_on:
                        plan['warnings'].append(
                            "CPU hot-add will be performed "
                            "(VM remains powered on)"
                        )
                else:
                    if vm_powered_on:
                        plan['errors'].append(
                            "CPU reduction requires VM to be powered off"
                        )
                        plan['requires_power_off'] = True

        # Analyze memory changes
        if request.new_memory_gb is not None:
            if request.new_memory_gb == current_memory_gb:
                plan['warnings'].append(
                    f"Memory unchanged ({current_memory_gb} GB)"
                )
            else:
                memory_increase = request.new_memory_gb > current_memory_gb

                plan['memory_change'] = {
                    'from': current_memory_gb,
                    'to': request.new_memory_gb,
                    'increase': memory_increase,
                }

                if memory_increase:
                    if (
                        vm_powered_on
                        and not plan['hot_add_supported']['memory']
                    ):
                        plan['errors'].append(
                            "Memory hot-add not supported - "
                            "VM must be powered off"
                        )
                        plan['requires_power_off'] = True
                    elif vm_powered_on:
                        # Check special Linux 64-bit / Windows 7 32-bit limitations
                        memory_validation = self._validate_memory_hot_add(
                            current_memory_gb, request.new_memory_gb, os_info
                        )
                        if memory_validation['allowed']:
                            plan['warnings'].append(
                                "Memory hot-add will be performed "
                                "(VM remains powered on)"
                            )
                            if memory_validation['warnings']:
                                plan['warnings'].extend(
                                    memory_validation['warnings']
                                )
                        else:
                            plan['errors'].extend(memory_validation['errors'])
                            plan['requires_power_off'] = True
                else:
                    if vm_powered_on:
                        plan['errors'].append(
                            "Memory reduction requires VM to be powered off"
                        )
                        plan['requires_power_off'] = True

        # Check if forced power off can resolve issues
        if plan['requires_power_off'] and not request.force_power_off:
            plan['errors'].append(
                "Use 'force_power_off: true' to automatically "
                "power off VM for this operation"
            )

        return plan

    @staticmethod
    def _validate_memory_hot_add(
        current_memory_gb: float, new_memory_gb: float, os_info: VmOsInfo
    ) -> Dict[str, Any]:
        """Validate memory hot-add based on OS-specific limitations."""

        result = {'allowed': True, 'warnings': [], 'errors': []}

        # Check if this is a restricted OS
        if not (os_info.is_linux_64bit or os_info.is_windows_32bit):
            return result  # No special restrictions

        current_memory_mb = current_memory_gb * 1024
        new_memory_mb = new_memory_gb * 1024

        # Apply the specific rules for Linux 64-bit and Windows 7 32-bit
        if current_memory_mb < 3072:  # Less than 3GB
            max_allowed_mb = 3072
            if new_memory_mb > max_allowed_mb:
                result['allowed'] = False
                result['errors'].append(
                    f"Cannot hot-add memory beyond 3GB "
                    f"limit for {os_info.guest_id}. "
                    f"Current: {current_memory_gb}GB, Requested: "
                    f"{new_memory_gb}GB, Max allowed: 3GB"
                )
            else:
                result['warnings'].append(
                    f"Memory hot-add restricted to 3GB total "
                    f"for {os_info.guest_id}"
                )
        elif current_memory_mb == 3072:  # Exactly 3GB
            result['allowed'] = False
            result['errors'].append(
                f"Cannot hot-add any memory when VM has exactly "
                f"3GB for {os_info['guest_id']}"
            )

        # Additional validation examples based on the rules
        if current_memory_gb == 1 and new_memory_gb > 3:
            result['warnings'].append(
                "Adding more than 2GB to 1GB VM - ensure this is intended"
            )
        elif current_memory_gb == 2 and new_memory_gb > 3:
            result['warnings'].append(
                "Adding more than 1GB to 2GB VM - ensure this is intended"
            )

        return result

    async def _execute_vm_resize(
        self,
        api_client: VssApiClient,
        vm_data: VMInfo,
        request: VmResizeRequest,
        plan: Dict[str, Any],
        ctx: Context,
    ) -> Dict[str, Any]:
        """Execute the VM resize operations."""

        results = {
            'cpu_result': None,
            'memory_result': None,
            'power_operations': [],
        }

        # Check for blocking errors
        if plan['errors'] and not request.force_power_off:
            raise VssError(
                f"Resize blocked by errors: {'; '.join(plan['errors'])}"
            )

        # Power off VM if required and authorized
        if plan['requires_power_off'] and request.force_power_off:
            await ctx.info('VM requires power off.')
            if vm_data.power_state == 'poweredOn':
                power_result = await api_client.post(
                    f"v2/vm/{vm_data.moref}/state/off",
                    f"powering off VM for resize operation",
                )
                results['power_operations'].append(
                    {
                        'action': 'power_off',
                        'result': power_result,
                        'reason': 'Required for resize operation',
                    }
                )

                # Wait a moment for power off to complete
                await asyncio.sleep(5)

        # Execute CPU resize
        if plan['cpu_change']:
            await ctx.info('VM requires cpu change.')
            cpu_payload = self._build_cpu_payload(
                request.new_cpu_count, request.new_cores_per_socket
            )

            cpu_result = await api_client.put(
                f"v2/vm/{vm_data.moref}/cpu",
                f"updating CPU allocation for VM '{vm_data.name}'",
                json_data=cpu_payload,
            )
            results['cpu_result'] = cpu_result

        # Execute memory resize
        if plan['memory_change']:
            await ctx.info('VM requires memory change.')
            memory_payload = {"value": request.new_memory_gb}

            memory_result = await api_client.put(
                f"v2/vm/{vm_data.moref}/memory",
                f"updating memory allocation for VM '{vm_data.name}'",
                json_data=memory_payload,
            )
            results['memory_result'] = memory_result

        return results

    @staticmethod
    def _build_cpu_payload(
        cpu_count: int, cores_per_socket: Optional[int]
    ) -> Dict[str, Any]:
        """Build the CPU configuration payload."""
        if cores_per_socket is not None:
            return {
                "value": {
                    "count": cpu_count,
                    "cores_per_socket": cores_per_socket,
                }
            }
        else:
            return {"value": cpu_count}

    @staticmethod
    def _format_resize_response(
        vm_data: VMInfo,
        request: VmResizeRequest,
        plan: Dict[str, Any],
        results: Dict[str, Any],
    ) -> str:
        """Format comprehensive resize operation response"""
        response = f"""VM Resource Resize Operation
{'=' * 50}

VM Details:
- Name: {vm_data.name}
- ID: {vm_data.moref}
- Original State: {vm_data.power_state}
- Client: {vm_data.client}

RESOURCE CHANGES:
"""

        # CPU Changes
        if plan['cpu_change']:
            cpu_change = plan['cpu_change']
            cores_info = ""
            if request.new_cores_per_socket:
                sockets = request.new_cpu_count // request.new_cores_per_socket
                cores_info = f" ({sockets} sockets × {request.new_cores_per_socket} cores)"

            status = "✅ SUCCESS" if results['cpu_result'] else "❌ FAILED"
            response += f"""
    📊 CPU Configuration:
    - Previous: {cpu_change['from']} vCPUs
    - New: {cpu_change['to']} vCPUs{cores_info}
    - Operation: {'Hot-add' if cpu_change['increase'] and vm_data.power_state == 'poweredOn' else 'Standard resize'}
    - Status: {status}
    """

            if results['cpu_result']:
                response += f"- Result: {results['cpu_result'].get('message', 'CPU updated successfully')}\n"

        # Memory Changes
        if plan['memory_change']:
            memory_change = plan['memory_change']
            status = "✅ SUCCESS" if results['memory_result'] else "❌ FAILED"
            response += f"""
    💾 Memory Configuration:
    - Previous: {memory_change['from']} GB
    - New: {memory_change['to']} GB
    - Change: {'+' if memory_change['increase'] else '-'}{abs(memory_change['to'] - memory_change['from'])} GB
    - Operation: {'Hot-add' if memory_change['increase'] and vm_data.power_state == 'poweredOn' else 'Standard resize'}
    - Status: {status}
    """

            if results['memory_result']:
                response += f"- Result: {results['memory_result'].get('message', 'Memory updated successfully')}\n"

        # Power Operations
        if results['power_operations']:
            response += f"""
    ⚡ POWER OPERATIONS:
    """
            for power_op in results['power_operations']:
                response += (
                    f"- {power_op['action'].title()}: {power_op['reason']}\n"
                )
                response += f"  Status: {power_op['result'].get('status', 'Completed')}\n"

        # Warnings and Notes
        if plan['warnings']:
            response += f"""
    ⚠️  WARNINGS:
    """
            for warning in plan['warnings']:
                response += f"- {warning}\n"

        # Hot-add Support Information
        response += f"""
    🔧 VM CAPABILITIES:
    - CPU Hot-add: {'✅ Supported' if plan['hot_add_supported']['cpu'] else '❌ Not supported'}
    - Memory Hot-add: {'✅ Supported' if plan['hot_add_supported']['memory'] else '❌ Not supported'}
    
    NEXT STEPS:
    """

        # Provide next steps based on what was changed
        if plan['cpu_change'] or plan['memory_change']:
            response += """- Verify VM boots successfully after resize
    - Monitor application performance with new resources
    - Update monitoring thresholds if needed
    - Document changes for capacity planning
    """

        # Add power state guidance
        if results['power_operations']:
            response += (
                "- Power on VM when ready (if it was powered off for resize)\n"
            )

        # Add OS-specific notes
        if plan['memory_change'] and plan['memory_change']['increase']:
            response += """
    💡 MEMORY HOT-ADD NOTES:
    - Guest OS may need to recognize new memory
    - Linux: Check 'free -h' and /proc/meminfo
    - Windows: Check Task Manager or Device Manager
    - Some applications may need restart to use new memory
    """

        if plan['cpu_change'] and plan['cpu_change']['increase']:
            response += """
    💡 CPU HOT-ADD NOTES:
    - Guest OS should automatically recognize new CPUs
    - Check CPU count in guest OS after hot-add
    - Applications may need restart to utilize new CPUs effectively
    - Monitor CPU load distribution across all cores
    """
        return response
