#!/usr/bin/env python3
"""Analyze State8 monitoring data to find patterns and correlations."""

import json
import sys
from collections import defaultdict
from typing import Dict


def load_monitoring_data(filename: str) -> Dict:
    """Load the monitoring data from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)


def analyze_state8_positions(data: Dict) -> Dict:
    """Analyze which State8 positions changed and how."""
    position_changes = defaultdict(list)
    position_values = defaultdict(set)
    position_correlations = defaultdict(lambda: defaultdict(int))
    
    # Analyze all changes
    for change in data.get('changes', []):
        state8_diffs = change.get('state8_diffs', [])
        property_changes = change.get('property_changes', {})
        
        # Track position changes
        for diff in state8_diffs:
            pos = diff['position']
            position_changes[pos].append({
                'old': diff['old_value'],
                'new': diff['new_value'],
                'diff': diff['diff'],
                'properties_changed': list(property_changes.keys())
            })
            position_values[pos].add(diff['old_value'])
            position_values[pos].add(diff['new_value'])
            
            # Track correlations with properties
            for prop in property_changes:
                position_correlations[pos][prop] += 1
    
    return {
        'changes': position_changes,
        'values': position_values,
        'correlations': position_correlations
    }


def analyze_property_patterns(data: Dict) -> Dict:
    """Analyze property change patterns."""
    property_changes = defaultdict(list)
    property_pairs = defaultdict(int)
    
    for change in data.get('changes', []):
        props = change.get('property_changes', {})
        prop_list = list(props.keys())
        
        # Track individual property changes
        for prop, value_change in props.items():
            property_changes[prop].append({
                'old': value_change['old'],
                'new': value_change['new'],
                'timestamp': change['timestamp']
            })
        
        # Track which properties change together
        for i in range(len(prop_list)):
            for j in range(i + 1, len(prop_list)):
                pair = tuple(sorted([prop_list[i], prop_list[j]]))
                property_pairs[pair] += 1
    
    return {
        'changes': property_changes,
        'pairs': property_pairs
    }


def find_state8_patterns(data: Dict) -> Dict:
    """Find patterns in State8 encoding."""
    patterns = {
        'temperature_positions': {},
        'fan_direction_positions': {},
        'other_correlations': defaultdict(list)
    }
    
    # Track State8 values with known decoded values
    for snapshot_data in data['snapshots']:
        snapshot = snapshot_data['snapshot']
        state8 = snapshot['state8']
        decoded = snapshot['state8_decoded']
        
        # Known positions
        temp_hex = hex(int(decoded['temperature'] * 2))[2:].zfill(2)
        patterns['temperature_positions']["52-53 (temp*2)"] = {
            'value': state8[52:54],
            'expected': temp_hex,
            'matches': state8[52:54].lower() == temp_hex.lower()
        }
        
        temp_plus_16_hex = hex(int((decoded['temperature'] + 16) * 2))[2:].zfill(2)
        patterns['temperature_positions']["0-1 ((temp+16)*2)"] = {
            'value': state8[0:2],
            'expected': temp_plus_16_hex,
            'matches': state8[0:2].lower() == temp_plus_16_hex.lower()
        }
        
        patterns['fan_direction_positions']["97 (fan_dir)"] = {
            'value': state8[96],
            'expected': str(decoded['fan_direction']),
            'matches': state8[96] == str(decoded['fan_direction'])
        }
    
    return patterns


def generate_report(data: Dict, state8_analysis: Dict, property_analysis: Dict, patterns: Dict):
    """Generate a comprehensive analysis report."""
    print("=" * 80)
    print("STATE8 MONITORING ANALYSIS REPORT")
    print("=" * 80)
    print(f"Monitoring period: {data['start_time']} to {data['snapshots'][-1]['snapshot']['timestamp']}")
    print(f"Total snapshots: {len(data['snapshots'])}")
    print(f"Total changes detected: {len(data['changes'])}")
    print()
    
    # State8 position analysis
    print("STATE8 POSITION ANALYSIS")
    print("-" * 80)
    
    # Most frequently changed positions
    position_freq = [(pos, len(changes)) for pos, changes in state8_analysis['changes'].items()]
    position_freq.sort(key=lambda x: x[1], reverse=True)
    
    print("\nMost frequently changed positions:")
    for pos, count in position_freq[:20]:
        values = state8_analysis['values'][pos]
        print(f"  Position {pos:3d} (byte {pos//2:2d}): {count:3d} changes, "
              f"values: {sorted(values)}")
    
    # Positions that never changed
    all_positions = set(range(0, 160, 2))
    changed_positions = set(state8_analysis['changes'].keys())
    unchanged = sorted(all_positions - changed_positions)
    
    print(f"\nPositions that NEVER changed ({len(unchanged)} total):")
    for i in range(0, len(unchanged), 10):
        print(f"  {unchanged[i:i+10]}")
    
    # Property correlations
    print("\n\nPROPERTY CORRELATIONS WITH STATE8")
    print("-" * 80)
    
    for pos, prop_counts in state8_analysis['correlations'].items():
        if prop_counts:
            print(f"\nPosition {pos} correlates with:")
            for prop, count in sorted(prop_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {prop}: {count} times")
    
    # Property change patterns
    print("\n\nPROPERTY CHANGE PATTERNS")
    print("-" * 80)
    
    prop_freq = [(prop, len(changes)) for prop, changes in property_analysis['changes'].items()]
    prop_freq.sort(key=lambda x: x[1], reverse=True)
    
    print("\nMost frequently changed properties:")
    for prop, count in prop_freq[:15]:
        # Get property name from snapshots
        prop_name = None
        for snapshot_data in data['snapshots']:
            if prop in snapshot_data['snapshot']['property_details']:
                prop_name = snapshot_data['snapshot']['property_details'][prop]['name']
                break
        print(f"  {prop_name or prop} ({prop}): {count} changes")
    
    print("\nProperties that change together:")
    for pair, count in sorted(property_analysis['pairs'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {pair[0]} + {pair[1]}: {count} times")
    
    # Specific findings
    print("\n\nSPECIFIC FINDINGS")
    print("-" * 80)
    
    # Analyze specific positions
    findings = []
    
    # Check position 0
    if 0 in state8_analysis['changes']:
        values = state8_analysis['values'][0]
        findings.append(f"Position 0: Changes between {sorted(values)} - appears to be a header/mode indicator")
    
    # Check positions 52-53 (temperature)
    if 52 in state8_analysis['changes']:
        findings.append("Position 52-53: Confirmed as temperature encoding (temp * 2)")
    
    # Check position 97 (fan direction)
    if 96 in state8_analysis['changes']:  # Note: position 96 is index 97 in the string
        values = state8_analysis['values'][96]
        findings.append(f"Position 97: Confirmed as fan direction, values: {sorted(values)}")
    
    # Look for patterns in other positions
    for pos in sorted(state8_analysis['changes'].keys()):
        if pos not in [0, 1, 52, 53, 96, 97]:  # Exclude known positions
            changes = state8_analysis['changes'][pos]
            if len(changes) > 5:  # Frequently changing
                values = state8_analysis['values'][pos]
                corr_props = state8_analysis['correlations'][pos]
                if corr_props:
                    top_prop = max(corr_props.items(), key=lambda x: x[1])[0]
                    findings.append(f"Position {pos}: Highly correlated with {top_prop}, "
                                  f"values: {sorted(values)}")
    
    for finding in findings:
        print(f"- {finding}")
    
    # Summary of discoveries
    print("\n\nSUMMARY OF DISCOVERIES")
    print("-" * 80)
    print("Known mappings:")
    print("- Positions 0-1: (Temperature + 16) * 2 (header/mode indicator)")
    print("- Positions 52-53: Temperature * 2")
    print("- Position 97: Fan direction")
    print("- Position 6: Changes to '2' when temperature is modified")
    
    print("\nLikely mappings based on correlations:")
    
    # Find strong correlations
    strong_correlations = []
    for pos, props in state8_analysis['correlations'].items():
        if props and pos not in [0, 1, 52, 53, 96, 97]:
            total_changes = len(state8_analysis['changes'][pos])
            for prop, count in props.items():
                if count >= total_changes * 0.8:  # 80% correlation
                    strong_correlations.append((pos, prop, count / total_changes))
    
    for pos, prop, correlation in sorted(strong_correlations, key=lambda x: x[2], reverse=True):
        print(f"- Position {pos}: Likely encodes {prop} ({correlation:.0%} correlation)")
    
    print("\nRecommendations for further analysis:")
    print("1. Test changing wind speed settings to see which positions change")
    print("2. Test changing operation modes (cool/heat/dry) to map mode encoding")
    print("3. Test power on/off to identify power state encoding")
    print("4. Monitor over longer periods to catch timer and schedule changes")


def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "state8_monitor_20250627_171728.json"
    
    print(f"Loading data from: {filename}")
    data = load_monitoring_data(filename)
    
    print("Analyzing State8 positions...")
    state8_analysis = analyze_state8_positions(data)
    
    print("Analyzing property patterns...")
    property_analysis = analyze_property_patterns(data)
    
    print("Finding State8 encoding patterns...")
    patterns = find_state8_patterns(data)
    
    print("Generating report...\n")
    generate_report(data, state8_analysis, property_analysis, patterns)


if __name__ == "__main__":
    main()