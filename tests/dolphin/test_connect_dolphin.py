from emulator_adapter.adapters.dolphin_adapter import DolphinAdapter
from emulator_adapter.core.input_event import InputEvent

import time

def test_dolphin_connection():
    adapter = DolphinAdapter()
    
    try:
        adapter.connect()
        print("[OK] Connected successfully")

        time.sleep(3)

        test_press_input = InputEvent(type="STICK", control="LEFT_STICK", value_x=0, value_y=0)
        adapter.send_input(test_press_input, input_callback_dict={"input_duration": 5, "input_release_event": InputEvent(type="STICK", control="LEFT_STICK", value_x=.5, value_y=.5)})

        print("[OK] Input sent successfully")

    except Exception as e:
        print("[FAIL] Error:", e)
        raise
    finally:
        adapter.disconnect()
        print("[OK] Disconnected successfully")

if __name__ == "__main__":
    test_dolphin_connection()
