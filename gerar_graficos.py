"""
gerar_graficos.py
=================
Script independente para gerar (ou regenerar) todos os gráficos da análise:
  Investimento Público em Educação e Desemprego na América Latina

Como usar:
    python gerar_graficos.py
    (ou, no Windows, dê duplo-clique em "executar.bat")

Requisitos (instalados automaticamente pelo executar.bat):
    pip install -r requirements.txt

Entrada (dados brutos versionados no repositório):
    dados_brutos_regional_LCN.csv
    dados_brutos_paises.csv

Saída (salva na mesma pasta do script):
    fig1_evolucao_regional.png
    fig2_scatter_correlacao.png
    fig3_top5_comparativo.png
    fig4_boxplot_grupos.png
    fig5_correlacao_paises.png

Os gráficos são reconstruídos integralmente a partir dos CSVs de dados brutos.
A origem do snapshot (API do Banco Mundial) está documentada em coletar_dados_api.py.
"""

import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")           # sem janela — muda para "TkAgg" se quiser ver ao vivo
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import mannwhitneyu

# ==============================================================================
# CONFIGURAÇÕES — edite aqui se precisar
# ==============================================================================
PASTA_SAIDA = "."                              # onde salvar os PNGs
DPI = 150                                       # resolução das imagens
CSV_REGIONAL = "dados_brutos_regional_LCN.csv"  # dados brutos do agregado regional
CSV_PAISES   = "dados_brutos_paises.csv"        # dados brutos por país

# ==============================================================================
# PASSO 1 — CARREGAR OS DADOS BRUTOS
# ==============================================================================

def coletar_dados():
    """
    Carrega os dados brutos (snapshot do Banco Mundial) versionados no repositório.
    Retorna: (df_regional, df_paises)
    """
    print("Carregando dados brutos dos CSVs...")
    df_reg = pd.read_csv(CSV_REGIONAL)
    df = pd.read_csv(CSV_PAISES).rename(columns={"Pais": "economy"})
    print(f"  {df['economy'].nunique()} países, {len(df)} observações.")
    return df_reg, df


# ==============================================================================
# PASSO 2 — CLASSIFICAÇÃO POR GRUPO DE INVESTIMENTO
# ==============================================================================

def classificar_grupos(df):
    media = df.groupby("economy")["Gasto_Educacao_pct_PIB"].mean().reset_index()
    media.columns = ["economy", "Gasto_Medio"]
    mediana = media["Gasto_Medio"].median()
    media["Grupo"] = media["Gasto_Medio"].apply(
        lambda x: "Alto Investimento" if x >= mediana else "Baixo Investimento"
    )
    return df.merge(media[["economy", "Grupo"]], on="economy", how="left")


# ==============================================================================
# PASSO 3 — GRÁFICOS
# ==============================================================================

CORES = {
    "Brasil":     "#009C3B", "México":    "#CE1126", "Argentina": "#74ACDF",
    "Colômbia":   "#FCD116", "Chile":     "#D52B1E", "Peru":      "#D91023",
    "Equador":    "#FFD100", "Bolívia":   "#007A33", "Uruguai":   "#5EB6E4",
    "Costa Rica": "#002B7F"
}
sns.set_theme(style="whitegrid", palette="muted")

