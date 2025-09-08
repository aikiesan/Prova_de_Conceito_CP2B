// ============================================================================
// CP2B PROJECT - GOOGLE EARTH ENGINE: EXTRAÇÃO DE DADOS GEOESPACIAIS
// Responsabilidade: APENAS extrair hectares por cultura e distâncias
// Processamento será feito no Jupyter Notebook
// ============================================================================

// =============================================================================
// PHASE 1: CONFIGURAÇÃO E CARREGAMENTO DE ASSETS
// =============================================================================
print('=== CP2B - EXTRAÇÃO DE DADOS GEOESPACIAIS ===');
print('Responsabilidade GEE: Extrair hectares + distâncias');
print('Processamento: Será feito no Jupyter Notebook');
print('Timestamp:', new Date());
print('');

// Load base datasets
var rmc_boundary = ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/Limites_RMC');
var sicar_polygons = ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/SICAR_RMC_polygons');

// Load MapBiomas para análise de uso do solo
var mapbiomas = ee.Image('projects/mapbiomas-public/assets/brazil/lulc/collection10/mapbiomas_brazil_collection10_coverage_v2')
                  .select('classification_2023')
                  .clip(rmc_boundary);

// Load infrastructure layers
var infrastructure = {
  subestacoes: {
    collection: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/SE_EXISTENTE'),
    name: 'Subestações Elétricas'
  },
  linhas_transmissao: {
    collection: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/LT_EXISTENTE'),
    name: 'Linhas de Transmissão'
  },
  rodovias_federais: {
    collection: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/rodovia-federal'),
    name: 'Rodovias Federais'
  },
  rodovias_estaduais: {
    collection: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/rodovia-estadual'),
    name: 'Rodovias Estaduais'
  },
  gasodutos: {
    collection: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/gasoduto-transporte'),
    name: 'Gasodutos de Transporte'
  },
  gasoduto_distribuicao: {
    collection: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/gasoduto-distribuicao'),
    name: 'Gasodutos de Distribuição'
  },
  aerodromos: {
    collection: ee.FeatureCollection('projects/prova-de-conceito-cp2b/assets/Aerodromos_publicos'),
    name: 'Aeródromos Públicos'
  }
};

// =============================================================================
// PHASE 2: CONFIGURAÇÃO DAS CLASSES MAPBIOMAS
// =============================================================================
var landUseClasses = {
  pasture: { class: 15, name: 'Pastagem' },
  sugarcane: { class: 20, name: 'Cana-de-açúcar' },
  soy: { class: 39, name: 'Soja' },
  rice: { class: 40, name: 'Arroz' },
  coffee: { class: 46, name: 'Café' },  
  citrus: { class: 47, name: 'Citros' },
  other_perennial: { class: 48, name: 'Outras Perenes' },
  other_temp: { class: 41, name: 'Outras Temporárias' }
};

print('📊 Classes MapBiomas configuradas:');
Object.keys(landUseClasses).forEach(function(key) {
  var landUse = landUseClasses[key];
  print('   •', landUse.name, '- Classe', landUse.class);
});

// =============================================================================
// PHASE 3: FUNÇÃO DE EXTRAÇÃO DE HECTARES POR BUFFER
// =============================================================================
function extractLandUseAreas(polygon, buffered, bufferSuffix) {
  var results = {};
  
  // Para cada classe de uso do solo, calcular hectares no buffer
  Object.keys(landUseClasses).forEach(function(landUseKey) {
    var landUse = landUseClasses[landUseKey];
    
    // Criar máscara para a classe específica
    var classMask = mapbiomas.eq(landUse.class);
    
    // Calcular área em pixels e converter para hectares
    var areaPixels = classMask.multiply(ee.Image.pixelArea())
                            .reduceRegion({
                              reducer: ee.Reducer.sum(),
                              geometry: buffered,
                              scale: 30,
                              maxPixels: 1e9
                            });
    
    // Converter de m² para hectares
    var areaHa = ee.Number(areaPixels.get('classification_2023')).divide(10000);
    
    // Armazenar resultado
    results[landUseKey + '_ha' + bufferSuffix] = areaHa;
  });
  
  // Adicionar área total do buffer
  var totalBufferArea = ee.Number(buffered.area()).divide(10000);
  results['buffer_total_ha' + bufferSuffix] = totalBufferArea;
  
  return results;
}

// =============================================================================
// PHASE 4: FUNÇÃO DE CÁLCULO DE DISTÂNCIAS DE INFRAESTRUTURA  
// =============================================================================
function calculateInfrastructureDistances(polygon) {
  var centroid = polygon.geometry().centroid();
  var distances = {};
  
  Object.keys(infrastructure).forEach(function(infraKey) {
    try {
      // Buscar infraestrutura próxima (até 50km)
      var nearbyInfra = infrastructure[infraKey].collection
        .filterBounds(centroid.buffer(50000))
        .limit(10);
      
      var count = nearbyInfra.size();
      var minDistance = ee.Algorithms.If(
        count.gt(0),
        nearbyInfra.distance(1).reduceRegion({
          reducer: ee.Reducer.min(),
          geometry: centroid,
          scale: 1000
        }).get('distance'),
        999999 // Valor grande se não há infraestrutura próxima
      );
      
      distances['dist_' + infraKey + '_km'] = ee.Number(minDistance).divide(1000);
    } catch (error) {
      distances['dist_' + infraKey + '_km'] = -1; // Erro no cálculo
    }
  });
  
  return distances;
}

