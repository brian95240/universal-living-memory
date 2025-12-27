"""
Agent Collaboration Enhancement
Vertex Genesis v1.4.0

Enhances multi-agent collaboration with:
- Agent handoff protocol
- Shared context management
- Parallel model usage via seat router
- Collaboration metrics
- Agent communication protocol
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent role types."""
    ARCHITECT = "architect"
    ENGINEER = "engineer"
    RESEARCHER = "researcher"
    REVIEWER = "reviewer"
    COORDINATOR = "coordinator"


class AgentStatus(Enum):
    """Agent status."""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentState:
    """Agent state representation."""
    agent_id: str
    role: AgentRole
    status: AgentStatus
    current_task: Optional[str] = None
    assigned_seat: Optional[int] = None
    context: Dict[str, Any] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class Handoff:
    """Agent handoff representation."""
    from_agent: str
    to_agent: str
    task: str
    context: Dict[str, Any]
    timestamp: float
    status: str = "pending"


class AgentCollaborationManager:
    """
    Manages multi-agent collaboration with enhanced features.
    """
    
    def __init__(self, memory_engine=None, seat_router=None):
        self.memory_engine = memory_engine
        self.seat_router = seat_router
        self.agents: Dict[str, AgentState] = {}
        self.handoffs: List[Handoff] = []
        self.shared_context: Dict[str, Any] = {}
        self.collaboration_metrics: Dict[str, Any] = {}
        
        logger.info("🤝 Agent Collaboration Manager initialized")
    
    def register_agent(self, agent_id: str, role: AgentRole) -> Dict[str, Any]:
        """
        Register agent in collaboration system.
        
        Args:
            agent_id: Unique agent identifier
            role: Agent role
            
        Returns:
            Registration result
        """
        if agent_id in self.agents:
            return {
                "status": "error",
                "message": f"Agent {agent_id} already registered"
            }
        
        self.agents[agent_id] = AgentState(
            agent_id=agent_id,
            role=role,
            status=AgentStatus.IDLE,
            context={}
        )
        
        logger.info(f"✅ Agent registered: {agent_id} ({role.value})")
        
        return {
            "status": "success",
            "agent_id": agent_id,
            "role": role.value,
            "message": f"Agent {agent_id} registered successfully"
        }
    
    def assign_task(self, agent_id: str, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Assign task to agent.
        
        Args:
            agent_id: Agent identifier
            task: Task description
            context: Optional task context
            
        Returns:
            Assignment result
        """
        if agent_id not in self.agents:
            return {
                "status": "error",
                "message": f"Agent {agent_id} not found"
            }
        
        agent = self.agents[agent_id]
        
        # Update agent state
        agent.current_task = task
        agent.status = AgentStatus.WORKING
        agent.start_time = time.time()
        
        # Merge context
        if context:
            agent.context.update(context)
        
        # Assign seat via seat router if available
        if self.seat_router:
            try:
                seat_result = self.seat_router.assign_seat(task)
                agent.assigned_seat = seat_result.get("seat_id")
                logger.info(f"✅ Seat {agent.assigned_seat} assigned to {agent_id}")
            except Exception as e:
                logger.warning(f"Seat assignment failed: {e}")
        
        logger.info(f"📋 Task assigned to {agent_id}: {task}")
        
        return {
            "status": "success",
            "agent_id": agent_id,
            "task": task,
            "assigned_seat": agent.assigned_seat,
            "message": f"Task assigned to {agent_id}"
        }
    
    def handoff_task(self, from_agent: str, to_agent: str, task: str, 
                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Hand off task from one agent to another.
        
        Args:
            from_agent: Source agent ID
            to_agent: Target agent ID
            task: Task description
            context: Handoff context
            
        Returns:
            Handoff result
        """
        if from_agent not in self.agents or to_agent not in self.agents:
            return {
                "status": "error",
                "message": "One or both agents not found"
            }
        
        # Create handoff
        handoff = Handoff(
            from_agent=from_agent,
            to_agent=to_agent,
            task=task,
            context=context or {},
            timestamp=time.time(),
            status="pending"
        )
        
        self.handoffs.append(handoff)
        
        # Update agent states
        source_agent = self.agents[from_agent]
        target_agent = self.agents[to_agent]
        
        source_agent.status = AgentStatus.WAITING
        source_agent.end_time = time.time()
        
        # Transfer context via shared memory if available
        if self.memory_engine:
            try:
                # Store handoff context in memory
                self.memory_engine.store(
                    text=f"Handoff from {from_agent} to {to_agent}: {task}",
                    metadata={
                        "type": "handoff",
                        "from_agent": from_agent,
                        "to_agent": to_agent,
                        "task": task,
                        "context": context
                    }
                )
                logger.info(f"✅ Handoff context stored in memory")
            except Exception as e:
                logger.warning(f"Memory storage failed: {e}")
        
        # Assign task to target agent
        self.assign_task(to_agent, task, context)
        
        handoff.status = "completed"
        
        logger.info(f"🤝 Task handed off: {from_agent} → {to_agent}")
        
        return {
            "status": "success",
            "from_agent": from_agent,
            "to_agent": to_agent,
            "task": task,
            "handoff_id": len(self.handoffs) - 1,
            "message": f"Task handed off from {from_agent} to {to_agent}"
        }
    
    def share_context(self, agent_id: str, context_key: str, context_value: Any) -> Dict[str, Any]:
        """
        Share context across all agents.
        
        Args:
            agent_id: Agent sharing the context
            context_key: Context key
            context_value: Context value
            
        Returns:
            Share result
        """
        if agent_id not in self.agents:
            return {
                "status": "error",
                "message": f"Agent {agent_id} not found"
            }
        
        # Store in shared context
        self.shared_context[context_key] = {
            "value": context_value,
            "shared_by": agent_id,
            "timestamp": time.time()
        }
        
        # Store in memory engine if available
        if self.memory_engine:
            try:
                self.memory_engine.store(
                    text=f"Shared context: {context_key}",
                    metadata={
                        "type": "shared_context",
                        "key": context_key,
                        "value": context_value,
                        "shared_by": agent_id
                    }
                )
            except Exception as e:
                logger.warning(f"Memory storage failed: {e}")
        
        logger.info(f"📤 Context shared by {agent_id}: {context_key}")
        
        return {
            "status": "success",
            "agent_id": agent_id,
            "context_key": context_key,
            "message": f"Context shared: {context_key}"
        }
    
    def get_shared_context(self, context_key: str) -> Optional[Any]:
        """
        Get shared context value.
        
        Args:
            context_key: Context key
            
        Returns:
            Context value or None
        """
        if context_key in self.shared_context:
            return self.shared_context[context_key]["value"]
        return None
    
    def complete_task(self, agent_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mark agent task as completed.
        
        Args:
            agent_id: Agent identifier
            result: Task result
            
        Returns:
            Completion result
        """
        if agent_id not in self.agents:
            return {
                "status": "error",
                "message": f"Agent {agent_id} not found"
            }
        
        agent = self.agents[agent_id]
        agent.status = AgentStatus.COMPLETED
        agent.end_time = time.time()
        
        # Calculate task duration
        duration = agent.end_time - agent.start_time if agent.start_time else 0
        
        # Release seat if assigned
        if agent.assigned_seat and self.seat_router:
            try:
                self.seat_router.unload_seat(agent.assigned_seat)
                logger.info(f"✅ Seat {agent.assigned_seat} released")
            except Exception as e:
                logger.warning(f"Seat release failed: {e}")
        
        # Update metrics
        self._update_metrics(agent_id, duration, result)
        
        logger.info(f"✅ Task completed by {agent_id} (duration: {duration:.2f}s)")
        
        return {
            "status": "success",
            "agent_id": agent_id,
            "duration_seconds": duration,
            "result": result,
            "message": f"Task completed by {agent_id}"
        }
    
    def _update_metrics(self, agent_id: str, duration: float, result: Dict[str, Any]):
        """Update collaboration metrics."""
        if agent_id not in self.collaboration_metrics:
            self.collaboration_metrics[agent_id] = {
                "total_tasks": 0,
                "total_duration": 0,
                "successful_tasks": 0,
                "failed_tasks": 0
            }
        
        metrics = self.collaboration_metrics[agent_id]
        metrics["total_tasks"] += 1
        metrics["total_duration"] += duration
        
        if result.get("status") == "success":
            metrics["successful_tasks"] += 1
        else:
            metrics["failed_tasks"] += 1
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent status.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent status dictionary or None
        """
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        
        return {
            "agent_id": agent.agent_id,
            "role": agent.role.value,
            "status": agent.status.value,
            "current_task": agent.current_task,
            "assigned_seat": agent.assigned_seat,
            "context_keys": list(agent.context.keys()),
            "start_time": agent.start_time,
            "end_time": agent.end_time
        }
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get status of all agents."""
        return [self.get_agent_status(agent_id) for agent_id in self.agents.keys()]
    
    def get_collaboration_metrics(self) -> Dict[str, Any]:
        """Get collaboration metrics."""
        total_handoffs = len(self.handoffs)
        successful_handoffs = len([h for h in self.handoffs if h.status == "completed"])
        
        return {
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.status == AgentStatus.WORKING]),
            "total_handoffs": total_handoffs,
            "successful_handoffs": successful_handoffs,
            "shared_context_keys": len(self.shared_context),
            "agent_metrics": self.collaboration_metrics
        }
    
    def get_handoff_history(self) -> List[Dict[str, Any]]:
        """Get handoff history."""
        return [
            {
                "from_agent": h.from_agent,
                "to_agent": h.to_agent,
                "task": h.task,
                "timestamp": h.timestamp,
                "status": h.status
            }
            for h in self.handoffs
        ]
    
    def clear_completed_agents(self):
        """Clear completed agents from active list."""
        completed = [aid for aid, agent in self.agents.items() 
                    if agent.status == AgentStatus.COMPLETED]
        
        for agent_id in completed:
            del self.agents[agent_id]
        
        logger.info(f"🗑️ Cleared {len(completed)} completed agents")


# Singleton instance
_collaboration_manager = None


def get_collaboration_manager(memory_engine=None, seat_router=None) -> AgentCollaborationManager:
    """Get singleton collaboration manager instance."""
    global _collaboration_manager
    if not _collaboration_manager:
        _collaboration_manager = AgentCollaborationManager(memory_engine, seat_router)
    return _collaboration_manager
