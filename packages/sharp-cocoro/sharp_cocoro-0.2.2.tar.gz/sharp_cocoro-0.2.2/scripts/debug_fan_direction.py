#!/usr/bin/env python3
"""Debug why fan direction changes aren't working."""

import asyncio
from sharp_cocoro.cocoro import Cocoro
from sharp_cocoro.devices.aircon.aircon import Aircon
from sharp_cocoro.state import State8


async def debug_fan_direction():
    """Debug fan direction changes."""
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
        current_state = aircon.get_state8()
        print(f"Current State8: {current_state.state}")
        print(f"Position 0: {current_state.state[0:2]} ({int(current_state.state[0:2], 16)} decimal)")
        print(f"Position 96 (fan dir): {current_state.state[96]}")
        print(f"Temperature: {current_state.temperature}°C")
        print(f"Fan direction: {current_state.fan_direction}")
        print()
        
        # Let's decode what C8 means
        pos0_value = int(current_state.state[0:2], 16)  # 200 decimal
        print(f"Position 0 analysis:")
        print(f"  Value: {pos0_value} (0x{current_state.state[0:2]})")
        print(f"  200 - 116 = {pos0_value - 116} (would be fan_dir if following 116+x pattern)")
        print(f"  200 - 27 = {pos0_value - 27} (offset from base 27)")
        print(f"  (200 - 27) / 2 = {(pos0_value - 27) / 2} (degrees above 18°C if temp pattern)")
        print()
        
        # Check if there's a different property for fan direction
        print("Checking all properties for fan direction:")
        for prop in aircon.properties:
            if 'direction' in prop.statusName.lower() or '風向' in prop.statusName:
                status = aircon.get_property_status(prop.statusCode)
                print(f"  {prop.statusName} ({prop.statusCode}): {status}")
        print()
        
        # Test what State8 we're actually sending
        print("Testing State8 generation:")
        
        # Create a fresh State8 from current
        test_state = State8(current_state.state)
        print(f"\nOriginal state: {test_state.state}")
        print(f"Original pos 0: {test_state.state[0:2]}")
        print(f"Original pos 96: {test_state.state[96]}")
        
        # Set fan direction
        test_state.fan_direction = 3
        print(f"\nAfter setting fan_direction=3:")
        print(f"New pos 0: {test_state.state[0:2]}")
        print(f"New pos 96: {test_state.state[96]}")
        print(f"First 20 chars: {test_state.state[:20]}")
        
        # Now test the actual queue method
        print("\n\nTesting actual queue method:")
        aircon.queue_fan_direction_update("3")
        
        # Check what's queued
        if 'FA' in aircon.property_updates:
            queued = aircon.property_updates['FA']
            state_to_send = queued.valueBinary['code']
            print(f"State8 queued to send: {state_to_send[:20]}...")
            print(f"Position 0: {state_to_send[0:2]}")
            print(f"Position 96: {state_to_send[96]}")
            
            # Compare with current
            print(f"\nDifferences from current:")
            for i in range(0, min(40, len(state_to_send)), 2):
                if current_state.state[i:i+2] != state_to_send[i:i+2]:
                    print(f"  Position {i}: {current_state.state[i:i+2]} -> {state_to_send[i:i+2]}")
        else:
            print("No update queued!")
        
        # Clear the queue
        aircon.property_updates.clear()
        
        # Check if position 96 is actually the right index
        print(f"\n\nDouble-checking position 96:")
        print(f"Character at index 96: '{current_state.state[96]}'")
        print(f"Character at index 97: '{current_state.state[97] if len(current_state.state) > 97 else 'N/A'}'")
        print(f"State8 length: {len(current_state.state)}")


if __name__ == "__main__":
    asyncio.run(debug_fan_direction())