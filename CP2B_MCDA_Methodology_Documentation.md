# CP2B - MCDA Methodology Documentation
## Multi-Criteria Decision Analysis for Biogas Development in São Paulo State

**Document Version:** 2.0  
**Date:** September 2025  
**Project:** CP2B - Sistema de Análise Geoespacial para Biogás  
**Coverage:** 645 municipalities in São Paulo State, Brazil  

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [MCDA Methodology Overview](#mcda-methodology-overview)
3. [Scoring Criteria & Components](#scoring-criteria--components)
4. [Biomass Coefficients & Methanogenic Potential](#biomass-coefficients--methanogenic-potential)
5. [Infrastructure Weighting System](#infrastructure-weighting-system)
6. [Adjustable Weight Framework](#adjustable-weight-framework)
7. [Multi-Distance Analysis System](#multi-distance-analysis-system)
8. [Viability Threshold Framework](#viability-threshold-framework)
9. [Data Quality & Completeness Management](#data-quality--completeness-management)
10. [Implementation Roadmap](#implementation-roadmap)
11. [Technical Specifications](#technical-specifications)
12. [References & Data Sources](#references--data-sources)

---

## Executive Summary

The CP2B project employs **Multi-Criteria Decision Analysis (MCDA)** to evaluate biogas development potential across São Paulo State's 645 municipalities. This methodology combines **biomass availability**, **infrastructure accessibility**, and **environmental restrictions** into a comprehensive scoring system that guides investment decisions and policy planning.

### Key Features:
- 🎯 **Objective, data-driven** property evaluation
- 🔧 **Stakeholder-adjustable** weighting system
- 📊 **Multi-distance** biomass analysis (10km/30km/50km)
- 📍 **Geospatial precision** with 30m resolution
- 🔍 **Transparent** scoring methodology
- ⚠️ **Data quality** indicators and completeness tracking

---

## MCDA Methodology Overview

### What is MCDA?

Multi-Criteria Decision Analysis (MCDA) is a **systematic approach** for evaluating complex decisions involving multiple, often conflicting criteria. In the context of biogas development, MCDA helps identify the **most promising properties** by simultaneously considering technical, economic, and regulatory factors.

### Why Use MCDA for Biogas Development?

**Traditional approaches** often focus on single factors (e.g., just biomass availability or just proximity to grid). **MCDA provides:**

1. **Holistic evaluation** - Considers all relevant factors simultaneously
2. **Objective prioritization** - Reduces human bias in site selection  
3. **Stakeholder flexibility** - Allows different perspectives through adjustable weights
4. **Transparent methodology** - All scoring components are visible and traceable
5. **Scalable analysis** - Applicable from individual properties to regional planning

### The Three-Pillar Framework

```
Final MCDA Score = (Biomass Score × W₁) + (Infrastructure Score × W₂) + (Restriction Score × W₃)

Where: W₁ + W₂ + W₃ = 1.0 (weights sum to 100%)
```

---

## Scoring Criteria & Components

### 1. Biomass Score (Biogas Production Potential)

**What it measures:** Availability of organic material for biogas production within defined radius

**Data Sources:**
- **Agricultural crops** (MapBiomas, 30m resolution)
- **Livestock populations** (IBGE Municipal Livestock Survey)
- **Industrial waste** (Municipal production data)
- **Urban organic waste** (Population-based estimates)

**Calculation Method:**
```
Biomass Score = Σ(Crop_Area × Yield_Rate × Methanogenic_Potential × Seasonal_Factor)
```

**Key Components:**
- **Sugarcane residues** (bagasse, straw, vinasse)
- **Citrus processing waste** (bagasse, peels)
- **Coffee residues** (husks, mucilage)
- **Livestock manure** (bovine, swine, poultry)
- **Agricultural crop residues** (soy, corn, wheat)
- **Urban organic waste** (food waste, sewage sludge)
- **Industrial organic waste** (brewery, dairy, slaughterhouse)

### 2. Infrastructure Score (Access & Connectivity)

**What it measures:** Proximity to essential infrastructure for biogas plant operation

**Components & Default Weights:**
- **Federal Highways** (25%) - Primary transportation access
- **Electrical Substations** (20%) - Grid connection capability
- **State Highways** (20%) - Regional connectivity
- **Transmission Lines** (15%) - Power infrastructure
- **Gas Pipelines** (10%) - Gas distribution network
- **Gas Distribution** (5%) - Local gas infrastructure  
- **Other Infrastructure** (5%) - Airports, ports, railways

**Distance Calculation:**
```
Infrastructure Score = Σ(Weight_i × Distance_Score_i)
Distance Score = max(0, 100 - (Distance_km × Penalty_Factor))
```

### 3. Restriction Score (Environmental & Legal Constraints)

**What it measures:** Environmental and legal limitations that impact project feasibility

**Restriction Factors:**
- **Conservation Units** (UCs) - Protected areas buffer zones
- **Indigenous Territories** - Indigenous land buffers
- **Urban Areas** - Urban development buffers  
- **Airports** - Aviation safety zones
- **Water Bodies** - Environmental protection zones
- **Slope & Terrain** - Technical implementation constraints

**Calculation Method:**
```
Restriction Score = 100 - Σ(Restriction_Penalty_i × Severity_Factor_i)
```

---

## Biomass Coefficients & Methanogenic Potential

### Comprehensive Residue Database

| **Category** | **Residue Type** | **Yield Rate** | **CH₄ Potential (m³/ton)** | **CH₄ Concentration (%)** | **Seasonality** | **Primary Region** |
|-------------|------------------|----------------|---------------------------|---------------------------|-----------------|-------------------|
| **Coffee** | Husk (pergaminho) | 0.18 kg/kg coffee | 150-200 | 55-65 | May-Sep | South SP, Mogiana |
| | Fermented mucilage | 0.05 kg/kg coffee | 300-400 | 60-70 | May-Sep | South SP, Mogiana |
| **Citrus** | Processing bagasse | 45-60% of fruit | 80-150 | 45-65 | May-Oct | North-Center SP |
| | Peels & waste | 30-40% of fruit | 100-200 | 50-70 | May-Oct | North-Center SP |
| **Sugarcane** | Bagasse | 250-280 kg/ton cane | 175 | 55 | May-Dec | Center-West SP |
| | Straw (palhada) | 280 kg/ton cane | 200 | 53 | May-Dec | Center-West SP |
| | Vinasse | 10-15 m³/m³ ethanol | 15-25 | 65 | May-Dec | Center-West SP |
| | Filter cake | 3-4 kg/ton cane | 150-200 | 58-62 | May-Dec | Center-West SP |
| **Soybean** | Straw residue | 2.5-3.0 ton/ha | 160-220 | 48-55 | Feb-May | West SP |
| | Empty pods | 0.8-1.2 ton/ha | 180-240 | 50-58 | Feb-May | West SP |
| **Corn** | Straw (palhada) | 8-12 ton/ha | 200-260 | 52-58 | Feb-Jul | West SP |
| | Cobs (sabugo) | 2.5 ton/ha | 150-220 | 50-55 | Feb-Jul | West SP |
| **Livestock** | Bovine manure | 10 kg/head/day | 150-300 | 60-68 | Year-round | Interior SP |
| | Bovine bedding | 2-3 kg/head/day | 200-300 | 58-65 | Year-round | Interior SP |
| | Swine manure | 2.3 kg/head/day | 450-650 | 65-70 | Year-round | West SP |
| | Poultry litter | 1.5-2.0 kg/bird/cycle | 180-280 | 60-65 | Year-round | Interior SP |
| | Poultry manure | 0.15 kg/bird/day | 280-380 | 58-68 | Year-round | Interior SP |
| **Forestry** | Eucalyptus bark | 15-20 m³/ha/cycle | 60-120 | 45-55 | Year-round | Vale do Paraíba |
| | Harvest residues | 10-15 m³/ha/cycle | 80-140 | 48-58 | Year-round | Vale do Paraíba |
| **Urban** | Food waste | 150-200 kg/hab/year | 200-600 | 55-65 | Year-round | Metropolitan |
| | Sewage sludge | 15-25 kg MS/hab/year | 200-400 | 50-60 | Year-round | Metropolitan |
| | Urban pruning | 50-80 kg/hab/year | 20-50 | 40-50 | Year-round | Metropolitan |
| **Industrial** | Dairy whey | 9 L/kg cheese | 400-600 | 60-70 | Year-round | Interior SP |
| | Brewery bagasse | 14-20 kg/hL beer | 80-150 | 50-60 | Year-round | Metropolitan |
| | Slaughter blood | 15-20 L/head | 200-350 | 68-72 | Year-round | Interior SP |
| | Rumen content | 40-60 kg/head | 120-200 | 55-62 | Year-round | Interior SP |

### Regional Specialization Factors

**South SP & Mogiana:** Coffee processing dominance  
**North-Center SP:** Citrus industry concentration  
**Center-West SP:** Sugarcane belt with ethanol production  
**West SP:** Soy-corn rotation with intensive livestock  
**Vale do Paraíba:** Forestry and mixed agriculture  
**Metropolitan Region:** Urban waste and food processing  

---

## Infrastructure Weighting System

### Current Literature-Based Weights

Based on academic research and industry best practices:

```yaml
Infrastructure Components:
  federal_highways: 25%      # Primary transportation
  electrical_substations: 20% # Grid connection
  state_highways: 20%        # Regional access  
  transmission_lines: 15%    # Power infrastructure
  gas_pipelines: 10%         # Gas distribution
  gas_distribution: 5%       # Local gas network
  other_infrastructure: 5%   # Airports, railways
```

### Distance Penalty Functions

```python
def calculate_distance_score(distance_km, max_distance=50):
    """
    Linear penalty function for infrastructure distance
    """
    if distance_km <= 1:
        return 100  # Perfect score
    elif distance_km >= max_distance:
        return 0   # No benefit
    else:
        return max(0, 100 - (distance_km / max_distance) * 100)
```

---

## Adjustable Weight Framework

### Stakeholder Customization System

**Purpose:** Allow different stakeholders to adjust weights based on their priorities and local conditions

### Proposed Interface Design

```yaml
Weight Categories:
  biomass_importance:
    default: 40%
    range: 20% - 70%
    description: "Importance of biomass availability"
    
  infrastructure_importance:
    default: 35%
    range: 20% - 60%
    description: "Importance of infrastructure access"
    
  restriction_importance:
    default: 25%
    range: 10% - 40%
    description: "Importance of environmental/legal constraints"

Infrastructure Subweights:
  federal_highways:
    default: 25%
    scenarios:
      rural_focus: 15%
      industrial_focus: 35%
      urban_access: 30%
      
  electrical_substations:
    default: 20%
    scenarios:
      rural_focus: 15%
      industrial_focus: 30%
      urban_access: 25%
```

### Predefined Scenarios

**1. Rural/Agricultural Focus**
- Biomass: 50%, Infrastructure: 30%, Restrictions: 20%
- Emphasizes agricultural waste availability
- Lower infrastructure requirements

**2. Industrial Development**
- Biomass: 35%, Infrastructure: 45%, Restrictions: 20%
- Prioritizes robust infrastructure access
- Suitable for large-scale facilities

**3. Urban Integration**
- Biomass: 30%, Infrastructure: 40%, Restrictions: 30%
- Balances all factors with higher restriction awareness
- Suitable for urban waste management

**4. Custom Profile**
- User-defined weights with real-time validation
- Dynamic recalculation of all property scores
- Save/load custom scenarios

### Municipality-Specific Profiles

```python
def generate_municipal_weights(municipality_code):
    """
    Generate custom weights based on local characteristics
    """
    municipal_data = get_municipal_profile(municipality_code)
    
    weights = {
        'biomass': base_weight_biomass,
        'infrastructure': base_weight_infrastructure,
        'restrictions': base_weight_restrictions
    }
    
    # Adjust based on local industrial activity
    if municipal_data['industrial_production'] > threshold_high:
        weights['infrastructure'] *= 1.2
        
    # Adjust based on agricultural intensity
    if municipal_data['agricultural_area_percent'] > threshold_high:
        weights['biomass'] *= 1.15
        
    return normalize_weights(weights)
```

---

## Multi-Distance Analysis System

### Distance Scenarios & Economic Rationale

#### **10km Radius - Local/On-site Development**
- **Target:** Small-scale, property-based biogas systems
- **Transport cost:** Minimal (€2-5/ton)
- **Collection efficiency:** 95%
- **Typical capacity:** 50-500 kW
- **Best for:** Individual farms, small cooperatives

#### **30km Radius - Regional Optimization (RECOMMENDED)**
- **Target:** Regional biogas hubs
- **Transport cost:** Moderate (€8-15/ton) 
- **Collection efficiency:** 85%
- **Typical capacity:** 1-5 MW
- **Best for:** Municipal partnerships, regional development
- **Economic sweet spot:** Balance between biomass availability and logistics

#### **50km Radius - Industrial Scale**
- **Target:** Large-scale industrial biogas facilities
- **Transport cost:** Higher (€15-25/ton)
- **Collection efficiency:** 70%
- **Typical capacity:** 5+ MW
- **Best for:** Major energy projects, industrial applications

### Implementation Framework

```python
distance_analysis = {
    '10km': {
        'radius_km': 10,
        'transport_cost_factor': 1.0,
        'collection_efficiency': 0.95,
        'economic_weight': 0.7,
        'use_case': 'On-site/Local'
    },
    '30km': {
        'radius_km': 30,
        'transport_cost_factor': 1.5,
        'collection_efficiency': 0.85,
        'economic_weight': 1.0,  # Optimal
        'use_case': 'Regional Hub'
    },
    '50km': {
        'radius_km': 50,
        'transport_cost_factor': 2.2,
        'collection_efficiency': 0.70,
        'economic_weight': 0.8,
        'use_case': 'Industrial Scale'
    }
}
```

### User Interface Features

- **Toggle between distance scenarios** with instant recalculation
- **Side-by-side comparison** showing all three distance analyses
- **Economic impact calculator** showing transport cost implications
- **Heat map visualization** showing biomass density at different radii
- **Export functionality** for comparative reports

---

## Viability Threshold Framework

### Multi-Tier Classification System

```yaml
Viability Categories:
  EXCELLENT: 
    range: 80-100
    color: "#28a745"  # Green
    description: "Prime development opportunities with high success probability"
    recommendation: "Immediate development recommended"
    
  GOOD:
    range: 60-79
    color: "#ffc107"  # Yellow
    description: "Viable projects with moderate investment requirements"
    recommendation: "Detailed feasibility study recommended"
    
  MODERATE:
    range: 40-59
    color: "#fd7e14"  # Orange
    description: "Marginal viability, requires careful assessment"
    recommendation: "Comprehensive risk analysis required"
    
  LOW:
    range: 20-39
    color: "#dc3545"  # Red
    description: "High-risk projects requiring specialized conditions"
    recommendation: "Alternative technologies or incentives needed"
    
  POOR:
    range: 0-19
    color: "#6c757d"  # Gray
    description: "Not recommended for biogas development"
    recommendation: "Consider alternative renewable energy options"
```

### Validation Against Existing Plants

#### Methodology for Threshold Calibration

```python
def calibrate_thresholds(existing_plants_database):
    """
    Calibrate viability thresholds based on operational biogas plants
    """
    # Analyze scores of existing successful plants
    successful_plants = existing_plants_database[
        existing_plants_database['operational_status'] == 'successful'
    ]
    
    # Calculate percentile-based thresholds
    thresholds = {
        'minimum_viable': np.percentile(successful_plants['mcda_score'], 25),
        'preferred_range': np.percentile(successful_plants['mcda_score'], 50),
        'optimal_range': np.percentile(successful_plants['mcda_score'], 75)
    }
    
    # Validate against failed projects
    failed_plants = existing_plants_database[
        existing_plants_database['operational_status'] == 'failed'
    ]
    
    return validate_thresholds(thresholds, successful_plants, failed_plants)
```

#### Proposed Validation Process

1. **Data Collection:** Survey existing biogas plants in São Paulo State
2. **Performance Classification:** Successful, marginal, failed operations  
3. **Score Calculation:** Apply current MCDA methodology to existing plant locations
4. **Statistical Analysis:** Identify score ranges corresponding to success rates
5. **Threshold Adjustment:** Calibrate classification ranges based on real performance
6. **Continuous Monitoring:** Annual review and adjustment of thresholds

### Dynamic Threshold Adjustment

#### Regional Calibration

```python
regional_adjustments = {
    'metropolitan': {
        'threshold_modifier': 1.1,  # Higher standards
        'reason': 'Higher competition for land, stricter regulations'
    },
    'agricultural': {
        'threshold_modifier': 0.9,  # More lenient
        'reason': 'Lower land costs, agricultural synergies'
    },
    'industrial': {
        'threshold_modifier': 1.0,  # Standard
        'reason': 'Balanced industrial infrastructure'
    }
}
```

#### Technology-Specific Thresholds

- **Small-scale digesters (<100kW):** Lower infrastructure requirements
- **Medium-scale plants (100kW-1MW):** Balanced requirements
- **Industrial facilities (>1MW):** Higher infrastructure and biomass requirements

---

## Data Quality & Completeness Management

### Data Quality Framework

#### Primary Data Sources & Accuracy

```yaml
Data Sources:
  MapBiomas:
    accuracy: "95% (30m pixel resolution)"
    update_frequency: "Annual"
    coverage: "Complete São Paulo State"
    validation: "Ground-truth validated"
    
  IBGE Municipal Data:
    accuracy: "Official census data"
    update_frequency: "Annual for agriculture, 10-year for population"
    coverage: "All 645 municipalities"
    reliability: "Government official statistics"
    
  SIDRA Database:
    accuracy: "Official agricultural statistics"
    update_frequency: "Annual"
    coverage: "Municipal level detail"
    validation: "Cross-validated with field surveys"
    
  Infrastructure Layers:
    accuracy: "±100m positional accuracy"
    update_frequency: "Every 2-3 years"
    source: "Government spatial databases"
    validation: "Satellite imagery verification"
```

### Incomplete Data Handling System

#### Data Completeness Categories

```python
data_completeness_framework = {
    'biomass_data': {
        'required_fields': [
            'agricultural_area_by_crop',
            'livestock_populations', 
            'industrial_production_data',
            'urban_population_density'
        ],
        'missing_indicator': '⚠️ Biomass data incomplete',
        'scoring_impact': 'Partial biomass scoring available',
        'confidence_modifier': 0.7
    },
    
    'infrastructure_data': {
        'required_fields': [
            'distance_to_substations',
            'road_network_access',
            'transmission_line_proximity',
            'gas_pipeline_access'
        ],
        'missing_indicator': '🔌 Infrastructure data incomplete',
        'scoring_impact': 'Infrastructure score may be underestimated', 
        'confidence_modifier': 0.8
    },
    
    'restriction_data': {
        'required_fields': [
            'conservation_units_buffer',
            'indigenous_territories_buffer',
            'urban_area_restrictions',
            'environmental_constraints'
        ],
        'missing_indicator': '🚫 Restriction analysis incomplete',
        'scoring_impact': 'Regulatory risk assessment limited',
        'confidence_modifier': 0.6
    }
}
```

#### Property Detail Display Enhancement

```markdown
## Property Analysis Report

### 📊 MCDA Score: 75.3/100 
**Data Confidence: 85%** ⚠️ *Based on available data*

---

### ✅ Complete Data Available:
- **Biomass Potential:** Sugarcane (850 ha), citrus (230 ha) within 30km
- **Highway Access:** BR-116 at 3.2km, SP-070 at 8.7km  
- **Municipal Data:** 2024 agricultural census, livestock populations

### ⚠️ Missing or Incomplete Data:
- **Electrical Infrastructure:** Substation distances not available
- **Industrial Waste:** Local food processing data missing
- **Recent Changes:** 2024 land use updates pending

### 🔍 Data Quality Indicators:
- **MapBiomas Accuracy:** 95% confidence (30m resolution)
- **IBGE Census Data:** Official 2023 municipal survey
- **Infrastructure Mapping:** Last updated 2024
- **Ground Validation:** Field verification recommended

### 📈 Score Components Breakdown:
- **Biomass Score:** 82/100 *(high confidence)*
- **Infrastructure Score:** 68/100 *(moderate confidence - missing electrical data)*
- **Restriction Score:** 76/100 *(high confidence)*

### 🎯 Recommendations for Data Improvement:
1. Contact local electricity distributor for substation mapping
2. Survey nearby food processing facilities for waste streams  
3. Verify current land use with recent satellite imagery
4. Consider field visit for infrastructure validation
```

#### Search & Filter Enhancements

**Enhanced Filtering Options:**
- **Data Completeness Filter:** "Show only properties with >90% data completeness"
- **Missing Data Categories:** Filter by specific data gaps
- **Confidence Score Range:** Filter by data reliability level
- **Update Recency:** Filter by when data was last updated

**Bulk Data Quality Reports:**
- **Regional completeness summary** for planning purposes
- **Data gap identification** for targeted data collection
- **Quality improvement recommendations** for stakeholders
- **Cost-benefit analysis** of additional data collection

---

## Implementation Roadmap

### Phase 1: Foundation Enhancement (Months 1-3)
**Priority: HIGH**

#### 1.1 Adjustable Weight System
- [ ] Design stakeholder interface with slider controls
- [ ] Implement real-time MCDA recalculation
- [ ] Create predefined scenario templates
- [ ] Add weight validation and normalization
- [ ] Test with stakeholder focus groups

#### 1.2 Multi-Distance Analysis
- [ ] Implement 10km/30km/50km toggle system
- [ ] Add comparative analysis visualization
- [ ] Include transport cost calculations
- [ ] Create economic impact dashboard
- [ ] Validate with existing biogas facilities

#### 1.3 Data Quality Management
- [ ] Implement data completeness indicators
- [ ] Add missing data tooltips and warnings
- [ ] Create confidence scoring system
- [ ] Design enhanced property detail pages
- [ ] Develop data quality reporting tools

### Phase 2: Advanced Features (Months 4-6)
**Priority: MEDIUM**

#### 2.1 Viability Threshold Calibration
- [ ] Survey existing biogas plants in São Paulo State
- [ ] Apply MCDA methodology to existing facilities
- [ ] Conduct statistical analysis of success factors
- [ ] Calibrate threshold ranges based on real performance
- [ ] Implement dynamic threshold adjustment

#### 2.2 Municipal Customization
- [ ] Develop municipality-specific weight profiles
- [ ] Integrate local industrial production data
- [ ] Create regional adjustment factors
- [ ] Add municipal comparison tools
- [ ] Implement collaborative planning features

#### 2.3 Enhanced Biomass Modeling
- [ ] Integrate comprehensive coefficient database
- [ ] Add seasonal availability modeling
- [ ] Implement co-digestion optimization
- [ ] Include transport logistics modeling
- [ ] Add economic feasibility calculations

### Phase 3: Advanced Analytics (Months 7-12)
**Priority: MEDIUM-LOW**

#### 3.1 Temporal Analysis
- [ ] Historical trend analysis
- [ ] Seasonal biomass availability modeling
- [ ] Market condition integration
- [ ] Policy impact assessment
- [ ] Future scenario modeling

#### 3.2 Economic Integration
- [ ] Detailed economic feasibility modeling
- [ ] ROI and payback period calculations
- [ ] Sensitivity analysis tools
- [ ] Market price integration
- [ ] Subsidy and incentive tracking

#### 3.3 Machine Learning Enhancement
- [ ] Pattern recognition for site optimization
- [ ] Predictive modeling for success factors
- [ ] Automated anomaly detection
- [ ] Continuous learning from new data
- [ ] Advanced recommendation engine

### Phase 4: System Integration (Months 13-18)
**Priority: LONG-TERM**

#### 4.1 Real-time Data Integration
- [ ] Automated annual data updates
- [ ] API integration with government databases
- [ ] Real-time market condition monitoring
- [ ] Continuous model calibration
- [ ] Alert system for significant changes

#### 4.2 Stakeholder Collaboration Platform
- [ ] Multi-user collaborative planning
- [ ] Project development tracking
- [ ] Stakeholder communication tools
- [ ] Decision documentation system
- [ ] Progress monitoring dashboard

---

## Technical Specifications

### System Architecture

```yaml
Backend:
  language: Python 3.9+
  framework: Streamlit
  database: SQLite/PostgreSQL
  geospatial: GeoPandas, Folium, PostGIS
  analytics: NumPy, Pandas, SciPy
  
Frontend:
  framework: Streamlit
  mapping: Folium/Plotly
  visualization: Plotly, Matplotlib
  styling: Custom CSS/Bootstrap
  
Data Processing:
  geospatial: GDAL, Shapely, PyProj
  raster: Rasterio, GDAL
  analysis: Scikit-learn, SciPy
  optimization: OR-Tools, PuLP
```

### Performance Requirements

```yaml
Response Times:
  map_loading: <3 seconds
  mcda_recalculation: <2 seconds
  property_search: <1 second
  report_generation: <5 seconds
  
Data Handling:
  max_properties: 100,000+
  concurrent_users: 50+
  data_update_frequency: annual
  backup_frequency: daily
  
Accuracy Requirements:
  spatial_precision: 30m (MapBiomas standard)
  mcda_calculation: 0.1 point precision
  distance_calculation: 100m accuracy
  area_calculation: 1ha precision
```

### Database Schema

```sql
-- Properties table
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    cod_imovel VARCHAR(50) UNIQUE,
    municipio VARCHAR(100),
    geometry GEOMETRY(POLYGON, 4326),
    area_ha DECIMAL(10,2),
    mcda_score DECIMAL(5,2),
    biomass_score DECIMAL(5,2),
    infrastructure_score DECIMAL(5,2),
    restriction_score DECIMAL(5,2),
    ranking INTEGER,
    data_completeness DECIMAL(3,2),
    last_updated TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Biomass data table
CREATE TABLE biomass_data (
    property_id INTEGER REFERENCES properties(id),
    residue_type VARCHAR(50),
    distance_km INTEGER,
    available_quantity DECIMAL(10,2),
    methanogenic_potential DECIMAL(8,2),
    seasonal_factor DECIMAL(3,2),
    last_updated TIMESTAMP
);

-- Infrastructure distances table
CREATE TABLE infrastructure_distances (
    property_id INTEGER REFERENCES properties(id),
    infrastructure_type VARCHAR(50),
    distance_km DECIMAL(6,2),
    facility_name VARCHAR(100),
    last_updated TIMESTAMP
);
```

---

## References & Data Sources

### Academic References

1. **Biogas Potential Assessment:**
   - Moraes, B.S. et al. (2015). "Anaerobic digestion of sugarcane vinasse: challenges and perspectives"
   - Zhang, W. et al. (2014). "Methane production from agricultural residues: A review"

2. **MCDA Methodology:**
   - Saaty, T.L. (2008). "Decision making with the analytic hierarchy process"
   - Belton, V. & Stewart, T. (2002). "Multiple Criteria Decision Analysis: An Integrated Approach"

3. **Spatial Analysis:**
   - Longley, P.A. et al. (2015). "Geographic Information Science and Systems"
   - Burrough, P.A. & McDonnell, R.A. (1998). "Principles of GIS"

### Data Sources

#### Government Databases
- **MapBiomas:** https://mapbiomas.org/
- **IBGE - Instituto Brasileiro de Geografia e Estatística:** https://www.ibge.gov.br/
- **SIDRA - Sistema IBGE de Recuperação Automática:** https://sidra.ibge.gov.br/
- **INCRA - Instituto Nacional de Colonização e Reforma Agrária:** https://www.incra.gov.br/

#### Research Institutions
- **EMBRAPA - Brazilian Agricultural Research Corporation**
- **University of São Paulo - Bioenergy Research Program**
- **UNICAMP - State University of Campinas**
- **UNESP - São Paulo State University**

#### Industry Organizations
- **ABIOGÁS - Brazilian Biogas Association**
- **ÚNICA - Brazilian Sugarcane Industry Association**
- **CNA - National Confederation of Agriculture**

### Scientific References by Residue Type

#### Biomass Coefficients Sources
1. **Coffee residues:** https://www.sciencedirect.com/science/article/abs/pii/S0360544223009982
2. **Citrus waste:** https://pmc.ncbi.nlm.nih.gov/articles/PMC4383308/
3. **Sugarcane residues:** Task37 IEA Bioenergy Report (2022)
4. **Livestock manure:** https://journals.ufrpe.br/index.php/geama/article/view/2691
5. **Agricultural residues:** https://www.repositorio.ufal.br/bitstream/123456789/8792/1/

---

## Document Control

**Version History:**
- v1.0 (March 2024): Initial methodology documentation
- v2.0 (September 2025): Enhanced MCDA framework with stakeholder adjustability

**Authors:**
- Technical Lead: CP2B Development Team
- MCDA Specialist: [Name]
- GIS Analyst: [Name]
- Domain Expert: [Name]

**Review Schedule:**
- Technical Review: Quarterly
- Stakeholder Review: Bi-annually  
- Major Updates: Annually

**Contact Information:**
- Project Email: cp2b@[organization].br
- Technical Support: [support-email]
- Documentation Feedback: [docs-feedback-email]

---

*This document serves as the comprehensive guide for understanding and implementing the CP2B MCDA methodology. For technical implementation details, please refer to the codebase documentation and API specifications.*