"""Tela de Dashboard: indicadores, graficos, listas e insights."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from components import cards, graficos, tabelas
from config.settings import TIPO_RECEITA
from services import auth_service, dashboard_service, movimentacao_service
from utils.formatters import formatar_moeda, formatar_percentual, primeiro_nome


def _cards_indicadores(
    resumo: dashboard_service.ResumoFinanceiro, moeda: str
) -> None:
    """Os quatro cards superiores."""
    colunas = st.columns(4, gap="small")

    with colunas[0]:
        cards.card_metrica(
            "Saldo Atual",
            formatar_moeda(resumo.saldo_atual, moeda),
            "Atualizado hoje",
            nome_icone="carteira",
            cor_valor="ff-neutro",
            cor_icone="ff-bg-azul",
        )

    with colunas[1]:
        cards.card_metrica(
            "Receitas do mês",
            formatar_moeda(resumo.receitas_mes, moeda),
            f"{formatar_percentual(resumo.variacao_receitas)} em relação ao mês passado",
            nome_icone="tendencia-alta",
            cor_valor="ff-positivo",
            cor_icone="ff-bg-verde",
        )

    with colunas[2]:
        cards.card_metrica(
            "Despesas do mês",
            formatar_moeda(resumo.despesas_mes, moeda),
            f"{formatar_percentual(resumo.variacao_despesas)} em relação ao mês passado",
            nome_icone="tendencia-baixa",
            cor_valor="ff-negativo",
            cor_icone="ff-bg-vermelho",
        )

    with colunas[3]:
        cards.card_metrica(
            "Economizado",
            formatar_moeda(resumo.economia_mes, moeda),
            f"{resumo.percentual_economia:.0f}% das receitas do mês",
            nome_icone="cofre",
            cor_valor="ff-azul" if resumo.economia_mes >= 0 else "ff-negativo",
            cor_icone="ff-bg-azul",
        )


def _paineis_graficos(df: pd.DataFrame, tema: str, moeda: str) -> None:
    """Grafico de evolucao e grafico de categorias lado a lado."""
    coluna_linha, coluna_pizza = st.columns([1.25, 1], gap="small")

    with coluna_linha, st.container(key="painel_evolucao"):
        cards.titulo_painel(
            "Evolução Financeira", "Receitas, despesas e saldo dos últimos meses"
        )
        evolucao = dashboard_service.evolucao_mensal(df)
        if evolucao.empty:
            cards.estado_vazio("Sem dados suficientes para montar o gráfico.")
        else:
            st.plotly_chart(
                graficos.grafico_evolucao(evolucao, tema, moeda),
                use_container_width=True,
                config={"displayModeBar": False},
            )

    with coluna_pizza, st.container(key="painel_categorias"):
        cards.titulo_painel(
            "Gastos por Categoria", "Distribuição das despesas do mês"
        )
        categorias = dashboard_service.gastos_por_categoria(df)
        if categorias.empty:
            cards.estado_vazio("Nenhuma despesa registrada neste mês.")
        else:
            grafico, legenda = st.columns([1, 1], gap="small")
            with grafico:
                st.plotly_chart(
                    graficos.grafico_categorias(categorias, tema, moeda),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            with legenda:
                tabelas.legenda_categorias(categorias, tema, moeda)


def _paineis_listas(df: pd.DataFrame, moeda: str) -> None:
    """Ultimas movimentacoes e contas do mes."""
    coluna_ultimas, coluna_contas = st.columns(2, gap="small")

    with coluna_ultimas, st.container(key="painel_ultimas"):
        cards.titulo_painel("Últimas movimentações", "Os cinco lançamentos mais recentes")
        ultimas = dashboard_service.ultimas_movimentacoes(df)
        if ultimas.empty:
            cards.estado_vazio("Você ainda não registrou movimentações.")
        else:
            for registro in ultimas.to_dict("records"):
                cards.item_lista(
                    registro["descricao"],
                    registro["categoria"],
                    registro["data"],
                    float(registro["valor"]),
                    registro["tipo"] == TIPO_RECEITA,
                    moeda,
                )

    with coluna_contas, st.container(key="painel_contas"):
        cards.titulo_painel("Contas do mês", "Despesas que ainda vão vencer")
        contas = dashboard_service.contas_do_mes(df)
        if contas.empty:
            cards.estado_vazio("Nenhuma conta pendente para este mês.")
        else:
            for registro in contas.to_dict("records"):
                cards.item_lista(
                    registro["descricao"],
                    registro["categoria"],
                    registro["data"],
                    float(registro["valor"]),
                    False,
                    moeda,
                )


def _painel_insights(df: pd.DataFrame, moeda: str) -> None:
    """Frases geradas automaticamente a partir dos dados."""
    with st.container(key="painel_insights"):
        cards.titulo_painel("Insights", "Leituras automáticas das suas finanças")
        for frase in dashboard_service.gerar_insights(df, moeda):
            cards.item_insight(frase)


def render() -> None:
    """Monta a tela de dashboard."""
    usuario = auth_service.usuario_logado()
    moeda = auth_service.moeda_atual()
    tema = auth_service.tema_atual()

    cards.cabecalho_pagina(
        f"Olá, {primeiro_nome(usuario['nome'])}",
        "Bem-vindo ao seu painel financeiro.",
        mostrar_data=True,
    )

    df = movimentacao_service.carregar_dataframe(usuario["id"])
    resumo = dashboard_service.calcular_resumo(df)

    _cards_indicadores(resumo, moeda)
    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
    _paineis_graficos(df, tema, moeda)
    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
    _paineis_listas(df, moeda)
    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
    _painel_insights(df, moeda)
