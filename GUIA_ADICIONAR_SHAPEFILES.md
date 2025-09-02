# Guia para Adicionar Novos Shapefiles

## Processo Correto (seguindo as lições aprendidas)

### Situação Atual
Os seguintes shapefiles já estão configurados:
- ✅ `Limite_SP.shp` - Contorno do estado
- ✅ `Plantas_Biogas_SP.shp` - Plantas existentes  
- ✅ `Regiao_Adm_SP.shp` - Regiões administrativas
- ✅ `Municipios_SP_shapefile.shp` - Municípios (shapefile principal)

### Para Adicionar Novos Shapefiles (ex: Areas_Urbanas_SP, gasodutos)

#### Passo 1: Colocar os Arquivos no Lugar Certo
```bash
# Adicionar todos os arquivos do shapefile em:
projeto_cp2b/shapefile/
├── Areas_Urbanas_SP.shp
├── Areas_Urbanas_SP.dbf
├── Areas_Urbanas_SP.prj
├── Areas_Urbanas_SP.shx
├── gasodutos_SP.shp
├── gasodutos_SP.dbf
├── gasodutos_SP.prj
└── gasodutos_SP.shx
```

#### Passo 2: Modificar maps.py em Três Lugares

##### 2.1 - Registrar no dicionário ADDITIONAL_SHAPEFILES (linha ~13):
```python
# ANTES:
ADDITIONAL_SHAPEFILES = {
    'limite_sp': ROOT / "shapefile" / "Limite_SP.shp",
    'plantas_biogas': ROOT / "shapefile" / "Plantas_Biogas_SP.shp",
    'regioes_admin': ROOT / "shapefile" / "Regiao_Adm_SP.shp"
}

# DEPOIS:
ADDITIONAL_SHAPEFILES = {
    'limite_sp': ROOT / "shapefile" / "Limite_SP.shp",
    'plantas_biogas': ROOT / "shapefile" / "Plantas_Biogas_SP.shp",
    'regioes_admin': ROOT / "shapefile" / "Regiao_Adm_SP.shp",
    'areas_urbanas': ROOT / "shapefile" / "Areas_Urbanas_SP.shp",
    'gasodutos': ROOT / "shapefile" / "gasodutos_SP.shp"
}
```

##### 2.2 - Adicionar checkboxes na função render_layer_controls() (linha ~676):
```python
# ANTES:
with col1:
    limite_sp = st.checkbox("🔴 Limite de SP", value=True, help="Contorno do estado de São Paulo")
    plantas_biogas = st.checkbox("🏭 Usinas Existentes", value=False, help="Plantas de biogás em operação")

with col2:
    regioes_admin = st.checkbox("🌍 Regiões Admin.", value=False, help="Regiões administrativas do estado")
    # Reservado para futuras camadas

# DEPOIS:
with col1:
    limite_sp = st.checkbox("🔴 Limite de SP", value=True, help="Contorno do estado de São Paulo")
    plantas_biogas = st.checkbox("🏭 Usinas Existentes", value=False, help="Plantas de biogás em operação")
    areas_urbanas = st.checkbox("🏙️ Áreas Urbanas", value=False, help="Delimitação das áreas urbanas")

with col2:
    regioes_admin = st.checkbox("🌍 Regiões Admin.", value=False, help="Regiões administrativas do estado")
    gasodutos = st.checkbox("🔧 Gasodutos", value=False, help="Rede de gasodutos existente")
```

##### 2.3 - Atualizar o return da função (linha ~685):
```python
# ANTES:
return {
    'limite_sp': limite_sp,
    'plantas_biogas': plantas_biogas,
    'regioes_admin': regioes_admin
}

# DEPOIS:
return {
    'limite_sp': limite_sp,
    'plantas_biogas': plantas_biogas,
    'regioes_admin': regioes_admin,
    'areas_urbanas': areas_urbanas,
    'gasodutos': gasodutos
}
```

##### 2.4 - Adicionar no layer_mapping (linha ~713):
```python
# ANTES:
layer_mapping = {
    "🏭 Plantas de Biogás Existentes": "plantas_biogas",
    "🏛️ Regiões Administrativas": "regioes_admin",
    "🗺️ Limite de São Paulo": "limite_sp",
}

# DEPOIS:
layer_mapping = {
    "🏭 Plantas de Biogás Existentes": "plantas_biogas",
    "🏛️ Regiões Administrativas": "regioes_admin",
    "🗺️ Limite de São Paulo": "limite_sp",
    "🏙️ Áreas Urbanas": "areas_urbanas",
    "🔧 Gasodutos": "gasodutos",
}
```

#### Passo 3: Testar com Segurança
1. Salvar os arquivos
2. Executar: `streamlit run src/streamlit/app.py`
3. Se não atualizar: usar "Clear cache" no menu do Streamlit
4. Se erro de porta: `taskkill /F /IM python.exe`

### ⚠️ Lembretes Importantes

1. **Ordem de Execução para Recriar BD:**
   - `python src/database/migrations.py` (cria tabelas)
   - `python src/database/data_loader.py` (popula dados)

2. **Evitar Processos Zumbis:**
   - `taskkill /F /IM python.exe` antes de executar comandos de limpeza

3. **Sincronia Git:**
   - Manter ambiente local alinhado com repositório
   - Evitar arquivos duplicados (_v2, _novo)

### Estrutura dos Três Pontos de Modificação

```
maps.py
├── ADDITIONAL_SHAPEFILES (linha ~13)     ← 1️⃣ Registrar arquivo
├── render_layer_controls() (linha ~676)  ← 2️⃣ Adicionar checkbox  
└── layer_mapping (linha ~713)            ← 3️⃣ Mapear para renderização
```

Este guia garante que todos os novos shapefiles sejam adicionados de forma consistente e segura.
