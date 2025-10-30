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
        adapter.send_input(test_press_input)

        time.sleep(.5)

        test_press_input_2 = InputEvent(type="STICK", control="LEFT_STICK", value_x=1, value_y=1)
        adapter.send_input(test_press_input_2)

        time.sleep(.5)

        test_release_input = InputEvent(type="STICK", control="LEFT_STICK", value_x=.5, value_y=.5)
        adapter.send_input(test_release_input)

        print("[OK] Input sent successfully")

    except Exception as e:
        print("[FAIL] Error:", e)
        raise
    finally:
        adapter.disconnect()
        print("[OK] Disconnected successfully")

if __name__ == "__main__":
    test_dolphin_connection()