def salvar(fig, nome):
    caminho = os.path.join(PASTA_SAIDA, nome)
    fig.savefig(caminho, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Salvo: {caminho}")


def fig1_evolucao_regional(df_reg):
    """Figura 1 — Evolução temporal do agregado regional com dois eixos Y."""
    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax2 = ax1.twinx()

    ax1.plot(df_reg["Ano"], df_reg["Gasto_Educacao_pct_PIB"],
             "b-o", linewidth=2.2, markersize=7, label="Gasto em Educação (% PIB)")
    ax2.plot(df_reg["Ano"], df_reg["Taxa_Desemprego"],
             "r--s", linewidth=2.2, markersize=7, label="Taxa de Desemprego (%)")

    ax1.set_xlabel("Ano", fontsize=12)
    ax1.set_ylabel("Gasto em Educação (% do PIB)", color="blue", fontsize=11)
    ax2.set_ylabel("Taxa de Desemprego (%)", color="red", fontsize=11)
    ax1.tick_params(axis="y", labelcolor="blue")
    ax2.tick_params(axis="y", labelcolor="red")
    ax1.set_xticks(df_reg["Ano"])
    ax1.set_xticklabels(df_reg["Ano"], rotation=45)

    # Destaque COVID-19
    ax1.axvspan(2019.5, 2021.5, alpha=0.10, color="gray")
    ax1.text(2020, ax1.get_ylim()[0] + 0.05, "COVID-19",
             fontsize=9, color="gray", ha="center")

    lines1, lab1 = ax1.get_legend_handles_labels()
    lines2, lab2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, lab1 + lab2, loc="upper left", fontsize=10)

    plt.title("Evolução do Gasto em Educação e Taxa de Desemprego\n"
              "América Latina e Caribe — Agregado Regional (2010–2022)",
              fontsize=13, fontweight="bold")
    plt.tight_layout()
    salvar(fig, "fig1_evolucao_regional.png")


