#!/usr/bin/env python3
"""Simple script to monitor windspeed and temperature every 5 seconds."""

import asyncio
from datetime import datetime
from sharp_cocoro.cocoro import Cocoro
from sharp_cocoro.devices.aircon.aircon import Aircon


async def monitor_simple():
    """Monitor windspeed and temperature."""
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
        
        print(f"Found aircon: {aircon.name}")
        print(f"Model: {aircon.model}")
        print("\nMonitoring windspeed and temperature (Ctrl+C to stop):\n")
        print("Time                | Temperature | Wind Speed")
        print("-" * 50)
        
        try:
            while True:
                # Refresh device state
                aircon = await cocoro.fetch_device(aircon)
                
                # Get current values
                temperature = aircon.get_temperature()
                windspeed = aircon.get_windspeed()
                room_temp = aircon.get_room_temperature()
                
                # Print values
                print(f"{datetime.now().strftime('%H:%M:%S')} | "
                      f"{temperature:>5.1f}°C | "
                      f"{windspeed.value:<20} | "
                      f"Room: {room_temp}°C")
                
                await asyncio.sleep(5)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")


if __name__ == "__main__":
    asyncio.run(monitor_simple())