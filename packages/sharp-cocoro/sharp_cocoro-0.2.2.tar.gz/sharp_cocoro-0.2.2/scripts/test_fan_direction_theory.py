#!/usr/bin/env python3
"""Test our theory about State8 position 0 encoding."""

import asyncio
from datetime import datetime
from sharp_cocoro.cocoro import Cocoro
from sharp_cocoro.devices.aircon.aircon import Aircon


async def test_position_0_theory():
    """Test if position 0 follows our discovered pattern."""
    cocoro = Cocoro(
        app_secret="pngtfljRoYsJE9NW7opn1t2cXA5MtZDKbwon368hs80",
        app_key="jXLhL_R8DKVlRX_HqsOXsOizfPPioGQUed2rKdNqFn8",
        service_name="iClub"
    )
    
    test_results = []
    
    async with cocoro:
        print("=== Testing State8 Position 0 Theory ===\n")
        print("Theory:")
        print("- When fan_direction = 7: pos0 = 27 + (temp - 18) * 2")
        print("- When fan_direction = 0-5: pos0 = 116 + fan_direction")
        print("\nLogging in...")
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
        initial_temp = initial_state.temperature
        initial_fan = initial_state.fan_direction
        
        print(f"Initial state:")
        print(f"  Temperature: {initial_temp}°C")
        print(f"  Fan direction: {initial_fan}")
        print(f"  Position 0: {initial_state.state[0:2]}")
        print(f"  Full State8: {initial_state.state}")
        print()
        
        # Test 1: Fan direction changes (0-5 and 7)
        print("=== Test 1: Fan Direction Changes ===")
        test_directions = [0, 1, 2, 3, 4, 5, 7]
        
        for fan_dir in test_directions:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Setting fan direction to {fan_dir}...")
            
            # Set fan direction
            aircon.queue_fan_direction_update(str(fan_dir))
            await cocoro.execute_queued_updates(aircon)
            
            print("Waiting 10 seconds for device to update...")
            await asyncio.sleep(10)
            
            # Refresh device state
            print("Fetching updated state...")
            aircon = await cocoro.fetch_device(aircon)
            new_state = aircon.get_state8()
            
            # Calculate expected position 0
            temp = new_state.temperature
            if fan_dir == 7:
                expected_pos0 = hex(27 + int((temp - 18) * 2))[2:].zfill(2).upper()
            else:
                expected_pos0 = hex(116 + fan_dir)[2:].zfill(2).upper()
            
            actual_pos0 = new_state.state[0:2]
            
            result = {
                'fan_direction': fan_dir,
                'temperature': temp,
                'expected_pos0': expected_pos0,
                'actual_pos0': actual_pos0,
                'match': expected_pos0 == actual_pos0,
                'full_state8': new_state.state
            }
            test_results.append(result)
            
            print(f"Results:")
            print(f"  Temperature: {temp}°C")
            print(f"  Fan direction: {new_state.fan_direction}")
            print(f"  Position 0: {actual_pos0}")
            print(f"  Expected: {expected_pos0}")
            print(f"  Match: {'✓' if result['match'] else '✗'}")
            
            if not result['match']:
                print(f"  MISMATCH! Expected {expected_pos0} but got {actual_pos0}")
        
        # Test 2: Temperature changes with fan_dir=7
        print("\n\n=== Test 2: Temperature Changes (fan_dir=7) ===")
        
        # First ensure fan direction is 7
        if new_state.fan_direction != 7:
            print("Setting fan direction to 7...")
            aircon.queue_fan_direction_update("7")
            await cocoro.execute_queued_updates(aircon)
            await asyncio.sleep(10)
            aircon = await cocoro.fetch_device(aircon)
        
        test_temps = [19.0, 20.0, 21.0, 18.0]  # Test different temperatures
        
        for temp in test_temps:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Setting temperature to {temp}°C...")
            
            # Set temperature
            aircon.queue_temperature_update(temp)
            await cocoro.execute_queued_updates(aircon)
            
            print("Waiting 10 seconds for device to update...")
            await asyncio.sleep(10)
            
            # Refresh device state
            print("Fetching updated state...")
            aircon = await cocoro.fetch_device(aircon)
            new_state = aircon.get_state8()
            
            # Calculate expected position 0 (fan_dir should be 7)
            if new_state.fan_direction == 7:
                expected_pos0 = hex(27 + int((temp - 18) * 2))[2:].zfill(2).upper()
            else:
                expected_pos0 = hex(116 + new_state.fan_direction)[2:].zfill(2).upper()
            
            actual_pos0 = new_state.state[0:2]
            
            result = {
                'temperature_set': temp,
                'temperature_actual': new_state.temperature,
                'fan_direction': new_state.fan_direction,
                'expected_pos0': expected_pos0,
                'actual_pos0': actual_pos0,
                'match': expected_pos0 == actual_pos0,
                'full_state8': new_state.state
            }
            test_results.append(result)
            
            print(f"Results:")
            print(f"  Set temperature: {temp}°C")
            print(f"  Actual temperature: {new_state.temperature}°C")
            print(f"  Fan direction: {new_state.fan_direction}")
            print(f"  Position 0: {actual_pos0}")
            print(f"  Expected: {expected_pos0}")
            print(f"  Match: {'✓' if result['match'] else '✗'}")
            
            if not result['match']:
                print(f"  MISMATCH! Expected {expected_pos0} but got {actual_pos0}")
        
        # Summary
        print("\n\n=== SUMMARY ===")
        print(f"Total tests: {len(test_results)}")
        matches = sum(1 for r in test_results if r['match'])
        print(f"Matches: {matches}")
        print(f"Mismatches: {len(test_results) - matches}")
        print(f"Success rate: {matches/len(test_results)*100:.1f}%")
        
        if matches < len(test_results):
            print("\nMismatches:")
            for r in test_results:
                if not r['match']:
                    if 'temperature_set' in r:
                        print(f"  Temp {r['temperature_set']}°C, Fan {r['fan_direction']}: "
                              f"expected {r['expected_pos0']}, got {r['actual_pos0']}")
                    else:
                        print(f"  Fan {r['fan_direction']}, Temp {r['temperature']}°C: "
                              f"expected {r['expected_pos0']}, got {r['actual_pos0']}")
        
        # Restore initial state
        print(f"\n\nRestoring initial state (fan={initial_fan}, temp={initial_temp}°C)...")
        if initial_fan != new_state.fan_direction:
            aircon.queue_fan_direction_update(str(initial_fan))
            await cocoro.execute_queued_updates(aircon)
            await asyncio.sleep(5)
        
        if abs(initial_temp - new_state.temperature) > 0.5:
            aircon = await cocoro.fetch_device(aircon)
            aircon.queue_temperature_update(initial_temp)
            await cocoro.execute_queued_updates(aircon)
        
        print("Done!")


if __name__ == "__main__":
    asyncio.run(test_position_0_theory())