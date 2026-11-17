"""Tela de Movimentacoes: listagem, filtros, cadastro, edicao e exclusao."""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
import streamlit as st

from components import cards, tabelas
from config.settings import FORMAS_PAGAMENTO, TIPO_DESPESA, TIPO_RECEITA, TIPOS
from services import auth_service, movimentacao_service
from utils.validations import ErroDeValidacao, categorias_do_tipo

CHAVE_DIALOGO = "mov_dialogo"
CHAVE_REGISTRO = "mov_registro"


# --------------------------------------------------------------------------- #
# Controle dos dialogos
# --------------------------------------------------------------------------- #
def _abrir_dialogo(tipo_dialogo: str, registro: dict[str, Any] | None = None) -> None:
    """Marca qual dialogo deve ser exibido na proxima execucao."""
    st.session_state[CHAVE_DIALOGO] = tipo_dialogo
    st.session_state[CHAVE_REGISTRO] = registro
    st.rerun()


def _fechar_dialogo(mensagem: str | None = None) -> None:
    """Fecha o dialogo aberto e opcionalmente mostra um aviso."""
    st.session_state[CHAVE_DIALOGO] = None
    st.session_state[CHAVE_REGISTRO] = None
    if mensagem:
        st.session_state["mov_mensagem"] = mensagem
    st.rerun()


@st.dialog("Movimentação", width="large")
def _dialogo_formulario() -> None:
    """Formulario de nova movimentacao ou edicao de uma existente."""
    registro: dict[str, Any] | None = st.session_state.get(CHAVE_REGISTRO)
    edicao = registro is not None

    st.markdown(
        f'<p class="ff-painel-sub">'
        f'{"Atualize os dados do lançamento." if edicao else "Cadastre uma nova receita ou despesa."}'
        "</p>",
        unsafe_allow_html=True,
    )

    tipo_padrao = registro["tipo"] if edicao else TIPO_RECEITA
    tipo = st.radio(
        "Tipo",
        TIPOS,
        index=TIPOS.index(tipo_padrao),
        horizontal=True,
    )

    categorias = categorias_do_tipo(tipo)
    indice_categoria = (
        categorias.index(registro["categoria"])
        if edicao and registro["categoria"] in categorias
        else 0
    )

    coluna_esquerda, coluna_direita = st.columns(2)
    with coluna_esquerda:
        categoria = st.selectbox("Categoria", categorias, index=indice_categoria)
        valor = st.number_input(
            "Valor",
            min_value=0.0,
            step=10.0,
            format="%.2f",
            value=float(registro["valor"]) if edicao else 0.0,
        )
        data_movimentacao = st.date_input(
            "Data",
            value=registro["data"] if edicao else date.today(),
            format="DD/MM/YYYY",
        )
    with coluna_direita:
        descricao = st.text_input(
            "Descrição",
            value=registro["descricao"] if edicao else "",
            placeholder="Ex.: Supermercado, Salário mensal...",
        )
        forma_pagamento = st.selectbox(
            "Forma de pagamento",
            FORMAS_PAGAMENTO,
            index=(
                FORMAS_PAGAMENTO.index(registro["forma_pagamento"])
                if edicao and registro["forma_pagamento"] in FORMAS_PAGAMENTO
                else 0
            ),
        )
        observacao = st.text_area(
            "Observação",
            value=registro["observacao"] if edicao else "",
            placeholder="Opcional",
            height=92,
        )

    botao_cancelar, botao_salvar = st.columns([1, 1])
    if botao_cancelar.button("Cancelar", use_container_width=True):
        _fechar_dialogo()

    if botao_salvar.button(
        "Salvar", type="primary", use_container_width=True
    ):
        dados = {
            "tipo": tipo,
            "categoria": categoria,
            "descricao": descricao,
            "valor": valor,
            "data": data_movimentacao,
            "forma_pagamento": forma_pagamento,
            "observacao": observacao,
        }
        try:
            if edicao:
                movimentacao_service.atualizar(
                    int(registro["id"]), auth_service.usuario_id(), dados
                )
                _fechar_dialogo("Movimentação atualizada com sucesso.")
            else:
                movimentacao_service.criar(auth_service.usuario_id(), dados)
                _fechar_dialogo("Movimentação cadastrada com sucesso.")
        except ErroDeValidacao as erro:
            st.error(str(erro))


