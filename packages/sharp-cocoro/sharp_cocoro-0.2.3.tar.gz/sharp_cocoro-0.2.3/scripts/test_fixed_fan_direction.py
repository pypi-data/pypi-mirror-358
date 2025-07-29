#!/usr/bin/env python3
"""Test the fixed fan direction implementation."""

import asyncio
from sharp_cocoro.cocoro import Cocoro
from sharp_cocoro.devices.aircon.aircon import Aircon
from sharp_cocoro.state import State8


async def test_fixed_fan_direction():
    """Test the fixed fan direction."""
    cocoro = Cocoro(
        app_secret="pngtfljRoYsJE9NW7opn1t2cXA5MtZDKbwon368hs80",
        app_key="jXLhL_R8DKVlRX_HqsOXsOizfPPioGQUed2rKdNqFn8",
        service_name="iClub"
    )
    
    async with cocoro:
        print("=== Testing Fixed Fan Direction ===\n")
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
        
        # Get initial state
        initial_state = aircon.get_state8()
        print(f"Initial State8: {initial_state.state[:40]}...")
        print(f"Initial fan direction: {initial_state.fan_direction}")
        print()
        
        # Test creating command states
        print("Testing command state generation:")
        for fan_dir in [0, 1, 2, 3, 7]:
            cmd_state = State8.create_fan_direction_command(fan_dir)
            print(f"Fan {fan_dir}: {cmd_state.state[:20]}... pos96={cmd_state.state[96]}")
        print()
        
        # Test actual fan direction changes
        test_directions = [1, 3, 5, 0, 7]
        
        for fan_dir in test_directions:
            print(f"\n{'='*50}")
            print(f"Setting fan direction to {fan_dir}...")
            
            # Queue the update
            aircon.queue_fan_direction_update(str(fan_dir))
            
            # Show what will be sent
            if 'FA' in aircon.property_updates:
                state_to_send = aircon.property_updates['FA'].valueBinary['code']
                print(f"State8 to send: {state_to_send[:40]}...")
                print(f"  Position 0: {state_to_send[0:2]}")
                print(f"  Position 12: {state_to_send[12:14]}")
                print(f"  Position 96: {state_to_send[96]}")
                print(f"  Position 98: {state_to_send[98:100]}")
                
                # Verify encoding
                expected_pos0 = f"{0xC1 + fan_dir:02X}"
                print(f"  Expected pos0: {expected_pos0}, Match: {state_to_send[0:2] == expected_pos0}")
            
            # Execute the update
            print("\nExecuting update...")
            try:
                await cocoro.execute_queued_updates(aircon)
                print("✓ Update successful!")
                
                # Wait for device to process
                print("Waiting 10 seconds for device to update...")
                await asyncio.sleep(10)
                
                # Refresh and check
                aircon = await cocoro.fetch_device(aircon)
                new_state = aircon.get_state8()
                print(f"New fan direction: {new_state.fan_direction}")
                print(f"New State8: {new_state.state[:40]}...")
                
                if new_state.fan_direction == fan_dir:
                    print("✓ Fan direction changed successfully!")
                else:
                    print(f"✗ Fan direction didn't change (expected {fan_dir}, got {new_state.fan_direction})")
                
            except Exception as e:
                print(f"✗ Update failed: {e}")
            
            await asyncio.sleep(2)
        
        print(f"\n\nRestoring initial fan direction ({initial_state.fan_direction})...")
        aircon.queue_fan_direction_update(str(initial_state.fan_direction))
        await cocoro.execute_queued_updates(aircon)
        
        print("Test complete!")


if __name__ == "__main__":
    asyncio.run(test_fixed_fan_direction())