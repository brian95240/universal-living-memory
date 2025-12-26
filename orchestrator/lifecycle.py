import time, threading, os, signal, logging

logger = logging.getLogger("Lifecycle")

IDLE_THRESHOLD = 1800  # 30 Minutes

class LifecycleMonitor:
    def __init__(self, enabled=True):
        self.last_activity = time.time()
        self.enabled = enabled
        if self.enabled:
            threading.Thread(target=self._monitor, daemon=True).start()
            logger.info(f"🕐 Lifecycle monitor started. Idle threshold: {IDLE_THRESHOLD}s")

    def touch(self):
        """Mark activity to prevent idle shutdown"""
        self.last_activity = time.time()
    
    def pulse(self):
        """Alias for touch() - Ghost Mode compatibility"""
        self.touch()

    def get_idle_time(self):
        """Get current idle time in seconds"""
        return time.time() - self.last_activity

    def _monitor(self):
        """Background thread monitoring idle time"""
        while True:
            time.sleep(60)  # Check every minute
            idle_time = self.get_idle_time()
            
            if idle_time > IDLE_THRESHOLD:
                logger.warning(f"💀 System Idle > {IDLE_THRESHOLD}s ({idle_time:.0f}s). Initiating graceful shutdown.")
                # Give a grace period for logging
                time.sleep(2)
                os.kill(os.getpid(), signal.SIGTERM)
                break
            elif idle_time > IDLE_THRESHOLD * 0.8:
                # Warning at 80% threshold
                logger.info(f"⚠️ Approaching idle threshold: {idle_time:.0f}s / {IDLE_THRESHOLD}s")
