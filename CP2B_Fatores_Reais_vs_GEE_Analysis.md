# CP2B - Análise Comparativa: Fatores Reais vs Google Earth Engine
## Discrepâncias Críticas Identificadas nos Cálculos de Biomassa

### 📊 Comparação Detalhada: Dados Reais vs Implementação GEE

| **Classe** | **Área SP (ha)** | **Fator Real (Nm³/ton)** | **GEE Atual (m³/ha/dia)** | **GEE Anual (m³/ha/ano)** | **Discrepância** | **Status** |
|------------|------------------|---------------------------|---------------------------|---------------------------|------------------|------------|
| **15 - Pastagem** | 3.842.653 | 150-300 | 37 | 13.505 | 🚨 **-75%** | **CRÍTICO** |
| **20 - Cana** | 5.812.461 | 94 | 180 | 65.700 | ❓ **Metodologia diferente** | **REVISAR** |
| **39 - Soja** | 1.508.984 | 215 | 150 | 54.750 | ✅ **Compatível** | **OK** |
| **40 - Arroz** | 31.667 | 220 | N/A | N/A | ⚠️ **Não implementado** | **ADICIONAR** |
| **46 - Café** | 316.067 | 310 | 50 | 18.250 | 🚨 **-83%** | **CRÍTICO** |
| **47 - Citros** | 112.826 | 20,90 | 80 | 29.200 | 🔄 **+283%** | **REVISAR** |

### 🚨 Problemas Críticos Identificados:

#### **1. PASTAGEM - Subestimação Severa**
```
📍 DADOS REAIS:
- Área SP: 3.842.653 ha (38.4% do total agrícola)
- Fator: 150-300 Nm³/ton
- Base: Dejetos bovinos + cama de curral

🔴 PROBLEMA GEE:
- Fator atual: 37 m³/ha/dia (13.505 m³/ha/ano)  
- Subestimação: ~75% do potencial real

✅ CORREÇÃO NECESSÁRIA:
- Usar 200 Nm³/ton (médio da faixa)
- Considerar 2.5 cabeças/ha (densidade média SP)
- Produção dejetos: 10 kg/cabeça/dia = 25 kg/ha/dia = 9,125 ton/ha/ano
- Potencial corrigido: 9.125 × 200 = 1.825 m³/ha/ano → 5 m³/ha/dia
```

#### **2. CAFÉ - Oportunidade Perdida**
```
📍 DADOS REAIS:
- Área SP: 316.067 ha (concentrado Sul SP/Mogiana)
- Produtividade: 10,43 ton/ha
- Fator: 310 Nm³/ton
- Potencial: 10.43 × 310 = 3.233 m³/ha/ano → 8,9 m³/ha/dia

🔴 PROBLEMA GEE:
- Fator atual: 50 m³/ha/dia (18.250 m³/ha/ano)
- Superestimação de base diária, mas subestimação do potencial real

✅ CORREÇÃO NECESSÁRIA:  
- Base científica: 310 Nm³/ton processado
- Produtividade real: 10,43 ton/ha
- Potencial corrigido: 3.233 m³/ha/ano → 8,9 m³/ha/dia
```

#### **3. CANA-DE-AÇÚCAR - Metodologia Diferente**
```
📍 DADOS REAIS:
- Área SP: 5.812.461 ha (maior cultura)
- Produtividade: 70,23 ton/ha
- Fator: 94 Nm³/ton
- Potencial: 70.23 × 94 = 6.602 m³/ha/ano → 18,1 m³/ha/dia

🔄 GEE ATUAL:
- Fator: 180 m³/ha/dia (65.700 m³/ha/ano)
- 10x maior que dados reais - provavelmente inclui bagaço + palha + vinhaça

❓ REVISAR METODOLOGIA:
- Verificar se inclui todos os resíduos (bagaço + palha + vinhaça)
- Ajustar para dados oficiais de produtividade
```

### 🎯 Fatores Corrigidos para Google Earth Engine:

