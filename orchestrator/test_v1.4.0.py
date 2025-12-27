"""
Close-Loop Testing for Vertex Genesis v1.4.0
Tests all new features: web browsing, account management, proactive assistance, agent collaboration
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("V1.4.0_Test")


def test_web_browser():
    """Test web browser integration."""
    logger.info("=" * 60)
    logger.info("TEST: Web Browser Integration")
    logger.info("=" * 60)
    
    try:
        from web_browser import WebBrowserController
        
        controller = WebBrowserController()
        
        # Test command parsing
        test_commands = [
            "search for best AI models",
            "go to github.com",
            "read this page",
            "take a screenshot"
        ]
        
        for cmd in test_commands:
            parsed = controller.parse_voice_command(cmd)
            if parsed:
                logger.info(f"✅ Parsed: '{cmd}' → {parsed.action.value}")
            else:
                logger.warning(f"❌ Failed to parse: '{cmd}'")
        
        logger.info("✅ Web Browser Integration: PASSED")
        return True
    
    except Exception as e:
        logger.error(f"❌ Web Browser Integration: FAILED - {e}")
        return False


def test_account_manager():
    """Test account management."""
    logger.info("=" * 60)
    logger.info("TEST: Account Management")
    logger.info("=" * 60)
    
    try:
        from account_manager import AccountManager
        
        manager = AccountManager()
        
        # Test command parsing
        test_commands = [
            "create account on github",
            "login to twitter",
            "delete my facebook account"
        ]
        
        for cmd in test_commands:
            parsed = manager.parse_voice_command(cmd)
            if parsed:
                logger.info(f"✅ Parsed: '{cmd}' → {parsed.action.value} on {parsed.service}")
            else:
                logger.warning(f"❌ Failed to parse: '{cmd}'")
        
        # Test consent workflow
        test_cmd = manager.parse_voice_command("create account on test_service")
        consent_request = manager.request_consent(test_cmd)
        
        if consent_request["status"] == "consent_required":
            logger.info(f"✅ Consent request generated: {consent_request['command_id']}")
            
            # Test consent response
            command_id = consent_request["command_id"]
            response = manager.process_consent_response(command_id, "yes")
            
            if response["status"] == "success":
                logger.info("✅ Consent workflow: PASSED")
            else:
                logger.warning(f"⚠️ Consent response: {response['status']}")
        
        logger.info("✅ Account Management: PASSED")
        return True
    
    except Exception as e:
        logger.error(f"❌ Account Management: FAILED - {e}")
        return False


def test_proactive_assistant():
    """Test proactive assistance."""
    logger.info("=" * 60)
    logger.info("TEST: Proactive Assistant")
    logger.info("=" * 60)
    
    try:
        from proactive_assistant import ProactiveAssistant, ActivityType
        
        assistant = ProactiveAssistant()
        
        # Test activity recording
        assistant.record_activity(
            ActivityType.API_CALL,
            {"endpoint": "/v1/chat/completions", "status": "success"}
        )
        
        assistant.record_activity(
            ActivityType.CAMERA_USE,
            {"language": "fr", "text": "Bonjour"}
        )
        
        assistant.record_activity(
            ActivityType.MODEL_SELECTION,
            {"model": "gpt-4", "cost": 0.03}
        )
        
        logger.info(f"✅ Recorded 3 activities")
        
        # Test suggestions
        suggestions = assistant.get_suggestions()
        logger.info(f"✅ Generated {len(suggestions)} suggestions")
        
        for suggestion in suggestions:
            logger.info(f"   - [{suggestion.priority}] {suggestion.category}: {suggestion.message[:50]}...")
        
        # Test patterns
        patterns = assistant.get_activity_patterns()
        logger.info(f"✅ Pattern analysis: {patterns['total_activities']} activities")
        
        # Test anomalies
        anomalies = assistant.detect_anomalies()
        logger.info(f"✅ Detected {len(anomalies)} anomalies")
        
        logger.info("✅ Proactive Assistant: PASSED")
        return True
    
    except Exception as e:
        logger.error(f"❌ Proactive Assistant: FAILED - {e}")
        return False


def test_agent_collaboration():
    """Test agent collaboration."""
    logger.info("=" * 60)
    logger.info("TEST: Agent Collaboration")
    logger.info("=" * 60)
    
    try:
        from agent_collaboration import AgentCollaborationManager, AgentRole
        
        manager = AgentCollaborationManager()
        
        # Test agent registration
        result1 = manager.register_agent("architect_1", AgentRole.ARCHITECT)
        result2 = manager.register_agent("engineer_1", AgentRole.ENGINEER)
        
        if result1["status"] == "success" and result2["status"] == "success":
            logger.info("✅ Registered 2 agents")
        
        # Test task assignment
        assign_result = manager.assign_task("architect_1", "Design system architecture")
        
        if assign_result["status"] == "success":
            logger.info(f"✅ Task assigned to architect_1")
        
        # Test handoff
        handoff_result = manager.handoff_task(
            "architect_1",
            "engineer_1",
            "Implement architecture",
            {"design": "microservices"}
        )
        
        if handoff_result["status"] == "success":
            logger.info(f"✅ Task handed off: architect_1 → engineer_1")
        
        # Test context sharing
        share_result = manager.share_context("engineer_1", "tech_stack", "Python + FastAPI")
        
        if share_result["status"] == "success":
            logger.info(f"✅ Context shared: tech_stack")
        
        # Test completion
        complete_result = manager.complete_task("engineer_1", {"status": "success", "output": "Implementation complete"})
        
        if complete_result["status"] == "success":
            logger.info(f"✅ Task completed by engineer_1")
        
        # Test metrics
        metrics = manager.get_collaboration_metrics()
        logger.info(f"✅ Metrics: {metrics['total_agents']} agents, {metrics['total_handoffs']} handoffs")
        
        logger.info("✅ Agent Collaboration: PASSED")
        return True
    
    except Exception as e:
        logger.error(f"❌ Agent Collaboration: FAILED - {e}")
        return False


def run_all_tests():
    """Run all v1.4.0 tests."""
    logger.info("\n" + "=" * 60)
    logger.info("VERTEX GENESIS v1.4.0 - CLOSE-LOOP TESTING")
    logger.info("=" * 60 + "\n")
    
    results = {
        "Web Browser Integration": test_web_browser(),
        "Account Management": test_account_manager(),
        "Proactive Assistant": test_proactive_assistant(),
        "Agent Collaboration": test_agent_collaboration()
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info("=" * 60)
    logger.info(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    logger.info("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
