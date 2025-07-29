#!/usr/bin/env python3
"""Test the fixed fan direction update."""

import asyncio
from sharp_cocoro.cocoro import Cocoro
from sharp_cocoro.devices.aircon.aircon import Aircon


async def test_fan_direction():
    """Test fan direction changes with the fixed State8."""
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
        
        # Get initial state
        initial_state = aircon.get_state8()
        print(f"Initial State8: {initial_state.state}")
        print(f"Initial temperature: {initial_state.temperature}°C")
        print(f"Initial fan direction: {initial_state.fan_direction}")
        print(f"Initial position 0: {initial_state.state[0:2]}")
        print()
        
        # Test fan direction changes
        test_directions = [0, 1, 2, 3, 4, 5, 7]
        
        for fan_dir in test_directions:
            print(f"\n=== Testing fan direction {fan_dir} ===")
            
            # Queue the update
            aircon.queue_fan_direction_update(str(fan_dir))
            
            # Check what will be sent
            queued_update = aircon.property_updates.get('FA')
            if queued_update:
                state8_to_send = queued_update.valueBinary['code']
                print(f"State8 to send: {state8_to_send}")
                print(f"Position 0: {state8_to_send[0:2]}")
                print(f"Position 96: {state8_to_send[96]}")
                
                # Verify position 0 calculation
                temp = initial_state.temperature
                if fan_dir == 7:
                    expected_pos0 = hex(27 + int((temp - 18) * 2))[2:].zfill(2).upper()
                else:
                    expected_pos0 = hex(116 + fan_dir)[2:].zfill(2).upper()
                
                print(f"Expected position 0: {expected_pos0}")
                print(f"Match: {state8_to_send[0:2] == expected_pos0}")
            
            # Execute the update
            print("Executing update...")
            try:
                await cocoro.execute_queued_updates(aircon)
                print("Update successful!")
                
                # Refresh and check
                await asyncio.sleep(2)
                aircon = await cocoro.fetch_device(aircon)
                
                new_state = aircon.get_state8()
                print(f"New fan direction: {new_state.fan_direction}")
                print(f"New position 0: {new_state.state[0:2]}")
                print(f"Temperature preserved: {new_state.temperature}°C")
                
            except Exception as e:
                print(f"Update failed: {e}")
            
            await asyncio.sleep(3)  # Wait between changes


if __name__ == "__main__":
    asyncio.run(test_fan_direction())