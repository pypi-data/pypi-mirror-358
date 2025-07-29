#!/usr/bin/env python3
"""Test the fan direction fix."""

import asyncio
from sharp_cocoro.cocoro import Cocoro
from sharp_cocoro.devices.aircon.aircon import Aircon
from sharp_cocoro.state import State8


async def test_fan_direction_fix():
    """Test the fixed fan direction implementation."""
    cocoro = Cocoro(
        app_secret="pngtfljRoYsJE9NW7opn1t2cXA5MtZDKbwon368hs80",
        app_key="jXLhL_R8DKVlRX_HqsOXsOizfPPioGQUed2rKdNqFn8",
        service_name="iClub"
    )
    
    async with cocoro:
        print("=== Testing Fan Direction Fix ===\n")
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
        print(f"Initial fan direction: {initial_state.fan_direction}")
        print(f"Initial temperature: {initial_state.temperature}°C")
        print()
        
        # Test the fix - verify command encoding is preserved
        print("Testing command state generation (verifying fix):")
        test_directions = [0, 2, 4]  # Top, Middle, Bottom
        
        for fan_dir in test_directions:
            # Create fresh command state
            cmd_state = State8("c20000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000101000000000000000000000000000000000000000000000000000000000000")
            cmd_state.fan_direction = fan_dir
            
            # Verify encoding is preserved
            print(f"\nFan direction {fan_dir}:")
            print(f"  State starts with: {cmd_state.state[:10]}")
            print(f"  Position 0-1: {cmd_state.state[0:2]} (should be c{fan_dir+1})")
            print(f"  Position 96: {cmd_state.state[96]} (should be {fan_dir})")
            
            # Verify command encoding is correct
            expected_pos0 = f"c{fan_dir+1}"
            if cmd_state.state[0:2] == expected_pos0:
                print("  ✓ Command encoding preserved!")
            else:
                print(f"  ✗ Command encoding lost! Expected {expected_pos0}, got {cmd_state.state[0:2]}")
        
        # Now test actual device control
        print("\n\n=== Testing Actual Device Control ===")
        print("I will cycle through fan directions: Middle (2) → Bottom (4) → Top (0)")
        print("Please watch your air conditioner and tell me if the fan direction changes.\n")
        
        test_sequence = [2, 4, 0]  # Middle, Bottom, Top
        
        for fan_dir in test_sequence:
            direction_names = {0: "Top", 1: "Top-Middle", 2: "Middle", 3: "Middle-Bottom", 4: "Bottom", 5: "Fixed", 7: "Auto/Swing"}
            direction_name = direction_names.get(fan_dir, f"Unknown ({fan_dir})")
            
            print(f"\nSetting fan direction to: {direction_name} (value: {fan_dir})")
            
            # Queue the update
            aircon.queue_fan_direction_update(str(fan_dir))
            
            # Verify what will be sent
            if 'FA' in aircon.property_updates:
                state_to_send = aircon.property_updates['FA'].valueBinary['code']
                print(f"State8 to send: {state_to_send[:20]}...")
                print(f"  Position 0-1: {state_to_send[0:2]} (should be c{fan_dir+1})")
                print(f"  Position 96: {state_to_send[96]} (should be {fan_dir})")
            
            # Execute the update
            print("Executing update...")
            try:
                await cocoro.execute_queued_updates(aircon)
                print("✓ Command sent successfully!")
                
                # Wait for user observation
                print(f"\n>>> DID THE FAN DIRECTION CHANGE TO {direction_name.upper()}? <<<")
                print("Waiting 10 seconds before next change...")
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"✗ Update failed: {e}")
        
        print("\n\nTest complete!")
        print("\nPlease tell me:")
        print("1. Did you see the fan direction change for each command?")
        print("2. Did it go: Middle → Bottom → Top?")
        print("3. Or did nothing happen at all?")




if __name__ == "__main__":
    asyncio.run(test_fan_direction_fix())