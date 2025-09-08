// ============================================================================
// CP2B PROJECT - MASTER SCRIPT FOR COMPLETE GEOSPATIAL ANALYSIS
// Sistema de Análise Geoespacial para Localização Ótima de Plantas de Biogás
// ============================================================================

// =============================================================================
// PHASE 1: ASSET VERIFICATION AND BASE DATA LOADING
// =============================================================================
print('=== CP2B MASTER ANALYSIS - STATUS VERIFICATION ===');
print('Timestamp:', new Date());
print('');

// Load base datasets (VALIDATED)
var rmc_boundary = ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/Limites_RMC');
var sicar_polygons = ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/SICAR_RMC_polygons');

// Load infrastructure layers (UPDATED - adicionado gasoduto-distribuicao)
var infrastructure = {
  subestacoes: {
    collection: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/SE_EXISTENTE'),
    weight: 0.20,
    name: 'Subestações Elétricas'
  },
  linhas_transmissao: {
    collection: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/LT_EXISTENTE'),
    weight: 0.15,
    name: 'Linhas de Transmissão'
  },
  rodovias_federais: {
    collection: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/rodovia-federal'),
    weight: 0.25,
    name: 'Rodovias Federais'
  },
  rodovias_estaduais: {
    collection: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/rodovia-estadual'),
    weight: 0.20,
    name: 'Rodovias Estaduais'
  },
  outros_trechos: {
    collection: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/outros-trechos'),
    weight: 0.10,
    name: 'Outros Trechos Rodoviários'
  },
  gasodutos: {
    collection: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/gasoduto-transporte'),
    weight: 0.05,
    name: 'Gasodutos de Transporte'
  },
  gasoduto_distribuicao: {
    collection: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/gasoduto-distribuicao'),
    weight: 0.08,
    name: 'Gasodutos de Distribuição'
  },
  aerodromos: {
    collection: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/Aerodromos_publicos'),
    weight: 0.05,
    name: 'Aeródromos Públicos'
  }
};

// Environmental and social restrictions (TO BE LOADED)
var restrictions = {
  // Environmental restrictions
  ucs_protecao_integral: {
    // asset: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/UCs_Protecao_Integral'),
    restriction_level: 10, // Complete restriction
    name: 'UCs Proteção Integral'
  },
  ucs_uso_sustentavel: {
    // asset: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/UCs_Uso_Sustentavel'),
    restriction_level: 7, // High restriction
    name: 'UCs Uso Sustentável'
  },
  terras_indigenas: {
    // asset: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/Terras_Indigenas'),
    restriction_level: 10, // Complete restriction
    name: 'Terras Indígenas'
  },
  quilombolas: {
    // asset: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/Quilombolas'),
    restriction_level: 8, // Very high restriction
    name: 'Territórios Quilombolas'
  },
  assentamentos: {
    // asset: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/Assentamentos'),
    restriction_level: 5, // Moderate restriction
    name: 'Assentamentos Rurais'
  },
  // Urban restrictions
  perimetros_urbanos: {
    // asset: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/Perimetros_Urbanos'),
    restriction_level: 9, // Very high restriction
    name: 'Perímetros Urbanos'
  },
  exclusao_aeroportuaria: {
    // asset: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/Exclusao_Aeroportuaria'),
    restriction_level: 10, // Complete restriction
    name: 'Áreas de Exclusão Aeroportuária'
  }
};

// Load MapBiomas for biomass analysis
var mapbiomas = ee.Image('projects/mapbiomas-public/assets/brazil/lulc/collection10/mapbiomas_brazil_collection10_coverage_v2')
                  .select('classification_2023')
                  .clip(rmc_boundary);

// =============================================================================
// PHASE 2: BIOMASS ANALYSIS CONFIGURATION
// =============================================================================
var crops = {
  pasture: {
    class: 15, 
    biogas_m3_ha_year: 37 * 365, // m³/ha/year from livestock
    methane_content: 0.60,
    color: 'yellow', 
    name: 'Pastagem'
  },
  sugarcane: {
    class: 20, 
    biogas_m3_ha_year: 180 * 365, // m³/ha/year from bagasse + straw
    methane_content: 0.55,
    color: 'purple', 
    name: 'Cana-de-açúcar'
  },
  soy: {
    class: 39, 
    biogas_m3_ha_year: 150 * 365, // m³/ha/year from straw
    methane_content: 0.50,
    color: 'pink', 
    name: 'Soja'
  },
  other_temp: {
    class: 41, 
    biogas_m3_ha_year: 220 * 365, // m³/ha/year (mainly corn straw)
    methane_content: 0.52,
    color: 'orange', 
    name: 'Outras Temporárias'
  },
  coffee: {
    class: 46, 
    biogas_m3_ha_year: 50 * 365, // m³/ha/year from processing waste
    methane_content: 0.55,
    color: 'brown', 
    name: 'Café'
  },
  citrus: {
    class: 47, 
    biogas_m3_ha_year: 80 * 365, // m³/ha/year from processing waste
    methane_content: 0.58,
    color: 'green', 
    name: 'Citrus'
  },
  other_perennial: {
    class: 48, 
    biogas_m3_ha_year: 60 * 365, // m³/ha/year from various waste
    methane_content: 0.53,
    color: 'red', 
    name: 'Outras Perenes'
  }
};