def fig2_scatter_correlacao(df):
    """Figura 2 — Scatter plot pooled com reta de tendência e r de Pearson."""
    dc = df.dropna(subset=["Gasto_Educacao_pct_PIB", "Taxa_Desemprego"])
    slope, intercept, r, p, _ = stats.linregress(
        dc["Gasto_Educacao_pct_PIB"], dc["Taxa_Desemprego"]
    )

    fig, ax = plt.subplots(figsize=(9, 6))
    for pais in dc["economy"].unique():
        d = dc[dc["economy"] == pais]
        ax.scatter(d["Gasto_Educacao_pct_PIB"], d["Taxa_Desemprego"],
                   label=pais, alpha=0.75, s=55, color=CORES.get(pais, "gray"))

    x = np.linspace(dc["Gasto_Educacao_pct_PIB"].min(),
                    dc["Gasto_Educacao_pct_PIB"].max(), 100)
    ax.plot(x, slope * x + intercept, "k--", linewidth=1.8,
            label=f"Tendência linear (r = {r:.2f}, p = {p:.3f})")

    ax.text(0.02, 0.96, f"r = {r:.2f}\np-valor = {p:.3f}\nN = {len(dc)}",
            transform=ax.transAxes, fontsize=10, va="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

    ax.set_xlabel("Gasto em Educação (% do PIB)", fontsize=12)
    ax.set_ylabel("Taxa de Desemprego (%)", fontsize=12)
    ax.set_title("Relação entre Investimento em Educação e Desemprego\n"
                 "(10 países × 13 anos, 2010–2022)", fontsize=13, fontweight="bold")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    salvar(fig, "fig2_scatter_correlacao.png")


def fig3_top5_comparativo(df):
    """Figura 3 — Linhas comparativas das 5 maiores economias."""
    top5 = ["Brasil", "México", "Argentina", "Colômbia", "Chile"]
    df5  = df[df["economy"].isin(top5)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    for pais, dados in df5.groupby("economy"):
        d = dados.sort_values("Ano")
        ax1.plot(d["Ano"], d["Gasto_Educacao_pct_PIB"],
                 marker="o", label=pais, linewidth=2, color=CORES[pais])
        ax2.plot(d["Ano"], d["Taxa_Desemprego"],
                 marker="s", label=pais, linewidth=2, linestyle="--", color=CORES[pais])

    for ax in [ax1, ax2]:
        ax.set_xticks(range(2010, 2023, 2))
        ax.grid(True, alpha=0.35)
        ax.legend(fontsize=10)
        ax.set_xlabel("Ano")
        ax.axvspan(2019.5, 2021.5, alpha=0.08, color="gray")

    ax1.set_title("Gasto em Educação (% PIB)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("% do PIB")
    ax2.set_title("Taxa de Desemprego (%)", fontsize=12, fontweight="bold")
    ax2.set_ylabel("% da força de trabalho")
    plt.suptitle("Comparativo das 5 Maiores Economias da América Latina (2010–2022)",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    salvar(fig, "fig3_top5_comparativo.png")


def fig4_boxplot_grupos(df):
    """Figura 4 — Boxplot por grupo de investimento + teste Mann-Whitney."""
    grupos = ["Alto Investimento", "Baixo Investimento"]
    dados_grupos = [
        df[df["Grupo"] == g]["Taxa_Desemprego"].dropna().values
        for g in grupos
    ]
    stat_u, p_mw = mannwhitneyu(*dados_grupos, alternative="two-sided")

    fig, ax = plt.subplots(figsize=(7, 5))
    cores_box = {"Alto Investimento": "#2E86AB", "Baixo Investimento": "#E84855"}
    bp = ax.boxplot(dados_grupos, tick_labels=grupos, patch_artist=True, widths=0.5)
    for patch, g in zip(bp["boxes"], grupos):
        patch.set_facecolor(cores_box[g])
        patch.set_alpha(0.7)

    # Marcar médias
    for i, d in enumerate(dados_grupos, 1):
        ax.scatter(i, np.mean(d), color="white", edgecolors="black",
                   zorder=5, s=60, marker="D", label="Média" if i == 1 else "")

    ax.set_ylabel("Taxa de Desemprego (%)", fontsize=12)
    ax.set_title("Distribuição da Taxa de Desemprego por\nGrupo de Investimento em Educação",
                 fontsize=12, fontweight="bold")
    ax.grid(axis="y", alpha=0.35)
    ax.legend()
    ax.text(0.98, 0.97,
            f"Teste Mann-Whitney\nU = {stat_u:.0f}\np-valor = {p_mw:.3f}",
            transform=ax.transAxes, ha="right", va="top", fontsize=9,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.6))
    plt.tight_layout()
    salvar(fig, "fig4_boxplot_grupos.png")


def fig5_correlacao_paises(df):
    """Figura 5 — Barras horizontais com correlação de Pearson por país."""
    corrs = {}
    for pais in df["economy"].unique():
        d = df[df["economy"] == pais].dropna(
            subset=["Gasto_Educacao_pct_PIB", "Taxa_Desemprego"]
        )
        if len(d) >= 5:
            r, _ = stats.pearsonr(d["Gasto_Educacao_pct_PIB"], d["Taxa_Desemprego"])
            corrs[pais] = round(r, 2)

    corr_df = (
        pd.DataFrame({"País": list(corrs.keys()), "r": list(corrs.values())})
          .sort_values("r")
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#E84855" if v < 0 else "#2E86AB" for v in corr_df["r"]]
    bars = ax.barh(corr_df["País"], corr_df["r"], color=colors,
                   edgecolor="white", height=0.65)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Coeficiente de Correlação de Pearson (r)", fontsize=11)
    ax.set_title("Correlação Educação-Desemprego por País (2010–2022)",
                 fontsize=12, fontweight="bold")
    for bar, val in zip(bars, corr_df["r"]):
        ax.text(val + (0.02 if val >= 0 else -0.02),
                bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}", va="center",
                ha="left" if val >= 0 else "right", fontsize=9)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    salvar(fig, "fig5_correlacao_paises.png")


# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================

if __name__ == "__main__":
    print("=" * 55)
    print("  GERADOR DE GRÁFICOS — Educação e Desemprego na AL")
    print("=" * 55)

    os.makedirs(PASTA_SAIDA, exist_ok=True)

    df_reg, df_paises = coletar_dados()
    df_paises = classificar_grupos(df_paises)

    print(f"\nGerando 5 gráficos em '{PASTA_SAIDA}/'...")
    fig1_evolucao_regional(df_reg)
    fig2_scatter_correlacao(df_paises)
    fig3_top5_comparativo(df_paises)
    fig4_boxplot_grupos(df_paises)
    fig5_correlacao_paises(df_paises)

    print("\nPronto! Todos os gráficos foram gerados.")