// =============================================================================
// PHASE 5: PROCESSAMENTO MULTI-DISTÂNCIA
// =============================================================================

// Configurar buffers para análise multi-distância
var bufferDistances = {
  '10km': 10000,   // Plantas locais
  '30km': 30000,   // Hub regional (ÓTIMO)
  '50km': 50000    // Escala industrial
};

print('');
print('🎯 INICIANDO EXTRAÇÃO MULTI-DISTÂNCIA');
print('Cenários configurados:', Object.keys(bufferDistances));

Object.keys(bufferDistances).forEach(function(distanceKey) {
  var bufferDistance = bufferDistances[distanceKey];
  var bufferSuffix = '_' + distanceKey;
  
  print('');
  print('📏 Processando cenário:', distanceKey);
  print('   Buffer:', bufferDistance/1000, 'km');
  
  // Configurar processamento em chunks
  var chunkSize = 250; // Menor para evitar timeout
  var totalFeatures = sicar_polygons.size();
  var featureList = sicar_polygons.toList(totalFeatures);
  
  print('   Total propriedades:', totalFeatures);
  print('   Chunk size:', chunkSize);
  
  // Processar primeiros 10 chunks para validação
  for (var i = 0; i < 10; i++) {
    var start = i * chunkSize;
    var chunkList = featureList.slice(start, start + chunkSize);
    var chunk = ee.FeatureCollection(chunkList);
    
    // Aplicar análise de extração de dados
    var chunkResult = chunk.map(function(polygon) {
      // Criar buffer
      var buffered = polygon.buffer(bufferDistance);
      
      // Extrair hectares por classe
      var landUseResults = extractLandUseAreas(polygon, buffered, bufferSuffix);
      
      // Calcular distâncias de infraestrutura (uma vez por propriedade)
      var infraResults = (distanceKey === '10km') ? 
        calculateInfrastructureDistances(polygon) : {};
      
      // Combinar resultados
      return polygon.set(landUseResults).set(infraResults);
    });
    
    // Exportar para Drive
    Export.table.toDrive({
      collection: chunkResult,
      description: 'CP2B_RAW_DATA_' + distanceKey + '_Chunk_' + String(i).padStart(2, '0'),
      fileFormat: 'CSV',
      folder: 'CP2B_Raw_Data'
    });
    
    print('   ✅ Chunk', i, '- Export queued');
  }
});

// =============================================================================
// PHASE 6: RELATÓRIO DE EXTRAÇÃO
// =============================================================================
print('');
print('=== RELATÓRIO DE EXTRAÇÃO ===');
print('');
print('📊 DADOS A SEREM EXTRAÍDOS:');
print('');
print('🌱 ÁREAS POR CULTURA (hectares):');
Object.keys(landUseClasses).forEach(function(key) {
  var landUse = landUseClasses[key];
  print('   • ' + landUse.name + '_ha_[10km|30km|50km]');
});
print('');
print('🏗️ DISTÂNCIAS DE INFRAESTRUTURA (km):');
Object.keys(infrastructure).forEach(function(key) {
  var infra = infrastructure[key];
  print('   • dist_' + key + '_km');
});
print('');
print('📁 ARQUIVOS DE SAÍDA:');
print('   Pasta: CP2B_Raw_Data/');
print('   Formato: CP2B_RAW_DATA_[10km|30km|50km]_Chunk_XX.csv');
print('');
print('🔄 PRÓXIMOS PASSOS (JUPYTER NOTEBOOK):');
print('   1. Consolidar chunks em arquivo único por distância');
print('   2. Aplicar fatores de conversão por cultura:');
print('      • Pastagem: 150-300 Nm³/ton dejetos');
print('      • Cana: 94 Nm³/ton (70.23 ton/ha produtividade)');
print('      • Café: 310 Nm³/ton (10.43 ton/ha produtividade)');
print('      • Soja: 215 Nm³/ton (2.84 ton/ha produtividade)');
print('      • Citros: 20.9 Nm³/ton (99 ton/ha produtividade)');
print('   3. Calcular potencial de biomassa por cenário');
print('   4. Implementar scores MCDA');
print('   5. Análise comparativa 10km vs 30km vs 50km');
print('');
print('✅ GOOGLE EARTH ENGINE - EXTRAÇÃO CONFIGURADA!');
print('⏳ Aguardando processamento dos exports...');

// =============================================================================
// PHASE 7: VISUALIZAÇÃO PARA VALIDAÇÃO
// =============================================================================
Map.centerObject(rmc_boundary, 10);
Map.addLayer(rmc_boundary, {color: 'red', fillColor: 'transparent'}, 'RMC Boundary');

// Adicionar amostra de propriedades para validação
Map.addLayer(sicar_polygons.limit(50), {color: 'blue', fillColor: 'transparent'}, 'SICAR Sample (50)');

// Adicionar layers de uso do solo
Object.keys(landUseClasses).forEach(function(landUseKey) {
  var landUse = landUseClasses[landUseKey];
  var classMask = mapbiomas.eq(landUse.class);
  
  Map.addLayer(classMask.selfMask(), {
    palette: ['green'],
    opacity: 0.7
  }, landUse.name + ' (Classe ' + landUse.class + ')', false);
});

print('🗺️ Layers adicionados para validação visual');
print('📍 Use o mapa para verificar distribuição das culturas na RMC');