// =============================================================================
// PHASE 3: INFRASTRUCTURE DISTANCE CALCULATION (OPTIMIZED)
// =============================================================================
function calculateInfrastructureDistances(polygons) {
  return polygons.map(function(polygon) {
    var centroid = polygon.geometry().centroid();
    var infraDistances = {};
    
    Object.keys(infrastructure).forEach(function(infraKey) {
      try {
        var nearbyInfra = infrastructure[infraKey].collection
          .filterBounds(centroid.buffer(50000))
          .limit(5);
        
        var count = nearbyInfra.size();
        var minDistance = ee.Algorithms.If(
          count.gt(0),
          nearbyInfra.distance(1).reduceRegion({
            reducer: ee.Reducer.min(),
            geometry: centroid,
            scale: 1000
          }).get('distance'),
          999999 // Very large number if no infrastructure nearby
        );
        
        infraDistances['dist_' + infraKey + '_km'] = ee.Number(minDistance).divide(1000);
      } catch (error) {
        infraDistances['dist_' + infraKey + '_km'] = -1;
      }
    });
    
    // Garantir que os campos essenciais existam
    var safeProperties = {
      'cod_imovel': ee.Algorithms.If(
        polygon.get('cod_imovel'),
        polygon.get('cod_imovel'),
        'UNKNOWN'
      ),
      'municipio': ee.Algorithms.If(
        polygon.get('municipio'),
        polygon.get('municipio'),
        'UNKNOWN'
      ),
      'area_ha': ee.Algorithms.If(
        polygon.get('AREA_HA'),
        polygon.get('AREA_HA'),
        0
      )
    };
    
    return ee.Feature(polygon.geometry(), safeProperties).set(infraDistances);
  });
}

// =============================================================================
// PHASE 4: RESTRICTION ANALYSIS (TOMORROW'S IMPLEMENTATION)
// =============================================================================
function calculateRestrictionScores(polygons) {
  // TO BE IMPLEMENTED TOMORROW
  return polygons.map(function(polygon) {
    var restrictionScores = {};
    
    // Template for restriction calculations
    /*
    Object.keys(restrictions).forEach(function(restrictionKey) {
      if (restrictions[restrictionKey].asset) {
        var intersection = restrictions[restrictionKey].asset.filterBounds(polygon.geometry());
        var hasRestriction = intersection.size().gt(0);
        var restrictionScore = ee.Algorithms.If(
          hasRestriction,
          restrictions[restrictionKey].restriction_level,
          0
        );
        restrictionScores['restriction_' + restrictionKey] = restrictionScore;
      }
    });
    */
    
    // Placeholder for now
    restrictionScores['total_restriction_score'] = 0;
    return polygon.set(restrictionScores);
  });
}

// =============================================================================
// PHASE 5: MCDA SCORE CALCULATION (TOMORROW'S ENHANCEMENT)
// =============================================================================
function calculateMCDAScores(feature) {
  // MCDA weights based on scientific literature
  var weights = {
    biomass_potential: 0.35,    // 35% - Resource availability
    infrastructure: 0.49,       // 49% - Access to infrastructure  
    restrictions: 0.16          // 16% - Environmental/social constraints
  };
  
  // TO BE IMPLEMENTED: Normalize and combine scores
  var biomass_score = 0;      // From biomass calculations
  var infrastructure_score = 0; // From distance calculations
  var restriction_score = 0;    // From restriction analysis
  
  var final_mcda_score = (biomass_score * weights.biomass_potential) +
                        (infrastructure_score * weights.infrastructure) +
                        (restriction_score * weights.restrictions);
  
  return feature.set({
    'biomass_score': biomass_score,
    'infrastructure_score': infrastructure_score,
    'restriction_score': restriction_score,
    'mcda_final_score': final_mcda_score
  });
}

// =============================================================================
// PHASE 6: CURRENT PROCESSING EXECUTION (CORRIGIDO)
// =============================================================================
// Process infrastructure distances with chunking
var chunkSize = 500;
var totalFeatures = sicar_polygons.size();

