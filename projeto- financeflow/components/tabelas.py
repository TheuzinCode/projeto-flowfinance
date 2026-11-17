"""Tabela responsiva de movimentacoes e legenda de categorias.

No desktop as colunas ficam lado a lado como uma tabela tradicional.
No celular o CSS quebra cada linha em um cartao, e os rotulos
(`ff-rotulo-mobile`) aparecem antes de cada valor.
"""

from __future__ import annotations

from html import escape
from typing import Literal

import pandas as pd
import streamlit as st

from components.estilos import cores_grafico
from components.icones import icone
from config.settings import ICONES_CATEGORIA, TIPO_RECEITA
from utils.formatters import formatar_data, formatar_moeda

Acao = Literal["editar", "excluir"]

LARGURAS = [3.0, 1.5, 1.7, 1.2, 1.8, 1.2, 1.4]
COLUNAS = [
    "Descrição",
    "Categoria",
    "Valor",
    "Data",
    "Forma de pagamento",
    "Status",
    "Ações",
]


def _celula(conteudo: str, rotulo: str = "", classe: str = "ff-celula") -> str:
    """Monta uma celula com rotulo visivel apenas no celular."""
    prefixo = f'<span class="ff-rotulo-mobile">{escape(rotulo)}</span>' if rotulo else ""
    return f'<div class="{classe}">{prefixo}{conteudo}</div>'


def _cabecalho() -> None:
    """Cabecalho da tabela (escondido no celular)."""
    with st.container(key="tabela_cabecalho"):
        colunas = st.columns(LARGURAS, vertical_alignment="center")
        for coluna, titulo in zip(colunas, COLUNAS):
            coluna.markdown(f"{titulo.upper()}")


def tabela_movimentacoes(
    df: pd.DataFrame, simbolo_moeda: str = "R$"
) -> tuple[Acao | None, int | None]:
    """Renderiza a tabela e devolve a acao solicitada pelo usuario."""
    if df.empty:
        st.markdown(
            '<div class="ff-vazio">Nenhuma movimentação encontrada com os '
            "filtros atuais.</div>",
            unsafe_allow_html=True,
        )
        return None, None

    _cabecalho()

    acao: Acao | None = None
    alvo: int | None = None

    for registro in df.to_dict("records"):
        identificador = int(registro["id"])
        e_receita = registro["tipo"] == TIPO_RECEITA
        nome_icone = ICONES_CATEGORIA.get(registro["categoria"], "caixa")
        seta = "seta-cima" if e_receita else "seta-baixo"
        classe_valor = "ff-positivo" if e_receita else "ff-negativo"
        sinal = "+" if e_receita else "-"
        status = registro["status"]
        classe_status = "ff-badge--ok" if status == "Concluído" else "ff-badge--pendente"

        with st.container(key=f"linha_{identificador}"):
            colunas = st.columns(LARGURAS, vertical_alignment="center")

            colunas[0].markdown(
                _celula(
                    f'<span class="{classe_valor}">{icone(seta, 15)}</span>'
                    f'<span class="ff-celula__icone">{icone(nome_icone, 16)}</span>'
                    f"<b>{escape(str(registro['descricao']))}</b>"
                ),
                unsafe_allow_html=True,
            )
            colunas[1].markdown(
                _celula(
                    escape(str(registro["categoria"])),
                    "Categoria",
                    "ff-celula ff-celula--suave",
                ),
                unsafe_allow_html=True,
            )
            colunas[2].markdown(
                _celula(
                    f'<b class="{classe_valor}">{sinal} '
                    f'{escape(formatar_moeda(float(registro["valor"]), simbolo_moeda))}</b>',
                    "Valor",
                ),
                unsafe_allow_html=True,
            )
            colunas[3].markdown(
                _celula(formatar_data(registro["data"]), "Data"),
                unsafe_allow_html=True,
            )
            colunas[4].markdown(
                _celula(
                    escape(str(registro["forma_pagamento"])),
                    "Pagamento",
                    "ff-celula ff-celula--suave",
                ),
                unsafe_allow_html=True,
            )
            colunas[5].markdown(
                _celula(
                    f'<span class="ff-badge {classe_status}">{escape(status)}</span>',
                    "Status",
                ),
                unsafe_allow_html=True,
            )

            with colunas[6]:
                botao_editar, botao_excluir = st.columns(2)
                if botao_editar.button(
                    "",
                    key=f"editar_{identificador}",
                    icon=":material/edit:",
                    help="Editar movimentação",
                ):
                    acao, alvo = "editar", identificador
                if botao_excluir.button(
                    "",
                    key=f"excluir_{identificador}",
                    icon=":material/delete:",
                    help="Excluir movimentação",
                ):
                    acao, alvo = "excluir", identificador

    return acao, alvo


def legenda_categorias(
    dados: pd.DataFrame, tema: str, simbolo_moeda: str = "R$"
) -> None:
    """Legenda colorida ao lado do grafico de pizza."""
    if dados.empty:
        return

    sequencia = cores_grafico(tema)["sequencia"]
    linhas: list[str] = []

    for posicao, registro in enumerate(dados.to_dict("records")):
        cor = sequencia[posicao % len(sequencia)]
        linhas.append(
            '<div class="ff-lista-item" style="padding:0.32rem 0;border:none">'
            f'<span style="width:9px;height:9px;border-radius:50%;background:{cor};'
            'flex:0 0 9px"></span>'
            f'<div class="ff-lista-item__corpo"><div class="ff-lista-item__titulo" '
            f'style="font-weight:500">{escape(str(registro["categoria"]))}</div></div>'
            f'<div class="ff-lista-item__valor">'
            f'{escape(formatar_moeda(float(registro["valor"]), simbolo_moeda))}</div>'
            "</div>"
        )

    st.markdown("".join(linhas), unsafe_allow_html=True)
