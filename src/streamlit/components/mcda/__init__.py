# CP2B MCDA Module
# Módulo integrado para análise MCDA das propriedades CP2B

from .data_loader import (
    load_cp2b_complete_database,
    load_cp2b_spatial_data,
    get_property_details,
    get_cp2b_summary_stats,
    search_properties,
    initialize_cp2b_session_state
)

from .map_component import (
    render_mcda_map,
    render_mcda_map_sidebar,
    apply_mcda_filters
)

from .interactive_map import (
    load_properties_geoparquet,
    render_interactive_mcda_map,
    detect_clicked_property_optimized
)

from .invisible_map import (
    render_invisible_polygons_map
)

from .report_component import (
    render_property_report_page
)

__all__ = [
    'load_cp2b_complete_database',
    'load_cp2b_spatial_data', 
    'get_property_details',
    'get_cp2b_summary_stats',
    'search_properties',
    'initialize_cp2b_session_state',
    'render_mcda_map',
    'render_mcda_map_sidebar',
    'apply_mcda_filters',
    'load_properties_geoparquet',
    'render_interactive_mcda_map',
    'render_invisible_polygons_map',
    'detect_clicked_property_optimized',
    'render_property_report_page'
]