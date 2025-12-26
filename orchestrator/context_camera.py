"""
Context-Aware Camera Controller
Vertex Genesis v1.3.0

Listens for camera-related context in voice input, then activates OCR
with optimal lightweight model selection based on use case.
"""

import logging
import re
from typing import Optional, Dict, Any, Tuple
from vision import OcrEye
from hf_indexer import get_indexer

logger = logging.getLogger(__name__)

# Camera activation keywords (flexible matching)
CAMERA_KEYWORDS = [
    'camera', 'photo', 'picture', 'snap', 'capture', 'scan', 'look',
    'see', 'view', 'show', 'read', 'ocr', 'text', 'translate', 'identify'
]

# Context patterns for use case detection
USE_CASE_PATTERNS = {
    'translation': [
        r'\btranslat(e|ion|ing)\b',
        r'\b(french|spanish|german|chinese|japanese|korean|arabic|russian|italian|portuguese)\b',
        r'\blanguage\b',
        r'\bforeign\b'
    ],
    'object_identification': [
        r'\bidentify\b',
        r'\bwhat (is|are)\b',
        r'\brecogniz(e|ing)\b',
        r'\bobject\b',
        r'\bthing\b',
        r'\bitem\b'
    ],
    'text_extraction': [
        r'\bread\b',
        r'\btext\b',
        r'\bdocument\b',
        r'\bpaper\b',
        r'\bpage\b',
        r'\bbook\b',
        r'\bscreen\b'
    ],
    'code_reading': [
        r'\bcode\b',
        r'\bprogram\b',
        r'\bscript\b',
        r'\bfunction\b',
        r'\bsyntax\b',
        r'\berror\b'
    ],
    'math_solving': [
        r'\bmath\b',
        r'\bequation\b',
        r'\bcalculat(e|ion)\b',
        r'\bsolve\b',
        r'\bformula\b'
    ],
    'receipt_scanning': [
        r'\breceipt\b',
        r'\binvoice\b',
        r'\bbill\b',
        r'\bprice\b',
        r'\btotal\b'
    ]
}

# Model requirements by use case (params in millions, pipeline tag)
USE_CASE_REQUIREMENTS = {
    'translation': {
        'max_params': 3000,  # 3B max for translation
        'pipeline_tag': 'translation',
        'keywords': ['translation', 'multilingual', 'language']
    },
    'object_identification': {
        'max_params': 5000,  # 5B for vision tasks
        'pipeline_tag': 'image-classification',
        'keywords': ['vision', 'image', 'object', 'detection']
    },
    'text_extraction': {
        'max_params': 1000,  # 1B for simple OCR
        'pipeline_tag': 'text-generation',
        'keywords': ['ocr', 'text', 'extraction', 'reading']
    },
    'code_reading': {
        'max_params': 2000,  # 2B for code understanding
        'pipeline_tag': 'text-generation',
        'keywords': ['code', 'programming', 'syntax']
    },
    'math_solving': {
        'max_params': 2000,  # 2B for math
        'pipeline_tag': 'text-generation',
        'keywords': ['math', 'equation', 'calculation']
    },
    'receipt_scanning': {
        'max_params': 1000,  # 1B for structured text
        'pipeline_tag': 'text-generation',
        'keywords': ['ocr', 'receipt', 'invoice', 'structured']
    }
}


