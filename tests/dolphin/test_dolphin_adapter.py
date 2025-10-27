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
    
    @patch('emulator_adapter.adapters.dolphin_adapter.time')
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_dolphin_send_input_button_press(self, mock_vg, mock_time):
        """Test sending a button press input"""
        # Setup mocks
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        mock_vg.DS4_BUTTONS.DS4_BUTTON_CROSS = "CROSS_BUTTON"
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Send input
        test_input = InputEvent(button="CROSS", action="press")
        adapter.send_input(test_input)
        
        # Verify button was pressed and released
        mock_gamepad.press_button.assert_called_once_with(button="CROSS_BUTTON")
        mock_gamepad.release_button.assert_called_once_with(button="CROSS_BUTTON")
        
        # Verify update was called twice (after press and after release)
        self.assertEqual(mock_gamepad.update.call_count, 2)
        
        # Verify sleep was called for button hold
        mock_time.sleep.assert_called_once_with(.1)
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_dolphin_send_input_without_connection(self):
        """Test that send_input fails when not connected"""
        adapter = DolphinAdapter()
        test_input = InputEvent(button="CROSS", action="press")
        
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
        
        invalid_input = InputEvent(button="INVALID_BUTTON", action="press")
        
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
            test_input = InputEvent(button=button, action="press")
            adapter.send_input(test_input)
        
        # Verify each button was pressed and released
        self.assertEqual(mock_gamepad.press_button.call_count, 3)
        self.assertEqual(mock_gamepad.release_button.call_count, 3)
    
    @patch('emulator_adapter.adapters.dolphin_adapter.vg')
    def test_dolphin_button_case_insensitivity(self, mock_vg):
        """Test that button names are case-insensitive"""
        mock_gamepad = MagicMock()
        mock_vg.VDS4Gamepad.return_value = mock_gamepad
        mock_vg.DS4_BUTTONS.DS4_BUTTON_CROSS = "CROSS_BUTTON"
        
        adapter = DolphinAdapter()
        adapter.connect()
        
        # Test lowercase button name
        test_input = InputEvent(button="cross", action="press")
        adapter.send_input(test_input)
        
        # Verify it was processed correctly
        mock_gamepad.press_button.assert_called_once_with(button="CROSS_BUTTON")
    
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
    def test_dolphin_disconnect_when_not_connected(self):
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
            test_input = InputEvent(button=button, action="press")
            adapter.send_input(test_input)
            
            # Verify button was pressed
            self.assertEqual(mock_gamepad.press_button.call_count, 1)
            self.assertEqual(mock_gamepad.release_button.call_count, 1)


if __name__ == '__main__':
    unittest.main()

