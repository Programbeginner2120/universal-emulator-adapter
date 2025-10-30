from emulator_adapter.core.adapter_base import EmulatorAdapter
from emulator_adapter.core.input_event import InputEvent
import vgamepad as vg
import time

class DolphinAdapter(EmulatorAdapter):
    def __init__(self):
        self.gamepad = None
        self.connected = False

                # --- Button map ---
        self.button_map = {
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

        # --- D-pad map ---
        self.dpad_map = {
            "DPAD_UP": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH,
            "DPAD_DOWN": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH,
            "DPAD_LEFT": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST,
            "DPAD_RIGHT": vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_EAST,
        }

        # --- Triggers map ---
        self.trigger_map = {
            "L2": "left_trigger",
            "R2": "right_trigger",
        }

        # --- Sticks map ---
        self.stick_map = {
            "LEFT_STICK": "left_joystick",
            "RIGHT_STICK": "right_joystick",
        }

    def connect(self):
        """Initialize a virtual PS4 controller"""
        try:
            self.gamepad = vg.VDS4Gamepad()
            self.connected = True
            print("Virtual gamepad created successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to create virtual gamepad: {e}")

    # ---------------------------------
    # Core input handling
    # ---------------------------------
    def send_input(self, event: InputEvent, *args, **kwargs):
        if not self.connected or not self.gamepad:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            if event.type == "BUTTON":
                self._handle_button(event, *args, **kwargs)
            elif event.type == "STICK":
                self._handle_stick(event, *args, **kwargs)
            elif event.type == "TRIGGER":
                self._handle_trigger(event, *args, **kwargs)
            elif event.type == "DPAD":
                self._handle_dpad(event, *args, **kwargs)
            else:
                raise ValueError(f"Unknown input type: {event.type}")
        except Exception as e:
            print(f"Error processing {event}: {e}")
            raise

    # ---------------------------------
    # Input Handlers
    # ---------------------------------
    def _handle_button(self, e: InputEvent, *args, **kwargs):
        btn = self.button_map.get(e.control.upper())
        if not btn:
            raise ValueError(f"Invalid button: {e.control}")
        if e.pressed:
            self.gamepad.press_button(btn)
        else:
            self.gamepad.release_button(btn)
        self.gamepad.update()

    def _handle_stick(self, e: InputEvent, *args, **kwargs):
        if e.control.upper() not in self.stick_map:
            raise ValueError(f"Invalid stick: {e.control}")
        x = int((e.value_x or 0.0) * 255)
        y = int((e.value_y or 0.0) * 255)
        if e.control.upper() == "LEFT_STICK":
            self.gamepad.left_joystick(x_value=x, y_value=y)
        else:
            self.gamepad.right_joystick(x_value=x, y_value=y)
        self.gamepad.update()

        if kwargs.get("input_callback_dict"):
            self._handle_input_callback(e, *args, **kwargs)

    def _handle_trigger(self, e: InputEvent, *args, **kwargs):
        if e.control.upper() not in self.trigger_map:
            raise ValueError(f"Invalid trigger: {e.control}")
        value = int((e.value_x or 0.0) * 255)  # DS4 triggers range 0–255
        if e.control.upper() == "L2":
            self.gamepad.left_trigger(value)
        else:
            self.gamepad.right_trigger(value)
        self.gamepad.update()

    def _handle_dpad(self, e: InputEvent, *args, **kwargs):
        direction = self.dpad_map.get(e.control.upper())
        if not direction:
            raise ValueError(f"Invalid D-pad direction: {e.control}")
        if e.pressed:
            self.gamepad.directional_pad(direction)
        else:
            # Neutral (no D-pad pressed)
            self.gamepad.directional_pad(vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
        self.gamepad.update()

    def _handle_input_callback(self, e: InputEvent, *args, **kwargs):
        if kwargs.get("input_callback_dict"):
            input_callback_dict = kwargs.get("input_callback_dict")
            input_duration = input_callback_dict.get("input_duration")
            input_release_event = input_callback_dict.get("input_release_event")
            time.sleep(input_duration)
            self.send_input(input_release_event)

    def disconnect(self):
        """Clean up the virtual gamepad"""
        if self.connected:
            # Release all buttons before disconnecting
            if self.gamepad:
                self.gamepad.reset()
                self.gamepad.update()
            self.connected = False
            print("Virtual gamepad disconnected")