"""
Voice Module - Speech Recognition and Synthesis for Ghost Mode
Vertex Genesis v1.2.0

SynthEar: Whisper-based speech-to-text
VoiceBox: TTS for voice output
"""

import logging
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class SynthEar:
    """
    Speech-to-text using Faster-Whisper.
    Lazy loading, offline capable, optimized for wake-word detection.
    """
    
    def __init__(self, model: str = "tiny", device: str = "cpu", compute_type: str = "int8"):
        """
        Initialize speech recognition.
        
        Args:
            model: Whisper model size (tiny, base, small, medium, large)
            device: Device to run on (cpu, cuda)
            compute_type: Computation type (int8, float16, float32)
        """
        self.model_name = model
        self.device = device
        self.compute_type = compute_type
        self.model = None
        self.pyaudio = None
        self.stream = None
        
        logger.info(f"👂 SynthEar initialized (model={model}, device={device})")
    
    def _lazy_load(self):
        """Lazy load Whisper model."""
        if self.model is None:
            try:
                from faster_whisper import WhisperModel
                self.model = WhisperModel(
                    self.model_name,
                    device=self.device,
                    compute_type=self.compute_type
                )
                logger.info(f"✅ Whisper {self.model_name} loaded")
            except ImportError:
                logger.error("❌ faster-whisper not installed. Install with: pip install faster-whisper")
                raise
    
    def listen(self, duration: int = 3, sample_rate: int = 16000) -> str:
        """
        Listen for speech and transcribe.
        
        Args:
            duration: Recording duration in seconds
            sample_rate: Audio sample rate
        
        Returns:
            Transcribed text
        """
        self._lazy_load()
        
        try:
            import pyaudio
            import wave
            import tempfile
            
            # Record audio
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                input=True,
                frames_per_buffer=1024
            )
            
            logger.info(f"🎤 Recording for {duration}s...")
            frames = []
            
            for _ in range(0, int(sample_rate / 1024 * duration)):
                data = stream.read(1024)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                wf = wave.open(temp_path, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(sample_rate)
                wf.writeframes(b''.join(frames))
                wf.close()
            
            # Transcribe
            segments, info = self.model.transcribe(temp_path, beam_size=1)
            text = " ".join([segment.text for segment in segments])
            
            logger.info(f"✅ Transcribed: {text}")
            
            # Cleanup
            import os
            os.unlink(temp_path)
            
            return text.strip()
        except Exception as e:
            logger.error(f"❌ Listen error: {e}")
            return ""
    
    def transcribe_file(self, audio_path: str) -> str:
        """
        Transcribe audio file.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Transcribed text
        """
        self._lazy_load()
        
        try:
            segments, info = self.model.transcribe(audio_path, beam_size=5)
            text = " ".join([segment.text for segment in segments])
            logger.info(f"✅ Transcribed file: {len(text)} characters")
            return text.strip()
        except Exception as e:
            logger.error(f"❌ Transcribe file error: {e}")
            return ""


class VoiceBox:
    """
    Text-to-speech using pyttsx3.
    Lazy loading, offline capable, cross-platform.
    """
    
    def __init__(self, rate: int = 150, volume: float = 0.9):
        """
        Initialize text-to-speech.
        
        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0-1.0)
        """
        self.rate = rate
        self.volume = volume
        self.engine = None
        
        logger.info(f"🔊 VoiceBox initialized (rate={rate}, volume={volume})")
    
    def _lazy_load(self):
        """Lazy load TTS engine."""
        if self.engine is None:
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', self.rate)
                self.engine.setProperty('volume', self.volume)
                logger.info("✅ TTS engine loaded")
            except ImportError:
                logger.error("❌ pyttsx3 not installed. Install with: pip install pyttsx3")
                raise
    
    def say(self, text: str, wait: bool = True):
        """
        Speak text.
        
        Args:
            text: Text to speak
            wait: Wait for speech to complete
        """
        self._lazy_load()
        
        try:
            logger.info(f"🔊 Speaking: {text[:50]}...")
            self.engine.say(text)
            if wait:
                self.engine.runAndWait()
        except Exception as e:
            logger.error(f"❌ Say error: {e}")
    
    def say_async(self, text: str):
        """
        Speak text asynchronously (non-blocking).
        
        Args:
            text: Text to speak
        """
        self.say(text, wait=False)
    
    def save_to_file(self, text: str, output_path: str):
        """
        Save speech to audio file.
        
        Args:
            text: Text to convert
            output_path: Path to save audio file
        """
        self._lazy_load()
        
        try:
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            logger.info(f"💾 Speech saved: {output_path}")
        except Exception as e:
            logger.error(f"❌ Save to file error: {e}")
    
    def set_voice(self, voice_id: Optional[int] = None):
        """
        Set voice by ID.
        
        Args:
            voice_id: Voice index (None = default)
        """
        self._lazy_load()
        
        try:
            voices = self.engine.getProperty('voices')
            if voice_id is not None and 0 <= voice_id < len(voices):
                self.engine.setProperty('voice', voices[voice_id].id)
                logger.info(f"✅ Voice set: {voices[voice_id].name}")
        except Exception as e:
            logger.error(f"❌ Set voice error: {e}")
    
    def list_voices(self) -> list:
        """
        List available voices.
        
        Returns:
            List of voice names
        """
        self._lazy_load()
        
        try:
            voices = self.engine.getProperty('voices')
            return [v.name for v in voices]
        except Exception as e:
            logger.error(f"❌ List voices error: {e}")
            return []


# Utility functions
def quick_listen(duration: int = 3) -> str:
    """
    Quick speech-to-text capture.
    
    Args:
        duration: Recording duration in seconds
    
    Returns:
        Transcribed text
    """
    ear = SynthEar(model="tiny")
    return ear.listen(duration=duration)


def quick_say(text: str):
    """
    Quick text-to-speech.
    
    Args:
        text: Text to speak
    """
    voice = VoiceBox()
    voice.say(text)


# Simple usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test TTS
    voice = VoiceBox()
    voice.say("Hello, I am Vertex Genesis Ghost Mode.")
    
    # Test STT
    ear = SynthEar(model="tiny")
    print("Speak now...")
    text = ear.listen(duration=3)
    print(f"You said: {text}")
    
    # Echo back
    if text:
        voice.say(f"You said: {text}")