```javascript
// =============================================================================
// FATORES CORRIGIDOS - BASEADOS EM DADOS REAIS SP
// =============================================================================
var crops = {
  pasture: {
    class: 15,
    area_sp_ha: 3842653,
    productivity_ton_ha: 9.125,          // NOVO: 25kg dejetos/ha/dia
    biogas_factor_nm3_ton: 200,          // MÉDIO da faixa 150-300
    biogas_m3_ha_year: 1825,             // 9.125 × 200
    biogas_m3_ha_day: 5.0,               // CORRIGIDO: era 37
    methane_content: 0.60,
    color: 'yellow',
    name: 'Pastagem',
    source: 'Dejetos bovinos + cama de curral'
  },
  
  sugarcane: {
    class: 20,
    area_sp_ha: 5812461,
    productivity_ton_ha: 70.23,          // DADO REAL SP
    biogas_factor_nm3_ton: 94,           // DADO REAL SP
    biogas_m3_ha_year: 6602,             // 70.23 × 94 (CORRIGIDO)
    biogas_m3_ha_day: 18.1,              // CORRIGIDO: era 180
    methane_content: 0.55,
    color: 'purple',
    name: 'Cana-de-açúcar',
    source: 'Bagaço + palha (dados oficiais SP)'
  },
  
  soy: {
    class: 39,
    area_sp_ha: 1508984,
    productivity_ton_ha: 2.84,           // DADO REAL SP
    biogas_factor_nm3_ton: 215,          // DADO REAL SP
    biogas_m3_ha_year: 611,              // 2.84 × 215
    biogas_m3_ha_day: 1.67,              // CORRIGIDO: era 150
    methane_content: 0.50,
    seasonal_factor: 0.4,                // Fev-Maio
    color: 'pink',
    name: 'Soja',
    source: 'Palha de soja'
  },
  
  corn: {                                // NOVO - Rotação da soja
    class: 39,                           // Mesmo MapBiomas da soja
    area_sp_ha: 275159,                  // Área específica milho
    productivity_ton_ha: 7.85,           // DADO REAL SP
    biogas_factor_nm3_ton: 225,          // DADO REAL SP
    biogas_m3_ha_year: 1766,             // 7.85 × 225
    biogas_m3_ha_day: 4.84,
    methane_content: 0.52,
    seasonal_factor: 0.5,                // Fev-Julho
    color: 'orange',
    name: 'Milho (Rotação Soja)',
    source: 'Palha + sabugo milho'
  },
  
  rice: {                                // NOVO - Não estava no GEE
    class: 40,
    area_sp_ha: 31667,
    productivity_ton_ha: 7.11,           // DADO REAL SP
    biogas_factor_nm3_ton: 220,          // DADO REAL SP
    biogas_m3_ha_year: 1564,             // 7.11 × 220
    biogas_m3_ha_day: 4.28,
    methane_content: 0.55,
    color: 'lightblue',
    name: 'Arroz',
    source: 'Palha de arroz'
  },
  
  coffee: {
    class: 46,
    area_sp_ha: 316067,
    productivity_ton_ha: 10.43,          // DADO REAL SP
    biogas_factor_nm3_ton: 310,          // DADO REAL SP
    biogas_m3_ha_year: 3233,             // 10.43 × 310 (CORRIGIDO)
    biogas_m3_ha_day: 8.86,              // CORRIGIDO: era 50
    methane_content: 0.55,
    seasonal_factor: 0.4,                // Maio-Setembro
    color: 'brown',
    name: 'Café',
    source: 'Casca pergaminho + mucilagem (dados oficiais SP)'
  },
  
  citrus: {
    class: 47,
    area_sp_ha: 112826,
    productivity_ton_ha: 99.00,          // DADO REAL SP - muito alta!
    biogas_factor_nm3_ton: 20.90,        // DADO REAL SP - baixo por ton fruta
    biogas_m3_ha_year: 2069,             // 99 × 20.90 (CORRIGIDO)
    biogas_m3_ha_day: 5.67,              // CORRIGIDO: era 80
    methane_content: 0.58,
    seasonal_factor: 0.6,                // Maio-Outubro
    color: 'green',
    name: 'Citros',
    source: 'Bagaço + cascas processamento (dados oficiais SP)'
  }
};
```

### 📊 Impacto das Correções no Potencial Total SP:

