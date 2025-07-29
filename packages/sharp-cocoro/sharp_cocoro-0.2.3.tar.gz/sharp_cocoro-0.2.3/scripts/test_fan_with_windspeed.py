#!/usr/bin/env python3
"""Test fan direction with wind speed (matching app behavior)."""

import asyncio
from sharp_cocoro.cocoro import Cocoro
from sharp_cocoro.devices.aircon.aircon import Aircon
from sharp_cocoro.devices.aircon.aircon_properties import ValueSingle
from sharp_cocoro.state import State8


async def test_fan_with_windspeed():
    """Test fan direction changes with wind speed set to auto (like the app)."""
    cocoro = Cocoro(
        app_secret="pngtfljRoYsJE9NW7opn1t2cXA5MtZDKbwon368hs80",
        app_key="jXLhL_R8DKVlRX_HqsOXsOizfPPioGQUed2rKdNqFn8",
        service_name="iClub"
    )
    
    async with cocoro:
        print("=== Testing Fan Direction with Wind Speed (App Behavior) ===\n")
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
        initial_ws = aircon.get_windspeed()
        print(f"Initial fan direction: {initial_state.fan_direction}")
        print(f"Initial wind speed: {initial_ws}")
        print()
        
        # Test sequence matching the captured requests
        test_sequence = [
            (0, "Top"),
            (2, "Middle"),
            (4, "Bottom"),
        ]
        
        print("=== Replicating App Behavior ===")
        print("The app sends BOTH wind speed (A0=41) and State8 (FA) together\n")
        
        for fan_dir, name in test_sequence:
            print(f"\nSetting fan direction to: {name} (value: {fan_dir})")
            
            # Queue BOTH updates like the app does
            print("1. Queueing wind speed = AUTO (41)")
            aircon.queue_windspeed_update(ValueSingle.WINDSPEED_LEVEL_AUTO)
            
            print("2. Queueing fan direction update")
            aircon.queue_fan_direction_update(str(fan_dir))
            
            # Show what will be sent
            print("\nQueued updates:")
            for status_code, update in aircon.property_updates.items():
                if status_code == 'A0':
                    print(f"  A0 (wind speed): {update.valueSingle['code']}")
                elif status_code == 'FA':
                    state = update.valueBinary['code']
                    print(f"  FA (State8): {state[:20]}...")
                    print(f"    Position 0-1: {state[0:2]}")
                    print(f"    Position 96: {state[96]}")
            
            # Execute the updates
            print("\nExecuting both updates together...")
            try:
                result = await cocoro.execute_queued_updates(aircon)
                
                # Show control IDs (should be 2)
                control_ids = []
                if 'controlList' in result:
                    for control in result['controlList']:
                        if 'id' in control:
                            control_ids.append(control['id'])
                
                print(f"✓ Commands sent! Control IDs: {control_ids}")
                print(f"  Number of controls: {len(control_ids)} (should be 2)")
                
                # Wait for observation
                print(f"\n>>> DID THE FAN DIRECTION CHANGE TO {name.upper()}? <<<")
                print("Waiting 10 seconds before next change...")
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"✗ Update failed: {e}")
        
        print("\n\nTest complete!")
        print("\nKey findings:")
        print("- The app always sends wind speed (A0) = 41 (AUTO) with fan direction")
        print("- Both commands are sent in a single request")
        print("- The server returns 2 control IDs")
        print("\nDid the fan direction change this time?")


if __name__ == "__main__":
    asyncio.run(test_fan_with_windspeed())