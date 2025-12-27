"""
Proactive Assistant
Vertex Genesis v1.4.0

Monitors user activity and provides proactive assistance:
- Activity pattern detection
- Context-aware suggestions
- Automatic task triggers
- Anomaly detection
- Predictive assistance
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)


class ActivityType(Enum):
    """User activity types."""
    API_CALL = "api_call"
    VOICE_COMMAND = "voice_command"
    CAMERA_USE = "camera_use"
    BROWSER_ACTION = "browser_action"
    ACCOUNT_ACTION = "account_action"
    MODEL_SELECTION = "model_selection"
    IDLE = "idle"


@dataclass
class Activity:
    """User activity record."""
    timestamp: float
    activity_type: ActivityType
    details: Dict[str, Any]
    context: Optional[str] = None


@dataclass
class Suggestion:
    """Proactive suggestion."""
    priority: int  # 1-5, 5 = highest
    category: str
    message: str
    action: Optional[str] = None
    parameters: Dict[str, Any] = None


class ProactiveAssistant:
    """
    Proactive assistant that monitors activity and provides suggestions.
    """
    
    def __init__(self, max_history: int = 1000):
        self.activity_history: deque = deque(maxlen=max_history)
        self.patterns: Dict[str, Any] = {}
        self.suggestions: List[Suggestion] = []
        self.last_activity_time: float = time.time()
        self.monitoring_enabled: bool = True
        
        logger.info("🤖 Proactive Assistant initialized")
    
    def record_activity(self, activity_type: ActivityType, details: Dict[str, Any], 
                       context: Optional[str] = None):
        """
        Record user activity.
        
        Args:
            activity_type: Type of activity
            details: Activity details
            context: Optional context string
        """
        if not self.monitoring_enabled:
            return
        
        activity = Activity(
            timestamp=time.time(),
            activity_type=activity_type,
            details=details,
            context=context
        )
        
        self.activity_history.append(activity)
        self.last_activity_time = activity.timestamp
        
        # Analyze patterns and generate suggestions
        self._analyze_activity(activity)
    
    def _analyze_activity(self, activity: Activity):
        """Analyze activity and generate suggestions."""
        
        # Check for repeated actions
        self._check_repeated_actions(activity)
        
        # Check for inefficient workflows
        self._check_inefficient_workflows(activity)
        
        # Check for foreign language detection
        if activity.activity_type == ActivityType.CAMERA_USE:
            self._check_foreign_language(activity)
        
        # Check for cost opportunities
        if activity.activity_type == ActivityType.MODEL_SELECTION:
            self._check_cost_optimization(activity)
    
    def _check_repeated_actions(self, activity: Activity):
        """Check for repeated actions that could be automated."""
        # Get recent activities of same type
        recent = [a for a in list(self.activity_history)[-10:] 
                 if a.activity_type == activity.activity_type]
        
        if len(recent) >= 3:
            # Check if similar actions
            similar_count = 0
            for act in recent[-3:]:
                if self._are_similar(act.details, activity.details):
                    similar_count += 1
            
            if similar_count >= 2:
                self.suggestions.append(Suggestion(
                    priority=4,
                    category="automation",
                    message=f"I notice you've repeated this {activity.activity_type.value} action. Would you like me to automate it?",
                    action="create_automation",
                    parameters={"activity_type": activity.activity_type.value}
                ))
    
    def _check_inefficient_workflows(self, activity: Activity):
        """Check for inefficient workflows."""
        # Get last 5 activities
        recent = list(self.activity_history)[-5:]
        
        # Check for camera → model selection pattern
        if len(recent) >= 2:
            if (recent[-2].activity_type == ActivityType.CAMERA_USE and 
                activity.activity_type == ActivityType.MODEL_SELECTION):
                
                self.suggestions.append(Suggestion(
                    priority=3,
                    category="efficiency",
                    message="I can automatically select the best model for camera tasks. Enable context-aware camera?",
                    action="enable_context_camera",
                    parameters={}
                ))
    
    def _check_foreign_language(self, activity: Activity):
        """Check for foreign language in camera activity."""
        # Check if OCR detected non-English text
        if activity.details.get("language") and activity.details["language"] != "en":
            lang = activity.details["language"]
            
            self.suggestions.append(Suggestion(
                priority=5,
                category="translation",
                message=f"I detected {lang} text. Would you like me to translate it?",
                action="translate_text",
                parameters={"language": lang, "text": activity.details.get("text")}
            ))
    
    def _check_cost_optimization(self, activity: Activity):
        """Check for cost optimization opportunities."""
        model = activity.details.get("model")
        cost = activity.details.get("cost", 0)
        
        if cost > 0:
            self.suggestions.append(Suggestion(
                priority=5,
                category="cost",
                message=f"⚠️ You selected a paid model ({model}, ${cost}/1k tokens). I found free alternatives with similar quality. Switch?",
                action="suggest_free_alternative",
                parameters={"current_model": model}
            ))
    
    def _are_similar(self, details1: Dict[str, Any], details2: Dict[str, Any]) -> bool:
        """Check if two activity details are similar."""
        # Simple similarity check based on common keys
        common_keys = set(details1.keys()) & set(details2.keys())
        
        if not common_keys:
            return False
        
        similar_count = 0
        for key in common_keys:
            if details1[key] == details2[key]:
                similar_count += 1
        
        return similar_count / len(common_keys) > 0.7
    
    def get_suggestions(self, priority_threshold: int = 3) -> List[Suggestion]:
        """
        Get proactive suggestions.
        
        Args:
            priority_threshold: Minimum priority (1-5)
            
        Returns:
            List of suggestions
        """
        # Filter by priority and sort
        filtered = [s for s in self.suggestions if s.priority >= priority_threshold]
        filtered.sort(key=lambda s: s.priority, reverse=True)
        
        return filtered
    
    def clear_suggestions(self):
        """Clear all suggestions."""
        self.suggestions = []
        logger.info("🗑️ Suggestions cleared")
    
    def detect_idle(self, idle_threshold: int = 300) -> bool:
        """
        Detect if user is idle.
        
        Args:
            idle_threshold: Idle threshold in seconds (default 5 minutes)
            
        Returns:
            True if idle
        """
        idle_time = time.time() - self.last_activity_time
        return idle_time > idle_threshold
    
    def get_activity_patterns(self) -> Dict[str, Any]:
        """
        Analyze activity patterns.
        
        Returns:
            Pattern analysis dictionary
        """
        if not self.activity_history:
            return {"error": "No activity history"}
        
        # Count activities by type
        type_counts = {}
        for activity in self.activity_history:
            type_name = activity.activity_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # Calculate activity frequency
        time_span = time.time() - self.activity_history[0].timestamp
        frequency = len(self.activity_history) / (time_span / 60)  # per minute
        
        # Find most common activity
        most_common = max(type_counts.items(), key=lambda x: x[1])
        
        # Calculate idle periods
        idle_periods = []
        for i in range(1, len(self.activity_history)):
            gap = self.activity_history[i].timestamp - self.activity_history[i-1].timestamp
            if gap > 60:  # More than 1 minute
                idle_periods.append(gap)
        
        avg_idle = sum(idle_periods) / len(idle_periods) if idle_periods else 0
        
        return {
            "total_activities": len(self.activity_history),
            "time_span_minutes": time_span / 60,
            "frequency_per_minute": frequency,
            "activity_counts": type_counts,
            "most_common_activity": most_common[0],
            "most_common_count": most_common[1],
            "idle_periods_count": len(idle_periods),
            "average_idle_seconds": avg_idle
        }
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """
        Detect anomalous activity patterns.
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check for sudden spike in activity
        if len(self.activity_history) >= 10:
            recent_10 = list(self.activity_history)[-10:]
            time_span = recent_10[-1].timestamp - recent_10[0].timestamp
            
            if time_span < 60:  # 10 activities in less than 1 minute
                anomalies.append({
                    "type": "activity_spike",
                    "message": "Detected unusual spike in activity (10 actions in <1 minute)",
                    "severity": "medium"
                })
        
        # Check for repeated errors
        recent_errors = [a for a in list(self.activity_history)[-20:] 
                        if a.details.get("status") == "error"]
        
        if len(recent_errors) >= 3:
            anomalies.append({
                "type": "repeated_errors",
                "message": f"Detected {len(recent_errors)} errors in recent activity",
                "severity": "high"
            })
        
        # Check for unusual cost
        recent_costs = [a for a in list(self.activity_history)[-10:] 
                       if a.details.get("cost", 0) > 0]
        
        if recent_costs:
            anomalies.append({
                "type": "unexpected_cost",
                "message": f"Detected {len(recent_costs)} paid operations (expected $0)",
                "severity": "critical"
            })
        
        return anomalies
    
    def enable_monitoring(self):
        """Enable activity monitoring."""
        self.monitoring_enabled = True
        logger.info("✅ Activity monitoring enabled")
    
    def disable_monitoring(self):
        """Disable activity monitoring."""
        self.monitoring_enabled = False
        logger.info("⏸️ Activity monitoring disabled")
    
    def get_status(self) -> Dict[str, Any]:
        """Get assistant status."""
        return {
            "monitoring_enabled": self.monitoring_enabled,
            "activity_count": len(self.activity_history),
            "suggestion_count": len(self.suggestions),
            "last_activity_time": self.last_activity_time,
            "idle": self.detect_idle(),
            "idle_seconds": time.time() - self.last_activity_time
        }


# Singleton instance
_proactive_assistant = None


def get_proactive_assistant() -> ProactiveAssistant:
    """Get singleton proactive assistant instance."""
    global _proactive_assistant
    if not _proactive_assistant:
        _proactive_assistant = ProactiveAssistant()
    return _proactive_assistant


def record_activity(activity_type: ActivityType, details: Dict[str, Any], 
                   context: Optional[str] = None):
    """Record user activity."""
    assistant = get_proactive_assistant()
    assistant.record_activity(activity_type, details, context)


def get_suggestions(priority_threshold: int = 3) -> List[Suggestion]:
    """Get proactive suggestions."""
    assistant = get_proactive_assistant()
    return assistant.get_suggestions(priority_threshold)
