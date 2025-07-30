"""
Fixed Search CLI commands - compatible with existing client functions
"""
import click
import json
import open_geodata_api as ogapi


def parse_bbox(bbox_str):
    """Parse bbox string to list of floats with better error handling."""
    if not bbox_str:
        raise click.BadParameter('bbox cannot be empty')
    
    try:
        bbox_str = bbox_str.strip()
        if not bbox_str:
            raise ValueError("bbox is empty after stripping whitespace")
        
        bbox = [float(x.strip()) for x in bbox_str.split(',')]
        
        if len(bbox) != 4:
            raise ValueError(f"bbox must have exactly 4 values, got {len(bbox)}")
        
        west, south, east, north = bbox
        
        # Basic validation
        if west >= east:
            raise ValueError("west coordinate must be less than east coordinate")
        if south >= north:
            raise ValueError("south coordinate must be less than north coordinate")
        
        # Coordinate range validation
        if not (-180 <= west <= 180) or not (-180 <= east <= 180):
            raise ValueError("longitude values must be between -180 and 180")
        if not (-90 <= south <= 90) or not (-90 <= north <= 90):
            raise ValueError("latitude values must be between -90 and 90")
        
        return bbox
    
    except ValueError as e:
        raise click.BadParameter(f'Invalid bbox format: {e}. Use: west,south,east,north (e.g., "-122.5,47.5,-122.0,48.0")')


def parse_query(query_str):
    """Parse query string to dictionary."""
    try:
        return json.loads(query_str)
    except json.JSONDecodeError:
        raise click.BadParameter('query must be valid JSON string')


def create_client(provider, verbose=False):
    """Create client with proper parameter handling."""
    try:
        if provider == 'pc':
            # Try with verbose parameter first
            try:
                return ogapi.planetary_computer(auto_sign=True, verbose=verbose)
            except TypeError:
                # Fallback to without verbose if not supported
                return ogapi.planetary_computer(auto_sign=True)
        else:
            # Try with verbose parameter first
            try:
                return ogapi.earth_search(verbose=verbose)
            except TypeError:
                # Fallback to without verbose if not supported
                try:
                    return ogapi.earth_search(auto_validate=False)
                except TypeError:
                    # Fallback to basic call
                    return ogapi.earth_search()
    except Exception as e:
        raise click.ClickException(f"Failed to create {provider} client: {e}")


@click.group(name='search')
def search_group():
    """
    🔍 Enhanced search for satellite data from multiple providers.
    
    Find satellite imagery and data products using spatial, temporal,
    and attribute filters. Now supports UNLIMITED item retrieval using
    enhanced pagination strategies (no more 100-item limit!).
    
    \b
    🔥 NEW FEATURES:
    • Unlimited results by default (bypasses API pagination limits)
    • Enhanced chunking strategies for large datasets  
    • Unified interface across all providers
    • Smart caching and progress feedback
    
    \b
    Common workflows:
    1. Quick search for recent data at a location
    2. Detailed search with multiple filters
    3. Provider comparison for optimal data source
    4. Export search results for batch processing
    
    \b
    Examples:
      ogapi search quick sentinel-2-l2a -b "bbox"     # Gets ALL items
      ogapi search items -c sentinel-2-l2a --bbox     # Enhanced search
      ogapi search compare -c sentinel-2-l2a -b bbox  # Compare providers
    """
    pass


@search_group.command('items')
@click.option('--provider', '-p',
              type=click.Choice(['pc', 'es'], case_sensitive=False),
              default='pc',
              help='Data provider (pc=Planetary Computer, es=EarthSearch)')
@click.option('--collections', '-c',
              required=True,
              help='Comma-separated collection names (e.g., "sentinel-2-l2a,landsat-c2-l2")')
@click.option('--bbox', '-b',
              callback=lambda ctx, param, value: parse_bbox(value) if value else None,
              help='Bounding box as "west,south,east,north" (e.g., "-122.5,47.5,-122.0,48.0")')
