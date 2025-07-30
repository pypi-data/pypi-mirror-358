"""
Open Geodata API: Unified Python client for open geospatial data APIs
Supports Microsoft Planetary Computer, AWS EarthSearch, and more
"""

__version__ = "0.2.1"
__author__ = "Mirjan Ali Sha"
__email__ = "mastools.help@gmail.com"

# Core imports - always available
from .planetary.client import PlanetaryComputerCollections
from .earthsearch.client import EarthSearchCollections
from .core.items import STACItem
from .core.assets import STACAsset, STACAssets
from .core.collections import STACItemCollection
from .core.search import STACSearch

# Signing and validation - core functionality
from .planetary.signing import sign_url, sign_item, sign_asset_urls
from .earthsearch.validation import validate_url, validate_item, validate_asset_urls

# Basic utilities
from .utils.filters import filter_by_cloud_cover

# Factory functions
def planetary_computer(auto_sign: bool = False, verbose: bool = False):
    """Create Planetary Computer client with enhanced pagination."""
    return PlanetaryComputerCollections(auto_sign=auto_sign, verbose=verbose)

def earth_search(auto_validate: bool = False, verbose: bool = False):
    """Create EarthSearch client with enhanced pagination."""
    return EarthSearchCollections(auto_validate=auto_validate, verbose=verbose)


def get_clients(pc_auto_sign: bool = False, es_auto_validate: bool = False):
    """Get both clients for unified access."""
    return {
        'planetary_computer': planetary_computer(auto_sign=pc_auto_sign),
        'earth_search': earth_search(auto_validate=es_auto_validate)
    }

def info():
    """Display package capabilities."""
    print(f"📦 Open Geodata API v{__version__}")
    print(f"🎯 Core Focus: API access, search, and URL management")
    print(f"")
    print(f"📡 Supported APIs:")
    print(f"   🌍 Microsoft Planetary Computer (with URL signing)")
    print(f"   🔗 AWS Element84 EarthSearch (with URL validation)")
    print(f"")
    print(f"🛠️ Core Capabilities:")
    print(f"   ✅ STAC API search and discovery")
    print(f"   ✅ Asset URL management (automatic signing/validation)")
    print(f"   ✅ DataFrame conversion (pandas/geopandas)")
    print(f"   ✅ Flexible data access (use any raster package you prefer)")
    print(f"")
    print(f"💡 Data Reading Philosophy:")
    print(f"   🔗 We provide URLs - you choose how to read them!")
    print(f"   📦 Use rioxarray, rasterio, GDAL, or any package you prefer")
    print(f"   🚀 Maximum flexibility, zero restrictions")

__all__ = [
    # Client classes
    'PlanetaryComputerCollections', 'EarthSearchCollections',
    # Core STAC classes  
    'STACItem', 'STACAsset', 'STACAssets', 'STACItemCollection', 'STACSearch',
    # URL management
    'sign_url', 'sign_item', 'sign_asset_urls',
    'validate_url', 'validate_item', 'validate_asset_urls',
    # Utilities
    'filter_by_cloud_cover',
    # Factory functions
    'planetary_computer', 'earth_search', 'get_clients', 'info'
]
