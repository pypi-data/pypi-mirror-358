"""
Pydantic models for P2P network communication.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class NodeMode(Enum):
    """P2P node operational modes."""

    SERVER = (
        "server"  # Server node - can create workers, handle general commands, can be elected broker
    )
    WORKER = "worker"  # Worker node - executes commands only, cannot create workers or be broker
    MONITOR = (
        "monitor"  # Monitor node - observes network, can be elected broker if no servers available
    )
    LOCAL = "local"  # Local node - operates independently without P2P network participation


class NodeInfo(BaseModel):
    """Information about a P2P network node with project boundaries."""

    node_id: str
    address: str
    managed_paths: List[str]  # Multiple root paths this node manages
    boundaries: Dict[str, List[Dict]]  # Boundaries keyed by managed path root
    parent: Optional[str] = None
    timestamp: float


class P2PMessage(BaseModel):
    """Base message structure for P2P communication."""

    cmd: str
    node_id: str
    timestamp: Optional[float] = Field(default_factory=lambda: datetime.now().timestamp())


class DiscoveryAnnouncement(P2PMessage):
    """UDP broadcast announcement for node discovery with project boundaries."""

    cmd: str = "announce"
    address: str
    managed_paths: List[str]  # Multiple root paths this node manages
    boundaries: Dict[str, List[Dict]]  # Boundaries keyed by managed path root
    parent: Optional[str] = None
    discovery_priority: int = Field(
        default=0,
        description="Discovery service priority (0=worker, 50=monitor, 100=dedicated server)",
    )


class DiscoveryBrokerAnnouncement(P2PMessage):
    """Announcement from a discovery broker about its status."""

    cmd: str = "broker_announce"
    broker_priority: int = Field(description="Discovery broker priority")
    broker_address: str = Field(description="Address of the discovery broker")
    active_since: float = Field(description="Timestamp when broker became active")


class DiscoveryTakeoverRequest(P2PMessage):
    """Request to take over discovery broker role."""

    cmd: str = "takeover_request"
    requester_priority: int = Field(description="Priority of the requesting service")
    requester_address: str = Field(description="Address of the requesting service")


class DiscoveryTakeoverResponse(P2PMessage):
    """Response to discovery takeover request."""

    cmd: str = "takeover_response"
    approved: bool = Field(description="Whether takeover is approved")
    current_broker_priority: int = Field(description="Current broker's priority")
    handover_delay: float = Field(default=0.2, description="Seconds to wait before taking over")


class RegistrationRequest(P2PMessage):
    """Request to register as a child node."""

    cmd: str = "register_child"
    address: str
    paths: List[str]
    boundaries: Dict[str, List[Dict]] = Field(default_factory=dict)


class NewParentNotification(P2PMessage):
    """Notification of a new parent in the hierarchy."""

    cmd: str = "new_parent"
    parent_node_id: str
    parent_address: str
    parent_path: str


class PathQuery(P2PMessage):
    """Query for path ownership."""

    cmd: str = "query_path"
    path: str


class PathQueryResponse(BaseModel):
    """Response to path ownership query."""

    root_owner: Optional[str] = None
    root_address: Optional[str] = None
    root_path: Optional[str] = None
    specific_handler: Optional[Dict[str, str]] = None
    should_start_delegate: Optional[str] = None
    error: Optional[str] = None


class PingMessage(P2PMessage):
    """Health check ping message."""

    cmd: str = "ping"


class PongResponse(BaseModel):
    """Response to ping message."""

    pong: bool = True


class StatusResponse(BaseModel):
    """Generic status response."""

    status: str
    message: Optional[str] = None
