#!/usr/bin/env python3
"""Fix for fan direction based on captured requests."""

# The issue is that commands use a different encoding than status reads:
# 
# For COMMANDS (what we send):
#   Position 0 = 0xC1 + fan_direction
#   Position 96 = fan_direction
#   Template is mostly zeros with specific control bytes
#
# For STATUS (what we read):
#   Position 0 varies based on temperature AND fan direction
#   - When fan_dir = 7: pos0 = 27 + (temp - 18) * 2
#   - When fan_dir = 0-5: pos0 = 116 + fan_direction
#
# The State8 class should handle BOTH cases

def create_fan_direction_command_state8(fan_direction: int) -> str:
    """Create a State8 command string for setting fan direction.
    
    Based on captured requests from the app.
    """
    # Start with zeros
    state8 = ['00'] * 80  # 160 chars / 2
    
    # Set fixed positions
    state8[0] = f"{0xC1 + fan_direction:02X}"  # Position 0
    state8[6] = "c0"  # Position 12-13
    state8[48] = f"{fan_direction:02X}"  # Position 96
    state8[49] = "01"  # Position 98-99
    
    return ''.join(state8)


def create_temperature_command_state8(temperature: float) -> str:
    """Create a State8 command string for setting temperature.
    
    This needs to be discovered from captured requests.
    For now, using the pattern from the original code.
    """
    # This is what the original code suggests
    state8 = ['00'] * 80
    
    # Temperature encoding
    temp_hex = f"{int(temperature * 2):02X}"
    state8[26] = temp_hex  # Position 52-53
    
    # Position 6 = '2' when temperature changes (from original code)
    state8[3] = "20"  # Position 6-7
    
    # Position 0 might need special handling for temperature commands
    # This needs to be verified with captured data
    
    return ''.join(state8)


# Test the patterns
if __name__ == "__main__":
    print("=== Fan Direction Command State8 ===\n")
    
    for fan_dir in [0, 1, 2, 3, 4, 5, 7]:
        state8 = create_fan_direction_command_state8(fan_dir)
        print(f"Fan direction {fan_dir}:")
        print(f"  State8: {state8}")
        print(f"  Pos 0: {state8[0:2]}")
        print(f"  Pos 96: {state8[96]}")
        print()
    
    print("\n=== Comparison with Working Template ===")
    
    # Your working template
    working_template = "c20000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000101000000000000000000000000000000000000000000000000000000000000"
    
    # Generate same fan direction
    generated = create_fan_direction_command_state8(1)
    
    print(f"Working template: {working_template[:40]}...")
    print(f"Generated:        {generated[:40]}...")
    print(f"Match: {generated.lower() == working_template.lower()}")