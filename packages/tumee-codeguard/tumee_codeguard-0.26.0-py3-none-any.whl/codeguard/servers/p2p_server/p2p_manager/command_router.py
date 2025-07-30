"""
P2P Command Router

Routes CLI commands between local and remote execution based on AI ownership
and path management. Handles decision-making for when to execute locally vs
forward to remote P2P nodes.
"""

from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple

from ....utils.logging_config import get_logger
from .command_classifier import CommandClassifier, CommandInfo, P2PRequirement

logger = get_logger(__name__)


class RoutingDecision:
    """Represents a routing decision for a command."""

    def __init__(
        self,
        execute_locally: bool,
        remote_node_info: Optional[Dict] = None,
        ai_owner_info: Optional[Dict] = None,
        paths_checked: Optional[List[str]] = None,
        reason: str = "",
    ):
        self.execute_locally = execute_locally
        self.remote_node_info = remote_node_info
        self.ai_owner_info = ai_owner_info
        self.paths_checked = paths_checked or []
        self.reason = reason

    def is_local(self) -> bool:
        """Check if the command should be executed locally."""
        return self.execute_locally

    def is_remote(self) -> bool:
        """Check if the command should be executed remotely."""
        return not self.execute_locally

    def get_remote_address(self) -> Optional[str]:
        """Get the remote node address if routing remotely."""
        if self.remote_node_info:
            return self.remote_node_info.get("address")
        return None

    def get_streaming_port(self) -> Optional[int]:
        """Get the streaming port for remote execution."""
        if self.remote_node_info:
            return self.remote_node_info.get("streaming_port")
        return None


