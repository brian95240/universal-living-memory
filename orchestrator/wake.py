"""
Ambient Listener for Ghost Mode - Vertex Genesis v1.2.0
Detects ambient noise spikes for wake-word activation.
"""

import numpy as np
import pyaudio
import logging
from typing import Optional
import threading
import time

logger = logging.getLogger(__name__)


class AmbientListener:
    """
    Monitors ambient audio for noise spikes that trigger wake-word detection.
    Lightweight, runs in background, minimal CPU usage.
    """
    
    def __init__(self, threshold: float = 0.02, chunk_size: int = 1024, rate: int = 16000):
        """
        Initialize ambient listener.
        
        Args:
            threshold: Volume threshold for spike detection (0.0-1.0)
            chunk_size: Audio chunk size in samples
            rate: Sample rate in Hz
        """
        self.threshold = threshold
        self.chunk_size = chunk_size
        self.rate = rate
        self.is_listening = False
        self.last_spike_time = 0
        self.spike_cooldown = 2.0  # seconds between spikes
        
        # Audio setup
        self.audio = None
        self.stream = None
        self.monitor_thread = None
        
        logger.info(f"🎤 AmbientListener initialized (threshold={threshold})")
    
    def start(self):
        """Start listening for ambient spikes."""
        if self.is_listening:
            logger.warning("⚠️ Already listening")
            return
        
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.is_listening = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            logger.info("✅ Ambient listener started")
        except Exception as e:
            logger.error(f"❌ Failed to start ambient listener: {e}")
            self.is_listening = False
    
    def stop(self):
        """Stop listening."""
        self.is_listening = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        logger.info("🛑 Ambient listener stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.is_listening:
            try:
                # Read audio chunk
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Calculate RMS (volume)
                rms = np.sqrt(np.mean(audio_data**2))
                normalized_rms = rms / 32768.0  # Normalize to 0-1
                
                # Check for spike
                if normalized_rms > self.threshold:
                    current_time = time.time()
                    if current_time - self.last_spike_time > self.spike_cooldown:
                        self.last_spike_time = current_time
                        logger.debug(f"🔊 Ambient spike detected: {normalized_rms:.3f}")
                        self._on_spike()
                
                time.sleep(0.01)  # Small sleep to reduce CPU
            except Exception as e:
                logger.error(f"❌ Monitor loop error: {e}")
                time.sleep(0.1)
    
    def _on_spike(self):
        """
        Called when ambient spike is detected.
        Override this method or set a callback.
        """
        pass
    
    def set_spike_callback(self, callback):
        """
        Set callback function to be called on spike detection.
        
        Args:
            callback: Function to call when spike detected
        """
        self._on_spike = callback
    
    def get_current_volume(self) -> float:
        """
        Get current ambient volume level.
        
        Returns:
            Normalized volume (0.0-1.0)
        """
        if not self.is_listening or not self.stream:
            return 0.0
        
        try:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_data**2))
            return rms / 32768.0
        except:
            return 0.0
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


# Simple usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    def on_spike():
        print("🔊 Spike detected!")
    
    listener = AmbientListener(threshold=0.03)
    listener.set_spike_callback(on_spike)
    listener.start()
    
    try:
        while True:
            time.sleep(1)
            vol = listener.get_current_volume()
            print(f"Current volume: {vol:.3f}")
    except KeyboardInterrupt:
        listener.stop()
