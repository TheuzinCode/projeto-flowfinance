"""Graficos Plotly do dashboard: evolucao mensal e distribuicao por categoria."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from components.estilos import cores_grafico
from utils.formatters import formatar_mes_ano, formatar_moeda

ALTURA_PADRAO = 330


def _layout_base(figura: go.Figure, tema: str, altura: int = ALTURA_PADRAO) -> go.Figure:
    """Aplica o visual comum aos graficos (fundo transparente e fontes suaves)."""
    cores = cores_grafico(tema)
    figura.update_layout(
        template=cores["template"],
        height=altura,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=cores["texto"], size=12),
        hoverlabel=dict(font_size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            title_text="",
        ),
    )
    return figura


def grafico_evolucao(
    dados: pd.DataFrame, tema: str, simbolo_moeda: str = "R$"
) -> go.Figure:
    """Linha de receitas, despesas e saldo acumulado por mes."""
    cores = cores_grafico(tema)
    figura = go.Figure()

    if dados.empty:
        return _layout_base(figura, tema)

    rotulos = [formatar_mes_ano(data) for data in dados["mes"]]
    series = (
        ("Despesas", cores["despesa"]),
        ("Receitas", cores["receita"]),
        ("Saldo", cores["saldo"]),
    )

    for nome, cor in series:
        figura.add_trace(
            go.Scatter(
                x=rotulos,
                y=dados[nome],
                name=nome,
                mode="lines+markers",
                line=dict(color=cor, width=2.6, shape="spline", smoothing=0.6),
                marker=dict(size=7, line=dict(width=2, color=cor)),
                hovertemplate=(
                    f"<b>{nome}</b><br>%{{x}}<br>"
                    + simbolo_moeda
                    + " %{y:,.2f}<extra></extra>"
                ),
            )
        )

    figura.update_xaxes(showgrid=False, linecolor=cores["grade"])
    figura.update_yaxes(
        gridcolor=cores["grade"], griddash="dot", zeroline=False, tickformat=",.0f"
    )
    return _layout_base(figura, tema)


def grafico_categorias(
    dados: pd.DataFrame, tema: str, simbolo_moeda: str = "R$"
) -> go.Figure:
    """Rosca com a distribuicao das despesas do mes por categoria."""
    cores = cores_grafico(tema)
    figura = go.Figure()

    if dados.empty:
        return _layout_base(figura, tema)

    total = float(dados["valor"].sum())
    figura.add_trace(
        go.Pie(
            labels=dados["categoria"],
            values=dados["valor"],
            hole=0.62,
            sort=False,
            marker=dict(colors=cores["sequencia"], line=dict(width=0)),
            textinfo="none",
            hovertemplate=(
                "<b>%{label}</b><br>"
                + simbolo_moeda
                + " %{value:,.2f} (%{percent})<extra></extra>"
            ),
        )
    )

    figura.update_layout(
        showlegend=False,
        annotations=[
            dict(
                text=(
                    "<span style='font-size:12px'>Total</span><br>"
                    f"<b>{formatar_moeda(total, simbolo_moeda)}</b>"
                ),
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=15, color=cores["texto"]),
            )
        ],
    )
    return _layout_base(figura, tema)
