#!/usr/bin/env python3
"""Monitor State8 and all properties with real-time logging."""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
from sharp_cocoro.cocoro import Cocoro
from sharp_cocoro.devices.aircon.aircon import Aircon
from sharp_cocoro.properties import SinglePropertyStatus, RangePropertyStatus, BinaryPropertyStatus


class RealTimeLogger:
    def __init__(self, filename: str):
        self.filename = filename
        self.file = open(filename, 'w')
        self.data = {
            "start_time": datetime.now().isoformat(),
            "snapshots": [],
            "changes": []
        }
        
    def log(self, message: str):
        """Log to both console and file."""
        print(message)
        self.file.write(f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.file.flush()
    
    def save_snapshot(self, snapshot_data: Dict[str, Any]):
        """Save a snapshot to the data structure."""
        self.data["snapshots"].append(snapshot_data)
        self._save_json()
    
    def save_change(self, change_data: Dict[str, Any]):
        """Save a change event to the data structure."""
        self.data["changes"].append(change_data)
        self._save_json()
    
    def _save_json(self):
        """Save the current data to a JSON file."""
        json_filename = self.filename.replace('.log', '.json')
        with open(json_filename, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def close(self):
        """Close the log file."""
        self.file.close()


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
    
    for prop_code, new_value in new_state.items():
        old_value = old_state.get(prop_code)
        if old_value != new_value:
            changes[prop_code] = {
                "old": old_value,
                "new": new_value
            }
    
    return changes


async def capture_device_snapshot(aircon: Aircon) -> Dict[str, Any]:
    """Capture a complete snapshot of the device state."""
    state8 = aircon.get_state8()
    
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


async def monitor_device():
    """Monitor the device and log all changes."""
    log_filename = f"state8_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger = RealTimeLogger(log_filename)
    
    logger.log("=== Sharp Cocoro State8 Monitor ===")
    logger.log(f"Log file: {log_filename}")
    logger.log(f"JSON file: {log_filename.replace('.log', '.json')}")
    logger.log("")
    
    cocoro = Cocoro(
        app_secret="pngtfljRoYsJE9NW7opn1t2cXA5MtZDKbwon368hs80",
        app_key="jXLhL_R8DKVlRX_HqsOXsOizfPPioGQUed2rKdNqFn8",
        service_name="iClub"
    )
    
    async with cocoro:
        logger.log("Logging in...")
        await cocoro.login()
        
        devices = await cocoro.query_devices()
        aircon = None
        
        for device in devices:
            if isinstance(device, Aircon):
                aircon = device
                break
        
        if not aircon:
            logger.log("ERROR: No aircon device found!")
            logger.close()
            return
        
        logger.log(f"Found aircon: {aircon.name}")
        logger.log(f"Model: {aircon.model}")
        logger.log("")
        
        # Take initial snapshot
        logger.log("Taking initial snapshot...")
        initial_snapshot = await capture_device_snapshot(aircon)
        logger.save_snapshot({
            "description": "Initial state",
            "snapshot": initial_snapshot
        })
        
        logger.log(f"Initial State8: {initial_snapshot['state8']}")
        logger.log(f"Initial temperature: {initial_snapshot['state8_decoded']['temperature']}°C")
        logger.log(f"Initial fan direction: {initial_snapshot['state8_decoded']['fan_direction']}")
        logger.log(f"Total properties: {len(initial_snapshot['all_properties'])}")
        logger.log("")
        logger.log("INSTRUCTIONS:")
        logger.log("1. Use your air conditioner remote or app to change settings")
        logger.log("2. Try changing: temperature, fan speed, mode, fan direction, etc.")
        logger.log("3. The script will detect and log all changes")
        logger.log("4. Status report every 20 seconds")
        logger.log("5. Press Ctrl+C to stop monitoring")
        logger.log("")
        logger.log("Monitoring for changes (checking every 5 seconds)...")
        
        last_snapshot = initial_snapshot
        last_report_snapshot = initial_snapshot
        check_count = 0
        report_count = 0
        
        try:
            while True:
                await asyncio.sleep(5)  # Check every 5 seconds
                check_count += 1
                
                # Show we're alive
                sys.stdout.write(f"\r[{datetime.now().strftime('%H:%M:%S')}] Check #{check_count} - Fetching device state...")
                sys.stdout.flush()
                
                # Refresh device state
                aircon = await cocoro.fetch_device(aircon)
                
                # Take new snapshot
                current_snapshot = await capture_device_snapshot(aircon)
                
                # Check for State8 changes
                state8_diffs = compare_hex_strings(last_snapshot['state8'], current_snapshot['state8'])
                
                # Check for property changes
                property_changes = compare_property_states(
                    last_snapshot['all_properties'], 
                    current_snapshot['all_properties']
                )
                
                # Update status line
                sys.stdout.write(f"\r[{datetime.now().strftime('%H:%M:%S')}] Check #{check_count} - Changes: {len(logger.data['changes'])}, Temp: {current_snapshot['state8_decoded']['temperature']}°C, Fan: {current_snapshot['state8_decoded']['fan_direction']}")
                sys.stdout.flush()
                
                # Log immediate changes
                if state8_diffs or property_changes:
                    sys.stdout.write('\r' + ' ' * 100 + '\r')  # Clear progress line
                    
                    change_data = {
                        "timestamp": datetime.now().isoformat(),
                        "check_number": check_count,
                        "state8_before": last_snapshot['state8'],
                        "state8_after": current_snapshot['state8'],
                        "state8_diffs": state8_diffs,
                        "property_changes": property_changes,
                        "snapshot": current_snapshot
                    }
                    
                    logger.log(f"\n{'='*60}")
                    logger.log(f"CHANGE DETECTED #{len(logger.data['changes']) + 1}")
                    logger.log(f"Time: {datetime.now().strftime('%H:%M:%S')}")
                    
                    if state8_diffs:
                        logger.log("\nState8 changes:")
                        for diff in state8_diffs:
                            logger.log(f"  Position {diff['position']} (byte {diff['byte_index']}): "
                                     f"{diff['old_value']} -> {diff['new_value']} "
                                     f"(decimal: {diff['old_int']} -> {diff['new_int']}, diff: {diff['diff']})")
                        
                        # Check if known positions changed
                        for diff in state8_diffs:
                            if diff['position'] in [52, 53]:
                                logger.log("  -> Temperature byte changed")
                            elif diff['position'] == 97:
                                logger.log("  -> Fan direction changed")
                            elif diff['position'] in [0, 1]:
                                logger.log("  -> Header byte changed")
                    
                    if property_changes:
                        logger.log("\nProperty changes:")
                        for prop_code, change in property_changes.items():
                            prop_name = current_snapshot['property_details'].get(prop_code, {}).get('name', prop_code)
                            logger.log(f"  {prop_name} ({prop_code}): {change['old']} -> {change['new']}")
                    
                    # Log decoded values
                    logger.log("\nDecoded value changes:")
                    old_decoded = last_snapshot['state8_decoded']
                    new_decoded = current_snapshot['state8_decoded']
                    if old_decoded['temperature'] != new_decoded['temperature']:
                        logger.log(f"  Temperature: {old_decoded['temperature']}°C -> {new_decoded['temperature']}°C")
                    if old_decoded['fan_direction'] != new_decoded['fan_direction']:
                        logger.log(f"  Fan direction: {old_decoded['fan_direction']} -> {new_decoded['fan_direction']}")
                    
                    # Log specific values
                    for key, value in current_snapshot['specific_values'].items():
                        old_value = last_snapshot['specific_values'].get(key)
                        if old_value != value:
                            logger.log(f"  {key}: {old_value} -> {value}")
                    
                    logger.log(f"{'='*60}\n")
                    
                    # Save change
                    logger.save_change(change_data)
                
                # Periodic report every 20 seconds (4 checks)
                if check_count % 4 == 0:
                    report_count += 1
                    sys.stdout.write('\r' + ' ' * 100 + '\r')  # Clear progress line
                    
                    logger.log(f"\n{'='*60}")
                    logger.log(f"PERIODIC REPORT #{report_count} (Check #{check_count})")
                    logger.log(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.log("")
                    
                    # Current values
                    logger.log("Current values:")
                    logger.log(f"  Temperature: {current_snapshot['state8_decoded']['temperature']}°C")
                    logger.log(f"  Fan direction: {current_snapshot['state8_decoded']['fan_direction']}")
                    logger.log(f"  Power: {current_snapshot['specific_values'].get('power', 'N/A')}")
                    logger.log(f"  Operation mode: {current_snapshot['specific_values'].get('operation_mode', 'N/A')}")
                    logger.log(f"  Room temperature: {current_snapshot['specific_values'].get('room_temperature', 'N/A')}°C")
                    logger.log(f"  Wind speed: {current_snapshot['specific_values'].get('windspeed', 'N/A')}")
                    
                    # Show State8
                    logger.log("\nCurrent State8:")
                    logger.log(f"  {current_snapshot['state8']}")
                    
                    # Compare with last report
                    report_state8_diffs = compare_hex_strings(last_report_snapshot['state8'], current_snapshot['state8'])
                    report_property_changes = compare_property_states(
                        last_report_snapshot['all_properties'], 
                        current_snapshot['all_properties']
                    )
                    
                    if report_state8_diffs or report_property_changes:
                        logger.log("\nChanges since last report:")
                        
                        if report_state8_diffs:
                            logger.log("  State8 positions changed: " + 
                                     ", ".join([str(d['position']) for d in report_state8_diffs]))
                        
                        if report_property_changes:
                            logger.log("  Properties changed: " + 
                                     ", ".join([f"{current_snapshot['property_details'].get(code, {}).get('name', code)} ({code})" 
                                              for code in report_property_changes.keys()]))
                    else:
                        logger.log("\nNo changes since last report")
                    
                    logger.log(f"Total changes detected so far: {len(logger.data['changes'])}")
                    logger.log(f"{'='*60}\n")
                    
                    # Save periodic snapshot
                    logger.save_snapshot({
                        "description": f"Periodic report #{report_count}",
                        "snapshot": current_snapshot,
                        "changes_since_last_report": {
                            "state8_diffs": report_state8_diffs,
                            "property_changes": report_property_changes
                        }
                    })
                    
                    last_report_snapshot = current_snapshot
                
                # Always update last snapshot
                last_snapshot = current_snapshot
                    
        except KeyboardInterrupt:
            sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear progress line
            logger.log("\n\nMonitoring stopped by user.")
            logger.log(f"Total checks: {check_count}")
            logger.log(f"Total changes detected: {len(logger.data['changes'])}")
            
            # Final analysis
            logger.log("\n=== ANALYSIS SUMMARY ===")
            
            # Track which positions changed
            all_changed_positions = set()
            position_frequency = {}
            
            for change in logger.data['changes']:
                for diff in change.get('state8_diffs', []):
                    pos = diff['position']
                    all_changed_positions.add(pos)
                    position_frequency[pos] = position_frequency.get(pos, 0) + 1
            
            logger.log(f"\nState8 positions that changed: {sorted(all_changed_positions)}")
            logger.log(f"Total positions changed: {len(all_changed_positions)} out of 160")
            
            logger.log("\nMost frequently changed positions:")
            for pos, count in sorted(position_frequency.items(), key=lambda x: x[1], reverse=True)[:10]:
                logger.log(f"  Position {pos}: changed {count} times")
            
            # Track property correlations
            property_frequency = {}
            for change in logger.data['changes']:
                for prop_code in change.get('property_changes', {}):
                    property_frequency[prop_code] = property_frequency.get(prop_code, 0) + 1
            
            logger.log("\nMost frequently changed properties:")
            for prop_code, count in sorted(property_frequency.items(), key=lambda x: x[1], reverse=True)[:10]:
                prop_name = None
                for snapshot in logger.data['snapshots']:
                    if prop_code in snapshot['snapshot']['property_details']:
                        prop_name = snapshot['snapshot']['property_details'][prop_code]['name']
                        break
                logger.log(f"  {prop_name} ({prop_code}): changed {count} times")
            
            logger.log(f"\nData saved to: {log_filename.replace('.log', '.json')}")
            logger.close()


if __name__ == "__main__":
    asyncio.run(monitor_device())