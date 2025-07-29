#!/usr/bin/env python3
"""Debug script to display Sharp Cocoro device information."""

import asyncio
from sharp_cocoro.cocoro import Cocoro
from sharp_cocoro.devices.aircon.aircon import Aircon
from sharp_cocoro.devices.purifier.purifier import Purifier


async def main():
    # Use the same credentials from the test file
    cocoro = Cocoro(
        app_secret="pngtfljRoYsJE9NW7opn1t2cXA5MtZDKbwon368hs80",
        app_key="jXLhL_R8DKVlRX_HqsOXsOizfPPioGQUed2rKdNqFn8",
        service_name="iClub"
    )
    
    async with cocoro:
        print("=== Logging in ===")
        await cocoro.login()
        print("Login successful!")
        print()
        
        print("=== Fetching devices ===")
        devices = await cocoro.query_devices()
        print(f"Found {len(devices)} device(s)")
        print()
        
        for i, device in enumerate(devices):
            print(f"=== Device {i+1}/{len(devices)} ===")
            print(f"Name: {device.name}")
            print(f"Type: {device.kind}")
            print(f"Device ID: {device.device_id}")
            print(f"Maker: {device.maker}")
            print(f"Model: {device.model}")
            print(f"Serial Number: {device.serial_number}")
            print(f"Echonet Node: {device.echonet_node}")
            print(f"Echonet Object: {device.echonet_object}")
            print()
            
            # Get all properties
            print("--- All Properties ---")
            all_properties = device.get_all_properties()
            print(f"Total properties available: {len(all_properties)}")
            print()
            
            # Dump all properties with their current values
            print("--- Property Dump ---")
            device.dump_all_properties()
            print()
            
            # For Aircon devices, also get State8 information
            if isinstance(device, Aircon):
                print("--- Aircon-specific State8 Information ---")
                try:
                    state8 = device.get_state8()
                    print(f"State8 raw hex: {state8.state}")
                    print(f"State8 length: {len(state8.state)} chars")
                    print(f"Temperature from State8: {state8.temperature}°C")
                    print(f"Fan direction from State8: {state8.fan_direction}")
                except Exception as e:
                    print(f"Error getting State8: {e}")
                print()
                
                # Also show other Aircon-specific getters
                print("--- Other Aircon Properties ---")
                try:
                    print(f"Power status: {device.get_power_status()}")
                    print(f"Operation mode: {device.get_operation_mode()}")
                    print(f"Room temperature: {device.get_room_temperature()}°C")
                    print(f"Wind speed: {device.get_windspeed()}")
                except Exception as e:
                    print(f"Error getting property: {e}")
                    
            elif isinstance(device, Purifier):
                print("--- Purifier-specific Properties ---")
                try:
                    print(f"Power status: {device.get_power_status()}")
                    print(f"Operation mode: {device.get_operation_mode()}")
                    print(f"Air volume: {device.get_air_volume()}")
                    print(f"Humidity: {device.get_humidity()}%")
                    print(f"Room temperature: {device.get_room_temperature()}°C")
                    print(f"PM2.5: {device.get_pm25()}")
                    print(f"Filter life: {device.get_filter_life()}%")
                except Exception as e:
                    print(f"Error getting property: {e}")
            else:
                print("This is an Unknown device type - no specific getters available")
                
            print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())