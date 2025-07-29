#!/usr/bin/env python3
"""Compare the working template with current state to find the issue."""

import asyncio
from sharp_cocoro.cocoro import Cocoro
from sharp_cocoro.devices.aircon.aircon import Aircon


async def compare_states():
    """Compare working template with current state."""
    # The working template from your code
    template = "c20000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000101000000000000000000000000000000000000000000000000000000000000"
    
    cocoro = Cocoro(
        app_secret="pngtfljRoYsJE9NW7opn1t2cXA5MtZDKbwon368hs80",
        app_key="jXLhL_R8DKVlRX_HqsOXsOizfPPioGQUed2rKdNqFn8",
        service_name="iClub"
    )
    
    async with cocoro:
        print("Logging in...")
        await cocoro.login()
        
        devices = await cocoro.query_devices()
        aircon = None
        
        for device in devices:
            if isinstance(device, Aircon):
                aircon = device
                break
        
        if not aircon:
            print("No aircon device found!")
            return
        
        # Get current state
        current_state = aircon.get_state8()
        current = current_state.state
        
        print("=== State8 Comparison ===\n")
        print(f"Template: {template}")
        print(f"Current:  {current}")
        print()
        
        # Find all differences
        differences = []
        for i in range(0, len(template), 2):
            if template[i:i+2].lower() != current[i:i+2].lower():
                differences.append({
                    'pos': i,
                    'template': template[i:i+2],
                    'current': current[i:i+2]
                })
        
        print(f"Found {len(differences)} differences:")
        print("\nPosition | Template | Current | Description")
        print("-" * 50)
        
        for diff in differences:
            pos = diff['pos']
            desc = ""
            if pos == 0:
                desc = "Position 0 (mode/state indicator)"
            elif pos == 52:
                desc = "Temperature encoding"
            elif pos == 96:
                desc = "Fan direction"
            elif pos == 6:
                desc = "Temperature change flag"
            elif pos == 12:
                desc = "Unknown - template has 'c0'"
            
            print(f"{pos:8} | {diff['template']:8} | {diff['current']:7} | {desc}")
        
        # Check which positions have non-zero values in current but zero in template
        print("\n\nPositions that are non-zero in current but zero in template:")
        for i in range(0, len(template), 2):
            if template[i:i+2] == "00" and current[i:i+2] != "00":
                print(f"  Position {i}: current={current[i:i+2]}")
        
        # Key observations
        print("\n\n=== Key Observations ===")
        print("1. The template is mostly zeros except for:")
        print("   - Position 0-1: c2 (194 decimal)")
        print("   - Position 12-13: c0")
        print("   - Position 96-97: 01")
        print("\n2. The current state has many non-zero values")
        print("3. This suggests the device might expect a 'clean' command")
        print("   with only the necessary fields set")
        
        # Test if the template-based approach would work
        print("\n\n=== Testing Template-Based State8 ===")
        from sharp_cocoro.state import State8
        
        # Use the template
        test_state = State8(template)
        test_state.fan_direction = 3
        
        print(f"Template after fan_direction=3:")
        print(f"  Position 0: {test_state.state[0:2]}")
        print(f"  Position 96: {test_state.state[96]}")
        print(f"  State: {test_state.state[:40]}...")
        
        # Compare with what we tried to send
        current_modified = State8(current)
        current_modified.fan_direction = 3
        
        print(f"\nCurrent after fan_direction=3:")
        print(f"  Position 0: {current_modified.state[0:2]}")
        print(f"  Position 96: {current_modified.state[96]}")
        print(f"  State: {current_modified.state[:40]}...")
        
        print("\n\nConclusion:")
        print("The device likely expects a specific State8 format for commands,")
        print("not a modification of the current state. The template approach")
        print("creates a 'clean' command structure that the device recognizes.")


if __name__ == "__main__":
    asyncio.run(compare_states())