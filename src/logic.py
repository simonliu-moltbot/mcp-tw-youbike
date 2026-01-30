import httpx
import math
import asyncio
from typing import List, Dict, Any, Optional
from src.config import TAIPEI_YOUBIKE_URL

class YouBikeClient:
    def __init__(self):
        self.url = TAIPEI_YOUBIKE_URL
        self._cache = None
        self._cache_time = 0
        self._cache_ttl = 60  # Cache for 60 seconds

    async def search_stations(self, keyword: str) -> List[Dict[str, Any]]:
        """Search for stations by name (case-insensitive)."""
        # Fetch data asynchronously
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                # In a real app, log error
                return []

        results = []
        keyword = keyword.lower() if keyword else ""
        
        for station in data:
            name = station.get('sna', '').replace('YouBike2.0_', '')
            address = station.get('ar', '')
            district = station.get('sarea', '')
            
            # Search in name, address, or district
            if not keyword or (keyword in name.lower() or keyword in address.lower() or keyword in district.lower()):
                # Handle various key formats (standard vs readable)
                total = station.get('tot') or station.get('Quantity') or 0
                bikes = station.get('sbi') or station.get('available_rent_bikes') or 0
                empty = station.get('bemp') or station.get('available_return_bikes') or 0
                lat = station.get('lat') or station.get('latitude') or 0
                lon = station.get('lng') or station.get('longitude') or 0
                update_time = station.get('mday') or station.get('updateTime') or ""

                results.append({
                    "station_no": station.get('sno'),
                    "name": name,
                    "district": district,
                    "address": address,
                    "total_spaces": int(total),
                    "available_bikes": int(bikes),
                    "empty_spaces": int(empty),
                    "update_time": update_time,
                    "lat": float(lat),
                    "lon": float(lon)
                })
        
        return results

    async def get_nearby_stations(self, lat: float, lon: float, radius_km: float = 0.5, limit: int = 5) -> List[Dict[str, Any]]:
        """Find stations near a specific location."""
        # Reuse search logic to get all data, then filter by distance
        all_stations = await self.search_stations("") 
        nearby = []
        
        R = 6371  # Earth radius in km

        for station in all_stations:
            try:
                s_lat = station['lat']
                s_lon = station['lon']
                
                # Haversine formula
                dlat = math.radians(s_lat - lat)
                dlon = math.radians(s_lon - lon)
                a = math.sin(dlat/2) * math.sin(dlat/2) + \
                    math.cos(math.radians(lat)) * math.cos(math.radians(s_lat)) * \
                    math.sin(dlon/2) * math.sin(dlon/2)
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                distance = R * c
                
                if distance <= radius_km:
                    station['distance_m'] = int(distance * 1000)
                    nearby.append(station)
            except (ValueError, TypeError):
                continue
                
        # Sort by distance
        nearby.sort(key=lambda x: x.get('distance_m', 999999))
        return nearby[:limit]
