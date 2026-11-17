"""Indicadores, séries dos gráficos e insights do dashboard (tudo com Pandas)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from config.settings import (
    MESES_GRAFICO_EVOLUCAO,
    QTD_ULTIMAS_MOVIMENTACOES,
    TIPO_DESPESA,
    TIPO_RECEITA,
)
from utils.formatters import formatar_moeda


@dataclass(frozen=True)
class ResumoFinanceiro:
    """Indicadores exibidos nos quatro cards superiores."""

    saldo_atual: float
    receitas_mes: float
    despesas_mes: float
    economia_mes: float
    variacao_receitas: float
    variacao_despesas: float
    percentual_economia: float


def _mes_referencia(referencia: date | None = None) -> pd.Timestamp:
    """Primeiro dia do mês de referência."""
    base = referencia or date.today()
    return pd.Timestamp(base).replace(day=1).normalize()


def _total(df: pd.DataFrame, tipo: str) -> float:
    """Soma os valores de um tipo de movimentação."""
    if df.empty:
        return 0.0
    return float(df.loc[df["tipo"] == tipo, "valor"].sum())


def _variacao(atual: float, anterior: float) -> float:
    """Variação percentual entre dois períodos."""
    if anterior == 0:
        return 100.0 if atual > 0 else 0.0
    return round(((atual - anterior) / anterior) * 100, 1)


def calcular_resumo(df: pd.DataFrame, referencia: date | None = None) -> ResumoFinanceiro:
    """Calcula saldo, receitas, despesas e economia do mês."""
    if df.empty:
        return ResumoFinanceiro(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    mes_atual = _mes_referencia(referencia)
    mes_anterior = (mes_atual - pd.offsets.MonthBegin(1)).normalize()

    dados_mes = df[df["mes"] == mes_atual]
    dados_anterior = df[df["mes"] == mes_anterior]

    receitas = _total(dados_mes, TIPO_RECEITA)
    despesas = _total(dados_mes, TIPO_DESPESA)
    economia = receitas - despesas

    saldo = float(df["valor_com_sinal"].sum())
    percentual = round((economia / receitas) * 100, 1) if receitas else 0.0

    return ResumoFinanceiro(
        saldo_atual=saldo,
        receitas_mes=receitas,
        despesas_mes=despesas,
        economia_mes=economia,
        variacao_receitas=_variacao(receitas, _total(dados_anterior, TIPO_RECEITA)),
        variacao_despesas=_variacao(despesas, _total(dados_anterior, TIPO_DESPESA)),
        percentual_economia=percentual,
    )


def evolucao_mensal(
    df: pd.DataFrame, meses: int = MESES_GRAFICO_EVOLUCAO
) -> pd.DataFrame:
    """Série de receitas, despesas e saldo acumulado dos últimos meses."""
    colunas = ["mes", "Receitas", "Despesas", "Saldo"]
    if df.empty:
        return pd.DataFrame(columns=colunas)

    agrupado = (
        df.pivot_table(
            index="mes", columns="tipo", values="valor", aggfunc="sum", fill_value=0.0
        )
        .rename(columns={TIPO_RECEITA: "Receitas", TIPO_DESPESA: "Despesas"})
        .sort_index()
    )

    for coluna in ("Receitas", "Despesas"):
        if coluna not in agrupado.columns:
            agrupado[coluna] = 0.0

    # Preenche meses sem movimentação para a linha não ficar com buracos.
    indice_completo = pd.date_range(
        start=agrupado.index.min(), end=agrupado.index.max(), freq="MS"
    )
    agrupado = agrupado.reindex(indice_completo, fill_value=0.0)

    agrupado["Saldo"] = (agrupado["Receitas"] - agrupado["Despesas"]).cumsum()
    resultado = agrupado.tail(meses).reset_index(names="mes")
    return resultado[colunas]


def gastos_por_categoria(
    df: pd.DataFrame, referencia: date | None = None
) -> pd.DataFrame:
    """Distribuição das despesas do mês por categoria."""
    colunas = ["categoria", "valor", "percentual"]
    if df.empty:
        return pd.DataFrame(columns=colunas)

    despesas = df[(df["tipo"] == TIPO_DESPESA) & (df["mes"] == _mes_referencia(referencia))]
    if despesas.empty:
        return pd.DataFrame(columns=colunas)

    agrupado = (
        despesas.groupby("categoria", as_index=False)["valor"]
        .sum()
        .sort_values("valor", ascending=False)
    )
    total = agrupado["valor"].sum()
    agrupado["percentual"] = (agrupado["valor"] / total * 100).round(1)
    return agrupado.reset_index(drop=True)


def ultimas_movimentacoes(
    df: pd.DataFrame, limite: int = QTD_ULTIMAS_MOVIMENTACOES
) -> pd.DataFrame:
    """Últimas movimentações registradas (já lançadas)."""
    if df.empty:
        return df
    hoje = pd.Timestamp(date.today())
    return df[df["data"] <= hoje].head(limite)


def contas_do_mes(df: pd.DataFrame) -> pd.DataFrame:
    """Despesas futuras ainda dentro do mês corrente."""
    if df.empty:
        return df
    hoje = pd.Timestamp(date.today())
    fim_do_mes = (_mes_referencia() + pd.offsets.MonthEnd(1)).normalize()
    futuras = df[
        (df["tipo"] == TIPO_DESPESA) & (df["data"] > hoje) & (df["data"] <= fim_do_mes)
    ]
    return futuras.sort_values("data").reset_index(drop=True)


def gerar_insights(
    df: pd.DataFrame, simbolo_moeda: str = "R$", referencia: date | None = None
) -> list[str]:
    """Gera frases automáticas a partir dos dados do mês."""
    if df.empty:
        return ["Cadastre sua primeira movimentação para liberar os insights."]

    resumo = calcular_resumo(df, referencia)
    insights: list[str] = []

    if resumo.economia_mes > 0:
        insights.append(
            f"Você economizou {formatar_moeda(resumo.economia_mes, simbolo_moeda)} "
            "neste mês. Continue assim!"
        )
    elif resumo.economia_mes < 0:
        insights.append(
            f"Suas despesas superaram as receitas em "
            f"{formatar_moeda(abs(resumo.economia_mes), simbolo_moeda)} neste mês."
        )

    if resumo.variacao_despesas > 0:
        insights.append(
            f"Você gastou {abs(resumo.variacao_despesas):.0f}% a mais que no mês passado."
        )
    elif resumo.variacao_despesas < 0:
        insights.append(
            f"Seus gastos caíram {abs(resumo.variacao_despesas):.0f}% em relação ao mês passado."
        )

    categorias = gastos_por_categoria(df, referencia)
    if not categorias.empty:
        maior = categorias.iloc[0]
        insights.append(
            f"Sua maior categoria é {maior['categoria']} com "
            f"{formatar_moeda(float(maior['valor']), simbolo_moeda)} "
            f"({maior['percentual']:.0f}% das despesas)."
        )

    pendentes = contas_do_mes(df)
    if not pendentes.empty:
        total = float(pendentes["valor"].sum())
        insights.append(
            f"Você tem {len(pendentes)} conta(s) a pagar ainda neste mês, "
            f"somando {formatar_moeda(total, simbolo_moeda)}."
        )

    if resumo.percentual_economia >= 30:
        insights.append(
            f"Sua taxa de economia está em {resumo.percentual_economia:.0f}% das receitas."
        )

    return insights or ["Seus números estão estáveis em relação ao mês passado."]
