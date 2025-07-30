"""
Planetary Computer client with unified interface
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from ..core.base_client import BaseSTACClient
from ..core.search import STACSearch

class PlanetaryComputerCollections(BaseSTACClient):
    """Planetary Computer client with enhanced pagination."""

    def __init__(self, auto_sign: bool = False, verbose: bool = False):
        super().__init__(
            base_url="https://planetarycomputer.microsoft.com/api/stac/v1",
            provider_name="planetary_computer",
            verbose=verbose
        )
        self.auto_sign = auto_sign

    def search(self,
               collections: Optional[List[str]] = None,
               intersects: Optional[Dict] = None,
               bbox: Optional[List[float]] = None,
               datetime: Optional[Union[str, List[str]]] = None,
               query: Optional[Dict] = None,
               limit: Optional[int] = None,
               max_items: Optional[int] = None) -> STACSearch:
        """🔥 UNIFIED SEARCH - Gets ALL items by default, not just 100!"""

        if collections:
            invalid_collections = [col for col in collections if col not in self.collections]
            if invalid_collections:
                raise ValueError(f"Invalid collections: {invalid_collections}")

        search_payload = self._build_search_payload(
            collections, intersects, bbox, datetime, query, limit
        )

        try:
            # For unlimited searches, get ALL items using pagination
            if limit is None or limit == 0:
                all_items = self._get_all_items_pagination(search_payload, max_items)
                if not self.verbose:
                    print(f"✅ Retrieved {len(all_items)} total items")
                
                return STACSearch({
                    "items": all_items,
                    "total_returned": len(all_items),
                    "search_params": search_payload,
                    "collections_searched": collections or "all",
                    "method_used": "planetary_computer_pagination",
                    "all_items_cached": True
                }, provider="planetary_computer", client_instance=self, original_search_params=search_payload)
            else:
                # Limited search
                search_payload["limit"] = min(limit, 10000)
                return self._search_single_page(search_payload, max_items)
                
        except Exception as e:
            print(f"Search error: {e}")
            return STACSearch({"items": [], "total_returned": 0, "error": str(e)}, 
                            provider="planetary_computer")

    def _get_all_items_pagination(self, search_params: Dict, max_items: Optional[int] = None) -> List[Dict]:
        """Planetary Computer pagination using time-based chunking."""
        
        if "datetime" in search_params and "/" in search_params["datetime"]:
            return self._chunked_time_search(search_params, max_items)
        else:
            return self._chunked_spatial_search(search_params, max_items)

    def _chunked_time_search(self, search_params: Dict, max_items: Optional[int] = None) -> List[Dict]:
        """Break time range into chunks to bypass 100-item limit."""
        
        start_date_str, end_date_str = search_params["datetime"].split("/")
        start_dt = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        
        all_items = []
        chunk_days = 30
        current_dt = start_dt
        chunk_count = 0
        
        headers = {'Content-Type': 'application/json', 'Accept': 'application/geo+json'}
        
        if self.verbose:
            print(f"🔍 Fetching all items using time-based chunking...")
        
        while current_dt < end_dt:
            chunk_count += 1
            chunk_end = min(current_dt + timedelta(days=chunk_days), end_dt)
            chunk_datetime = f"{current_dt.strftime('%Y-%m-%dT%H:%M:%SZ')}/{chunk_end.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            
            chunk_payload = search_params.copy()
            chunk_payload["datetime"] = chunk_datetime
            chunk_payload["limit"] = 1000
            
            try:
                response = requests.post(self.search_url, json=chunk_payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                chunk_items = data.get("features", [])
                all_items.extend(chunk_items)
                
                if self.verbose:
                    print(f"   Chunk {chunk_count}: {len(chunk_items)} items (total: {len(all_items)})")
                
                if max_items and len(all_items) >= max_items:
                    all_items = all_items[:max_items]
                    break
                    
            except Exception as e:
                if self.verbose:
                    print(f"   Error in chunk {chunk_count}: {e}")
            
            current_dt = chunk_end
        
        return all_items

    def _chunked_spatial_search(self, search_params: Dict, max_items: Optional[int] = None) -> List[Dict]:
        """Break spatial area into chunks for non-date searches."""
        
        if "bbox" not in search_params:
            return self._single_large_request(search_params, max_items)
        
        bbox = search_params["bbox"]
        west, south, east, north = bbox
        
        mid_lon = (west + east) / 2
        mid_lat = (south + north) / 2
        
        quadrants = [
            [west, south, mid_lon, mid_lat],
            [mid_lon, south, east, mid_lat],
            [west, mid_lat, mid_lon, north],
            [mid_lon, mid_lat, east, north]
        ]
        
        all_items = []
        headers = {'Content-Type': 'application/json', 'Accept': 'application/geo+json'}
        
        if self.verbose:
            print(f"🔍 Fetching all items using spatial chunking...")
        
        for i, quad_bbox in enumerate(quadrants):
            quad_payload = search_params.copy()
            quad_payload["bbox"] = quad_bbox
            quad_payload["limit"] = 1000
            
            try:
                response = requests.post(self.search_url, json=quad_payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                quad_items = data.get("features", [])
                existing_ids = {item.get('id') for item in all_items}
                new_items = [item for item in quad_items if item.get('id') not in existing_ids]
                
                all_items.extend(new_items)
                
                if self.verbose:
                    print(f"   Quadrant {i+1}: {len(new_items)} new items (total: {len(all_items)})")
                
                if max_items and len(all_items) >= max_items:
                    all_items = all_items[:max_items]
                    break
                    
            except Exception as e:
                if self.verbose:
                    print(f"   Error in quadrant {i+1}: {e}")
        
        return all_items

    def _single_large_request(self, search_params: Dict, max_items: Optional[int] = None) -> List[Dict]:
        """Fallback: single large request."""
        headers = {'Content-Type': 'application/json', 'Accept': 'application/geo+json'}
        
        large_payload = search_params.copy()
        large_payload["limit"] = max_items or 10000
        
        try:
            response = requests.post(self.search_url, json=large_payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("features", [])
        except Exception as e:
            if self.verbose:
                print(f"Single request failed: {e}")
            return []

    def _search_single_page(self, search_payload: Dict, max_items: Optional[int]) -> STACSearch:
        """Search with specified limit (single page)."""
        headers = {'Content-Type': 'application/json', 'Accept': 'application/geo+json'}
        
        response = requests.post(self.search_url, json=search_payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        items = data.get("features", [])
        
        if max_items and len(items) > max_items:
            items = items[:max_items]
        
        return STACSearch({
            "items": items,
            "total_returned": len(items),
            "search_params": search_payload,
            "collections_searched": search_payload.get("collections", "all"),
            "method_used": "single_page"
        }, provider="planetary_computer")