@click.option('--datetime', '-d',
              help='Date range as "YYYY-MM-DD/YYYY-MM-DD" or single date "YYYY-MM-DD"')
@click.option('--query', '-q',
              callback=lambda ctx, param, value: parse_query(value) if value else None,
              help='Filter query as JSON (e.g., \'{"eo:cloud_cover":{"lt":30}}\')')
@click.option('--limit', '-l',
              type=int,
              default=None,
              help='Maximum number of items to return (default: unlimited - gets ALL items)')
@click.option('--all', '-a',
              is_flag=True,
              help='Explicitly get all available items (default behavior)')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save search results to JSON file for later processing')
@click.option('--show-assets/--no-assets',
              default=False,
              help='Display available assets/bands for each item (only when not saving to file)')
@click.option('--cloud-cover', '-cc',
              type=float,
              help='Maximum cloud cover percentage (shortcut for common filter)')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Show detailed progress information')
@click.pass_context
def search_items(ctx, provider, collections, bbox, datetime, query, limit, all, output, show_assets, cloud_cover, verbose):
    """
    🛰️ Enhanced search for satellite data items with UNLIMITED results.
    
    🔥 NEW: This command now gets ALL available items by default (not just 100)
    using enhanced pagination strategies. Perfect for comprehensive data discovery.
    """
    from datetime import datetime as dt
    
    # Handle --all flag or --limit 0 to mean unlimited
    if all or limit == 0:
        actual_limit = None  # No limit = get ALL items
        display_limit = "unlimited"
    else:
        actual_limit = limit
        display_limit = str(limit) if limit else "unlimited"
    
    if verbose:
        click.echo(f"🔍 Searching {provider.upper()} for items...")
        click.echo(f"📊 Parameters: collections={collections}, bbox={bbox}, datetime={datetime}")
        click.echo(f"📏 Limit: {display_limit}")
    
    try:
        # 🔥 USE FIXED CLIENT CREATION
        client = create_client(provider, verbose)
        
        if verbose:
            if provider == 'pc':
                click.echo("🌍 Using enhanced Planetary Computer client")
            else:
                click.echo("🔗 Using enhanced EarthSearch client")
        
        # Parse collections
        collections_list = [c.strip() for c in collections.split(',')]
        if verbose:
            click.echo(f"📁 Searching collections: {collections_list}")
        
        # Add cloud cover to query if specified
        if cloud_cover is not None:
            if query is None:
                query = {}
            query['eo:cloud_cover'] = {'lt': cloud_cover}
            if verbose:
                click.echo(f"☁️ Added cloud cover filter: <{cloud_cover}%")
        
        # 🔥 SIMPLIFIED SEARCH using enhanced clients
        click.echo(f"🔍 Searching {provider.upper()}...")
        
        # The new clients handle ALL pagination automatically!
        results = client.search(
            collections=collections_list,
            bbox=bbox,
            datetime=datetime,
            query=query,
            limit=actual_limit  # None = unlimited, gets ALL items
        )
        
        # Get all items - now handled by enhanced clients
        items = results.get_all_items()
        
        if len(items) == 0:
            click.echo("❌ No items found matching search criteria")
            click.echo("\n💡 Try adjusting your search parameters:")
            click.echo("   • Expand the bounding box area")
            click.echo("   • Extend the date range")
            click.echo("   • Increase cloud cover threshold")
            click.echo("   • Check collection names with 'ogapi collections list'")
            return
        
        # Show results summary
        if actual_limit is None:
            click.echo(f"\n✅ Found {len(items)} items (all available)")
        else:
            click.echo(f"\n✅ Found {len(items)} items")
        
        # Only show detailed results if NO output file is specified
        if not output:
            # Display results summary
            if len(items) > 0:
                # Calculate statistics
                cloud_covers = [item.properties.get('eo:cloud_cover') for item in items 
                               if item.properties.get('eo:cloud_cover') is not None]
                
                if cloud_covers:
                    avg_cloud = sum(cloud_covers) / len(cloud_covers)
                    min_cloud = min(cloud_covers)
                    max_cloud = max(cloud_covers)
                    click.echo(f"☁️ Cloud cover: {min_cloud:.1f}% - {max_cloud:.1f}% (avg: {avg_cloud:.1f}%)")
                
                # Show date range
                dates = [item.properties.get('datetime') for item in items 
                        if item.properties.get('datetime')]
                if dates:
                    click.echo(f"📅 Date range: {min(dates)} to {max(dates)}")
            
            # Display individual items (limit to first 10 for console display)
            display_items = items[:10] if len(items) > 10 else items
            for i, item in enumerate(display_items):
                click.echo(f"\n📄 Item {i+1}: {item.id}")
                click.echo(f"   📁 Collection: {item.collection}")
                click.echo(f"   📅 Date: {item.properties.get('datetime', 'N/A')}")
                
                cloud_cover_val = item.properties.get('eo:cloud_cover')
                if cloud_cover_val is not None:
                    click.echo(f"   ☁️ Cloud Cover: {cloud_cover_val:.1f}%")
                
                platform = item.properties.get('platform', item.properties.get('constellation'))
                if platform:
                    click.echo(f"   🛰️ Platform: {platform}")
                
                if show_assets:
                    assets = item.list_assets()
                    if len(assets) <= 8:
                        click.echo(f"   🎯 Assets: {', '.join(assets)}")
                    else:
                        click.echo(f"   🎯 Assets: {', '.join(assets[:8])} ... (+{len(assets)-8} more)")
            
            # Show if there are more items
            if len(items) > 10:
                click.echo(f"\n   ... and {len(items) - 10} more items")
        
        # Save to file if requested
        if output:
            results_data = {
                'search_metadata': {
                    'provider': provider,
                    'collections': collections_list,
                    'bbox': bbox,
                    'datetime': datetime,
                    'query': query,
                    'limit': actual_limit,
                    'unlimited': actual_limit is None,
                    'items_found': len(items),
                    'search_timestamp': dt.now().isoformat(),
                    'enhanced_pagination': True
                },
                'search_params': {
                    'provider': provider,
                    'collections': collections_list,
                    'bbox': bbox,
                    'datetime': datetime,
                    'query': query,
                    'limit': actual_limit
                },
                'returned_count': len(items),
                'items': [item.to_dict() for item in items]
            }
            
            with open(output, 'w') as f:
                json.dump(results_data, f, indent=2)
            click.echo(f"\n💾 Results saved to: {output} ({len(items)} items)")
            
            if len(items) > 100:
                click.echo(f"   🔥 Enhanced pagination retrieved {len(items)} total items (bypassed 100-item limit)")
        
        # Dynamic "Next steps" suggestions
        click.echo(f"\n💡 Next steps:")
        
        # Build the original command dynamically
        cmd_parts = ["ogapi", "search", "items", "-c", f'"{collections}"']
        
        if provider != 'pc':
            cmd_parts.extend(["-p", provider])
        if bbox:
            bbox_str = ",".join(map(str, bbox))
            cmd_parts.extend(["-b", f'"{bbox_str}"'])
        if datetime:
            cmd_parts.extend(["-d", f'"{datetime}"'])
        if cloud_cover:
            cmd_parts.extend(["--cloud-cover", str(cloud_cover)])
        if actual_limit:
            cmd_parts.extend(["--limit", str(actual_limit)])
        if show_assets and not output:
            cmd_parts.append("--show-assets")
        
        original_command = " ".join(cmd_parts)
        
        if not output:
            click.echo(f"   {original_command} -o results.json")
        else:
            click.echo(f"   ogapi download search-results {output}")
        
        # Alternative suggestions
        if bbox:
            bbox_str = ",".join(map(str, bbox))
            main_collection = collections_list[0]
            click.echo(f"   # Alternative quick search:")
            click.echo(f"   ogapi search quick {main_collection} -b \"{bbox_str}\" -o quick_results.json")
    
    except Exception as e:
        click.echo(f"❌ Search failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        
        click.echo("\n💡 Troubleshooting tips:")
        click.echo("   • Check collection names: ogapi collections list")
        click.echo("   • Verify bbox format: west,south,east,north")
        click.echo("   • Check date format: YYYY-MM-DD or YYYY-MM-DD/YYYY-MM-DD")
        click.echo("   • Validate JSON query syntax")
        raise click.Abort()


@search_group.command('quick')
@click.argument('collection')
@click.argument('location', required=False)
@click.option('--bbox', '-b',
              help='Bounding box as "west,south,east,north"')
@click.option('--provider', '-p',
              type=click.Choice(['pc', 'es'], case_sensitive=False),
              default='pc',
              help='Data provider (default: pc)')
@click.option('--days', '-d',
              type=int,
              default=30,
              help='Number of days back to search (default: 30)')
@click.option('--cloud-cover', '-cc',
              type=float,
              default=30,
              help='Maximum cloud cover percentage (default: 30)')
@click.option('--limit', '-l',
              type=int,
              default=None,
              help='Maximum results to show (default: unlimited - gets ALL items)')
@click.option('--all', '-a',
              is_flag=True,
              help='Get all available items (default behavior)')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save results to JSON file')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Show detailed progress information')
