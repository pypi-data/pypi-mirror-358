"""
MCP P2P Router

Routes MCP (Model Context Protocol) requests through the P2P network based on
AI ownership, ensuring that context gathering and analysis operations respect
ownership boundaries and leverage remote AI capabilities.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ....utils.logging_config import get_logger

logger = get_logger(__name__)


class MCPRoutingDecision:
    """Represents routing decision for an MCP request."""

    def __init__(
        self,
        execute_locally: bool,
        remote_node_info: Optional[Dict] = None,
        ai_capabilities: Optional[List[str]] = None,
        paths_involved: Optional[List[str]] = None,
        reason: str = "",
    ):
        self.execute_locally = execute_locally
        self.remote_node_info = remote_node_info
        self.ai_capabilities = ai_capabilities or []
        self.paths_involved = paths_involved or []
        self.reason = reason

    def is_local(self) -> bool:
        return self.execute_locally

    def is_remote(self) -> bool:
        return not self.execute_locally

    def get_remote_address(self) -> Optional[str]:
        if self.remote_node_info:
            return self.remote_node_info.get("address")
        return None


class MCPRouter:
    """Routes MCP requests through P2P network based on ownership and capabilities."""

    def __init__(self, network_manager=None):
        self.network_manager = network_manager

    def set_network_manager(self, network_manager):
        """Set or update the network manager."""
        self.network_manager = network_manager

    async def route_mcp_request(
        self, method: str, params: Dict, required_capabilities: Optional[List[str]] = None
    ) -> MCPRoutingDecision:
        """
        Route an MCP request based on the method and parameters.

        Args:
            method: MCP method name (e.g., "context/analyze", "context/scan")
            params: MCP request parameters
            required_capabilities: Required AI capabilities for this request

        Returns:
            MCPRoutingDecision with routing information
        """
        if not self.network_manager:
            return MCPRoutingDecision(
                execute_locally=True, reason="No P2P network manager available"
            )

        # Extract paths from MCP parameters
        paths = self._extract_paths_from_mcp_params(method, params)

        if not paths:
            return MCPRoutingDecision(execute_locally=True, reason="No paths found in MCP request")

        # Check ownership and capabilities for each path
        routing_decisions = []
        for path in paths:
            decision = await self._check_mcp_path_ownership(path, method, required_capabilities)
            routing_decisions.append((path, decision))

        # Consolidate decisions
        return await self._consolidate_mcp_decisions(
            routing_decisions, method, required_capabilities
        )

    def _extract_paths_from_mcp_params(self, method: str, params: Dict) -> List[str]:
        """Extract file/directory paths from MCP request parameters."""
        paths = []

        # Common path parameter names in MCP requests
        path_params = [
            "directory",
            "path",
            "file_path",
            "project_path",
            "target_path",
            "source_path",
            "paths",
        ]

        for param_name in path_params:
            if param_name in params:
                value = params[param_name]
                if isinstance(value, str):
                    paths.append(value)
                elif isinstance(value, list):
                    paths.extend(str(p) for p in value)

        # Method-specific path extraction
        if method.startswith("context/"):
            if "context_request" in params:
                context_req = params["context_request"]
                if "project_root" in context_req:
                    paths.append(context_req["project_root"])
                if "file_paths" in context_req:
                    paths.extend(context_req["file_paths"])

        elif method.startswith("codeguard/"):
            # CodeGuard-specific MCP methods
            if "original" in params:
                paths.append(params["original"])
            if "modified" in params:
                paths.append(params["modified"])

        return [str(p) for p in paths if p]

    async def _check_mcp_path_ownership(
        self, path: str, method: str, required_capabilities: Optional[List[str]] = None
    ) -> tuple[bool, Optional[Dict], str]:
        """
        Check ownership and capabilities for an MCP request path.

        Returns:
            Tuple of (is_local, remote_info, reason)
        """
        try:
            # Check for AI ownership first (higher priority for MCP)
            local_ai_owner = self.network_manager.get_ai_owner_for_path(path)
            if local_ai_owner:
                # Check if local AI owner has required capabilities
                if required_capabilities:
                    local_capabilities = set(local_ai_owner.get("capabilities", []))
                    required_set = set(required_capabilities)
                    if not required_set.issubset(local_capabilities):
                        # Local AI doesn't have required capabilities, check remote
                        remote_owner = await self._find_remote_ai_with_capabilities(
                            path, required_capabilities
                        )
                        if remote_owner:
                            return (
                                False,
                                remote_owner,
                                f"Remote AI has required capabilities for {path}",
                            )

                return True, local_ai_owner, f"Local AI ownership for {path}"

            # Check for remote AI ownership
            remote_ai_owner = await self.network_manager.query_ai_ownership(path)
            if remote_ai_owner and remote_ai_owner.get("node_id") != self.network_manager.node_id:
                # Check capabilities if required
                if required_capabilities:
                    remote_capabilities = set(remote_ai_owner.get("capabilities", []))
                    required_set = set(required_capabilities)
                    if required_set.issubset(remote_capabilities):
                        return False, remote_ai_owner, f"Remote AI with capabilities for {path}"
                    else:
                        # Remote AI doesn't have capabilities, fall back to local
                        return (
                            True,
                            None,
                            f"Remote AI lacks capabilities, executing locally for {path}",
                        )
                else:
                    return False, remote_ai_owner, f"Remote AI ownership for {path}"

            # No AI ownership, check basic path ownership
            path_owner = self.network_manager.find_owner(path)
            if path_owner and path_owner.node_id != self.network_manager.node_id:
                remote_info = {
                    "node_id": path_owner.node_id,
                    "address": path_owner.address,
                    "capabilities": [],  # Basic node may not have AI capabilities
                }
                return False, remote_info, f"Remote path ownership for {path}"

            # Local ownership or unmanaged
            return True, None, f"Local ownership or unmanaged path: {path}"

        except Exception as e:
            logger.warning(f"Error checking MCP path ownership for {path}: {e}")
            return True, None, f"Error checking ownership, defaulting to local: {e}"

    async def _find_remote_ai_with_capabilities(
        self, path: str, required_capabilities: List[str]
    ) -> Optional[Dict]:
        """Find a remote AI node with the required capabilities for a path."""
        # This would query the P2P network for nodes with specific capabilities
        # For now, return None and let it fall back to local
        return None

    async def _consolidate_mcp_decisions(
        self,
        path_decisions: List[tuple[str, tuple[bool, Optional[Dict], str]]],
        method: str,
        required_capabilities: Optional[List[str]],
    ) -> MCPRoutingDecision:
        """Consolidate multiple path decisions into a single MCP routing decision."""
        local_paths = []
        remote_decisions = []

        for path, (is_local, remote_info, reason) in path_decisions:
            if is_local:
                local_paths.append(path)
            else:
                remote_decisions.append((path, remote_info, reason))

        all_paths = [path for path, _ in path_decisions]

        # If all paths are local, execute locally
        if not remote_decisions:
            return MCPRoutingDecision(
                execute_locally=True,
                paths_involved=all_paths,
                reason="All paths have local ownership",
            )

        # If all paths are remote and owned by the same AI-capable node, execute remotely
        if not local_paths:
            ai_nodes = {}
            for path, remote_info, reason in remote_decisions:
                if remote_info and remote_info.get("capabilities"):
                    node_id = remote_info["node_id"]
                    ai_nodes[node_id] = remote_info

            if len(ai_nodes) == 1:
                remote_info = list(ai_nodes.values())[0]
                return MCPRoutingDecision(
                    execute_locally=False,
                    remote_node_info=remote_info,
                    ai_capabilities=remote_info.get("capabilities", []),
                    paths_involved=all_paths,
                    reason=f"All paths owned by remote AI node {remote_info['node_id']}",
                )

        # Mixed ownership - prefer AI-capable nodes for MCP requests
        ai_capable_remote = None
        for path, remote_info, reason in remote_decisions:
            if remote_info and remote_info.get("capabilities"):
                # Check if this remote node has required capabilities
                if required_capabilities:
                    remote_caps = set(remote_info.get("capabilities", []))
                    required_set = set(required_capabilities)
                    if required_set.issubset(remote_caps):
                        ai_capable_remote = remote_info
                        break
                else:
                    ai_capable_remote = remote_info
                    break

        if ai_capable_remote:
            return MCPRoutingDecision(
                execute_locally=False,
                remote_node_info=ai_capable_remote,
                ai_capabilities=ai_capable_remote.get("capabilities", []),
                paths_involved=all_paths,
                reason=f"Remote AI node {ai_capable_remote['node_id']} has required capabilities",
            )

        # Default to local execution for mixed ownership
        return MCPRoutingDecision(
            execute_locally=True,
            paths_involved=all_paths,
            reason="Mixed ownership resolved to local execution",
        )

    async def execute_mcp_request(
        self, method: str, params: Dict, routing_decision: MCPRoutingDecision
    ) -> Dict[str, Any]:
        """
        Execute an MCP request either locally or remotely based on routing decision.
        """
        if routing_decision.is_local():
            return await self._execute_mcp_locally(method, params)
        else:
            return await self._execute_mcp_remotely(method, params, routing_decision)

    async def _execute_mcp_locally(self, method: str, params: Dict) -> Dict[str, Any]:
        """Execute MCP request locally."""
        # This would call the actual MCP handler locally
        # For now, return a placeholder response
        return {
            "status": "success",
            "method": method,
            "execution": "local",
            "result": "Local MCP execution placeholder",
        }

    async def _execute_mcp_remotely(
        self, method: str, params: Dict, routing_decision: MCPRoutingDecision
    ) -> Dict[str, Any]:
        """Execute MCP request on remote node."""
        try:
            remote_address = routing_decision.get_remote_address()
            if not remote_address:
                raise ValueError("No remote address for MCP execution")

            # Prepare MCP request for remote execution
            remote_request = {
                "cmd": "execute_mcp_request",
                "method": method,
                "params": params,
                "requesting_node": self.network_manager.node_id,
                "timestamp": asyncio.get_event_loop().time(),
            }

            # Send to remote node
            response = await self.network_manager._send_to_node(remote_address, remote_request)

            if not response:
                raise Exception("No response from remote node")

            if response.get("status") == "error":
                raise Exception(f"Remote MCP error: {response.get('error')}")

            return response

        except Exception as e:
            logger.error(f"Remote MCP execution error: {e}")
            # Fallback to local execution
            logger.info("Falling back to local MCP execution")
            return await self._execute_mcp_locally(method, params)

    def should_route_mcp_method(self, method: str) -> bool:
        """Check if an MCP method should be routed through P2P."""
        # Methods that typically involve file/directory access
        routable_methods = [
            "context/analyze",
            "context/scan",
            "context/gather",
            "codeguard/verify",
            "codeguard/analyze",
            "codeguard/scan",
            "files/read",
            "files/write",
            "files/list",
            "directory/scan",
            "directory/analyze",
        ]

        # Check if method matches any routable patterns
        for routable in routable_methods:
            if method.startswith(routable) or method == routable:
                return True

        return False

    def extract_ai_requirements_from_method(self, method: str, params: Dict) -> List[str]:
        """Extract required AI capabilities from MCP method and parameters."""
        capabilities = []

        # Method-based capability requirements
        if "analyze" in method:
            capabilities.append("analysis")
        if "generate" in method:
            capabilities.append("code_generation")
        if "debug" in method:
            capabilities.append("debugging")
        if "context" in method:
            capabilities.append("context_analysis")

        # Parameter-based capability requirements
        if "analysis_type" in params:
            analysis_type = params["analysis_type"]
            capabilities.append(f"analysis:{analysis_type}")

        if "generation_type" in params:
            gen_type = params["generation_type"]
            capabilities.append(f"generation:{gen_type}")

        return capabilities
