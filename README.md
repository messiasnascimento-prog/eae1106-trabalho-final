# Investimento Público em Educação e Desemprego na América Latina

**EAE1106 – Métodos Computacionais para Economia** · Prof. Arthur Viaro · USP, 1º Sem/2026
**Autor:** Messias Victor Assunção Ribeiro do Nascimento (trabalho individual)

## Pergunta de pesquisa
Existe relação entre o gasto público em educação (% do PIB) e a taxa de desemprego
nos países da América Latina na última década (2010–2022)?

## Dados (fonte e proveniência)
Fonte: **World Bank Open Data** — <https://databank.worldbank.org>

| Código | Indicador | Unidade |
|---|---|---|
| `SE.XPD.TOTL.GD.ZS` | Gasto público em educação | % do PIB |
| `SL.UEM.TOTL.ZS` | Taxa de desemprego total | % da força de trabalho |

Os dados brutos foram coletados da API do Banco Mundial (`wbgapi`) e estão
versionados como **snapshot** neste repositório, garantindo reprodutibilidade exata:

- [`dados_brutos_paises.csv`](dados_brutos_paises.csv) — séries por país (10 países × 13 anos)
- [`dados_brutos_regional_LCN.csv`](dados_brutos_regional_LCN.csv) — agregado regional (América Latina e Caribe)

A coleta da fonte original está documentada e é reexecutável em
[`coletar_dados_api.py`](coletar_dados_api.py). O notebook reconstrói **toda** a
análise a partir dos CSVs brutos — nenhum dado tratado é versionado.

## Como reproduzir
```bash
pip install -r requirements.txt
jupyter notebook analise_banco_mundial_FINAL.ipynb   # Run > Run All Cells
# ou, só os gráficos:
python gerar_graficos.py
```
No Windows, basta dar duplo-clique em `abrir_notebook.bat` (notebook) ou
`executar.bat` (gráficos). Requisito único: Python 3.

## Estrutura
| Arquivo | Descrição |
|---|---|
| `analise_banco_mundial_FINAL.ipynb` | Notebook completo (coleta → limpeza → análise → gráficos) |
| `dados_brutos_paises.csv` / `dados_brutos_regional_LCN.csv` | Dados brutos (snapshot do Banco Mundial) |
| `coletar_dados_api.py` | Proveniência: coleta da API do Banco Mundial |
| `gerar_graficos.py` | Regenera as 5 figuras a partir dos CSVs |
| `requirements.txt` | Dependências (versões exatas) |
| `relatorio_final - Messias.pdf` | Relatório final |
| `fig1…fig5 .png` | Figuras geradas |
