# CP2B - Sistema de Análise Geoespacial para Biogás

Este projeto é um protótipo em Streamlit para análise do potencial de biogás nos 645 municípios do estado de São Paulo. Inclui importação de dados a partir de Excel para SQLite, visualizações geoespaciais, filtros interativos e simulador de cenários.

## Como executar

1) Instalar dependências

```bash
cd projeto_cp2b
pip install -r requirements.txt
```

2) Preparar banco de dados e importar dados

```bash
python -m src.database.migrations
python -m src.database.data_loader
```

3) Executar a aplicação

```bash
streamlit run src/streamlit/app.py
```

## Estrutura

Consulte `src/` para módulos de banco, cálculos e UI. Arquivos de configuração do Streamlit em `.streamlit/config.toml`.

