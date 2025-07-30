"""
Common filtering utilities for both PC and EarthSearch
"""
from typing import List, Dict
from ..core.collections import STACItemCollection

def filter_by_cloud_cover(item_collection: STACItemCollection, max_cloud_cover: float) -> STACItemCollection:
    """Filter items by maximum cloud cover percentage."""
    filtered_items = []
    for item_data in item_collection._raw_items:
        cloud_cover = item_data.get('properties', {}).get('eo:cloud_cover')
        if cloud_cover is None or cloud_cover <= max_cloud_cover:
            filtered_items.append(item_data)
    return STACItemCollection(filtered_items, provider=item_collection.provider)
