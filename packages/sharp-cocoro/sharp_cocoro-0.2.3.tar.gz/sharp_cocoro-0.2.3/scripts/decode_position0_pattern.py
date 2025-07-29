#!/usr/bin/env python3
"""Decode the actual pattern for position 0."""

# Data from the analysis
data_points = [
    # (pos0_hex, pos0_dec, temperature, fan_direction)
    ('1B', 27, 18.0, 7),
    ('1D', 29, 19.0, 7),
    ('1F', 31, 20.0, 7),
    ('74', 116, 18.0, 0),
    ('75', 117, 18.0, 1),
    ('76', 118, 18.0, 2),
    ('77', 119, 18.0, 3),
    ('78', 120, 18.0, 4),
    ('79', 121, 18.0, 5),
    ('7B', 123, 18.0, 7),
]

print("=== DECODING POSITION 0 PATTERN ===\n")

# Group by temperature
temp_groups = {}
for hex_val, dec_val, temp, fan_dir in data_points:
    if temp not in temp_groups:
        temp_groups[temp] = []
    temp_groups[temp].append((hex_val, dec_val, fan_dir))

print("Grouped by temperature:")
for temp in sorted(temp_groups.keys()):
    print(f"\nTemperature {temp}°C:")
    for hex_val, dec_val, fan_dir in sorted(temp_groups[temp], key=lambda x: x[2]):
        print(f"  Fan dir {fan_dir}: pos0 = {hex_val} ({dec_val} decimal)")

# Look for patterns
print("\n=== PATTERN ANALYSIS ===\n")

# When fan_dir = 7, the values seem to depend on temperature
fan7_values = [(t, h, d) for h, d, t, f in data_points if f == 7]
print("When fan_direction = 7:")
for temp, hex_val, dec_val in sorted(fan7_values):
    print(f"  Temp {temp}°C: {hex_val} ({dec_val})")
    # Check if it follows a pattern
    if temp == 18.0:
        base = dec_val
    else:
        diff = dec_val - 27  # 27 is the value for 18°C
        print(f"    Difference from 18°C value: {diff}")

print("\nWhen temperature = 18.0°C:")
temp18_values = [(f, h, d) for h, d, t, f in data_points if t == 18.0]
for fan_dir, hex_val, dec_val in sorted(temp18_values):
    print(f"  Fan dir {fan_dir}: {hex_val} ({dec_val})")
    if fan_dir == 0:
        base = dec_val
    elif fan_dir < 7:
        diff = dec_val - 116  # 116 is the value for fan_dir=0
        print(f"    Difference from fan_dir=0 value: {diff}")

# The pattern seems to be:
# - When fan_dir = 7: values are 1B, 1D, 1F (based on temperature)
# - When fan_dir < 7: values are 74-79, 7B (based on fan direction)

print("\n=== DISCOVERED PATTERN ===\n")
print("Position 0 encodes BOTH temperature and fan direction!")
print("\nWhen fan_direction = 7 (likely AUTO or OFF):")
print("  - Uses lower values (1B-1F range)")
print("  - Value increases with temperature")
print("  - 18°C -> 1B (27), 19°C -> 1D (29), 20°C -> 1F (31)")
print("  - Pattern: value = 27 + (temp - 18) * 2")

print("\nWhen fan_direction = 0-5:")
print("  - Uses higher values (74-79 range)")  
print("  - Value = 116 + fan_direction")
print("  - 74 (116) = fan_dir 0")
print("  - 75 (117) = fan_dir 1")
print("  - 76 (118) = fan_dir 2")
print("  - 77 (119) = fan_dir 3")
print("  - 78 (120) = fan_dir 4")
print("  - 79 (121) = fan_dir 5")

print("\nSpecial case:")
print("  - 7B (123) appears when fan_dir = 7 at 18°C (maybe after changing from another mode?)")

print("\n=== IMPLICATIONS ===")
print("1. The fan_direction setter that sets pos0='c' is WRONG")
print("2. Position 0 should be calculated based on BOTH temperature and fan direction")
print("3. Position 1 might have a different purpose than (fan_dir + 1)")
print("4. We need to fix the State8 class to properly encode position 0")

# Verify the patterns
print("\n=== PATTERN VERIFICATION ===")
print("\nTesting temperature pattern (fan_dir=7):")
for temp, hex_val, dec_val in [(18.0, '1B', 27), (19.0, '1D', 29), (20.0, '1F', 31)]:
    predicted = 27 + int((temp - 18) * 2)
    print(f"  Temp {temp}: actual={dec_val}, predicted={predicted}, match={dec_val==predicted}")

print("\nTesting fan direction pattern (temp=18.0):")
for fan_dir in range(6):
    predicted = 116 + fan_dir
    actual = next((d for h, d, t, f in data_points if t == 18.0 and f == fan_dir), None)
    print(f"  Fan dir {fan_dir}: actual={actual}, predicted={predicted}, match={actual==predicted}")