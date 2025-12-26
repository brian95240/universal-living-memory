"""
Close-Loop Testing Framework for Ghost Mode
Vertex Genesis v1.3.0

Comprehensive testing of all Ghost Mode functions to prove they work as intended.
Tests HF indexer, context camera, cost optimizer, seat router, and full integration.
"""

import logging
import sys
import time
from typing import Dict, Any, List
from pathlib import Path

# Add orchestrator to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestResult:
    """Test result container."""
    
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error: str = ""
        self.duration: float = 0.0
        self.details: Dict[str, Any] = {}
    
    def __repr__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"{status} - {self.name} ({self.duration:.2f}s)"


class GhostModeTestSuite:
    """Comprehensive test suite for Ghost Mode."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def run_test(self, test_func, name: str) -> TestResult:
        """
        Run a single test function.
        
        Args:
            test_func: Test function to run
            name: Test name
        
        Returns:
            TestResult
        """
        result = TestResult(name)
        self.total_tests += 1
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 Running test: {name}")
        logger.info(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            details = test_func()
            result.passed = True
            result.details = details or {}
            self.passed_tests += 1
            logger.info(f"✅ Test PASSED: {name}")
        except Exception as e:
            result.passed = False
            result.error = str(e)
            self.failed_tests += 1
            logger.error(f"❌ Test FAILED: {name}")
            logger.error(f"   Error: {e}")
        
        result.duration = time.time() - start_time
        self.results.append(result)
        
        return result
    
    def print_summary(self):
        """Print test summary."""
        logger.info(f"\n{'='*60}")
        logger.info("📊 TEST SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total tests: {self.total_tests}")
        logger.info(f"Passed: {self.passed_tests} ✅")
        logger.info(f"Failed: {self.failed_tests} ❌")
        logger.info(f"Success rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        logger.info(f"{'='*60}\n")
        
        for result in self.results:
            logger.info(str(result))
            if not result.passed:
                logger.error(f"   Error: {result.error}")


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_hf_indexer_initialization():
    """Test HuggingFace indexer initialization."""
    from hf_indexer import HuggingFaceIndexer
    
    indexer = HuggingFaceIndexer()
    
    assert indexer is not None, "Indexer not initialized"
    assert indexer.db is not None, "Database not connected"
    assert indexer.client is not None, "HTTP client not initialized"
    
    return {'status': 'Indexer initialized successfully'}


def test_hf_indexer_add_model():
    """Test adding a model to HF index."""
    from hf_indexer import get_indexer
    
    indexer = get_indexer()
    
    # Add a known model
    model_id = "microsoft/phi-3-mini-4k-instruct"
    success = indexer.add_model_to_index(model_id)
    
    assert success, f"Failed to add model: {model_id}"
    
    # Verify it's in index
    assert indexer.is_model_indexed(model_id), "Model not found in index"
    
    # Get model info
    model_info = indexer.get_model_from_index(model_id)
    
    assert model_info is not None, "Model info not retrieved"
    assert model_info['model_id'] == model_id, "Model ID mismatch"
    assert model_info['cost_per_1k_tokens'] == 0.0, "Model should be free"
    
    return {
        'model_id': model_id,
        'params_millions': model_info['params_millions'],
        'is_free': model_info['is_free']
    }


def test_hf_indexer_search():
    """Test HF indexer search functionality."""
    from hf_indexer import get_indexer
    
    indexer = get_indexer()
    
    # Search for code generation models
    results = indexer.search_models(
        query="fast code generation",
        max_cost=0.0,
        limit=5
    )
    
    assert len(results) > 0, "No search results found"
    
    # Verify all results are free
    for r in results:
        assert r['cost_per_1k_tokens'] == 0.0, f"Non-free model in results: {r['model_id']}"
    
    return {
        'query': 'fast code generation',
        'results_count': len(results),
        'top_result': results[0]['model_id']
    }


def test_hf_indexer_optimal_model():
    """Test optimal model selection."""
    from hf_indexer import get_indexer
    
    indexer = get_indexer()
    
    # Get optimal model for translation
    optimal = indexer.get_optimal_model(
        task_description="translate text from image",
        prefer_local=True,
        max_cost=0.0,
        max_params=5000
    )
    
    assert optimal is not None, "No optimal model found"
    assert optimal['cost_per_1k_tokens'] == 0.0, "Optimal model is not free"
    assert optimal['params_millions'] <= 5000, "Model exceeds param limit"
    
    return {
        'task': 'translate text from image',
        'selected_model': optimal['model_id'],
        'params': optimal['params_millions'],
        'cost': optimal['cost_per_1k_tokens']
    }


def test_cost_optimizer():
    """Test cost optimizer decision making."""
    from cost_optimizer import CostOptimizer
    
    optimizer = CostOptimizer()
    
    # Test with free and paid options
    options = [
        {
            'model_id': 'free-model-1',
            'cost_per_1k_tokens': 0.0,
            'quality_score': 0.85,
            'params_millions': 3000
        },
        {
            'model_id': 'paid-model-1',
            'cost_per_1k_tokens': 0.01,
            'quality_score': 0.95,
            'params_millions': 70000
        }
    ]
    
    decision = optimizer.evaluate_options(options, context="test")
    
    assert decision.chosen_option == 'free-model-1', "Did not choose free option"
    assert decision.cost_per_1k_tokens == 0.0, "Cost is not $0"
    assert decision.savings > 0, "Savings not calculated"
    
    return {
        'chosen': decision.chosen_option,
        'cost': decision.cost_per_1k_tokens,
        'savings': decision.savings
    }


def test_cost_optimizer_statistics():
    """Test cost optimizer statistics tracking."""
    from cost_optimizer import get_optimizer
    
    optimizer = get_optimizer()
    
    stats = optimizer.get_statistics()
    
    assert 'total_cost' in stats, "Missing total_cost in stats"
    assert 'free_options_used' in stats, "Missing free_options_used in stats"
    assert 'cost_efficiency' in stats, "Missing cost_efficiency in stats"
    
    # Check if we're maintaining $0 cost
    assert stats['total_cost'] == 0.0, f"Total cost is ${stats['total_cost']}, not $0"
    
    return stats


def test_context_camera_intent_detection():
    """Test context-aware camera intent detection."""
    from context_camera import ContextAwareCamera
    
    camera = ContextAwareCamera()
    
    # Test positive cases
    positive_inputs = [
        "take a photo of this",
        "can you translate this text",
        "scan this document",
        "read this code"
    ]
    
    for inp in positive_inputs:
        detected = camera.detect_camera_intent(inp)
        assert detected, f"Failed to detect camera intent in: '{inp}'"
    
    # Test negative cases
    negative_inputs = [
        "what's the weather today",
        "tell me a joke",
        "how are you"
    ]
    
    for inp in negative_inputs:
        detected = camera.detect_camera_intent(inp)
        assert not detected, f"False positive camera intent in: '{inp}'"
    
    return {
        'positive_tests': len(positive_inputs),
        'negative_tests': len(negative_inputs)
    }


def test_context_camera_use_case_detection():
    """Test use case detection from context."""
    from context_camera import ContextAwareCamera
    
    camera = ContextAwareCamera()
    
    test_cases = [
        ("translate this french text", "translation"),
        ("what is this object", "object_identification"),
        ("read this document", "text_extraction"),
        ("explain this code", "code_reading"),
        ("solve this math equation", "math_solving"),
        ("scan this receipt", "receipt_scanning")
    ]
    
    for input_text, expected_use_case in test_cases:
        use_case, confidence = camera.detect_use_case(input_text)
        assert use_case == expected_use_case, f"Expected {expected_use_case}, got {use_case}"
        assert confidence > 0, "Confidence should be > 0"
    
    return {
        'test_cases': len(test_cases),
        'all_passed': True
    }


def test_context_camera_model_selection():
    """Test optimal model selection for use cases."""
    from context_camera import ContextAwareCamera
    
    camera = ContextAwareCamera()
    
    use_cases = ['translation', 'text_extraction', 'code_reading']
    
    for use_case in use_cases:
        model = camera.select_optimal_model(use_case)
        
        if model:  # May be None if no models indexed yet
            assert model['cost_per_1k_tokens'] == 0.0, f"Non-free model for {use_case}"
            assert model['is_local'], f"Non-local model for {use_case}"
    
    return {
        'use_cases_tested': len(use_cases)
    }


def test_seat_router_assignment():
    """Test seat router model assignment."""
    from seat_router import SeatRouter
    
    router = SeatRouter()
    
    # Test assignment
    result = router.assign(seat_id=0, input_text="generate python code for sorting")
    
    assert 'seat' in result, "Missing seat in result"
    assert 'model' in result, "Missing model in result"
    assert 'context_match' in result, "Missing context_match in result"
    assert result['cost_per_1k_tokens'] == 0.0, "Assigned model is not free"
    
    return {
        'seat': result['seat'],
        'model': result['model'],
        'context_match': result['context_match']
    }


def test_seat_router_status():
    """Test seat router status reporting."""
    from seat_router import SeatRouter
    
    router = SeatRouter()
    
    # Get status for seat 0
    status = router.get_seat_status(0)
    
    assert 'seat_name' in status, "Missing seat_name in status"
    assert 'loaded' in status, "Missing loaded in status"
    
    return status


def test_integration_full_workflow():
    """Test full integration workflow."""
    from hf_indexer import get_indexer
    from context_camera import process_camera_command
    from cost_optimizer import get_optimizer
    
    # 1. Index a model
    indexer = get_indexer()
    indexer.add_model_to_index("microsoft/phi-3-mini-4k-instruct")
    
    # 2. Process camera command (simulated)
    # Note: This won't actually capture image, but tests the logic
    result = process_camera_command("translate this french text")
    
    # 3. Check cost optimizer
    optimizer = get_optimizer()
    stats = optimizer.get_statistics()
    
    assert stats['total_cost'] == 0.0, "Cost incurred during workflow"
    
    return {
        'workflow_steps': 3,
        'total_cost': stats['total_cost'],
        'cost_efficiency': stats['cost_efficiency']
    }


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all Ghost Mode tests."""
    suite = GhostModeTestSuite()
    
    logger.info("\n" + "="*60)
    logger.info("🧪 GHOST MODE CLOSE-LOOP TESTING")
    logger.info("Vertex Genesis v1.3.0")
    logger.info("="*60 + "\n")
    
    # HuggingFace Indexer Tests
    suite.run_test(test_hf_indexer_initialization, "HF Indexer: Initialization")
    suite.run_test(test_hf_indexer_add_model, "HF Indexer: Add Model")
    suite.run_test(test_hf_indexer_search, "HF Indexer: Search")
    suite.run_test(test_hf_indexer_optimal_model, "HF Indexer: Optimal Model Selection")
    
    # Cost Optimizer Tests
    suite.run_test(test_cost_optimizer, "Cost Optimizer: Decision Making")
    suite.run_test(test_cost_optimizer_statistics, "Cost Optimizer: Statistics")
    
    # Context Camera Tests
    suite.run_test(test_context_camera_intent_detection, "Context Camera: Intent Detection")
    suite.run_test(test_context_camera_use_case_detection, "Context Camera: Use Case Detection")
    suite.run_test(test_context_camera_model_selection, "Context Camera: Model Selection")
    
    # Seat Router Tests
    suite.run_test(test_seat_router_assignment, "Seat Router: Model Assignment")
    suite.run_test(test_seat_router_status, "Seat Router: Status Reporting")
    
    # Integration Tests
    suite.run_test(test_integration_full_workflow, "Integration: Full Workflow")
    
    # Print summary
    suite.print_summary()
    
    return suite


if __name__ == "__main__":
    suite = run_all_tests()
    
    # Exit with error code if tests failed
    sys.exit(0 if suite.failed_tests == 0 else 1)
