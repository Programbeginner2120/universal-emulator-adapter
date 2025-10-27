from emulator_adapter.adapters.dolphin_adapter import DolphinAdapter
from emulator_adapter.core.input_event import InputEvent

def test_dolphin_connection():
    adapter = DolphinAdapter()
    
    try:
        adapter.connect()
        print("[OK] Connected successfully")

        # Optional: send a dummy input (e.g., press 'CROSS')
        test_input = InputEvent(button="OPTIONS", action="press")
        adapter.send_input(test_input)
        print("[OK] Input sent successfully")

    except Exception as e:
        print("[FAIL] Error:", e)
        raise
    finally:
        adapter.disconnect()
        print("[OK] Disconnected successfully")

if __name__ == "__main__":
    test_dolphin_connection()