class ContextAwareCamera:
    """
    Context-aware camera controller.
    Detects camera intent from voice input and selects optimal model.
    """
    
    def __init__(self):
        self.camera: Optional[OcrEye] = None
        self.current_model: Optional[str] = None
        self.indexer = get_indexer()
        logger.info("📷 Context-aware camera initialized")
    
    def detect_camera_intent(self, voice_input: str) -> bool:
        """
        Detect if voice input contains camera-related intent.
        
        Args:
            voice_input: Voice input text
        
        Returns:
            True if camera intent detected, False otherwise
        """
        voice_lower = voice_input.lower()
        
        # Check for camera keywords
        for keyword in CAMERA_KEYWORDS:
            if keyword in voice_lower:
                logger.info(f"📷 Camera intent detected: '{keyword}' in input")
                return True
        
        return False
    
    def detect_use_case(self, voice_input: str) -> Tuple[str, float]:
        """
        Detect use case from voice input using pattern matching.
        
        Args:
            voice_input: Voice input text
        
        Returns:
            Tuple of (use_case, confidence)
        """
        voice_lower = voice_input.lower()
        
        # Score each use case
        scores = {}
        for use_case, patterns in USE_CASE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, voice_lower, re.IGNORECASE):
                    score += 1
            scores[use_case] = score
        
        # Get best match
        if not scores or max(scores.values()) == 0:
            # Default to text extraction
            return 'text_extraction', 0.5
        
        best_use_case = max(scores, key=scores.get)
        confidence = scores[best_use_case] / len(USE_CASE_PATTERNS[best_use_case])
        
        logger.info(f"🎯 Use case detected: {best_use_case} (confidence: {confidence:.2f})")
        
        return best_use_case, confidence
    
    def select_optimal_model(self, use_case: str) -> Optional[Dict[str, Any]]:
        """
        Select optimal lightweight model for use case.
        
        Args:
            use_case: Detected use case
        
        Returns:
            Model information dictionary or None
        """
        requirements = USE_CASE_REQUIREMENTS.get(use_case, USE_CASE_REQUIREMENTS['text_extraction'])
        
        # Build search query from keywords
        query = ' '.join(requirements['keywords'])
        
        # Search for optimal model
        optimal = self.indexer.get_optimal_model(
            task_description=query,
            pipeline_tag=requirements.get('pipeline_tag'),
            prefer_local=True,
            max_cost=0.0,  # $0-cost priority
            max_params=requirements['max_params']
        )
        
        if optimal:
            logger.info(f"✅ Selected model: {optimal['model_id']} ({optimal['params_millions']}M params)")
        else:
            logger.warning(f"⚠️ No suitable model found for {use_case}")
        
        return optimal
    
    def activate_camera(self, voice_input: str) -> Dict[str, Any]:
        """
        Activate camera with context-aware model selection.
        
        Args:
            voice_input: Voice input containing camera intent and context
        
        Returns:
            Result dictionary with OCR text and model info
        """
        try:
            # Detect use case
            use_case, confidence = self.detect_use_case(voice_input)
            
            # Select optimal model
            optimal_model = self.select_optimal_model(use_case)
            
            if not optimal_model:
                return {
                    'success': False,
                    'error': 'No suitable model found',
                    'use_case': use_case
                }
            
            # Activate camera (lazy load)
            if self.camera is None:
                self.camera = OcrEye(backoff=3)
                logger.info("📷 Camera activated")
            
            # Capture and extract text
            ocr_text = self.camera.snap()
            
            if not ocr_text:
                return {
                    'success': False,
                    'error': 'No text detected in image',
                    'use_case': use_case,
                    'model': optimal_model['model_id']
                }
            
            # Store current model
            self.current_model = optimal_model['model_id']
            
            return {
                'success': True,
                'ocr_text': ocr_text,
                'use_case': use_case,
                'confidence': confidence,
                'model': optimal_model['model_id'],
                'model_params': optimal_model['params_millions'],
                'model_cost': optimal_model['cost_per_1k_tokens'],
                'is_local': optimal_model['is_local']
            }
        
        except Exception as e:
            logger.error(f"❌ Camera activation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_with_model(self, ocr_text: str, use_case: str) -> str:
        """
        Process OCR text with selected model.
        
        Args:
            ocr_text: Extracted OCR text
            use_case: Detected use case
        
        Returns:
            Processed result text
        """
        # This would integrate with the actual model inference
        # For now, return a placeholder
        return f"[{use_case.upper()}] Processed: {ocr_text[:100]}..."
    
    def deactivate_camera(self):
        """Deactivate camera and free resources."""
        if self.camera:
            self.camera.kill()
            self.camera = None
            self.current_model = None
            logger.info("📷 Camera deactivated")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get camera status.
        
        Returns:
            Status dictionary
        """
        return {
            'active': self.camera is not None and self.camera.is_active,
            'current_model': self.current_model,
            'supported_use_cases': list(USE_CASE_PATTERNS.keys())
        }


# Global camera instance
_global_camera: Optional[ContextAwareCamera] = None


def get_context_camera() -> ContextAwareCamera:
    """Get or create global context-aware camera instance."""
    global _global_camera
    if _global_camera is None:
        _global_camera = ContextAwareCamera()
    return _global_camera


# Convenience function for Ghost Mode integration
def process_camera_command(voice_input: str) -> Dict[str, Any]:
    """
    Process camera command from voice input.
    
    Args:
        voice_input: Voice input text
    
    Returns:
        Result dictionary
    """
    camera = get_context_camera()
    
    # Check if camera intent detected
    if not camera.detect_camera_intent(voice_input):
        return {
            'success': False,
            'error': 'No camera intent detected in input'
        }
    
    # Activate camera with context
    result = camera.activate_camera(voice_input)
    
    # If successful, process with model
    if result.get('success'):
        processed = camera.process_with_model(
            result['ocr_text'],
            result['use_case']
        )
        result['processed'] = processed
    
    # Auto-deactivate after use (collapse to 0)
    camera.deactivate_camera()
    
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    camera = ContextAwareCamera()
    
    # Test: Translation use case
    result1 = process_camera_command("can you translate this french text from my screen?")
    print(f"Translation test: {result1}")
    
    # Test: Object identification
    result2 = process_camera_command("what is this object in the picture?")
    print(f"Object ID test: {result2}")
    
    # Test: Code reading
    result3 = process_camera_command("read this code and explain the error")
    print(f"Code reading test: {result3}")
    
    # Test: Math solving
    result4 = process_camera_command("solve this math equation from the paper")
    print(f"Math solving test: {result4}")
