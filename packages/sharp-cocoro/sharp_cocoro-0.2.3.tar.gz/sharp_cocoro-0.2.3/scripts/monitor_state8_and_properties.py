#!/usr/bin/env python3
"""Monitor State8 and all properties to find correlations and mappings."""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Set
from sharp_cocoro.cocoro import Cocoro
from sharp_cocoro.devices.aircon.aircon import Aircon
from sharp_cocoro.properties import SinglePropertyStatus, RangePropertyStatus, BinaryPropertyStatus


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


def extract_property_value(status) -> Any:
    """Extract the actual value from a PropertyStatus object."""
    if isinstance(status, SinglePropertyStatus):
        return status.valueSingle.get('code', status.valueSingle)
    elif isinstance(status, RangePropertyStatus):
        return status.valueRange.get('code', status.valueRange)
    elif isinstance(status, BinaryPropertyStatus):
        return status.valueBinary.get('code', status.valueBinary)
    else:
        return str(status)


def compare_property_states(old_state: Dict[str, Any], new_state: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two property states and return what changed."""
    changes = {}
    
    # Check for changed properties
    for prop_code, new_value in new_state.items():
        old_value = old_state.get(prop_code)
        if old_value != new_value:
            changes[prop_code] = {
                "old": old_value,
                "new": new_value
            }
    
    # Check for removed properties
    for prop_code in old_state:
        if prop_code not in new_state:
            changes[prop_code] = {
                "old": old_state[prop_code],
                "new": None
            }
    
    return changes


async def capture_device_snapshot(aircon: Aircon) -> Dict[str, Any]:
    """Capture a complete snapshot of the device state."""
    # Get State8
    state8 = aircon.get_state8()
    
    # Collect all properties with their values
    all_properties = {}
    property_details = {}
    
    for prop in aircon.properties:
        status = aircon.get_property_status(prop.statusCode)
        if status:
            value = extract_property_value(status)
            all_properties[prop.statusCode] = value
            property_details[prop.statusCode] = {
                "name": prop.statusName,
                "value": value,
                "type": status.valueType.value if hasattr(status.valueType, 'value') else str(status.valueType),
                "get": prop.get,
                "set": prop.set,
                "inf": prop.inf
            }
    
    # Get specific values using getter methods
    specific_values = {}
    try:
        specific_values["power"] = aircon.get_power_status().value
    except:
        pass
    
    try:
        specific_values["operation_mode"] = aircon.get_operation_mode().value
    except:
        pass
    
    try:
        specific_values["temperature"] = aircon.get_temperature()
    except:
        pass
    
    try:
        specific_values["room_temperature"] = aircon.get_room_temperature()
    except:
        pass
    
    try:
        specific_values["windspeed"] = aircon.get_windspeed().value
    except:
        pass
    
    try:
        specific_values["fan_direction"] = aircon.get_fan_direction().value
    except:
        pass
    
    return {
        "timestamp": datetime.now().isoformat(),
        "state8": state8.state,
        "state8_decoded": {
            "temperature": state8.temperature,
            "fan_direction": state8.fan_direction
        },
        "specific_values": specific_values,
        "all_properties": all_properties,
        "property_details": property_details
    }


async def monitor_passive_changes():
    """Monitor the device passively to see natural state changes."""
    cocoro = Cocoro(
        app_secret="pngtfljRoYsJE9NW7opn1t2cXA5MtZDKbwon368hs80",
        app_key="jXLhL_R8DKVlRX_HqsOXsOizfPPioGQUed2rKdNqFn8",
        service_name="iClub"
    )
    
    snapshots = []
    
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
        
        # Take initial snapshot
        print("Taking initial snapshot...")
        initial_snapshot = await capture_device_snapshot(aircon)
        snapshots.append({
            "description": "Initial state",
            "snapshot": initial_snapshot
        })
        
        print(f"Initial State8: {initial_snapshot['state8']}")
        print(f"Total properties: {len(initial_snapshot['all_properties'])}")
        print()
        
        # Monitor for changes
        print("Monitoring for changes... (Press Ctrl+C to stop)")
        print("Change device settings using your remote or app to see what changes.")
        print()
        
        last_state8 = initial_snapshot['state8']
        last_properties = initial_snapshot['all_properties']
        
        try:
            while True:
                await asyncio.sleep(5)  # Check every 5 seconds
                
                # Refresh device state
                aircon = await cocoro.fetch_device(aircon)
                
                # Take new snapshot
                current_snapshot = await capture_device_snapshot(aircon)
                current_state8 = current_snapshot['state8']
                current_properties = current_snapshot['all_properties']
                
                # Check for State8 changes
                state8_diffs = compare_hex_strings(last_state8, current_state8)
                
                # Check for property changes
                property_changes = compare_property_states(last_properties, current_properties)
                
                if state8_diffs or property_changes:
                    print(f"\n{'='*60}")
                    print(f"Change detected at {datetime.now().strftime('%H:%M:%S')}")
                    
                    if state8_diffs:
                        print("\nState8 changes:")
                        for diff in state8_diffs:
                            print(f"  Position {diff['position']} (byte {diff['byte_index']}): "
                                  f"{diff['old_value']} -> {diff['new_value']} "
                                  f"(decimal: {diff['old_int']} -> {diff['new_int']}, diff: {diff['diff']})")
                    
                    if property_changes:
                        print("\nProperty changes:")
                        for prop_code, change in property_changes.items():
                            prop_name = current_snapshot['property_details'].get(prop_code, {}).get('name', prop_code)
                            print(f"  {prop_name} ({prop_code}): {change['old']} -> {change['new']}")
                    
                    # Show specific value changes
                    print("\nSpecific value changes:")
                    for key, value in current_snapshot['specific_values'].items():
                        old_value = snapshots[-1]['snapshot']['specific_values'].get(key)
                        if old_value != value:
                            print(f"  {key}: {old_value} -> {value}")
                    
                    # Save snapshot with changes
                    snapshots.append({
                        "description": f"Change detected at {datetime.now().strftime('%H:%M:%S')}",
                        "snapshot": current_snapshot,
                        "state8_diffs": state8_diffs,
                        "property_changes": property_changes
                    })
                    
                    # Update last state
                    last_state8 = current_state8
                    last_properties = current_properties
                    
                    print(f"{'='*60}\n")
                else:
                    print(".", end="", flush=True)
                    
        except KeyboardInterrupt:
            print("\n\nStopping monitoring...")
        
        # Save all snapshots
        filename = f"state8_monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(snapshots, f, indent=2)
        
        print(f"\n=== Monitoring data saved to {filename} ===")
        
        # Analyze correlations
        print("\n=== Analysis of correlations ===")
        
        # Track which State8 positions changed with which properties
        position_to_properties: Dict[int, Set[str]] = {}
        property_to_positions: Dict[str, Set[int]] = {}
        
        for snapshot_data in snapshots[1:]:  # Skip initial
            if 'state8_diffs' in snapshot_data and 'property_changes' in snapshot_data:
                state8_diffs = snapshot_data['state8_diffs']
                property_changes = snapshot_data['property_changes']
                
                for diff in state8_diffs:
                    pos = diff['position']
                    if pos not in position_to_properties:
                        position_to_properties[pos] = set()
                    
                    for prop_code in property_changes:
                        position_to_properties[pos].add(prop_code)
                        
                        if prop_code not in property_to_positions:
                            property_to_positions[prop_code] = set()
                        property_to_positions[prop_code].add(pos)
        
        print("\nState8 positions that changed with specific properties:")
        for pos in sorted(position_to_properties.keys()):
            props = position_to_properties[pos]
            if props:
                prop_names = []
                for prop_code in props:
                    for snapshot in snapshots:
                        if prop_code in snapshot['snapshot']['property_details']:
                            prop_names.append(f"{snapshot['snapshot']['property_details'][prop_code]['name']} ({prop_code})")
                            break
                print(f"  Position {pos}: {', '.join(set(prop_names))}")
        
        print("\nProperties and their correlated State8 positions:")
        for prop_code in sorted(property_to_positions.keys()):
            positions = sorted(property_to_positions[prop_code])
            prop_name = None
            for snapshot in snapshots:
                if prop_code in snapshot['snapshot']['property_details']:
                    prop_name = snapshot['snapshot']['property_details'][prop_code]['name']
                    break
            print(f"  {prop_name} ({prop_code}): positions {positions}")


async def monitor_with_active_changes():
    """Actively change settings and monitor all changes."""
    cocoro = Cocoro(
        app_secret="pngtfljRoYsJE9NW7opn1t2cXA5MtZDKbwon368hs80",
        app_key="jXLhL_R8DKVlRX_HqsOXsOizfPPioGQUed2rKdNqFn8",
        service_name="iClub"
    )
    
    snapshots = []
    
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
        
        # Take initial snapshot
        print("Taking initial snapshot...")
        initial_snapshot = await capture_device_snapshot(aircon)
        snapshots.append({
            "description": "Initial state",
            "snapshot": initial_snapshot
        })
        
        # Test temperature changes
        print("\n=== Testing temperature changes ===")
        for temp in [20.0, 22.0, 24.0]:
            print(f"\nChanging temperature to {temp}°C...")
            aircon.queue_temperature_update(temp)
            await cocoro.execute_queued_updates(aircon)
            await asyncio.sleep(2)
            
            aircon = await cocoro.fetch_device(aircon)
            new_snapshot = await capture_device_snapshot(aircon)
            
            state8_diffs = compare_hex_strings(snapshots[-1]['snapshot']['state8'], new_snapshot['state8'])
            property_changes = compare_property_states(snapshots[-1]['snapshot']['all_properties'], new_snapshot['all_properties'])
            
            snapshots.append({
                "description": f"Temperature changed to {temp}°C",
                "snapshot": new_snapshot,
                "state8_diffs": state8_diffs,
                "property_changes": property_changes
            })
            
            print(f"State8 positions changed: {[d['position'] for d in state8_diffs]}")
            print(f"Properties changed: {list(property_changes.keys())}")
        
        # Save results
        filename = f"state8_active_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(snapshots, f, indent=2)
        
        print(f"\n=== Analysis saved to {filename} ===")


if __name__ == "__main__":
    print("Choose monitoring mode:")
    print("1. Passive monitoring (watch for manual changes)")
    print("2. Active monitoring (make controlled changes)")
    
    choice = input("Enter 1 or 2: ").strip()
    
    if choice == "1":
        asyncio.run(monitor_passive_changes())
    elif choice == "2":
        asyncio.run(monitor_with_active_changes())
    else:
        print("Invalid choice")