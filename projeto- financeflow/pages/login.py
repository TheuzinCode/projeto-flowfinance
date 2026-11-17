"""Tela de autenticacao: entrar e criar conta."""

from __future__ import annotations

import streamlit as st

from components.estilos import logo_svg, sem_indentacao
from config.settings import APP_NOME
from services import auth_service
from utils.validations import ErroDeValidacao


def _marca() -> None:
    """Logo centralizado acima do formulario."""
    st.markdown(
        sem_indentacao(
            f"""
            <div style="display:flex;flex-direction:column;align-items:center;
                        gap:0.6rem;margin-bottom:1.1rem">
                <div class="ff-logo__marca"
                     style="width:52px;height:52px;border-radius:15px">
                    {logo_svg()}
                </div>
                <div class="ff-logo__texto" style="font-size:1.5rem">{APP_NOME}</div>
                <p class="ff-painel-sub" style="margin:0">
                    Organize suas receitas e despesas em um só lugar.
                </p>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _formulario_login() -> None:
    """Formulario de acesso."""
    with st.form("form_login", border=False):
        email = st.text_input("E-mail", placeholder="nome@email.com")
        senha = st.text_input("Senha", type="password", placeholder="••••••••")
        enviado = st.form_submit_button(
            "Entrar", use_container_width=True, type="primary"
        )

    if not enviado:
        return

    try:
        usuario = auth_service.autenticar(email, senha)
    except ErroDeValidacao as erro:
        st.error(str(erro))
        return

    auth_service.iniciar_sessao(usuario)
    st.rerun()


def _formulario_cadastro() -> None:
    """Formulario de criacao de conta."""
    with st.form("form_cadastro", border=False):
        nome = st.text_input("Nome completo", placeholder="Como devemos te chamar?")
        email = st.text_input("E-mail", placeholder="nome@email.com")
        senha = st.text_input("Senha", type="password", placeholder="Mínimo 6 caracteres")
        confirmacao = st.text_input("Confirmar senha", type="password")
        enviado = st.form_submit_button(
            "Criar conta", use_container_width=True, type="primary"
        )

    if not enviado:
        return

    try:
        usuario = auth_service.registrar(nome, email, senha, confirmacao)
    except ErroDeValidacao as erro:
        st.error(str(erro))
        return

    auth_service.iniciar_sessao(usuario)
    st.rerun()


def render() -> None:
    """Desenha a tela de login centralizada e responsiva."""
    _, centro, _ = st.columns([1, 1.5, 1])

    with centro:
        _marca()
        with st.container(key="login_card"):
            entrar, cadastrar = st.tabs(["Entrar", "Criar conta"])
            with entrar:
                _formulario_login()
            with cadastrar:
                _formulario_cadastro()
