"""
Enhanced EarthSearch client with 502 error handling and smaller chunks
"""

import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
from ..core.base_client import BaseSTACClient
from ..core.search import STACSearch

class EarthSearchCollections(BaseSTACClient):
    """EarthSearch client with enhanced 502 error handling and smaller chunks."""

    def __init__(self, auto_validate: bool = False, verbose: bool = False):
        super().__init__(
            base_url="https://earth-search.aws.element84.com/v1",
            provider_name="earthsearch",
            verbose=verbose
        )
        self.auto_validate = auto_validate
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def _make_request_with_retry(self, url, json_data=None, headers=None):
        """Make request with retry logic for 502 errors."""
        
        for attempt in range(self.max_retries):
            try:
                if json_data:
                    response = requests.post(url, json=json_data, headers=headers, timeout=30)
                else:
                    response = requests.get(url, headers=headers, timeout=30)
                
                # Handle 502 specifically
                if response.status_code == 502:
                    if attempt < self.max_retries - 1:
                        if self.verbose:
                            print(f"   ⚠️ 502 error, retrying in {self.retry_delay}s (attempt {attempt + 1}/{self.max_retries})")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        raise requests.exceptions.HTTPError(f"502 Bad Gateway after {self.max_retries} attempts")
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    if self.verbose:
                        print(f"   ⚠️ Timeout, retrying in {self.retry_delay}s (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise
            except requests.exceptions.RequestException as e:
                if "502" in str(e) and attempt < self.max_retries - 1:
                    if self.verbose:
                        print(f"   ⚠️ Server error, retrying in {self.retry_delay}s (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise
        
        return response

    def search(self,
               collections: Optional[List[str]] = None,
               intersects: Optional[Dict] = None,
               bbox: Optional[List[float]] = None,
               datetime: Optional[Union[str, List[str], Tuple[str, str]]] = None,
               query: Optional[Dict] = None,
               limit: Optional[int] = None,
               max_items: Optional[int] = None) -> STACSearch:
        """🔥 ENHANCED SEARCH for EarthSearch with 502 error handling."""

        if collections:
            invalid_collections = [col for col in collections if col not in self.collections]
            if invalid_collections:
                raise ValueError(f"Invalid collections: {invalid_collections}")

        # Handle tuple datetime format
        if isinstance(datetime, tuple) and len(datetime) == 2:
            start_date, end_date = datetime
            datetime = f"{start_date}/{end_date}"

        search_payload = self._build_search_payload(
            collections, intersects, bbox, datetime, query, limit
        )

        try:
            # For unlimited searches, use enhanced chunking with 502 handling
            if limit is None or limit == 0:
                all_items = self._get_all_items_pagination(search_payload, max_items)
                if not self.verbose and len(all_items) > 0:
                    print(f"✅ Retrieved {len(all_items)} total items")
                
                return STACSearch({
                    "items": all_items,
                    "total_returned": len(all_items),
                    "search_params": search_payload,
                    "collections_searched": collections or "all",
                    "method_used": "earthsearch_enhanced_pagination",
                    "all_items_cached": True
                }, provider="earthsearch", client_instance=self, original_search_params=search_payload)
            else:
                # Limited search with smaller chunks
                search_payload["limit"] = min(limit, 100)  # Smaller limit for ES
                return self._search_single_page(search_payload, max_items)
                
        except Exception as e:
            # Better error handling for 502s
            if "502" in str(e) or "Bad Gateway" in str(e):
                print(f"❌ EarthSearch server overloaded (502 error). Try:")
                print(f"   • Shorter time period (current: {search_payload.get('datetime', 'not specified')})")
                print(f"   • Use Planetary Computer instead: -p pc")
                print(f"   • Smaller area or stricter cloud cover filter")
            else:
                print(f"❌ Search error: {e}")
            
            return STACSearch({"items": [], "total_returned": 0, "error": str(e)}, 
                            provider="earthsearch")

    def _get_all_items_pagination(self, search_payload: Dict, max_items: Optional[int] = None) -> List[Dict]:
        """🔥 ENHANCED EarthSearch pagination with 502 error handling and smaller chunks."""
        
        # For large time ranges, use aggressive time-based chunking
        if "datetime" in search_payload and "/" in search_payload["datetime"]:
            return self._chunked_time_search_es(search_payload, max_items)
        else:
            return self._standard_pagination_es(search_payload, max_items)

    def _chunked_time_search_es(self, search_params: Dict, max_items: Optional[int] = None) -> List[Dict]:
        """🔥 AGGRESSIVE time-based chunking for EarthSearch to avoid 502s."""
        
        start_date_str, end_date_str = search_params["datetime"].split("/")
        start_dt = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        
        # Calculate total days and determine chunk size
        total_days = (end_dt - start_dt).days
        
        # 🔥 SMALLER CHUNKS for EarthSearch to prevent 502s
        if total_days > 365:
            chunk_days = 15  # Very small chunks for large ranges
        elif total_days > 180:
            chunk_days = 20  # Small chunks for medium ranges
        else:
            chunk_days = 30  # Standard chunks for small ranges
        
        all_items = []
        current_dt = start_dt
        chunk_count = 0
        failed_chunks = 0
        
        headers = {'Content-Type': 'application/json', 'Accept': 'application/geo+json'}
        
        if self.verbose:
            print(f"🔍 EarthSearch: Using {chunk_days}-day chunks for {total_days} total days...")
        
        while current_dt < end_dt:
            chunk_count += 1
            chunk_end = min(current_dt + timedelta(days=chunk_days), end_dt)
            chunk_datetime = f"{current_dt.strftime('%Y-%m-%dT%H:%M:%SZ')}/{chunk_end.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            
            chunk_params = search_params.copy()
            chunk_params["datetime"] = chunk_datetime
            chunk_params["limit"] = 50  # 🔥 VERY SMALL limit for EarthSearch
            
            try:
                if self.verbose:
                    print(f"   📅 Chunk {chunk_count}: {chunk_datetime[:10]} to {chunk_end.strftime('%Y-%m-%d')}")
                
                # Use retry logic for this chunk
                response = self._make_request_with_retry(
                    self.search_url, 
                    json_data=chunk_params, 
                    headers=headers
                )
                
                data = response.json()
                
                if isinstance(data, dict) and 'features' in data:
                    chunk_items = data.get("features", [])
                elif isinstance(data, list):
                    chunk_items = data
                else:
                    chunk_items = []
                
                all_items.extend(chunk_items)
                
                if self.verbose:
                    print(f"   ✅ Chunk {chunk_count}: {len(chunk_items)} items (total: {len(all_items)})")
                
                if max_items and len(all_items) >= max_items:
                    all_items = all_items[:max_items]
                    break
                    
            except Exception as e:
                failed_chunks += 1
                if "502" in str(e) or "Bad Gateway" in str(e):
                    if self.verbose:
                        print(f"   ❌ Chunk {chunk_count}: 502 error, skipping")
                    # Try with even smaller chunk for this time period
                    if chunk_days > 7:
                        smaller_chunks = self._try_smaller_chunk(search_params, current_dt, chunk_end, chunk_days // 2)
                        all_items.extend(smaller_chunks)
                else:
                    if self.verbose:
                        print(f"   ❌ Chunk {chunk_count}: {e}")
            
            current_dt = chunk_end
            
            # Add small delay to avoid overwhelming the server
            time.sleep(0.5)
        
        if failed_chunks > 0:
            print(f"⚠️ EarthSearch: {failed_chunks} chunks failed due to server issues")
        
        return all_items

    def _try_smaller_chunk(self, search_params: Dict, start_dt: datetime, end_dt: datetime, smaller_days: int) -> List[Dict]:
        """Try with smaller chunks when 502 errors occur."""
        
        items = []
        current_dt = start_dt
        headers = {'Content-Type': 'application/json', 'Accept': 'application/geo+json'}
        
        while current_dt < end_dt:
            chunk_end = min(current_dt + timedelta(days=smaller_days), end_dt)
            chunk_datetime = f"{current_dt.strftime('%Y-%m-%dT%H:%M:%SZ')}/{chunk_end.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            
            chunk_params = search_params.copy()
            chunk_params["datetime"] = chunk_datetime
            chunk_params["limit"] = 25  # Even smaller limit
            
            try:
                response = self._make_request_with_retry(
                    self.search_url, 
                    json_data=chunk_params, 
                    headers=headers
                )
                
                data = response.json()
                
                if isinstance(data, dict) and 'features' in data:
                    chunk_items = data.get("features", [])
                elif isinstance(data, list):
                    chunk_items = data
                else:
                    chunk_items = []
                
                items.extend(chunk_items)
                
                if self.verbose:
                    print(f"   🔧 Smaller chunk: {len(chunk_items)} items")
                    
            except Exception:
                # Skip this smaller chunk if it still fails
                if self.verbose:
                    print(f"   🔧 Smaller chunk failed, skipping")
                pass
            
            current_dt = chunk_end
            time.sleep(0.3)  # Slower processing
        
        return items

    def _standard_pagination_es(self, search_payload: Dict, max_items: Optional[int] = None) -> List[Dict]:
        """Standard EarthSearch pagination with 502 handling."""
        
        all_items = []
        page_limit = 50  # 🔥 SMALLER page size for EarthSearch
        next_link = None
        page_count = 0
        
        headers = {'Content-Type': 'application/json', 'Accept': 'application/geo+json'}
        
        if self.verbose:
            print(f"🔍 EarthSearch: Using standard pagination with {page_limit} items per page...")
        
        while True:
            page_count += 1
            
            try:
                if next_link is None:
                    # First request
                    current_payload = {**search_payload, "limit": page_limit}
                    response = self._make_request_with_retry(
                        self.search_url, 
                        json_data=current_payload, 
                        headers=headers
                    )
                else:
                    # Follow next link
                    response = self._make_request_with_retry(next_link, headers=headers)
                
                data = response.json()
                
                # Get items from this page
                if isinstance(data, dict) and 'features' in data:
                    page_items = data.get("features", [])
                elif isinstance(data, list):
                    page_items = data
                else:
                    page_items = []
                
                if not page_items:
                    break
                
                all_items.extend(page_items)
                
                if self.verbose:
                    print(f"   📄 Page {page_count}: {len(page_items)} items (total: {len(all_items)})")
                
                # Check if we've reached max_items
                if max_items and len(all_items) >= max_items:
                    all_items = all_items[:max_items]
                    break
                
                # Look for next link
                next_link = None
                if isinstance(data, dict):
                    links = data.get("links", [])
                    for link in links:
                        if link.get("rel") == "next":
                            next_link = link.get("href")
                            break
                
                # If no next link, we're done
                if not next_link:
                    break
                
                # If we got fewer items than page_limit, we're likely done
                if len(page_items) < page_limit:
                    break
                
                # Add delay between pages
                time.sleep(0.3)
                
            except Exception as e:
                if "502" in str(e) or "Bad Gateway" in str(e):
                    if self.verbose:
                        print(f"   ❌ Page {page_count}: 502 error, stopping pagination")
                    break
                else:
                    if self.verbose:
                        print(f"   ❌ Page {page_count}: {e}")
                    break
        
        return all_items

    def _search_single_page(self, search_payload: Dict, max_items: Optional[int]) -> STACSearch:
        """Search with specified limit using retry logic."""
        
        headers = {'Content-Type': 'application/json', 'Accept': 'application/geo+json'}
        
        try:
            response = self._make_request_with_retry(
                self.search_url, 
                json_data=search_payload, 
                headers=headers
            )
            data = response.json()
            
            if isinstance(data, dict) and 'features' in data:
                items = data.get("features", [])
            elif isinstance(data, list):
                items = data
            else:
                items = []
            
            if max_items and len(items) > max_items:
                items = items[:max_items]
            
            return STACSearch({
                "items": items,
                "total_returned": len(items),
                "search_params": search_payload,
                "collections_searched": search_payload.get("collections", "all"),
                "method_used": "single_page_with_retry"
            }, provider="earthsearch")
            
        except Exception as e:
            if "502" in str(e) or "Bad Gateway" in str(e):
                print(f"❌ EarthSearch overloaded. Try: shorter time period or use -p pc")
            raise e
