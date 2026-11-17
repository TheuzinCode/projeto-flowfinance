"""Tela de Configuracoes: perfil, conta, preferencias e dados."""

from __future__ import annotations

from datetime import date

import streamlit as st

from components import cards
from components.estilos import sem_indentacao
from components.icones import icone
from config.settings import IDIOMAS, MOEDAS, TEMAS, nome_do_banco, resumo_conexao
from services import auth_service, movimentacao_service
from utils.formatters import iniciais
from utils.validations import ErroDeValidacao


def _nome_da_moeda(simbolo: str) -> str:
    """Converte o simbolo salvo no banco no rotulo exibido no selectbox."""
    for rotulo, valor in MOEDAS.items():
        if valor == simbolo:
            return rotulo
    return next(iter(MOEDAS))


def _bloco_perfil(usuario: dict) -> None:
    """Formulario de dados pessoais."""
    with st.container(key="cfg_perfil"):
        cards.titulo_painel("Perfil", "Suas informações pessoais")

        avatar, _ = st.columns([1, 3], vertical_alignment="center")
        avatar.markdown(
            f'<div class="ff-avatar" style="width:58px;height:58px;font-size:1.1rem">'
            f"{iniciais(usuario['nome'])}</div>",
            unsafe_allow_html=True,
        )

        with st.form("form_perfil", border=False):
            nome = st.text_input("Nome", value=usuario["nome"])
            email = st.text_input("Email", value=usuario["email"])
            telefone = st.text_input(
                "Telefone", value=usuario.get("telefone", ""), placeholder="+55 (11) 90000-0000"
            )
            if st.form_submit_button("Salvar alterações", type="primary"):
                try:
                    auth_service.atualizar_perfil(
                        usuario["id"], nome, email, telefone
                    )
                except ErroDeValidacao as erro:
                    st.error(str(erro))
                else:
                    st.session_state["cfg_mensagem"] = "Perfil atualizado com sucesso."
                    st.rerun()


def _bloco_conta(usuario: dict) -> None:
    """Troca de senha e preferencias regionais."""
    with st.container(key="cfg_conta"):
        cards.titulo_painel("Conta", "Segurança e preferências regionais")

        with st.form("form_senha", border=False):
            nova_senha = st.text_input(
                "Alterar senha", type="password", placeholder="Nova senha"
            )
            confirmacao = st.text_input(
                "Confirmar nova senha", type="password", placeholder="Repita a nova senha"
            )
            if st.form_submit_button("Atualizar senha", type="primary"):
                try:
                    auth_service.alterar_senha(usuario["id"], nova_senha, confirmacao)
                except ErroDeValidacao as erro:
                    st.error(str(erro))
                else:
                    st.session_state["cfg_mensagem"] = "Senha alterada com sucesso."
                    st.rerun()

        st.selectbox("Idioma", IDIOMAS, index=0)
        rotulos_moeda = list(MOEDAS)
        moeda = st.selectbox(
            "Moeda",
            rotulos_moeda,
            index=rotulos_moeda.index(_nome_da_moeda(usuario["moeda"])),
        )
        if MOEDAS[moeda] != usuario["moeda"]:
            auth_service.atualizar_preferencias(
                usuario["id"], usuario["tema"], MOEDAS[moeda]
            )
            st.rerun()


def _bloco_preferencias(usuario: dict) -> None:
    """Escolha do tema da interface."""
    with st.container(key="cfg_preferencias"):
        cards.titulo_painel("Preferências", "Aparência e organização")

        tema = st.radio(
            "Tema",
            TEMAS,
            index=TEMAS.index(usuario["tema"]),
            horizontal=True,
            format_func=lambda valor: (
                f"{':material/light_mode:' if valor == 'Claro' else ':material/dark_mode:'}"
                f" Modo {valor}"
            ),
        )
        if tema != usuario["tema"]:
            auth_service.atualizar_preferencias(
                usuario["id"], tema, usuario["moeda"]
            )
            st.rerun()


def _bloco_dados(usuario: dict) -> None:
    """Exportacao de dados e informacoes do banco."""
    with st.container(key="cfg_dados"):
        cards.titulo_painel("Dados", "Backup e informações do sistema")

        df = movimentacao_service.carregar_dataframe(usuario["id"])
        st.download_button(
            "Exportar dados (CSV)",
            data=movimentacao_service.exportar_csv(df),
            file_name=f"financeflow_{date.today():%Y-%m-%d}.csv",
            mime="text/csv",
            icon=":material/download:",
            use_container_width=True,
        )
        st.caption(
            f"{len(df)} movimentação(ões) serão exportadas no formato CSV "
            "(separador ponto e vírgula, compatível com Excel)."
        )

        st.markdown(
            sem_indentacao(
                f"""
                <div class="ff-insight" style="border-left-color:var(--ff-texto-suave)">
                    <span class="ff-insight__icone">{icone("banco-dados", 17)}</span>
                    <span><b>Banco em uso:</b> {nome_do_banco()}<br>
                    <span class="ff-celula--suave">{resumo_conexao()}</span></span>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )


def render() -> None:
    """Monta a tela de configuracoes."""
    usuario = auth_service.usuario_logado()

    mensagem = st.session_state.pop("cfg_mensagem", None)
    if mensagem:
        st.toast(mensagem, icon=":material/check_circle:")

    cards.cabecalho_pagina(
        "Configurações", "Gerencie seu perfil, preferências e dados do sistema."
    )

    coluna_esquerda, coluna_direita = st.columns(2, gap="small")
    with coluna_esquerda:
        _bloco_perfil(usuario)
        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        _bloco_preferencias(usuario)
    with coluna_direita:
        _bloco_conta(usuario)
        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        _bloco_dados(usuario)