@st.dialog("Excluir movimentação")
def _dialogo_exclusao() -> None:
    """Confirmacao antes de remover um lancamento."""
    registro: dict[str, Any] | None = st.session_state.get(CHAVE_REGISTRO)
    if registro is None:
        _fechar_dialogo()
        return

    st.warning(
        f"Deseja realmente excluir **{registro['descricao']}**? "
        "Essa ação não pode ser desfeita."
    )

    botao_cancelar, botao_excluir = st.columns(2)
    if botao_cancelar.button("Cancelar", use_container_width=True):
        _fechar_dialogo()
    if botao_excluir.button(
        "Excluir", type="primary", use_container_width=True
    ):
        try:
            movimentacao_service.excluir(
                int(registro["id"]), auth_service.usuario_id()
            )
            _fechar_dialogo("Movimentação excluída.")
        except ErroDeValidacao as erro:
            st.error(str(erro))


# --------------------------------------------------------------------------- #
# Filtros
# --------------------------------------------------------------------------- #
CHAVE_VERSAO_FILTROS = "filtros_versao"


def _limpar_filtros() -> None:
    """Zera os filtros trocando a versao das chaves dos widgets.

    Apenas apagar as chaves nao limparia os campos na tela: o Streamlit
    reaproveita o valor quando o widget mantem a mesma identidade.
    """
    st.session_state[CHAVE_VERSAO_FILTROS] = (
        st.session_state.get(CHAVE_VERSAO_FILTROS, 0) + 1
    )


def _barra_de_filtros(df: pd.DataFrame) -> dict[str, str]:
    """Campos de busca e filtros, devolvidos como dicionario."""
    versao = st.session_state.get(CHAVE_VERSAO_FILTROS, 0)
    opcoes_categoria = [
        "Todas as categorias",
        *movimentacao_service.categorias_do_dataframe(df),
    ]
    # Evita estado invalido quando a categoria filtrada deixa de existir.
    chave_categoria = f"filtro_categoria_{versao}"
    if st.session_state.get(chave_categoria) not in opcoes_categoria:
        st.session_state.pop(chave_categoria, None)

    with st.container(key="mov_filtros"):
        busca, periodo, categoria, tipo = st.columns([2, 1.3, 1.3, 1])

        return {
            "texto": busca.text_input(
                "Pesquisar",
                key=f"filtro_texto_{versao}",
                placeholder="Pesquisar",
                label_visibility="collapsed",
            ),
            "periodo": periodo.selectbox(
                "Período",
                movimentacao_service.PERIODOS,
                key=f"filtro_periodo_{versao}",
                label_visibility="collapsed",
            ),
            "categoria": categoria.selectbox(
                "Categoria",
                opcoes_categoria,
                key=chave_categoria,
                label_visibility="collapsed",
            ),
            "tipo": tipo.selectbox(
                "Tipo",
                ["Todos", TIPO_RECEITA, TIPO_DESPESA],
                key=f"filtro_tipo_{versao}",
                label_visibility="collapsed",
            ),
        }


# --------------------------------------------------------------------------- #
# Pagina
# --------------------------------------------------------------------------- #
def render() -> None:
    """Monta a tela de movimentacoes."""
    usuario_id = auth_service.usuario_id()
    moeda = auth_service.moeda_atual()

    mensagem = st.session_state.pop("mov_mensagem", None)
    if mensagem:
        st.toast(mensagem, icon=":material/check_circle:")

    coluna_titulo, coluna_botao = st.columns([3, 1], vertical_alignment="center")
    with coluna_titulo:
        cards.cabecalho_pagina(
            "Movimentações", "Receitas e despesas reunidas em um só lugar."
        )
    with coluna_botao:
        if st.button(
            "Nova Movimentação",
            type="primary",
            icon=":material/add:",
            use_container_width=True,
        ):
            _abrir_dialogo("formulario", None)

    df = movimentacao_service.carregar_dataframe(usuario_id)
    filtros = _barra_de_filtros(df)
    filtrado = movimentacao_service.aplicar_filtros(df, **filtros)

    coluna_contagem, coluna_limpar = st.columns([3, 1], vertical_alignment="center")
    coluna_contagem.markdown(
        f'<p class="ff-painel-sub" style="margin:0.6rem 0 0.2rem 0.2rem">'
        f"{len(filtrado)} registro(s) encontrados</p>",
        unsafe_allow_html=True,
    )
    if coluna_limpar.button(
        "Limpar filtros",
        icon=":material/filter_alt_off:",
        use_container_width=True,
    ):
        _limpar_filtros()
        st.rerun()

    with st.container(key="mov_tabela"):
        acao, alvo = tabelas.tabela_movimentacoes(filtrado, moeda)

    if acao and alvo is not None:
        selecionado = filtrado[filtrado["id"] == alvo].to_dict("records")
        if selecionado:
            registro = selecionado[0]
            registro["data"] = registro["data"].date()
            _abrir_dialogo("formulario" if acao == "editar" else "exclusao", registro)

    dialogo = st.session_state.get(CHAVE_DIALOGO)
    if dialogo == "formulario":
        _dialogo_formulario()
    elif dialogo == "exclusao":
        _dialogo_exclusao()
