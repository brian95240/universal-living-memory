"""
Ghost Mode Daemon - Voice-Activated Agent System
Vertex Genesis v1.2.0

State machine for wake-word detection and agent activation.
Lazy loading, full collapse on idle, integrates with lifecycle monitor.
"""

import time
import threading
import signal
import os
import logging
from pathlib import Path
from typing import Optional

# Local imports
from wake import AmbientListener
from model import ModelBank
from vision import OcrEye
from voice import SynthEar, VoiceBox
from lifecycle import LifecycleMonitor

logger = logging.getLogger(__name__)

# State file: 0=dead, 1=listening, 2=active
STATE_FILE = Path('./ghost.state')

# Lazy globals
whisper: Optional[SynthEar] = None
camera: Optional[OcrEye] = None
voice: Optional[VoiceBox] = None
model_bank: Optional[ModelBank] = None
ambient_listener: Optional[AmbientListener] = None

# Lifecycle integration
lifecycle: Optional[LifecycleMonitor] = None


def init_ghost_daemon(lifecycle_monitor: LifecycleMonitor):
    """
    Initialize Ghost Mode daemon.
    
    Args:
        lifecycle_monitor: Lifecycle monitor instance from main.py
    """
    global lifecycle
    lifecycle = lifecycle_monitor
    
    # Ensure state file exists
    if not STATE_FILE.exists():
        STATE_FILE.write_text('0')
    
    logger.info("👻 Ghost Mode daemon initialized")


def get_state() -> str:
    """Get current ghost state."""
    if not STATE_FILE.exists():
        STATE_FILE.write_text('0')
    return STATE_FILE.read_text().strip()


def set_state(state: str):
    """Set ghost state."""
    STATE_FILE.write_text(state)
    logger.info(f"👻 State changed: {state}")


def wake() -> Optional[str]:
    """
    Wake sequence: detect ambient spike → start whisper → listen for wake-word.
    
    Returns:
        'alive' if activated, None otherwise
    """
    global whisper, voice, model_bank
    
    current_state = get_state()
    
    if current_state == '1':  # Listening state
        try:
            # Start whisper for wake-word detection
            if whisper is None:
                whisper = SynthEar(model='tiny')  # 0.5s load, offline
            
            # Listen for wake-word
            word = whisper.listen(duration=2)
            logger.info(f"👂 Heard: {word}")
            
            # Check for wake-words (configurable)
            wake_words = ['ghost', 'go', 'on', 'vertex', 'genesis']
            if any(w in word.lower() for w in wake_words):
                set_state('2')  # Active state
                
                # Wake model
                if model_bank is None:
                    model_bank = ModelBank.from_context('pass-through')
                
                # Wake voice
                if voice is None:
                    voice = VoiceBox()
                
                # Announce activation
                voice.say("Ghost mode activated")
                
                # Touch lifecycle
                if lifecycle:
                    lifecycle.touch()
                
                logger.info("✅ Ghost mode activated!")
                return 'alive'
        except Exception as e:
            logger.error(f"❌ Wake error: {e}")
    
    return None


def on_command(cmd: str):
    """
    Handle voice command.
    
    Args:
        cmd: Voice command text
    """
    global camera, model_bank, voice
    
    try:
        cmd_lower = cmd.lower()
        
        # OCR/Translation commands
        if any(kw in cmd_lower for kw in ['ocr', 'translate', 'read', 'scan']):
            if camera is None:
                camera = OcrEye(backoff=3)  # 3 sec burst, then die
            
            text = camera.snap()
            
            if model_bank and text:
                # Use model to translate or process
                import asyncio
                answer = asyncio.run(model_bank.ask(f'translate or summarize: {text}'))
                
                if voice:
                    voice.say(answer)
            
            # Touch lifecycle
            if lifecycle:
                lifecycle.touch()
        
        # Model swap commands
        elif 'swap' in cmd_lower and 'model' in cmd_lower:
            words = cmd.split()
            if len(words) > 0:
                new_model = words[-1]
                if model_bank:
                    model_bank.swap(new_model)
                    if voice:
                        voice.say(f"Switched to {new_model}")
            
            # Touch lifecycle
            if lifecycle:
                lifecycle.touch()
        
        # Deactivate command
        elif any(kw in cmd_lower for kw in ['sleep', 'stop', 'off', 'deactivate']):
            if voice:
                voice.say("Deactivating ghost mode")
            set_state('0')
            cleanup()
        
        # Status command
        elif 'status' in cmd_lower:
            if model_bank and voice:
                status = model_bank.get_status()
                voice.say(f"Current provider: {status['current_provider']}")
            
            # Touch lifecycle
            if lifecycle:
                lifecycle.touch()
        
        # General query
        else:
            if model_bank and voice:
                import asyncio
                answer = asyncio.run(model_bank.ask(cmd))
                voice.say(answer)
            
            # Touch lifecycle
            if lifecycle:
                lifecycle.touch()
    
    except Exception as e:
        logger.error(f"❌ Command error: {e}")


