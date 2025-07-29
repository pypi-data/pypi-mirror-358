#!/usr/bin/env python3
"""Test with exact State8 matching captured payloads."""

import asyncio
from sharp_cocoro.cocoro import Cocoro
from sharp_cocoro.devices.aircon.aircon import Aircon
from sharp_cocoro.devices.aircon.aircon_properties import ValueSingle
from sharp_cocoro.state import State8


async def test_exact_state8():
    """Test with exact State8 from captured requests."""
    cocoro = Cocoro(
        app_secret="pngtfljRoYsJE9NW7opn1t2cXA5MtZDKbwon368hs80",
        app_key="jXLhL_R8DKVlRX_HqsOXsOizfPPioGQUed2rKdNqFn8",
        service_name="iClub"
    )
    
    async with cocoro:
        print("=== Testing with Exact State8 from Captures ===\n")
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
        
        # Test our State8 generation vs captured
        print("=== Comparing our State8 with captured ===")
        
        captured_state8 = {
            0: "c10000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000",
            2: "c30000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000201000000000000000000000000000000000000000000000000000000000000",
            4: "c50000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000401000000000000000000000000000000000000000000000000000000000000",
        }
        
        for fan_dir, expected in captured_state8.items():
            # Generate our State8
            s8 = State8("c20000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000101000000000000000000000000000000000000000000000000000000000000")
            s8.fan_direction = fan_dir
            
            print(f"\nFan direction {fan_dir}:")
            print(f"  Expected: {expected}")
            print(f"  Generated: {s8.state}")
            print(f"  Match: {s8.state == expected}")
            
            if s8.state != expected:
                # Find differences
                for i in range(0, 160, 2):
                    if expected[i:i+2] != s8.state[i:i+2]:
                        print(f"  Diff at {i}-{i+1}: expected '{expected[i:i+2]}', got '{s8.state[i:i+2]}'")
        
        print("\n\n=== Testing with App Request ===")
        print("Sending fan direction = Middle (2) with exact captured State8\n")
        
        # Queue updates exactly as the app does
        aircon.queue_windspeed_update(ValueSingle.WINDSPEED_LEVEL_AUTO)
        
        # Use the exact captured State8 for middle position
        from sharp_cocoro.properties import BinaryPropertyStatus
        from sharp_cocoro.devices.aircon.aircon_properties import StatusCode
        
        aircon.queue_property_status_update(BinaryPropertyStatus(StatusCode.STATE_DETAIL, {
            "code": "c30000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000201000000000000000000000000000000000000000000000000000000000000"
        }))
        
        print("Executing with exact captured State8...")
        try:
            result = await cocoro.execute_queued_updates(aircon)
            control_ids = []
            if 'controlList' in result:
                for control in result['controlList']:
                    if 'id' in control:
                        control_ids.append(control['id'])
            
            print(f"✓ Commands sent! Control IDs: {control_ids}")
            print("\n>>> DID THE FAN DIRECTION CHANGE TO MIDDLE THIS TIME? <<<")
            
        except Exception as e:
            print(f"✗ Update failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_exact_state8())