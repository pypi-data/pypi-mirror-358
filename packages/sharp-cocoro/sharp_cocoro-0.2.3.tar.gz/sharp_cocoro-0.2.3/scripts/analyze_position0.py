#!/usr/bin/env python3
"""Analyze position 0 patterns from monitoring data."""

import json


def analyze_position_0():
    """Analyze what position 0 values mean."""
    with open('state8_monitor_20250627_171728.json', 'r') as f:
        data = json.load(f)
    
    print("=== POSITION 0 ANALYSIS ===\n")
    
    # Collect all State8 values with their contexts
    states = []
    
    # From snapshots
    for snapshot_data in data['snapshots']:
        snapshot = snapshot_data['snapshot']
        states.append({
            'state8': snapshot['state8'],
            'pos0': snapshot['state8'][0:2],
            'temperature': snapshot['state8_decoded']['temperature'],
            'fan_direction': snapshot['state8_decoded']['fan_direction'],
            'power': snapshot['specific_values'].get('power'),
            'operation_mode': snapshot['specific_values'].get('operation_mode'),
            'description': snapshot_data['description']
        })
    
    # From changes
    for change in data.get('changes', []):
        snapshot = change['snapshot']
        states.append({
            'state8': snapshot['state8'],
            'pos0': snapshot['state8'][0:2],
            'temperature': snapshot['state8_decoded']['temperature'],
            'fan_direction': snapshot['state8_decoded']['fan_direction'],
            'power': snapshot['specific_values'].get('power'),
            'operation_mode': snapshot['specific_values'].get('operation_mode'),
            'description': f"Change at {change['timestamp']}"
        })
    
    # Group by position 0 value
    pos0_groups = {}
    for state in states:
        pos0_val = state['pos0']
        if pos0_val not in pos0_groups:
            pos0_groups[pos0_val] = []
        pos0_groups[pos0_val].append(state)
    
    print(f"Found {len(pos0_groups)} different values for position 0: {sorted(pos0_groups.keys())}\n")
    
    # Analyze each value
    for pos0_val in sorted(pos0_groups.keys()):
        group = pos0_groups[pos0_val]
        print(f"Position 0 = '{pos0_val}' ({int(pos0_val, 16)} decimal):")
        
        # Get unique temperatures and fan directions for this pos0 value
        temps = set(s['temperature'] for s in group)
        fan_dirs = set(s['fan_direction'] for s in group)
        
        print(f"  Occurrences: {len(group)}")
        print(f"  Temperatures: {sorted(temps)}")
        print(f"  Fan directions: {sorted(fan_dirs)}")
        
        # Check the formula (temp + 16) * 2
        for temp in sorted(temps):
            expected = hex(int((temp + 16) * 2))[2:].zfill(2).upper()
            print(f"  Temp {temp}°C -> expected pos0: {expected}")
        
        print()
    
    # Look for patterns
    print("=== PATTERN ANALYSIS ===\n")
    
    # Check if position 0 follows temperature formula
    temp_formula_matches = 0
    temp_formula_mismatches = 0
    
    for state in states:
        expected = hex(int((state['temperature'] + 16) * 2))[2:].zfill(2).upper()
        actual = state['pos0'].upper()
        
        if expected == actual:
            temp_formula_matches += 1
        else:
            temp_formula_mismatches += 1
            print(f"Mismatch: temp={state['temperature']}°C, expected={expected}, actual={actual}, "
                  f"fan_dir={state['fan_direction']}")
    
    print("\nTemperature formula (temp+16)*2:")
    print(f"  Matches: {temp_formula_matches}")
    print(f"  Mismatches: {temp_formula_mismatches}")
    
    # Check for fan direction influence
    print("\n=== FAN DIRECTION INFLUENCE ===\n")
    
    # The fan_direction setter sets pos0 to 'c' and pos1 to (fan_dir + 1)
    for state in states:
        if state['pos0'][0].lower() == 'c':
            pos1_val = int(state['state8'][1], 16)
            expected_fan_dir = pos1_val - 1
            actual_fan_dir = state['fan_direction']
            print(f"When pos0 starts with 'c': pos1={pos1_val}, "
                  f"expected fan_dir={expected_fan_dir}, actual fan_dir={actual_fan_dir}")


if __name__ == "__main__":
    analyze_position_0()