```javascript
// CÁLCULO DO IMPACTO DAS CORREÇÕES
var impact_analysis = {
  pasture: {
    area_ha: 3842653,
    old_potential: 3842653 * 13.505,      // 51.9 milhões m³/ano
    new_potential: 3842653 * 1825,        // 7.0 milhões m³/ano  
    change: -86.5,                        // REDUÇÃO (correção de superestimação)
    note: "Correção baseada em produtividade real de dejetos"
  },
  
  coffee: {
    area_ha: 316067,
    old_potential: 316067 * 18250,        // 5.8 milhões m³/ano
    new_potential: 316067 * 3233,         // 1.0 milhão m³/ano
    change: -82.3,                        // REDUÇÃO (correção de superestimação)
    note: "Ajuste para produtividade real 10.43 ton/ha"
  },
  
  sugarcane: {
    area_ha: 5812461,
    old_potential: 5812461 * 65700,       // 381.9 bilhões m³/ano (!!)
    new_potential: 5812461 * 6602,        // 38.4 milhões m³/ano
    change: -89.9,                        // CORREÇÃO CRÍTICA
    note: "Alinhamento com produtividade real 70.23 ton/ha"
  },
  
  citrus: {
    area_ha: 112826,
    old_potential: 112826 * 29200,        // 3.3 milhões m³/ano  
    new_potential: 112826 * 2069,         // 0.23 milhões m³/ano
    change: -92.9,                        // CORREÇÃO CRÍTICA
    note: "Fator corrigido para 20.90 Nm³/ton (processamento real)"
  }
};
```

### 🎯 Recomendações Críticas:

#### **Fase 1 - Correção Urgente (Esta Semana)**
1. 🚨 **APLICAR FATORES REAIS** no Google Earth Engine
2. 🚨 **REPROCESSAR DADOS** com coeficientes corretos
3. 🚨 **VALIDAR RESULTADOS** com dados de produção SP
4. 🚨 **DOCUMENTAR MUDANÇAS** para stakeholders

#### **Fase 2 - Validação (Próxima Semana)**
1. ✅ **COMPARAR** potencial total antes/depois das correções
2. ✅ **VALIDAR** com dados de plantas existentes
3. ✅ **AJUSTAR** interface Streamlit para novos dados
4. ✅ **COMUNICAR** impacto das correções

### 🔍 Script Corrigido para Google Earth Engine:

```javascript
// FUNÇÃO CORRIGIDA DE CÁLCULO DE BIOMASSA
function calculateBiomassInBuffer_CORRECTED(polygon, buffered, bufferSuffix) {
  var biomassResults = {};
  
  Object.keys(crops).forEach(function(cropKey) {
    var crop = crops[cropKey];
    
    // Calcular área da cultura no buffer
    var cropMask = mapbiomas.eq(crop.class);
    var cropArea = cropMask.multiply(ee.Image.pixelArea())
                          .reduceRegion({
                            reducer: ee.Reducer.sum(),
                            geometry: buffered,
                            scale: 30,
                            maxPixels: 1e9
                          });
    
    var areaHa = ee.Number(cropArea.get('classification_2023')).divide(10000);
    
    // NOVO: Usar produtividade e fator reais
    var production_ton = areaHa.multiply(crop.productivity_ton_ha);
    var biogas_potential_m3 = production_ton.multiply(crop.biogas_factor_nm3_ton);
    
    // Aplicar fator sazonal se existir
    var seasonal_potential = biogas_potential_m3.multiply(crop.seasonal_factor || 1.0);
    var methane_potential = seasonal_potential.multiply(crop.methane_content);
    
    // Armazenar resultados com nova metodologia
    biomassResults[cropKey + '_ha' + bufferSuffix] = areaHa;
    biomassResults[cropKey + '_production_ton' + bufferSuffix] = production_ton;
    biomassResults[cropKey + '_biogas_m3' + bufferSuffix] = biogas_potential_m3;
    biomassResults[cropKey + '_seasonal_m3' + bufferSuffix] = seasonal_potential;
    biomassResults[cropKey + '_methane_m3' + bufferSuffix] = methane_potential;
  });
  
  return biomassResults;
}
```

### 📈 Conclusão:

**Os cálculos atuais do GEE têm discrepâncias significativas com os dados reais de SP:**
- ✅ **Metodologia correta**: Usar produtividade × fator de conversão
- 🚨 **Correções críticas**: Especialmente cana, café e pastagem  
- 📊 **Resultado mais realista**: Alinhado com dados oficiais SP
- 🎯 **Prioridade**: Aplicar correções antes de expandir análise multi-distância

**Quer que eu ajude a implementar essas correções no Google Earth Engine primeiro, antes de avançar com a interface multi-distância?**