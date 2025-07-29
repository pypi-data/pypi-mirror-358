#!/usr/bin/env python3
"""Decode the fan direction pattern from captured requests."""

# Data from the captured requests
captured_data = [
    # (position_0, position_96, description)
    ('c1', '00', 'Request 1'),
    ('c2', '01', 'Request 2'),
    ('c3', '02', 'Request 3'),
    ('c4', '03', 'Request 4'),
    ('c5', '04', 'Request 5'),
    ('c6', '05', 'Request 6'),
    ('c8', '07', 'Request 7'),
]

print("=== FAN DIRECTION ENCODING PATTERN ===\n")

print("Captured State8 values:")
print("Pos 0 | Pos 96 | Decimal Pos 0")
print("-" * 30)

for pos0, pos96, desc in captured_data:
    decimal_pos0 = int(pos0, 16)
    decimal_pos96 = int(pos96, 16)
    print(f"{pos0}    | {pos96}     | {decimal_pos0} (0x{pos0})")

print("\n\nPattern Analysis:")
print("Position 0 = 0xC1 + fan_direction")
print("Position 96 = fan_direction")

print("\nVerification:")
for pos0, pos96, desc in captured_data:
    fan_dir = int(pos96, 16)
    expected_pos0 = 0xC1 + fan_dir
    actual_pos0 = int(pos0, 16)
    match = expected_pos0 == actual_pos0
    print(f"Fan dir {fan_dir}: Expected pos0=0x{expected_pos0:02X}, Actual=0x{actual_pos0:02X}, Match={match}")

print("\n\nKey Findings:")
print("1. Position 0 = 0xC1 (193) + fan_direction")
print("2. Position 96 = fan_direction")
print("3. Position 12 is always 'c0'")
print("4. Position 98 is always '01'")
print("5. All other positions are '00' (command template)")
print("6. Wind speed (A0) is sent as a separate status update")

print("\n\nComparing with our previous theory:")
print("- Previous: When fan_dir 0-5, pos0 = 116 + fan_dir (0x74-0x79)")
print("- Actual: When setting fan_dir, pos0 = 193 + fan_dir (0xC1-0xC8)")
print("- The values we saw before (74-79) were likely from reading state, not commands")

print("\n\nState8 Command Template for Fan Direction:")
template = "XX0000000000c00000000000000000000000000000000000000000000000000000000000000000000000000000000000YY01000000000000000000000000000000000000000000000000000000000000"
print(f"Template: {template}")
print("Where:")
print("  XX = hex(0xC1 + fan_direction)")
print("  YY = hex(fan_direction)")
print("  All other bytes are fixed or zero")