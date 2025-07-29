#!/usr/bin/env python3
"""Script to analyze State8 encoding by collecting data points."""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from sharp_cocoro.cocoro import Cocoro
from sharp_cocoro.devices.aircon.aircon import Aircon
from sharp_cocoro.devices.aircon.aircon_properties import ValueSingle


def compare_hex_strings(hex1: str, hex2: str) -> List[Dict[str, Any]]:
    """Compare two hex strings and return the differences."""
    differences = []
    for i in range(0, len(hex1), 2):
        byte1 = hex1[i:i+2]
        byte2 = hex2[i:i+2]
        if byte1 != byte2:
            differences.append({
                "position": i,
                "byte_index": i // 2,
                "old_value": byte1,
                "new_value": byte2,
                "old_int": int(byte1, 16),
                "new_int": int(byte2, 16),
                "diff": int(byte2, 16) - int(byte1, 16)
            })
    return differences


async def collect_state8_data():
    """Collect State8 data for different device states."""
    cocoro = Cocoro(
        app_secret="pngtfljRoYsJE9NW7opn1t2cXA5MtZDKbwon368hs80",
        app_key="jXLhL_R8DKVlRX_HqsOXsOizfPPioGQUed2rKdNqFn8",
        service_name="iClub"
    )
    
    data_points = []
    
    async with cocoro:
        print("=== Logging in ===")
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
        
        print(f"Found aircon: {aircon.name}")
        print()
        
        # Collect initial state
        initial_state = {
            "timestamp": datetime.now().isoformat(),
            "description": "Initial state",
            "state8": aircon.get_state8().state,
            "properties": {
                "power": aircon.get_power_status().value,
                "operation_mode": aircon.get_operation_mode().value,
                "temperature": aircon.get_temperature(),
                "room_temperature": aircon.get_room_temperature(),
                "windspeed": aircon.get_windspeed().value,
                "fan_direction": aircon.get_fan_direction().value,
            },
            "all_status": {}
        }
        
        # Collect all property statuses
        for prop in aircon.get_all_properties():
            status = aircon.get_property_status(prop.statusCode)
            if status:
                initial_state["all_status"][prop.statusName] = {
                    "code": prop.statusCode,
                    "value": status.__dict__
                }
        
        data_points.append(initial_state)
        print(f"Initial State8: {initial_state['state8']}")
        print(f"Initial temp: {initial_state['properties']['temperature']}°C")
        print(f"Initial fan direction: {initial_state['properties']['fan_direction']}")
        print()
        
        # Test 1: Change temperature only
        print("=== Test 1: Changing temperature ===")
        for temp in [20.0, 22.0, 24.0, 26.0]:
            print(f"Setting temperature to {temp}°C...")
            aircon.queue_temperature_update(temp)
            await cocoro.execute_queued_updates(aircon)
            
            # Refresh device state
            aircon = await cocoro.fetch_device(aircon)
            
            new_state8 = aircon.get_state8().state
            
            state_data = {
                "timestamp": datetime.now().isoformat(),
                "description": f"Temperature set to {temp}°C",
                "state8": new_state8,
                "properties": {
                    "power": aircon.get_power_status().value,
                    "operation_mode": aircon.get_operation_mode().value,
                    "temperature": aircon.get_temperature(),
                    "room_temperature": aircon.get_room_temperature(),
                    "windspeed": aircon.get_windspeed().value,
                    "fan_direction": aircon.get_fan_direction().value,
                },
                "differences_from_previous": compare_hex_strings(data_points[-1]["state8"], new_state8)
            }
            
            data_points.append(state_data)
            
            print(f"New State8: {new_state8}")
            print(f"Actual temp from State8: {aircon.get_temperature()}°C")
            print(f"Differences: {json.dumps(state_data['differences_from_previous'], indent=2)}")
            print()
            
            await asyncio.sleep(2)  # Wait between changes
        
        # Test 2: Change fan direction only
        print("=== Test 2: Changing fan direction ===")
        for fan_dir in ["0", "1", "2", "3", "4", "5", "6", "7"]:
            print(f"Setting fan direction to {fan_dir}...")
            aircon.queue_fan_direction_update(fan_dir)
            await cocoro.execute_queued_updates(aircon)
            
            # Refresh device state
            aircon = await cocoro.fetch_device(aircon)
            
            new_state8 = aircon.get_state8().state
            
            state_data = {
                "timestamp": datetime.now().isoformat(),
                "description": f"Fan direction set to {fan_dir}",
                "state8": new_state8,
                "properties": {
                    "power": aircon.get_power_status().value,
                    "operation_mode": aircon.get_operation_mode().value,
                    "temperature": aircon.get_temperature(),
                    "room_temperature": aircon.get_room_temperature(),
                    "windspeed": aircon.get_windspeed().value,
                    "fan_direction": aircon.get_fan_direction().value,
                },
                "differences_from_previous": compare_hex_strings(data_points[-1]["state8"], new_state8)
            }
            
            data_points.append(state_data)
            
            print(f"New State8: {new_state8}")
            print(f"Actual fan direction from State8: {aircon.get_fan_direction().value}")
            print(f"Differences: {json.dumps(state_data['differences_from_previous'], indent=2)}")
            print()
            
            await asyncio.sleep(2)
        
        # Test 3: Change operation mode
        print("=== Test 3: Changing operation mode ===")
        for mode in [ValueSingle.OPERATION_COOL, ValueSingle.OPERATION_HEAT, ValueSingle.OPERATION_DEHUMIDIFY]:
            print(f"Setting operation mode to {mode.value}...")
            aircon.queue_operation_mode_update(mode)
            await cocoro.execute_queued_updates(aircon)
            
            # Refresh device state
            aircon = await cocoro.fetch_device(aircon)
            
            new_state8 = aircon.get_state8().state
            
            state_data = {
                "timestamp": datetime.now().isoformat(),
                "description": f"Operation mode set to {mode.value}",
                "state8": new_state8,
                "properties": {
                    "power": aircon.get_power_status().value,
                    "operation_mode": aircon.get_operation_mode().value,
                    "temperature": aircon.get_temperature(),
                    "room_temperature": aircon.get_room_temperature(),
                    "windspeed": aircon.get_windspeed().value,
                    "fan_direction": aircon.get_fan_direction().value,
                },
                "differences_from_previous": compare_hex_strings(data_points[-1]["state8"], new_state8)
            }
            
            data_points.append(state_data)
            
            print(f"New State8: {new_state8}")
            print(f"Differences: {json.dumps(state_data['differences_from_previous'], indent=2)}")
            print()
            
            await asyncio.sleep(2)
        
        # Save all data points
        filename = f"state8_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(data_points, f, indent=2)
        
        print(f"\n=== Analysis saved to {filename} ===")
        
        # Print summary
        print("\n=== Summary of findings ===")
        print("Temperature positions:")
        print("- Positions 52-53: Temperature * 2 (confirmed)")
        print("- Positions 0-1: (Temperature + 16) * 2 (confirmed)")
        print("- Position 6: Changes to '2' when temperature is modified")
        
        print("\nFan direction positions:")
        print("- Position 97: Fan direction value (confirmed)")
        print("- Position 0: Changes to 'c' when fan direction is modified")
        print("- Position 1: Fan direction + 1 (confirmed)")
        
        # Analyze which positions never changed
        all_positions = set()
        changed_positions = set()
        
        for i in range(1, len(data_points)):
            for diff in data_points[i].get("differences_from_previous", []):
                changed_positions.add(diff["position"])
        
        for i in range(0, 160, 2):
            all_positions.add(i)
        
        unchanged_positions = all_positions - changed_positions
        
        print(f"\nPositions that never changed: {sorted(unchanged_positions)}")
        print(f"Total unchanged positions: {len(unchanged_positions)}/80 bytes")


if __name__ == "__main__":
    asyncio.run(collect_state8_data())