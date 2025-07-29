#!/usr/bin/env python3
"""Analyze captured deviceControl requests to understand State8 format."""

import json
import re
from pathlib import Path


def extract_json_from_request(content: str) -> dict:
    """Extract JSON from HTTP request content."""
    # Find JSON content after headers
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            print("Failed to parse JSON")
            return {}
    return {}


def analyze_device_control_requests():
    """Analyze all deviceControl requests."""
    control_dir = Path("/Users/david/src/sharp-cocoro/deviceControl.folder")
    
    # Get all request files
    request_files = sorted([f for f in control_dir.glob("*Request*deviceControl.txt")])
    
    print(f"Found {len(request_files)} deviceControl requests\n")
    
    all_state8_values = []
    
    for i, request_file in enumerate(request_files):
        print(f"\n=== Request {i+1}: {request_file.name} ===")
        
        with open(request_file, 'r') as f:
            content = f.read()
        
        # Extract JSON
        data = extract_json_from_request(content)
        
        if data and 'controlList' in data:
            control = data['controlList'][0]
            status_list = control.get('status', [])
            
            # Find FA (State8) status
            for status in status_list:
                if status.get('statusCode') == 'FA':
                    state8_value = status.get('valueBinary', {}).get('code', '')
                    if state8_value:
                        all_state8_values.append({
                            'file': request_file.name,
                            'state8': state8_value,
                            'other_status': [s for s in status_list if s['statusCode'] != 'FA']
                        })
                        
                        print(f"State8: {state8_value}")
                        print(f"Position 0: {state8_value[0:2]}")
                        print(f"Position 6: {state8_value[6:8]}")
                        print(f"Position 12: {state8_value[12:14]}")
                        print(f"Position 52-53 (temp): {state8_value[52:54]}")
                        print(f"Position 96 (fan dir): {state8_value[96]}")
                        
                        # Check for other status codes sent together
                        other_codes = [s['statusCode'] for s in status_list if s['statusCode'] != 'FA']
                        if other_codes:
                            print(f"Other status codes: {other_codes}")
    
    # Analyze patterns
    print("\n\n=== ANALYSIS ===")
    
    if all_state8_values:
        # Compare all State8 values
        print(f"\nComparing {len(all_state8_values)} State8 values:\n")
        
        # Find common positions (always the same)
        common_positions = {}
        varying_positions = {}
        
        first_state8 = all_state8_values[0]['state8']
        
        for pos in range(0, len(first_state8), 2):
            values_at_pos = set()
            for item in all_state8_values:
                values_at_pos.add(item['state8'][pos:pos+2])
            
            if len(values_at_pos) == 1:
                common_positions[pos] = values_at_pos.pop()
            else:
                varying_positions[pos] = sorted(values_at_pos)
        
        print("Positions that NEVER change (template values):")
        for pos in sorted(common_positions.keys()):
            if common_positions[pos] != '00':  # Only show non-zero
                print(f"  Position {pos}: {common_positions[pos]}")
        
        print(f"\nPositions that vary ({len(varying_positions)} total):")
        for pos in sorted(varying_positions.keys()):
            print(f"  Position {pos}: {varying_positions[pos]}")
        
        # Show all State8 values with their position 96 (fan direction)
        print("\n\nAll State8 values with key positions:")
        print("Pos 0 | Pos 6 | Pos 12 | Pos 96 | Full State8")
        print("-" * 60)
        
        for item in all_state8_values:
            s8 = item['state8']
            print(f"{s8[0:2]}    | {s8[6:8]}    | {s8[12:14]}     | {s8[96]}      | {s8[:40]}...")
        
        # Extract template
        print("\n\nExtracted template (common structure):")
        template = ['00'] * 80  # 160 chars / 2
        for pos, value in common_positions.items():
            template[pos//2] = value
        
        template_str = ''.join(template)
        print(f"Template: {template_str}")
        
        # Compare with the hardcoded template
        hardcoded = "c20000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000101000000000000000000000000000000000000000000000000000000000000"
        
        print(f"\nHardcoded template from code: {hardcoded[:40]}...")
        print(f"Matches extracted template: {template_str.lower() == hardcoded.lower()}")


if __name__ == "__main__":
    analyze_device_control_requests()