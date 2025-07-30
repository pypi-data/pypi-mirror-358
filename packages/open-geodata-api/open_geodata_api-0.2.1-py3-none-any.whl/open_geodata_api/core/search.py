"""
Unified STAC Search results class for all providers
"""

from typing import Dict, Optional, Any, List, Union, Callable
from .collections import STACItemCollection

class STACSearch:
    """Universal search results class that works with all providers."""

    def __init__(self, search_results: Dict, provider: str = "unknown", 
                 client_instance=None, original_search_params: Optional[Dict] = None):
        self._results = search_results
        self._items = search_results.get('items', search_results.get('features', []))
        self.provider = provider
        self._client = client_instance
        self._original_params = original_search_params or {}
        
        # Check if all items are already cached
        self._all_items_cached = search_results.get('all_items_cached', False)
        self._all_items_cache = None
        
        # If all items are already cached, set them up immediately
        if self._all_items_cached:
            self._all_items_cache = STACItemCollection(self._items, provider=self.provider)

    def get_all_items(self) -> STACItemCollection:
        """Return all items - works with any provider's pagination."""
        
        # If all items are already cached, return immediately
        if self._all_items_cache:
            return self._all_items_cache
        
        # If items were already fetched during search, use them
        if self._all_items_cached:
            self._all_items_cache = STACItemCollection(self._items, provider=self.provider)
            return self._all_items_cache
        
        # If we have a client that supports pagination, use it
        if self._client and hasattr(self._client, '_get_all_items_pagination'):
            try:
                all_items = self._client._get_all_items_pagination(self._original_params)
                self._all_items_cache = STACItemCollection(all_items, provider=self.provider)
                self._all_items_cached = True
                return self._all_items_cache
            except Exception as e:
                print(f"⚠️ Pagination failed, returning available items: {e}")
            
        # Otherwise return the items we have
        return STACItemCollection(self._items, provider=self.provider)

    def item_collection(self) -> STACItemCollection:
        """Alias for get_all_items()."""
        return self.get_all_items()
    
    def items(self):
        """Return iterator over current items."""
        for item_data in self._items:
            from .items import STACItem
            yield STACItem(item_data, provider=self.provider)

    def matched(self) -> Optional[int]:
        """Return total number of matched items if available."""
        return self._results.get('numberMatched', self._results.get('matched'))

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"STACSearch({len(self._items)} items found, provider='{self.provider}')"
