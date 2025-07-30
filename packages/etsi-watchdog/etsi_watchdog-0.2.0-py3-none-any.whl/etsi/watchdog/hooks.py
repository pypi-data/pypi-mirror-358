# etsi/watchdog/hooks.py

class DriftHook:
    def trigger(self, action):
        try:
            action()
        except Exception as e:
            print(f"[DriftHook] Error in action: {e}")
