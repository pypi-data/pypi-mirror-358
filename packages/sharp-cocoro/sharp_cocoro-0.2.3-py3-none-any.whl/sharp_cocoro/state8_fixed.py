"""Fixed State8 class with proper position 0 encoding."""

class State8Fixed:
    def __init__(self, state: str = '0' * 160):
        self.state = state
        self._last_temp = None  # Track temperature for position 0 calculation
    
    @property
    def temperature(self) -> float:
        """Get temperature from positions 52-53."""
        t = f"{self.state[52]}{self.state[53]}"
        temp = int(t, 16) / 2
        self._last_temp = temp
        return temp
    
    @temperature.setter
    def temperature(self, t: float) -> None:
        """Set temperature and update related positions."""
        s = list(self.state)
        
        # Position 52-53: temperature * 2
        hex_temp = hex(int(t * 2))[2:].zfill(2)
        s[52] = hex_temp[0]
        s[53] = hex_temp[1]
        
        # Position 6: set to '2' when temperature changes
        s[6] = '2'
        
        # Position 0: depends on both temperature and fan direction
        # We need to preserve the current fan direction mode
        current_fan_dir = self.fan_direction
        self._update_position_0(s, t, current_fan_dir)
        
        self.state = ''.join(s)
        self._last_temp = t
    
    @property
    def fan_direction(self) -> int:
        """Get fan direction from position 97."""
        try:
            return int(self.state[96])
        except ValueError:
            # If position 96 is not a valid digit, return 7 (auto/unknown)
            return 7
    
    @fan_direction.setter
    def fan_direction(self, fan_state: int) -> None:
        """Set fan direction and update related positions."""
        s = list(self.state)
        
        # Position 96 (string index) = position 97 (1-based): fan direction
        s[96] = str(fan_state)
        
        # Position 0: depends on both temperature and fan direction
        # Get current temperature
        current_temp = self.temperature
        self._update_position_0(s, current_temp, fan_state)
        
        self.state = ''.join(s)
    
    def _update_position_0(self, state_list: list, temperature: float, fan_direction: int) -> None:
        """Update position 0 based on temperature and fan direction.
        
        Pattern discovered:
        - When fan_direction = 7 (AUTO/OFF): pos0 = 27 + (temp - 18) * 2
        - When fan_direction = 0-5: pos0 = 116 + fan_direction
        - Special case: 7B (123) sometimes appears for fan_dir=7
        """
        if fan_direction == 7:
            # Temperature-based encoding for auto/off mode
            # Base value 27 (0x1B) at 18°C, increases by 2 per degree
            value = 27 + int((temperature - 18) * 2)
            # Clamp to reasonable range
            value = max(27, min(31, value))  # 0x1B to 0x1F
        elif 0 <= fan_direction <= 5:
            # Fan direction based encoding
            value = 116 + fan_direction  # 0x74 to 0x79
        elif fan_direction == 6:
            # Not seen in data, but extrapolating the pattern
            value = 122  # 0x7A
        else:
            # Unknown fan direction, use a safe default
            value = 27  # 0x1B
        
        hex_val = hex(value)[2:].zfill(2).upper()
        state_list[0] = hex_val[0]
        state_list[1] = hex_val[1]
    
    def clone(self) -> 'State8Fixed':
        """Create a copy of this State8."""
        return State8Fixed(self.state)


# Test the fixed implementation
if __name__ == "__main__":
    print("=== Testing State8Fixed ===\n")
    
    # Test 1: Temperature changes with fan_dir=7
    print("Test 1: Temperature changes with fan_dir=7")
    s = State8Fixed('1B' + '0' * 94 + '7' + '0' * 62)  # Fan dir 7 at position 96
    s.temperature = 18.0
    print(f"Temp=18, Fan=7: pos0={s.state[0:2]} (expected: 1B)")
    
    s.temperature = 19.0
    print(f"Temp=19, Fan=7: pos0={s.state[0:2]} (expected: 1D)")
    
    s.temperature = 20.0
    print(f"Temp=20, Fan=7: pos0={s.state[0:2]} (expected: 1F)")
    
    # Test 2: Fan direction changes with temp=18
    print("\nTest 2: Fan direction changes with temp=18")
    s = State8Fixed('0' * 52 + '24' + '0' * 106)  # Temp = 18 (0x24 = 36 = 18*2)
    for fan in range(6):
        s.fan_direction = fan
        print(f"Temp=18, Fan={fan}: pos0={s.state[0:2]} (expected: {hex(116+fan)[2:].upper()})")
    
    # Test 3: Preserve temperature when changing fan direction
    print("\nTest 3: Preserve temperature when changing fan direction")
    s = State8Fixed('0' * 52 + '28' + '0' * 42 + '7' + '0' * 62)  # Temp=20, Fan=7
    print(f"Initial: Temp={s.temperature}, Fan={s.fan_direction}, pos0={s.state[0:2]}")
    
    s.fan_direction = 3
    print(f"After fan=3: Temp={s.temperature}, Fan={s.fan_direction}, pos0={s.state[0:2]} (expected: 77)")
    
    s.fan_direction = 7
    print(f"After fan=7: Temp={s.temperature}, Fan={s.fan_direction}, pos0={s.state[0:2]} (expected: 1F)")