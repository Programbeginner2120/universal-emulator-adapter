from emulator_adapter.core.adapter_base import EmulatorAdapter
from emulator_adapter.core.input_event import InputEvent
import vgamepad as vg
import time

class DolphinAdapter(EmulatorAdapter):
    def __init__(self):
        self.gamepad = None
        self.connected = False

    def connect(self):
        """Initialize a virtual PS4 controller"""
        try:
            self.gamepad = vg.VDS4Gamepad()
            self.connected = True
            print("Virtual gamepad created successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to create virtual gamepad: {e}")

    def send_input(self, input_event):
        """Send a button press to Dolphin using vgamepad"""
        if not self.connected:
            raise RuntimeError("Not connected. Call connect() first.")
        
        # Map button names to vgamepad buttons (PS4 DualShock 4)
        button_map = {
            "CROSS": vg.DS4_BUTTONS.DS4_BUTTON_CROSS,
            "CIRCLE": vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE,
            "SQUARE": vg.DS4_BUTTONS.DS4_BUTTON_SQUARE,
            "TRIANGLE": vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE,
            "OPTIONS": vg.DS4_BUTTONS.DS4_BUTTON_OPTIONS,
            "SHARE": vg.DS4_BUTTONS.DS4_BUTTON_SHARE,
            "L1": vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT,
            "R1": vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT,
            "L3": vg.DS4_BUTTONS.DS4_BUTTON_THUMB_LEFT,
            "R3": vg.DS4_BUTTONS.DS4_BUTTON_THUMB_RIGHT,
        }
        
        button_name = input_event.button.upper()
        if button_name not in button_map:
            raise ValueError(f"Invalid button: {input_event.button}. Valid buttons: {list(button_map.keys())}")
        
        try:
            button = button_map[button_name]
            
            # Press the button
            self.gamepad.press_button(button=button)
            self.gamepad.update()
            print(f"Pressed {input_event.button} button")
            
            # Hold for a short duration
            time.sleep(.1)
            
            # Release the button
            self.gamepad.release_button(button=button)
            self.gamepad.update()
            print(f"Released {input_event.button} button")
            
        except Exception as e:
            print(f"Error sending input: {e}")
            raise

    def disconnect(self):
        """Clean up the virtual gamepad"""
        if self.connected:
            # Release all buttons before disconnecting
            if self.gamepad:
                self.gamepad.reset()
                self.gamepad.update()
            self.connected = False
            print("Virtual gamepad disconnected")