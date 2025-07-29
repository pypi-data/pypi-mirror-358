#!/usr/bin/env python3
"""Test the control result polling functions."""

import asyncio
import time
from sharp_cocoro.cocoro import Cocoro
from sharp_cocoro.devices.aircon.aircon import Aircon
from sharp_cocoro.devices.aircon.aircon_properties import ValueSingle
from sharp_cocoro.properties import ControlResultStatus


async def test_manual_polling():
    """Test manual polling with check_control_results."""
    cocoro = Cocoro(
        app_secret="pngtfljRoYsJE9NW7opn1t2cXA5MtZDKbwon368hs80",
        app_key="jXLhL_R8DKVlRX_HqsOXsOizfPPioGQUed2rKdNqFn8",
        service_name="iClub"
    )
    
    async with cocoro:
        print("=== Testing Manual Control Result Polling ===\n")
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
        
        # Get initial wind speed
        initial_ws = aircon.get_windspeed()
        print(f"Initial wind speed: {initial_ws}")
        
        # Queue a wind speed change
        new_windspeed = ValueSingle.WINDSPEED_LEVEL_3
        if initial_ws == ValueSingle.WINDSPEED_LEVEL_3:
            new_windspeed = ValueSingle.WINDSPEED_LEVEL_5
        
        print(f"Changing wind speed to: {new_windspeed}")
        aircon.queue_windspeed_update(new_windspeed)
        
        # Execute the update and get control IDs
        print("\nExecuting control command...")
        result = await cocoro.execute_queued_updates(aircon)
        
        # Extract control IDs from the response
        control_ids = []
        if 'controlList' in result:
            for control in result['controlList']:
                if 'id' in control:
                    control_ids.append(control['id'])
        
        print(f"Control IDs: {control_ids}")
        
        if not control_ids:
            print("No control IDs returned!")
            return
        
        # Manual polling loop
        print("\n--- Manual Polling ---")
        start_time = time.time()
        poll_count = 0
        max_polls = 30  # Maximum 30 polls (30 seconds with 1 second interval)
        
        while poll_count < max_polls:
            poll_count += 1
            elapsed = time.time() - start_time
            
            print(f"\nPoll #{poll_count} (elapsed: {elapsed:.1f}s)")
            
            # Check control results
            control_result = await cocoro.check_control_results(aircon, control_ids)
            
            # Display results
            for item in control_result.resultList:
                print(f"  Control {item.id}:")
                print(f"    Status: {item.status}")
                print(f"    Error Code: {item.errorCode or 'None'}")
            
            # Check if all are finished
            finished_states = {ControlResultStatus.SUCCESS, ControlResultStatus.UNMATCH}
            all_finished = all(
                item.status in finished_states for item in control_result.resultList
            )
            
            if all_finished:
                print("\n✓ All controls completed!")
                break
            
            # Wait before next poll
            await asyncio.sleep(1.0)
        
        if poll_count >= max_polls:
            print("\n✗ Timeout: Controls did not complete within 30 seconds")
        
        # Check final device state
        print("\nRefreshing device state...")
        await asyncio.sleep(2)
        aircon = await cocoro.fetch_device(aircon)
        new_ws = aircon.get_windspeed()
        print(f"New wind speed: {new_ws}")
        
        if new_ws == new_windspeed:
            print("✓ Wind speed changed successfully!")
        else:
            print("✗ Wind speed did not change as expected")


async def test_automatic_polling():
    """Test automatic polling with wait_for_control_completion."""
    cocoro = Cocoro(
        app_secret="pngtfljRoYsJE9NW7opn1t2cXA5MtZDKbwon368hs80",
        app_key="jXLhL_R8DKVlRX_HqsOXsOizfPPioGQUed2rKdNqFn8",
        service_name="iClub"
    )
    
    async with cocoro:
        print("\n\n=== Testing Automatic Control Result Polling ===\n")
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
        
        # Get initial wind speed
        initial_ws = aircon.get_windspeed()
        print(f"Initial wind speed: {initial_ws}")
        
        # Queue a wind speed change
        new_windspeed = ValueSingle.WINDSPEED_LEVEL_7
        if initial_ws == ValueSingle.WINDSPEED_LEVEL_7:
            new_windspeed = ValueSingle.WINDSPEED_LEVEL_2
        
        print(f"Changing wind speed to: {new_windspeed}")
        aircon.queue_windspeed_update(new_windspeed)
        
        # Execute the update and get control IDs
        print("\nExecuting control command...")
        result = await cocoro.execute_queued_updates(aircon)
        
        # Extract control IDs from the response
        control_ids = []
        if 'controlList' in result:
            for control in result['controlList']:
                if 'id' in control:
                    control_ids.append(control['id'])
        
        print(f"Control IDs: {control_ids}")
        
        if not control_ids:
            print("No control IDs returned!")
            return
        
        # Automatic polling
        print("\n--- Automatic Polling ---")
        print("Waiting for control completion (timeout: 15s, poll interval: 1s)...")
        
        try:
            start_time = time.time()
            final_result = await cocoro.wait_for_control_completion(
                aircon, 
                control_ids,
                timeout=15.0,
                poll_interval=1.0
            )
            elapsed = time.time() - start_time
            
            print(f"\n✓ Controls completed after {elapsed:.1f} seconds!")
            
            # Display final results
            for item in final_result.resultList:
                print(f"  Control {item.id}:")
                print(f"    Final Status: {item.status}")
                print(f"    Error Code: {item.errorCode or 'None'}")
            
        except TimeoutError as e:
            print(f"\n✗ {e}")
        except Exception as e:
            print(f"\n✗ Error: {e}")
        
        # Check final device state
        print("\nRefreshing device state...")
        await asyncio.sleep(2)
        aircon = await cocoro.fetch_device(aircon)
        new_ws = aircon.get_windspeed()
        print(f"New wind speed: {new_ws}")
        
        if new_ws == new_windspeed:
            print("✓ Wind speed changed successfully!")
        else:
            print("✗ Wind speed did not change as expected")


async def main():
    """Run both tests."""
    # Test manual polling
    await test_manual_polling()
    
    # Wait a bit between tests
    await asyncio.sleep(5)
    
    # Test automatic polling
    await test_automatic_polling()


if __name__ == "__main__":
    asyncio.run(main())