class CommandRouter:
    """Routes commands between local and remote execution based on ownership."""

    def __init__(self, network_manager=None):
        self.network_manager = network_manager
        self.classifier = CommandClassifier()
        self._local_fallback = True  # Fallback to local execution if P2P unavailable

    def set_network_manager(self, network_manager):
        """Set or update the network manager."""
        self.network_manager = network_manager

    async def route_command(
        self,
        progress_callback: Callable[..., Coroutine[Any, Any, None]],
        command_name: str,
        subcommand: Optional[str] = None,
        args: Optional[Dict] = None,
    ) -> RoutingDecision:
        """
        Determine how to route a command: local vs remote execution.

        Args:
            command_name: Main command name (e.g., "verify", "context")
            subcommand: Subcommand if applicable (e.g., "analyze" for "context analyze")
            args: Command arguments dictionary

        Returns:
            RoutingDecision with execution details
        """
        args = args or {}

        # Classify the command
        command_info = self.classifier.classify_command(command_name, subcommand)

        # If command never uses P2P, execute locally
        if command_info.p2p_requirement == P2PRequirement.NEVER:
            return RoutingDecision(
                execute_locally=True, reason="Command doesn't require P2P routing"
            )

        # If no network manager available, execute locally
        if not self.network_manager:
            await progress_callback(
                component_event="update",
                component_id="routing",
                current=100,
                message="No P2P network manager available, executing locally",
            )
            return RoutingDecision(execute_locally=True, reason="No P2P network manager available")

        # Extract paths from command arguments
        paths = self.classifier.extract_paths_from_args(command_info, args)
        logger.debug(
            f"P2P routing for {command_name} {subcommand or ''}: extracted paths = {paths}, node_id = {getattr(self.network_manager, 'node_id', 'UNKNOWN')}"
        )

        if not paths:
            # No paths to check, execute locally
            logger.debug("No paths extracted, executing locally")
            return RoutingDecision(
                execute_locally=True, reason="No paths specified for ownership checking"
            )

        # For priority 0 workers, wait for hierarchy before routing
        if (
            hasattr(self.network_manager, "discovery_priority")
            and self.network_manager.discovery_priority == 0
        ):
            await progress_callback(
                component_event="update",
                component_id="routing",
                current=20,
                message="Waiting for P2P hierarchy from broker...",
            )
            hierarchy_manager = getattr(
                self.network_manager.topology_manager, "hierarchy_manager", None
            )

            if hierarchy_manager:
                hierarchy_received = await hierarchy_manager.wait_for_hierarchy(timeout_seconds=2.0)

                if not hierarchy_received:
                    # No hierarchy received - P2P network unavailable, fall back to local
                    await progress_callback(
                        component_event="update",
                        component_id="routing",
                        current=100,
                        message="No P2P hierarchy available, falling back to local execution",
                    )
                    return RoutingDecision(
                        execute_locally=True,
                        reason="No P2P hierarchy available - falling back to local",
                    )
                else:
                    await progress_callback(
                        component_event="update",
                        component_id="routing",
                        current=40,
                        message="P2P hierarchy received, checking path ownership...",
                    )
            else:
                await progress_callback(
                    component_event="update",
                    component_id="routing",
                    current=100,
                    message="No hierarchy manager available, falling back to local execution",
                )
                return RoutingDecision(
                    execute_locally=True, reason="No hierarchy manager available"
                )

        # Check ownership for each path
        routing_decisions = []
        for i, path in enumerate(paths):
            logger.debug(f"Checking ownership for path: {path}")
            decision = await self._check_path_ownership(path, command_info)
            logger.debug(f"Decision for {path}: local={decision[0]}, reason='{decision[2]}'")
            routing_decisions.append((path, decision))

            # Update progress as we check paths
            progress = 40 + int((i + 1) / len(paths) * 40)  # 40-80% range
            await progress_callback(
                component_event="update",
                component_id="routing",
                current=progress,
                message=f"Checked ownership for {i + 1}/{len(paths)} paths",
            )

        # Determine final routing decision
        return await self._consolidate_routing_decisions(
            progress_callback, routing_decisions, command_info, paths, args
        )

    async def _check_path_ownership(
        self, path: str, command_info: CommandInfo
    ) -> Tuple[bool, Optional[Dict], str]:
        """
        Check ownership for a single path.

        Returns:
            Tuple of (is_local, remote_info, reason)
        """
        logger.debug(f"Checking ownership for path: {path}")
        try:
            # Check if we have local AI ownership
            if not self.network_manager:
                return True, None, "No network manager available - executing locally"
            local_ai_owner = self.network_manager.get_ai_owner_for_path(path)
            logger.debug(f"Local AI owner for {path}: {local_ai_owner}")
            if local_ai_owner:
                logger.debug(f"Found local AI ownership for {path}")
                return True, None, f"Local AI ownership for {path}"

            # Check for remote AI ownership
            path_abs = str(Path(path).absolute())
            logger.debug(f"Querying remote AI ownership for {path} (abs: {path_abs})")
            remote_ai_owner = await self.network_manager.query_ai_ownership(path_abs)
            logger.debug(f"Remote AI owner for {path}: {remote_ai_owner}")
            if remote_ai_owner and remote_ai_owner.get("node_id") != self.network_manager.node_id:
                logger.debug(
                    f"Found remote AI ownership for {path} by node {remote_ai_owner.get('node_id')}"
                )
                return False, remote_ai_owner, f"Remote AI ownership for {path}"

            # Check basic path ownership (non-AI)
            logger.debug(f"Checking basic path ownership for {path_abs}")
            path_owner = self.network_manager.find_owner(path_abs)
            logger.debug(f"Path owner for {path}: {path_owner}")
            if path_owner and path_owner.node_id != self.network_manager.node_id:
                # Remote ownership but no AI capability
                remote_info = {
                    "node_id": path_owner.node_id,
                    "address": path_owner.address,
                    "streaming_port": None,  # Basic P2P node may not have streaming
                    "token": None,  # Will be provided by worker directory service
                }
                logger.debug(f"Found remote path ownership for {path} by node {path_owner.node_id}")
                return False, remote_info, f"Remote path ownership for {path}"

            # We own this path or it's unmanaged
            logger.debug(f"Path {path} is local or unmanaged")
            return True, None, f"Local ownership or unmanaged path: {path}"

        except Exception as e:
            logger.warning(f"Error checking ownership for {path}: {e}")
            return True, None, f"Error checking ownership, defaulting to local: {e}"

    async def _consolidate_routing_decisions(
        self,
        progress_callback: Callable[..., Coroutine[Any, Any, None]],
        path_decisions: List[Tuple[str, Tuple[bool, Optional[Dict], str]]],
        command_info: CommandInfo,
        all_paths: List[str],
        args: Optional[Dict] = None,
    ) -> RoutingDecision:
        """
        Consolidate multiple path ownership decisions into a single routing decision.
        """
        logger.debug(
            f"Consolidating routing decisions for {len(path_decisions)} paths: {[p[0] for p in path_decisions]}"
        )
        local_paths = []
        remote_decisions = []

        for path, (is_local, remote_info, reason) in path_decisions:
            logger.debug(f"Path {path}: local={is_local}, reason='{reason}'")
            if is_local:
                local_paths.append(path)
            else:
                remote_decisions.append((path, remote_info, reason))

        logger.debug(
            f"Decision summary: {len(local_paths)} local paths, {len(remote_decisions)} remote paths"
        )

        # If all paths are local, execute locally
        if not remote_decisions:
            logger.debug("All paths are local, executing locally")
            await progress_callback(
                component_event="update",
                component_id="routing",
                current=100,
                message="All paths are local, executing locally",
            )
            return RoutingDecision(
                execute_locally=True,
                paths_checked=all_paths,
                reason="All paths have local ownership",
            )

        # If all paths are remote and owned by the same node, execute remotely
        if not local_paths and len(set(d[1]["node_id"] for d in remote_decisions)) == 1:
            remote_info = remote_decisions[0][1]
            # Report P2P connection established via progress callback
            await progress_callback(
                component_event="update",
                component_id="routing",
                current=100,
                message=f"🌐 Executing on remote node {remote_info['node_id']}",
            )
            return RoutingDecision(
                execute_locally=False,
                remote_node_info=remote_info,
                paths_checked=all_paths,
                reason=f"All paths owned by remote node {remote_info['node_id']}",
            )

        # Mixed ownership or multiple remote nodes
        return await self._handle_mixed_ownership(
            progress_callback, local_paths, remote_decisions, command_info, all_paths
        )

    async def _handle_mixed_ownership(
        self,
        progress_callback: Callable[..., Coroutine[Any, Any, None]],
        local_paths: List[str],
        remote_decisions: List[Tuple[str, Dict, str]],
        command_info: CommandInfo,
        all_paths: List[str],
    ) -> RoutingDecision:
        """Handle cases where paths have mixed local/remote ownership."""

        # For required P2P commands, we need to be more careful
        if command_info.p2p_requirement == P2PRequirement.REQUIRED:

            # If there's only one remote node and it has AI capabilities, prefer it
            remote_nodes = {d[1]["node_id"]: d[1] for _, d, _ in remote_decisions}
            if len(remote_nodes) == 1:
                remote_info = list(remote_nodes.values())[0]
                if remote_info.get("ai_enabled") or remote_info.get("capabilities"):
                    return RoutingDecision(
                        execute_locally=False,
                        remote_node_info=remote_info,
                        paths_checked=all_paths,
                        reason="Single remote node with AI capabilities handles mixed ownership",
                    )

        # Default: execute locally and let the command handle remote paths as needed
        return RoutingDecision(
            execute_locally=True,
            paths_checked=all_paths,
            reason="Mixed ownership resolved to local execution with remote delegation",
        )

    async def check_ai_capability_routing(
        self, paths: List[str], required_capability: str
    ) -> RoutingDecision:
        """
        Route based on AI capability requirements rather than just ownership.

        Args:
            paths: Paths that need the capability
            required_capability: Required AI capability (e.g., "analysis", "debugging")

        Returns:
            RoutingDecision for capability-based routing
        """
        if not self.network_manager:
            return RoutingDecision(
                execute_locally=True, reason="No network manager for capability checking"
            )

        # Check each path for the required capability
        capable_nodes = {}

        for path in paths:
            # Check local capability
            if self.network_manager.has_ai_capability_for_path(path, required_capability):
                capable_nodes[self.network_manager.node_id] = {
                    "node_id": self.network_manager.node_id,
                    "address": f"{self.network_manager.get_local_ip()}:{self.network_manager.port}",
                    "streaming_port": self.network_manager.streaming_port,
                    "local": True,
                }
                continue

            # Check remote capability
            path_abs = str(Path(path).absolute())
            remote_ai_owner = await self.network_manager.query_ai_ownership(path_abs)
            if remote_ai_owner and required_capability in remote_ai_owner.get("capabilities", []):
                node_id = remote_ai_owner["node_id"]
                capable_nodes[node_id] = remote_ai_owner

        if not capable_nodes:
            return RoutingDecision(
                execute_locally=True,
                paths_checked=paths,
                reason=f"No nodes found with required capability: {required_capability}",
            )

        # Prefer local execution if we have the capability
        local_node_id = self.network_manager.node_id
        if local_node_id in capable_nodes:
            return RoutingDecision(
                execute_locally=True,
                ai_owner_info=capable_nodes[local_node_id],
                paths_checked=paths,
                reason=f"Local node has required capability: {required_capability}",
            )

        # Route to the first capable remote node
        remote_node = list(capable_nodes.values())[0]
        return RoutingDecision(
            execute_locally=False,
            remote_node_info=remote_node,
            ai_owner_info=remote_node,
            paths_checked=paths,
            reason=f"Remote node {remote_node['node_id']} has required capability: {required_capability}",
        )

    def enable_local_fallback(self, enable: bool = True):
        """Enable or disable fallback to local execution when P2P is unavailable."""
        self._local_fallback = enable

    def should_use_streaming(self, command_name: str, subcommand: Optional[str] = None) -> bool:
        """Check if a command should use streaming for remote execution."""
        return self.classifier.needs_streaming(command_name, subcommand)

    async def get_preferred_node_for_paths(self, paths: List[str]) -> Optional[Dict]:
        """
        Get the preferred node for executing commands on the given paths.

        Returns the node info if a single node is preferred, None if mixed.
        """
        if not self.network_manager or not paths:
            return None

        node_votes = {}  # node_id -> count of paths it owns

        for path in paths:
            # Check AI ownership first (higher priority)
            ai_owner = await self.network_manager.query_ai_ownership(path)
            if ai_owner:
                node_id = ai_owner["node_id"]
                node_votes[node_id] = node_votes.get(node_id, 0) + 2  # AI ownership gets 2 votes
                continue

            # Check basic path ownership
            path_abs = str(Path(path).absolute())
            path_owner = self.network_manager.find_owner(path_abs)
            if path_owner:
                node_id = path_owner.node_id
                node_votes[node_id] = node_votes.get(node_id, 0) + 1  # Basic ownership gets 1 vote

        if not node_votes:
            return None

        # Find the node with the most votes
        preferred_node_id = max(node_votes.keys(), key=lambda k: node_votes[k])

        # If it's our node, return local info
        if preferred_node_id == self.network_manager.node_id:
            return {
                "node_id": self.network_manager.node_id,
                "address": f"{self.network_manager.get_local_ip()}:{self.network_manager.port}",
                "streaming_port": self.network_manager.streaming_port,
                "local": True,
            }

        # Look for the remote node info
        for path in paths:
            ai_owner = await self.network_manager.query_ai_ownership(path)
            if ai_owner and ai_owner["node_id"] == preferred_node_id:
                return ai_owner

        return None