@click.pass_context
def quick_search(ctx, collection, location, bbox, provider, days, cloud_cover, limit, all, output, verbose):
    """
    ⚡ Enhanced quick search with UNLIMITED results.
    
    🔥 NEW: Now gets ALL available items by default (not just 5 or 100)
    using enhanced pagination strategies for comprehensive data discovery.
    """
    import json
    from datetime import datetime, timedelta
    
    bbox_str = bbox or location
    if not bbox_str:
        click.echo("❌ Location is required. Use either:")
        click.echo("   ogapi search quick collection --bbox \"-122.5,47.5,-122.0,48.0\"")
        click.echo("   ogapi search quick collection -b \"-122.5,47.5,-122.0,48.0\"")
        return
    
    try:
        bbox_coords = parse_bbox(bbox_str)
        
        # Handle --all flag or --limit 0 to mean unlimited
        if all or limit == 0:
            actual_limit = None  # No limit = get ALL items
            display_limit = "unlimited"
        else:
            actual_limit = limit
            display_limit = str(limit) if limit else "unlimited"
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
        
        if verbose:
            click.echo(f"🔍 Quick search parameters:")
            click.echo(f"   Collection: {collection}")
            click.echo(f"   Bbox: {bbox_coords}")
            click.echo(f"   Provider: {provider.upper()}")
            click.echo(f"   Date range: {date_range}")
            click.echo(f"   Max cloud cover: {cloud_cover}%")
            click.echo(f"   Limit: {display_limit}")
        
        click.echo(f"⚡ Quick search: {collection} (last {days} days, <{cloud_cover}% clouds)")
        
        # 🔥 USE FIXED CLIENT CREATION
        client = create_client(provider, verbose)
        
        # 🔥 SIMPLIFIED SEARCH using enhanced clients
        results = client.search(
            collections=[collection],
            bbox=bbox_coords,
            datetime=date_range,
            query={'eo:cloud_cover': {'lt': cloud_cover}},
            limit=actual_limit  # None = unlimited, gets ALL items
        )
        
        # Get all items - handled by enhanced clients
        items = results.get_all_items()
        
        if items:
            # Show results summary
            if actual_limit is None:
                click.echo(f"\n✅ Found {len(items)} items (all available)")
            else:
                click.echo(f"\n✅ Found {len(items)} clear items")
            
            # Only show item details if NO output file is specified
            if not output:
                # Show best item (lowest cloud cover)
                best_item = min(items, key=lambda x: x.properties.get('eo:cloud_cover', 100))
                click.echo(f"\n🏆 Best item (clearest):")
                click.echo(f"   📄 ID: {best_item.id}")
                click.echo(f"   📅 Date: {best_item.properties.get('datetime')}")
                cloud_cover_val = best_item.properties.get('eo:cloud_cover')
                if cloud_cover_val is not None:
                    click.echo(f"   ☁️ Cloud Cover: {cloud_cover_val:.1f}%")
                
                # Show summary (limited to first 5 for console)
                display_items = items[:5] if len(items) > 5 else items
                if len(display_items) > 1:
                    click.echo(f"\n📋 Items summary (showing first {len(display_items)}):")
                    for i, item in enumerate(display_items):
                        date = item.properties.get('datetime', '')[:10]
                        cloud = item.properties.get('eo:cloud_cover', 0)
                        cloud_str = f"{cloud:.1f}%" if cloud is not None else "N/A"
                        click.echo(f"   {i+1}. {date} - {cloud_str} clouds")
                    
                    if len(items) > 5:
                        click.echo(f"   ... and {len(items) - 5} more items")
            
            # Save results if requested
            if output:
                results_data = {
                    'search_params': {
                        'provider': provider,
                        'collections': [collection],
                        'bbox': bbox_coords,
                        'datetime': date_range,
                        'query': {'eo:cloud_cover': {'lt': cloud_cover}},
                        'limit': actual_limit,
                        'unlimited': actual_limit is None,
                        'enhanced_pagination': True
                    },
                    'returned_count': len(items),
                    'items': [item.to_dict() for item in items]
                }
                
                with open(output, 'w') as f:
                    json.dump(results_data, f, indent=2)
                click.echo(f"\n💾 Results saved to: {output} ({len(items)} items)")
                
                if len(items) > 100:
                    click.echo(f"   🔥 Enhanced pagination retrieved {len(items)} total items")
            
            # Next steps suggestions
            click.echo(f"\n💡 Next steps:")
            
            # Build the original command dynamically
            cmd_parts = ["ogapi", "search", "quick", collection]
            
            if bbox:
                cmd_parts.extend(["-b", f'"{bbox_str}"'])
            elif location:
                cmd_parts.extend(["--", f'"{bbox_str}"'])
            
            if provider != 'pc':
                cmd_parts.extend(["-p", provider])
            if days != 30:
                cmd_parts.extend(["--days", str(days)])
            if cloud_cover != 30:
                cmd_parts.extend(["--cloud-cover", str(cloud_cover)])
            if actual_limit:
                cmd_parts.extend(["--limit", str(actual_limit)])
            
            original_command = " ".join(cmd_parts)
            
            if not output:
                click.echo(f"   {original_command} -o results.json")
            else:
                click.echo(f"   ogapi download search-results {output}")
            
            # Alternative suggestions
            bbox_str_display = ",".join(map(str, bbox_coords))
            click.echo(f"   # Alternative using items command:")
            click.echo(f"   ogapi search items -c {collection} -b \"{bbox_str_display}\" -o items_results.json")
            
        else:
            click.echo(f"❌ No clear items found in the last {days} days")
            click.echo(f"\n💡 Try adjusting search parameters:")
            
            cmd_parts = ["ogapi", "search", "quick", collection]
            if bbox:
                cmd_parts.extend(["-b", f'"{bbox_str}"'])
            
            if provider != 'pc':
                cmd_parts.extend(["-p", provider])
            
            base_command = " ".join(cmd_parts)
            
            click.echo(f"   • Increase days: {base_command} --days {days * 2}")
            click.echo(f"   • Relax cloud cover: {base_command} --cloud-cover {min(cloud_cover + 20, 80)}")
            click.echo(f"   • Expand area (make bbox larger)")
            if provider == 'pc':
                click.echo(f"   • Try EarthSearch: {base_command} -p es")
            else:
                click.echo(f"   • Try Planetary Computer: {base_command} -p pc")
    
    except click.BadParameter as e:
        click.echo(f"❌ Invalid bbox format: {e}")
        return
    
    except Exception as e:
        click.echo(f"❌ Quick search failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()


@search_group.command('compare')
@click.option('--collections', '-c',
              required=True,
              help='Comma-separated collection names to compare')
@click.option('--bbox', '-b',
              required=True,
              callback=lambda ctx, param, value: parse_bbox(value),
              help='Bounding box as "west,south,east,north"')
@click.option('--datetime', '-d',
              help='Date range as "YYYY-MM-DD/YYYY-MM-DD"')
@click.option('--cloud-cover', '-cc',
              type=float,
              default=50,
              help='Maximum cloud cover percentage (default: 50)')
@click.option('--limit', '-l',
              type=int,
              default=None,
              help='Maximum items per provider (default: unlimited - gets ALL items)')
@click.option('--all', '-a',
              is_flag=True,
              help='Get all available items from both providers (default behavior)')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save comparison results to JSON file')
@click.option('--show-details/--no-details',
              default=False,
              help='Show detailed item information (only when not saving to file)')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Show detailed progress information')
@click.pass_context
def compare_providers(ctx, collections, bbox, datetime, cloud_cover, limit, all, output, show_details, verbose):
    """
    🔄 Enhanced provider comparison with UNLIMITED results.
    
    🔥 NEW: Now gets ALL available items from both providers by default
    for comprehensive comparison using enhanced pagination strategies.
    """
    from datetime import datetime as dt
    
    # Handle --all flag or --limit 0 to mean unlimited
    if all or limit == 0:
        actual_limit = None  # No limit = get ALL items
        display_limit = "unlimited"
    else:
        actual_limit = limit
        display_limit = str(limit) if limit else "unlimited"
    
    try:
        collections_list = [c.strip() for c in collections.split(',')]
        
        click.echo(f"🔄 Enhanced provider comparison:")
        click.echo(f"   📁 Collections: {', '.join(collections_list)}")
        click.echo(f"   📍 Area: {bbox}")
        if datetime:
            click.echo(f"   📅 Period: {datetime}")
        click.echo(f"   ☁️ Max clouds: {cloud_cover}%")
        click.echo(f"   📏 Limit per provider: {display_limit}")
        
        search_params = {
            'collections': collections_list,
            'bbox': bbox,
            'datetime': datetime,
            'query': {'eo:cloud_cover': {'lt': cloud_cover}},
            'limit': actual_limit
        }
        
        results = {}
        
        # 🔥 USE FIXED CLIENT CREATION for comparison
        
        # Search Planetary Computer
        try:
            if verbose:
                click.echo("\n🌍 Searching Planetary Computer...")
            pc = create_client('pc', verbose)
            pc_results = pc.search(**search_params)
            pc_items = pc_results.get_all_items()
            
            results['planetary_computer'] = {
                'items_found': len(pc_items),
                'items': [item.to_dict() for item in pc_items] if pc_items else []
            }
            
            if actual_limit is None:
                click.echo(f"🌍 Planetary Computer: {len(pc_items)} items (all available)")
            else:
                click.echo(f"🌍 Planetary Computer: {len(pc_items)} items")
                
        except Exception as e:
            results['planetary_computer'] = {'error': str(e), 'items_found': 0}
            click.echo(f"❌ Planetary Computer error: {e}")
        
        # Search EarthSearch
        try:
            if verbose:
                click.echo("🔗 Searching EarthSearch...")
            es = create_client('es', verbose)
            es_results = es.search(**search_params)
            es_items = es_results.get_all_items()
            
            results['earthsearch'] = {
                'items_found': len(es_items),
                'items': [item.to_dict() for item in es_items] if es_items else []
            }
            
            if actual_limit is None:
                click.echo(f"🔗 EarthSearch: {len(es_items)} items (all available)")
            else:
                click.echo(f"🔗 EarthSearch: {len(es_items)} items")
                
        except Exception as e:
            results['earthsearch'] = {'error': str(e), 'items_found': 0}
            click.echo(f"❌ EarthSearch error: {e}")
        
        # Comparison summary
        pc_count = results['planetary_computer']['items_found']
        es_count = results['earthsearch']['items_found']
        
        click.echo(f"\n📊 Enhanced Comparison Summary:")
        click.echo(f"   🌍 Planetary Computer: {pc_count} items")
        click.echo(f"   🔗 EarthSearch: {es_count} items")
        
        # Show detailed comparison if requested and not saving to file
        if not output and show_details and (pc_count > 0 or es_count > 0):
            click.echo(f"\n📋 Detailed Comparison:")
            
            if pc_count > 0:
                pc_items_obj = results['planetary_computer']['items']
                pc_dates = [item.get('properties', {}).get('datetime') for item in pc_items_obj 
                           if item.get('properties', {}).get('datetime')]
                if pc_dates:
                    click.echo(f"   🌍 PC Date range: {min(pc_dates)[:10]} to {max(pc_dates)[:10]}")
            
            if es_count > 0:
                es_items_obj = results['earthsearch']['items']
                es_dates = [item.get('properties', {}).get('datetime') for item in es_items_obj 
                           if item.get('properties', {}).get('datetime')]
                if es_dates:
                    click.echo(f"   🔗 ES Date range: {min(es_dates)[:10]} to {max(es_dates)[:10]}")
        
        # Comparison analysis
        if pc_count > 0 and es_count > 0:
            if pc_count > es_count:
                click.echo(f"   🏆 PC has {pc_count - es_count} more items available")
            elif es_count > pc_count:
                click.echo(f"   🏆 ES has {es_count - pc_count} more items available")
            else:
                click.echo(f"   🤝 Both providers have equal coverage")
        
        # Save results
        if output:
            comparison_data = {
                'comparison_metadata': {
                    'search_params': search_params,
                    'comparison_timestamp': dt.now().isoformat(),
                    'limit_per_provider': actual_limit,
                    'unlimited_search': actual_limit is None,
                    'enhanced_pagination': True
                },
                'search_params': search_params,
                'results': results,
                'summary': {
                    'pc_items_found': pc_count,
                    'es_items_found': es_count,
                    'best_provider': 'planetary_computer' if pc_count > es_count else 'earthsearch' if es_count > pc_count else 'equal'
                }
            }
            
            with open(output, 'w') as f:
                json.dump(comparison_data, f, indent=2)
            click.echo(f"\n💾 Enhanced comparison saved to: {output}")
            
            if pc_count > 100 or es_count > 100:
                click.echo(f"   🔥 Enhanced pagination retrieved {pc_count + es_count} total items")
        
        # Recommendations
        click.echo(f"\n💡 Recommendations:")
        if pc_count > es_count:
            click.echo("   • Use Planetary Computer for this search")
            click.echo("   • PC offers more data coverage")
            best_collection = collections_list[0]
            bbox_str = ",".join(map(str, bbox))
            click.echo(f"   ogapi search quick {best_collection} -b \"{bbox_str}\" -p pc -o pc_results.json")
        elif es_count > pc_count:
            click.echo("   • Use EarthSearch for this search")
            click.echo("   • ES offers more data coverage")
            best_collection = collections_list[0]
            bbox_str = ",".join(map(str, bbox))
            click.echo(f"   ogapi search quick {best_collection} -b \"{bbox_str}\" -p es -o es_results.json")
        else:
            click.echo("   • Both providers offer similar coverage")
            click.echo("   • Choose based on your workflow needs:")
            click.echo("     - PC: Auto-signed URLs, faster access")
            click.echo("     - ES: Open access, no authentication required")
    
    except Exception as e:
        click.echo(f"❌ Comparison failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()
