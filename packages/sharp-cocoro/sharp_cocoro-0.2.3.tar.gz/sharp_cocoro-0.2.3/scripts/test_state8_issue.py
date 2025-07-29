#!/usr/bin/env python3
"""Test State8 fan direction issue."""

import asyncio
from sharp_cocoro.cocoro import Cocoro
from sharp_cocoro.devices.aircon.aircon import Aircon
from sharp_cocoro.state import State8


async def test_state8_issue():
    """Test why fan direction update doesn't work with current state."""
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
        
        print(f"Found aircon: {aircon.name}\n")
        
        # Get current state
        current_state8 = aircon.get_state8()
        print(f"Current State8: {current_state8.state}")
        print(f"Current temp: {current_state8.temperature}°C")
        print(f"Current fan direction: {current_state8.fan_direction}")
        print()
        
        # Compare with the hardcoded template
        template = "c20000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000101000000000000000000000000000000000000000000000000000000000000"
        print(f"Template State8: {template}")
        print()
        
        # Find differences
        print("Differences between current and template:")
        differences = []
        for i in range(0, len(current_state8.state), 2):
            if current_state8.state[i:i+2] != template[i:i+2]:
                differences.append({
                    'pos': i,
                    'current': current_state8.state[i:i+2],
                    'template': template[i:i+2]
                })
        
        for diff in differences[:20]:  # Show first 20 differences
            print(f"  Position {diff['pos']:3d}: current={diff['current']}, template={diff['template']}")
        
        if len(differences) > 20:
            print(f"  ... and {len(differences)-20} more differences")
        
        print(f"\nTotal differences: {len(differences)} positions")
        
        # Test what happens with fan direction setter
        print("\n--- Testing fan_direction setter behavior ---")
        
        # Create a copy of current state
        test_state = State8(current_state8.state)
        print("\nBefore fan_direction setter:")
        print(f"  Position 0-1: {test_state.state[0:2]}")
        print(f"  Position 97: {test_state.state[97]}")
        print(f"  Temperature: {test_state.temperature}°C")
        
        # Set fan direction
        test_state.fan_direction = 3
        print("\nAfter fan_direction = 3:")
        print(f"  Position 0-1: {test_state.state[0:2]} (changed to 'c' + (fan_dir + 1))")
        print(f"  Position 97: {test_state.state[97]} (changed to fan_dir)")
        print(f"  Temperature: {test_state.temperature}°C (should be preserved)")
        
        # Check if the state would be valid
        print(f"\nResulting State8: {test_state.state}")
        
        # Try with template approach
        print("\n--- Testing template approach ---")
        template_state = State8(template)
        template_state.fan_direction = 3
        print("Template after fan_direction = 3:")
        print(f"  Position 0-1: {template_state.state[0:2]}")
        print(f"  Position 97: {template_state.state[97]}")
        print(f"  Full state: {template_state.state}")
        
        # Identify critical positions
        print("\n--- Analyzing critical positions ---")
        print("Positions that might be device/mode specific:")
        
        # Check specific ranges
        print(f"Positions 10-20: current={current_state8.state[10:20]}, template={template[10:20]}")
        print(f"Positions 48-58: current={current_state8.state[48:58]}, template={template[48:58]}")
        print(f"Positions 96-106: current={current_state8.state[96:106]}, template={template[96:106]}")


if __name__ == "__main__":
    asyncio.run(test_state8_issue())