"""
coletar_dados_api.py
====================
Proveniência dos dados — documenta COMO o snapshot de dados brutos foi obtido
diretamente da API pública do Banco Mundial (World Bank Open Data), via wbgapi.

Os arquivos `dados_brutos_paises.csv` e `dados_brutos_regional_LCN.csv` versionados
no repositório são um SNAPSHOT desta coleta, congelado para garantir que a análise
seja 100% reproduzível mesmo que o Banco Mundial revise as séries no futuro
(o que é comum: dados de gasto em educação são frequentemente atualizados).

Como usar (opcional — apenas para reobter/atualizar os dados da fonte):
    pip install wbgapi pandas
    python coletar_dados_api.py            # imprime o que viria da API hoje
    python coletar_dados_api.py --salvar   # sobrescreve os CSVs com os dados atuais

ATENÇÃO: reexecutar com --salvar substitui o snapshot pelos valores atuais da API,
que podem diferir dos usados no relatório. Para reproduzir o relatório, mantenha
os CSVs versionados.

Fonte: https://databank.worldbank.org
Indicadores:
    SE.XPD.TOTL.GD.ZS  Gasto público em educação (% do PIB)
    SL.UEM.TOTL.ZS     Taxa de desemprego total (% da força de trabalho)
Período: 2010-2022 | Agregado regional: LCN (Latin America & Caribbean)
"""

import sys

INDICADORES = {
    "SE.XPD.TOTL.GD.ZS": "Gasto_Educacao_pct_PIB",
    "SL.UEM.TOTL.ZS":     "Taxa_Desemprego",
}

# 18 países candidatos da América Latina e Caribe (códigos ISO-3 do Banco Mundial).
CANDIDATOS = {
    "BRA": "Brasil",   "MEX": "México",    "ARG": "Argentina",
    "COL": "Colômbia", "CHL": "Chile",     "PER": "Peru",
    "ECU": "Equador",  "BOL": "Bolívia",   "PRY": "Paraguai",
    "URY": "Uruguai",  "VEN": "Venezuela", "CRI": "Costa Rica",
    "PAN": "Panamá",   "GTM": "Guatemala", "HND": "Honduras",
    "SLV": "El Salvador", "NIC": "Nicarágua", "DOM": "Rep. Dominicana",
}

ANOS = range(2010, 2023)
COBERTURA_MINIMA = 70.0  # % de anos não-ausentes exigido em cada indicador


def coletar():
    """Coleta os dados da API e aplica o critério de cobertura (>= 70%)."""
    import pandas as pd
    import wbgapi as wb

    # ---- Agregado regional (LCN) ----
    df_reg = wb.data.DataFrame(list(INDICADORES), economy="LCN", time=ANOS, db=2)
    df_reg = df_reg.rename(index=INDICADORES).T
    df_reg.index.name = "Ano"
    df_reg = df_reg.reset_index()
    df_reg["Ano"] = df_reg["Ano"].str.replace("YR", "").astype(int)
    df_reg = df_reg[["Ano", "Gasto_Educacao_pct_PIB", "Taxa_Desemprego"]]

    # ---- Por país (18 candidatos) ----
    bruto = wb.data.DataFrame(list(INDICADORES), economy=list(CANDIDATOS),
                              time=ANOS, db=2)
    df = bruto.copy().reset_index()
    df["series"]  = df["series"].map(INDICADORES)
    df["economy"] = df["economy"].map(CANDIDATOS)
    df = (
        df.melt(id_vars=["economy", "series"], var_name="Ano", value_name="Valor")
          .assign(Ano=lambda x: x["Ano"].str.replace("YR", "").astype(int))
          .pivot(index=["economy", "Ano"], columns="series", values="Valor")
          .reset_index()
    )

    # ---- Critério de cobertura: manter países com >= 70% em ambos indicadores ----
    cob = df.groupby("economy")[["Gasto_Educacao_pct_PIB", "Taxa_Desemprego"]] \
            .apply(lambda x: x.notna().mean() * 100)
    validos = cob[(cob["Gasto_Educacao_pct_PIB"] >= COBERTURA_MINIMA) &
                  (cob["Taxa_Desemprego"] >= COBERTURA_MINIMA)].index.tolist()
    df = df[df["economy"].isin(validos)].sort_values(["economy", "Ano"]).reset_index(drop=True)
    df = df.rename(columns={"economy": "Pais"})
    return df_reg, df, validos


if __name__ == "__main__":
    df_reg, df, validos = coletar()
    print(f"Países com cobertura >= {COBERTURA_MINIMA:.0f}%: {len(validos)}")
    print(sorted(validos))
    print(f"Observações por país: {len(df)} | Anos regionais: {len(df_reg)}")

    if "--salvar" in sys.argv:
        df_reg.to_csv("dados_brutos_regional_LCN.csv", index=False, encoding="utf-8")
        df.to_csv("dados_brutos_paises.csv", index=False, encoding="utf-8")
        print("Snapshot sobrescrito: dados_brutos_regional_LCN.csv e dados_brutos_paises.csv")
    else:
        print("\n(Use --salvar para sobrescrever os CSVs com os dados atuais da API.)")
