"""Componentes visuais reutilizaveis: cabecalhos, cards de metrica e listas."""

from __future__ import annotations

from html import escape

import streamlit as st

from components.estilos import sem_indentacao
from components.icones import icone
from config.settings import ICONES_CATEGORIA
from utils.formatters import formatar_data, formatar_data_extenso, formatar_moeda


def cabecalho_pagina(
    titulo: str, subtitulo: str = "", mostrar_data: bool = False
) -> None:
    """Renderiza o titulo da pagina e, opcionalmente, a data de hoje."""
    bloco = (
        '<div class="ff-cabecalho">'
        f"<h1>{escape(titulo)}</h1>"
        f"<p>{escape(subtitulo)}</p>"
        "</div>"
    )

    if not mostrar_data:
        st.markdown(bloco, unsafe_allow_html=True)
        return

    coluna_titulo, coluna_data = st.columns([3, 1], vertical_alignment="center")
    coluna_titulo.markdown(bloco, unsafe_allow_html=True)
    coluna_data.markdown(
        f'<div class="ff-data-hoje">{icone("calendario", 15)}'
        f"<span>{formatar_data_extenso()}</span></div>",
        unsafe_allow_html=True,
    )


def card_metrica(
    titulo: str,
    valor: str,
    legenda: str = "",
    nome_icone: str = "carteira",
    cor_valor: str = "ff-neutro",
    cor_icone: str = "ff-bg-azul",
) -> None:
    """Card de indicador usado no topo do dashboard."""
    st.markdown(
        sem_indentacao(
            f"""
            <div class="ff-card">
                <div class="ff-metrica__topo">
                    <span class="ff-metrica__titulo">{escape(titulo)}</span>
                    <span class="ff-metrica__icone {cor_icone}">
                        {icone(nome_icone, 17)}
                    </span>
                </div>
                <div class="ff-metrica__valor {cor_valor}">{escape(valor)}</div>
                <div class="ff-metrica__legenda">{escape(legenda)}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def titulo_painel(titulo: str, subtitulo: str = "") -> None:
    """Titulo interno dos paineis (graficos, listas e formularios)."""
    st.markdown(
        f'<p class="ff-painel-titulo">{escape(titulo)}</p>'
        f'<p class="ff-painel-sub">{escape(subtitulo)}</p>',
        unsafe_allow_html=True,
    )


def item_lista(
    descricao: str,
    categoria: str,
    data_movimentacao,
    valor: float,
    e_receita: bool,
    simbolo_moeda: str = "R$",
) -> None:
    """Linha compacta usada em 'Ultimas movimentacoes' e 'Contas do mes'."""
    nome_icone = ICONES_CATEGORIA.get(categoria, "caixa")
    classe_valor = "ff-positivo" if e_receita else "ff-negativo"
    sinal = "+" if e_receita else "-"
    st.markdown(
        sem_indentacao(
            f"""
            <div class="ff-lista-item">
                <div class="ff-lista-item__icone">{icone(nome_icone, 17)}</div>
                <div class="ff-lista-item__corpo">
                    <div class="ff-lista-item__titulo">{escape(descricao)}</div>
                    <div class="ff-lista-item__meta">
                        {escape(categoria)} &middot; {formatar_data(data_movimentacao)}
                    </div>
                </div>
                <div class="ff-lista-item__valor {classe_valor}">
                    {sinal} {escape(formatar_moeda(valor, simbolo_moeda))}
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def item_insight(texto: str) -> None:
    """Frase de insight gerada automaticamente."""
    st.markdown(
        f'<div class="ff-insight"><span class="ff-insight__icone">'
        f'{icone("lampada", 17)}</span><span>{escape(texto)}</span></div>',
        unsafe_allow_html=True,
    )


def estado_vazio(mensagem: str) -> None:
    """Mensagem exibida quando nao ha dados para mostrar."""
    st.markdown(f'<div class="ff-vazio">{escape(mensagem)}</div>', unsafe_allow_html=True)
