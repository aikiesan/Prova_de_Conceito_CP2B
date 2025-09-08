# CP2B MCDA Module
# Módulo integrado para análise MCDA das propriedades CP2B

from .data_loader import (
    load_cp2b_complete_database,
    load_cp2b_spatial_data,
    load_mcda_geoparquet_by_radius,
    get_property_details,
    get_cp2b_summary_stats,
    get_mcda_summary_stats_by_radius,
    search_properties,
    initialize_cp2b_session_state,
    MCDA_SCENARIOS
)

from .map_component import (
    render_mcda_map,
    render_mcda_map_sidebar,
    apply_mcda_filters
)

from .interactive_map import (
    load_properties_geoparquet,
    load_properties_geoparquet_by_radius,
    render_interactive_mcda_map,
    detect_clicked_property_optimized
)

from .invisible_map import (
    render_invisible_polygons_map
)

from .report_component import (
    render_property_report_page
)

# Report components (now in same directory)
try:
    from .simple_report_component import render_simple_property_report
    SIMPLE_REPORT_AVAILABLE = True
except ImportError:
    SIMPLE_REPORT_AVAILABLE = False

try:
    from .enhanced_report_component import render_enhanced_property_report
    ENHANCED_REPORT_AVAILABLE = True
except ImportError:
    ENHANCED_REPORT_AVAILABLE = False

__all__ = [
    'load_cp2b_complete_database',
    'load_cp2b_spatial_data',
    'load_mcda_geoparquet_by_radius',
    'get_property_details',
    'get_cp2b_summary_stats',
    'get_mcda_summary_stats_by_radius',
    'search_properties',
    'initialize_cp2b_session_state',
    'MCDA_SCENARIOS',
    'render_mcda_map',
    'render_mcda_map_sidebar',
    'apply_mcda_filters',
    'load_properties_geoparquet',
    'load_properties_geoparquet_by_radius',
    'render_interactive_mcda_map',
    'render_invisible_polygons_map',
    'detect_clicked_property_optimized',
    'render_property_report_page'
]

# Add reports if available
if SIMPLE_REPORT_AVAILABLE:
    __all__.append('render_simple_property_report')
if ENHANCED_REPORT_AVAILABLE:
    __all__.append('render_enhanced_property_report')