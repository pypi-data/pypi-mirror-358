def run_hook(func):
    try:
        func()
    except Exception as e:
        print(f"[etsi-watchdog] Hook failed: {e}")