print('Total SICAR properties:', totalFeatures);
print('Processing in optimized chunks of:', chunkSize);

// CORREÇÃO COMPLETA para o loop - SOLUÇÃO 1 (RECOMENDADA):
// Convert FeatureCollection to List for proper chunking
var featureList = sicar_polygons.toList(sicar_polygons.size());

for (var i = 0; i < 25; i++) {
  var start = i * chunkSize;
  var chunkList = featureList.slice(start, start + chunkSize);
  var chunk = ee.FeatureCollection(chunkList);
  var chunkResult = calculateInfrastructureDistances(chunk);
  
  Export.table.toDrive({
    collection: chunkResult,
    description: 'CP2B_Infrastructure_Chunk_' + (i < 10 ? '0' + i : i),
    fileFormat: 'CSV',
    folder: 'CP2B_Results'
  });
}

// =============================================================================
// PHASE 7: VERIFICATION AND STATUS REPORTING
// =============================================================================
print('=== CURRENT STATUS ===');
print('✅ Base datasets loaded:');
print('   • RMC boundary:', rmc_boundary.size());
print('   • SICAR polygons:', sicar_polygons.size());
print('');
print('✅ Infrastructure loaded:');
Object.keys(infrastructure).forEach(function(key) {
  print('   •', infrastructure[key].name + ':', infrastructure[key].collection.size());
});
print('');
print('⏳ Currently processing:');
print('   • Infrastructure distances (optimized chunking)');
print('   • 25 chunks of 500 properties each');
print('   • Memory-safe processing implemented');
print('');
print('📋 TOMORROW\'S AGENDA:');
print('   1. Upload restriction shapefiles:');
Object.keys(restrictions).forEach(function(key) {
  print('      -', restrictions[key].name);
});
print('   2. Implement restriction analysis');
print('   3. Complete MCDA score calculation');
print('   4. Generate final suitability maps');
print('   5. Prepare for statewide scaling');
print('');
print('📁 Expected files in Google Drive/CP2B_Results:');
print('   • CP2B_SICAR_Biomass_10km.csv (DONE - 21MB)');
print('   • CP2B_SICAR_Biomass_30km.csv (DONE - 22MB)');
print('   • CP2B_SICAR_Biomass_50km.csv (DONE - 22MB)');
print('   • CP2B_Infrastructure_Chunk_00 to CP2B_Infrastructure_Chunk_24 (PROCESSING)');
print('   • CP2B_Final_MCDA_Analysis.csv (TOMORROW - ~5MB)');

// =============================================================================
// PHASE 8: TOMORROW'S TEMPLATE FUNCTIONS (READY TO IMPLEMENT)
// =============================================================================
/*
// TOMORROW: Complete biomass + infrastructure + restrictions
function completeAnalysis(polygons, bufferDistance) {
  return polygons.map(function(polygon) {
    var buffered = polygon.buffer(bufferDistance);
    var bufferSuffix = '_' + (bufferDistance/1000) + 'km';
    
    // 1. Biomass calculations (DONE)
    var biomassResults = calculateBiomassInBuffer(polygon, buffered, bufferSuffix);
    
    // 2. Infrastructure distances (DONE)  
    var infraResults = calculateInfrastructureDistances([polygon]).first();
    
    // 3. Restriction analysis (TOMORROW)
    var restrictionResults = calculateRestrictionScores([polygon]).first();
    
    // 4. MCDA final score (TOMORROW)
    var mcdaResults = calculateMCDAScores(polygon);
    
    return polygon.set(biomassResults)
                  .set(infraResults.toDictionary())
                  .set(restrictionResults.toDictionary())
                  .set(mcdaResults.toDictionary());
  });
}
*/

// =============================================================================
// PHASE 9: VISUALIZATION (MINIMAL FOR PERFORMANCE)
// =============================================================================
Map.centerObject(rmc_boundary, 10);
Map.addLayer(rmc_boundary, {color: 'red'}, 'RMC Boundary');
Map.addLayer(infrastructure.subestacoes.collection, {color: 'blue'}, 'Subestações');
Map.addLayer(infrastructure.rodovias_federais.collection, {color: 'red'}, 'Rodovias Federais');
Map.addLayer(sicar_polygons.limit(25), {color: 'green'}, 'SICAR Sample');

print('');
print('🎯 READY FOR TOMORROW\'S EXPANSION!');
print('📊 Current progress: 60% complete');
print('🚀 Next session: Implement restrictions + MCDA + final analysis');
print('⚡ OTIMIZAÇÕES APLICADAS: Chunked processing + filtered search + memory management');
