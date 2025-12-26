"""
OcrEye - On-Demand OCR for Ghost Mode
Vertex Genesis v1.2.0

Camera-based OCR with lazy loading and automatic cleanup.
"""

import logging
from typing import Optional
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class OcrEye:
    """
    On-demand OCR with camera capture.
    Lazy loads dependencies, captures single frame, then dies.
    """
    
    def __init__(self, backoff: int = 3, device: int = 0):
        """
        Initialize OCR eye.
        
        Args:
            backoff: Seconds to keep camera active before auto-shutdown
            device: Camera device index (0 = default)
        """
        self.backoff = backoff
        self.device = device
        self.camera = None
        self.last_capture_time = 0
        self.is_active = False
        
        # Lazy imports
        self.cv2 = None
        self.pytesseract = None
        
        logger.info(f"👁️ OcrEye initialized (backoff={backoff}s)")
    
    def _lazy_load(self):
        """Lazy load heavy dependencies."""
        if self.cv2 is None:
            try:
                import cv2
                self.cv2 = cv2
                logger.info("✅ OpenCV loaded")
            except ImportError:
                logger.error("❌ OpenCV not installed. Install with: pip install opencv-python")
                raise
        
        if self.pytesseract is None:
            try:
                import pytesseract
                self.pytesseract = pytesseract
                logger.info("✅ Pytesseract loaded")
            except ImportError:
                logger.error("❌ Pytesseract not installed. Install with: pip install pytesseract")
                raise
    
    def _open_camera(self):
        """Open camera device."""
        if self.camera is not None:
            return
        
        self._lazy_load()
        
        try:
            self.camera = self.cv2.VideoCapture(self.device)
            if not self.camera.isOpened():
                raise RuntimeError(f"Failed to open camera device {self.device}")
            
            self.is_active = True
            logger.info(f"📷 Camera opened (device={self.device})")
        except Exception as e:
            logger.error(f"❌ Failed to open camera: {e}")
            raise
    
    def snap(self, save_path: Optional[str] = None) -> str:
        """
        Capture single frame and extract text via OCR.
        
        Args:
            save_path: Optional path to save captured image
        
        Returns:
            Extracted text from image
        """
        self._open_camera()
        
        try:
            # Capture frame
            ret, frame = self.camera.read()
            if not ret:
                logger.error("❌ Failed to capture frame")
                return "[Error: Camera capture failed]"
            
            # Save image if requested
            if save_path:
                self.cv2.imwrite(save_path, frame)
                logger.info(f"💾 Image saved: {save_path}")
            
            # Convert to grayscale for better OCR
            gray = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2GRAY)
            
            # Apply threshold for better text detection
            _, thresh = self.cv2.threshold(gray, 0, 255, self.cv2.THRESH_BINARY + self.cv2.THRESH_OTSU)
            
            # Extract text
            text = self.pytesseract.image_to_string(thresh)
            
            self.last_capture_time = time.time()
            logger.info(f"✅ OCR extracted {len(text)} characters")
            
            # Auto-kill after backoff
            if self.backoff > 0:
                import threading
                threading.Timer(self.backoff, self.kill).start()
            
            return text.strip()
        except Exception as e:
            logger.error(f"❌ OCR snap error: {e}")
            return f"[Error: {e}]"
    
    def snap_to_file(self, output_path: str) -> str:
        """
        Capture frame, save to file, and return path.
        
        Args:
            output_path: Path to save captured image
        
        Returns:
            Path to saved image
        """
        self._open_camera()
        
        try:
            ret, frame = self.camera.read()
            if not ret:
                logger.error("❌ Failed to capture frame")
                return ""
            
            self.cv2.imwrite(output_path, frame)
            logger.info(f"💾 Image saved: {output_path}")
            
            self.last_capture_time = time.time()
            
            # Auto-kill after backoff
            if self.backoff > 0:
                import threading
                threading.Timer(self.backoff, self.kill).start()
            
            return output_path
        except Exception as e:
            logger.error(f"❌ Snap to file error: {e}")
            return ""
    
    def kill(self):
        """Kill camera and free resources."""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            self.is_active = False
            logger.info("🛑 Camera killed")
    
    def __enter__(self):
        """Context manager entry."""
        self._open_camera()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.kill()
    
    def __del__(self):
        """Destructor - ensure camera is released."""
        self.kill()


# Utility function for quick OCR
def quick_ocr(device: int = 0, save_path: Optional[str] = None) -> str:
    """
    Quick one-shot OCR capture.
    
    Args:
        device: Camera device index
        save_path: Optional path to save image
    
    Returns:
        Extracted text
    """
    with OcrEye(backoff=0, device=device) as eye:
        return eye.snap(save_path=save_path)


# Simple usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Quick OCR
    text = quick_ocr()
    print(f"Extracted text:\n{text}")
    
    # Or with context manager
    with OcrEye(backoff=5) as eye:
        text = eye.snap(save_path="capture.jpg")
        print(f"Extracted text:\n{text}")
