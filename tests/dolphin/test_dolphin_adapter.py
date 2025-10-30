import unittest
from unittest.mock import MagicMock, patch, call
import sys

from emulator_adapter.core.input_event import InputEvent


# Mock vgamepad before importing DolphinAdapter
sys.modules['vgamepad'] = MagicMock()

from emulator_adapter.adapters.dolphin_adapter import DolphinAdapter


class TestDolphinAdapterWithMocks(unittest.TestCase):
    """Test the DolphinAdapter using mocks to avoid actual hardware"""
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_dolphin_connect_success(self, mock_vg):
        """Test successful connection to Dolphin emulator"""
        # Create a mock gamepad
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Verify gamepad was created
        mock_vg.VDS4Gamepad.assert_called_once()
        self.assertTrue(adapter.connected)
        self.assertEqual(adapter.gamepad, mock_gamepad)
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_dolphin_connect_failure(self, mock_vg):
        """Test connection failure handling"""
        # Simulate connection failure
        mock_vg.VDS4Gamepad.side_effect = Exception("Hardware not available")
        
        adapter = DolphinAdapter()
        
        with self.assertRaises(RuntimeError) as context:
            adapter.connect()
        
        self.assertIn("Failed to create virtual gamepad", str(context.exception))
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_dolphin_send_input_button_press(self, mock_vg):
        """Test sending a button press input"""
        # Setup mocks
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        mock_vg.DS4_BUTTONS.DS4_BUTTON_CROSS = "CROSS_BUTTON"
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Send input - button press
        test_input = InputEvent(type="BUTTON", control="CROSS", pressed=True)
        adapter.send_input(test_input)
        
        # Verify button was pressed
        mock_gamepad.press_button.assert_called_once_with("CROSS_BUTTON")
        
        # Verify update was called once (after press)
        self.assertEqual(mock_gamepad.update.call_count, 1)
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_dolphin_send_input_without_connection(self, mock_vg):
        """Test that send_input fails when not connected"""
        adapter = DolphinAdapter()
        test_input = InputEvent(type="BUTTON", control="CROSS", pressed=True)
        
        with self.assertRaises(RuntimeError) as context:
            adapter.send_input(test_input)
        
        self.assertIn("Not connected", str(context.exception))
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_dolphin_send_invalid_button(self, mock_vg):
        """Test that invalid button names raise ValueError"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        invalid_input = InputEvent(type="BUTTON", control="INVALID_BUTTON", pressed=True)
        
        with self.assertRaises(ValueError) as context:
            adapter.send_input(invalid_input)
        
        self.assertIn("Invalid button", str(context.exception))
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_dolphin_send_multiple_buttons(self, mock_vg):
        """Test sending multiple different button presses"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        
        # Setup button mocks
        mock_vg.DS4_BUTTONS.DS4_BUTTON_CROSS = "CROSS_BUTTON"
        mock_vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE = "CIRCLE_BUTTON"
        mock_vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE = "TRIANGLE_BUTTON"
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Send multiple inputs
        buttons = ["CROSS", "CIRCLE", "TRIANGLE"]
        for button in buttons:
            test_input = InputEvent(type="BUTTON", control=button, pressed=True)
            adapter.send_input(test_input)
        
        # Verify each button was pressed
        self.assertEqual(mock_gamepad.press_button.call_count, 3)
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_dolphin_button_case_insensitivity(self, mock_vg):
        """Test that button names are case-insensitive"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        mock_vg.DS4_BUTTONS.DS4_BUTTON_CROSS = "CROSS_BUTTON"
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Test lowercase button name
        test_input = InputEvent(type="BUTTON", control="cross", pressed=True)
        adapter.send_input(test_input)
        
        # Verify it was processed correctly
        mock_gamepad.press_button.assert_called_once_with("CROSS_BUTTON")
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_dolphin_disconnect(self, mock_vg):
        """Test disconnection and cleanup"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        
        adapter = DolphinAdapter()
        adapter.connect()
        adapter.disconnect()
        
        # Verify reset was called before disconnecting
        mock_gamepad.reset.assert_called_once()
        mock_gamepad.update.assert_called()
        self.assertFalse(adapter.connected)
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_dolphin_disconnect_when_not_connected(self, mock_vg):
        """Test that disconnect is safe when not connected"""
        adapter = DolphinAdapter()
        # Should not raise an error
        adapter.disconnect()
        self.assertFalse(adapter.connected)
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_dolphin_reconnect_after_disconnect(self, mock_vg):
        """Test that adapter can reconnect after disconnecting"""
        mock_gamepad1 = MagicMock()
        mock_gamepad2 = MagicMock()
        mock_vg.VDS4Gamepad.side_effect = [mock_gamepad1, mock_gamepad2]
        
        adapter = DolphinAdapter()
        
        # First connection
        adapter.connect()
        self.assertTrue(adapter.connected)
        self.assertEqual(adapter.gamepad, mock_gamepad1)
        
        # Disconnect
        adapter.disconnect()
        self.assertFalse(adapter.connected)
        
        # Reconnect
        adapter.connect()
        self.assertTrue(adapter.connected)
        self.assertEqual(adapter.gamepad, mock_gamepad2)
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_all_supported_buttons(self, mock_vg):
        """Test that all supported buttons in the button map work"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        
        # Setup all button mocks
        mock_vg.DS4_BUTTONS.DS4_BUTTON_CROSS = "CROSS_BUTTON"
        mock_vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE = "CIRCLE_BUTTON"
        mock_vg.DS4_BUTTONS.DS4_BUTTON_SQUARE = "SQUARE_BUTTON"
        mock_vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE = "TRIANGLE_BUTTON"
        mock_vg.DS4_BUTTONS.DS4_BUTTON_OPTIONS = "OPTIONS_BUTTON"
        mock_vg.DS4_BUTTONS.DS4_BUTTON_SHARE = "SHARE_BUTTON"
        mock_vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT = "L1_BUTTON"
        mock_vg.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT = "R1_BUTTON"
        mock_vg.DS4_BUTTONS.DS4_BUTTON_THUMB_LEFT = "L3_BUTTON"
        mock_vg.DS4_BUTTONS.DS4_BUTTON_THUMB_RIGHT = "R3_BUTTON"
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Test all supported buttons
        supported_buttons = [
            "CROSS", "CIRCLE", "SQUARE", "TRIANGLE",
            "OPTIONS", "SHARE", "L1", "R1", "L3", "R3"
        ]
        
        for button in supported_buttons:
            mock_gamepad.reset_mock()  # Clear previous calls
            test_input = InputEvent(type="BUTTON", control=button, pressed=True)
            adapter.send_input(test_input)
            
            # Verify button was pressed
            self.assertEqual(mock_gamepad.press_button.call_count, 1)
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_button_release(self, mock_vg):
        """Test button release functionality"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        mock_vg.DS4_BUTTONS.DS4_BUTTON_CROSS = "CROSS_BUTTON"
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Send button release
        test_input = InputEvent(type="BUTTON", control="CROSS", pressed=False)
        adapter.send_input(test_input)
        
        # Verify button was released
        mock_gamepad.release_button.assert_called_once_with("CROSS_BUTTON")
        mock_gamepad.update.assert_called_once()
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_stick_input(self, mock_vg):
        """Test analog stick input"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Test left stick
        test_input = InputEvent(type="STICK", control="LEFT_STICK", value_x=0.5, value_y=-0.75)
        adapter.send_input(test_input)
        
        # Verify stick was moved (values should be scaled to -255 to 255)
        expected_x = int(0.5 * 255)
        expected_y = int(-0.75 * 255)
        mock_gamepad.left_joystick.assert_called_once_with(x_value=expected_x, y_value=expected_y)
        mock_gamepad.update.assert_called_once()
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_right_stick_input(self, mock_vg):
        """Test right analog stick input"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Test right stick
        test_input = InputEvent(type="STICK", control="RIGHT_STICK", value_x=-0.3, value_y=0.9)
        adapter.send_input(test_input)
        
        # Verify stick was moved
        expected_x = int(-0.3 * 255)
        expected_y = int(0.9 * 255)
        mock_gamepad.right_joystick.assert_called_once_with(x_value=expected_x, y_value=expected_y)
        mock_gamepad.update.assert_called_once()
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_invalid_stick(self, mock_vg):
        """Test that invalid stick names raise ValueError"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        invalid_input = InputEvent(type="STICK", control="INVALID_STICK", value_x=0.5, value_y=0.5)
        
        with self.assertRaises(ValueError) as context:
            adapter.send_input(invalid_input)
        
        self.assertIn("Invalid stick", str(context.exception))
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_trigger_input(self, mock_vg):
        """Test trigger input"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Test L2 trigger
        test_input = InputEvent(type="TRIGGER", control="L2", value_x=0.6)
        adapter.send_input(test_input)
        
        # Verify trigger was pressed (values should be scaled to 0 to 255)
        expected_value = int(0.6 * 255)
        mock_gamepad.left_trigger.assert_called_once_with(expected_value)
        mock_gamepad.update.assert_called_once()
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_right_trigger_input(self, mock_vg):
        """Test R2 trigger input"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Test R2 trigger
        test_input = InputEvent(type="TRIGGER", control="R2", value_x=1.0)
        adapter.send_input(test_input)
        
        # Verify trigger was pressed
        expected_value = int(1.0 * 255)
        mock_gamepad.right_trigger.assert_called_once_with(expected_value)
        mock_gamepad.update.assert_called_once()
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_invalid_trigger(self, mock_vg):
        """Test that invalid trigger names raise ValueError"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        invalid_input = InputEvent(type="TRIGGER", control="L3", value_x=0.5)
        
        with self.assertRaises(ValueError) as context:
            adapter.send_input(invalid_input)
        
        self.assertIn("Invalid trigger", str(context.exception))
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_dpad_input(self, mock_vg):
        """Test D-pad input"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        mock_vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH = "DPAD_NORTH"
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Test D-pad up
        test_input = InputEvent(type="DPAD", control="DPAD_UP", pressed=True)
        adapter.send_input(test_input)
        
        # Verify D-pad was pressed
        mock_gamepad.directional_pad.assert_called_once_with("DPAD_NORTH")
        mock_gamepad.update.assert_called_once()
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_dpad_release(self, mock_vg):
        """Test D-pad release (neutral position)"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        mock_vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE = "DPAD_NONE"
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Test D-pad release
        test_input = InputEvent(type="DPAD", control="DPAD_UP", pressed=False)
        adapter.send_input(test_input)
        
        # Verify D-pad was set to neutral
        mock_gamepad.directional_pad.assert_called_once_with("DPAD_NONE")
        mock_gamepad.update.assert_called_once()
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_all_dpad_directions(self, mock_vg):
        """Test all D-pad directions"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        
        # Setup D-pad direction mocks
        mock_vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH = "DPAD_NORTH"
        mock_vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH = "DPAD_SOUTH"
        mock_vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST = "DPAD_WEST"
        mock_vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_EAST = "DPAD_EAST"
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Test all D-pad directions
        directions = [
            ("DPAD_UP", "DPAD_NORTH"),
            ("DPAD_DOWN", "DPAD_SOUTH"),
            ("DPAD_LEFT", "DPAD_WEST"),
            ("DPAD_RIGHT", "DPAD_EAST")
        ]
        
        for control, expected_direction in directions:
            mock_gamepad.reset_mock()
            test_input = InputEvent(type="DPAD", control=control, pressed=True)
            adapter.send_input(test_input)
            
            # Verify correct direction was pressed
            mock_gamepad.directional_pad.assert_called_once_with(expected_direction)
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_invalid_dpad_direction(self, mock_vg):
        """Test that invalid D-pad directions raise ValueError"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        invalid_input = InputEvent(type="DPAD", control="DPAD_CENTER", pressed=True)
        
        with self.assertRaises(ValueError) as context:
            adapter.send_input(invalid_input)
        
        self.assertIn("Invalid D-pad direction", str(context.exception))
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_unknown_input_type(self, mock_vg):
        """Test that unknown input types raise ValueError"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Create an invalid input event (this requires bypassing type checking)
        invalid_input = InputEvent.__new__(InputEvent)
        invalid_input.type = "UNKNOWN"
        invalid_input.control = "TEST"
        
        with self.assertRaises(ValueError) as context:
            adapter.send_input(invalid_input)
        
        self.assertIn("Unknown input type", str(context.exception))


if __name__ == '__main__':
    unittest.main()