def daemon_loop():
    """Main daemon loop."""
    global whisper, voice
    
    logger.info("👻 Ghost daemon loop started")
    
    while True:
        try:
            current_state = get_state()
            
            if current_state == '0':  # Dead state
                time.sleep(60)  # Long sleep when dead
            
            elif current_state == '1':  # Listening state
                wake_result = wake()
                time.sleep(0.1)
            
            elif current_state == '2':  # Active state
                if whisper and voice:
                    # Listen for command
                    cmd = whisper.listen(duration=5)
                    if cmd:
                        logger.info(f"🎤 Command: {cmd}")
                        on_command(cmd)
                time.sleep(0.1)
            
            else:
                # Invalid state, reset
                set_state('0')
        
        except KeyboardInterrupt:
            logger.info("👻 Ghost daemon interrupted")
            break
        except Exception as e:
            logger.error(f"❌ Daemon loop error: {e}")
            time.sleep(1)


def start_daemon():
    """Start ghost daemon in background thread."""
    daemon_thread = threading.Thread(target=daemon_loop, daemon=True)
    daemon_thread.start()
    logger.info("✅ Ghost daemon thread started")
    return daemon_thread


def cleanup():
    """Clean shutdown of all ghost components."""
    global camera, model_bank, whisper, voice, ambient_listener
    
    logger.info("🧹 Cleaning up ghost components...")
    
    if camera:
        camera.kill()
        camera = None
    
    if model_bank:
        model_bank.unload()
        model_bank = None
    
    whisper = None
    voice = None
    
    if ambient_listener:
        ambient_listener.stop()
        ambient_listener = None
    
    logger.info("✅ Ghost cleanup complete")


def quit_handler(signum, frame):
    """Signal handler for clean shutdown."""
    logger.info("👻 Ghost daemon shutting down...")
    set_state('0')
    cleanup()
    os._exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, quit_handler)
signal.signal(signal.SIGTERM, quit_handler)


# API functions for external control
def activate_ghost_mode():
    """Activate ghost mode (listening state)."""
    set_state('1')
    logger.info("👻 Ghost mode activated (listening)")


def deactivate_ghost_mode():
    """Deactivate ghost mode."""
    set_state('0')
    cleanup()
    logger.info("👻 Ghost mode deactivated")


def get_ghost_status() -> dict:
    """
    Get current ghost mode status.
    
    Returns:
        Status dictionary
    """
    current_state = get_state()
    state_names = {'0': 'dead', '1': 'listening', '2': 'active'}
    
    return {
        "state": state_names.get(current_state, 'unknown'),
        "state_code": current_state,
        "whisper_loaded": whisper is not None,
        "camera_active": camera is not None and camera.is_active,
        "voice_loaded": voice is not None,
        "model_loaded": model_bank is not None
    }


if __name__ == "__main__":
    # Standalone mode for testing
    logging.basicConfig(level=logging.INFO)
    
    # Create lifecycle monitor
    from lifecycle import LifecycleMonitor
    test_lifecycle = LifecycleMonitor(enabled=True)
    
    # Initialize
    init_ghost_daemon(test_lifecycle)
    
    # Start daemon
    start_daemon()
    
    # Keep alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()
