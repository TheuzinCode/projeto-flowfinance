"""Menu lateral fixo com navegacao, identificacao do usuario e logout."""

from __future__ import annotations

from html import escape

import streamlit as st

from components.estilos import logo_svg, sem_indentacao
from config.settings import APP_NOME
from services import auth_service
from utils.formatters import iniciais

# Chave da pagina, rotulo e icone (Material Symbols nativo do Streamlit).
ITENS_MENU: tuple[tuple[str, str, str], ...] = (
    ("dashboard", "Dashboard", ":material/dashboard:"),
    ("movimentacoes", "Movimentações", ":material/swap_vert:"),
    ("configuracoes", "Configurações", ":material/settings:"),
)


def _marca() -> None:
    """Logo e nome do produto."""
    st.markdown(
        f'<div class="ff-logo">'
        f'<div class="ff-logo__marca">{logo_svg()}</div>'
        f'<div class="ff-logo__texto">{escape(APP_NOME)}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def _rodape_usuario(nome: str) -> None:
    """Avatar e nome do usuario logado."""
    st.markdown(
        sem_indentacao(
            f"""
            <div class="ff-usuario">
                <div class="ff-avatar">{escape(iniciais(nome))}</div>
                <div>
                    <div class="ff-usuario__nome">{escape(nome)}</div>
                    <div class="ff-usuario__plano">Plano Pessoal</div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    """Desenha a sidebar e devolve a chave da pagina selecionada."""
    usuario = auth_service.usuario_logado()
    pagina_atual = st.session_state.get(auth_service.CHAVE_PAGINA, "dashboard")

    with st.sidebar:
        _marca()
        st.markdown('<p class="ff-menu-titulo">Menu</p>', unsafe_allow_html=True)

        for chave, rotulo, icone in ITENS_MENU:
            selecionado = chave == pagina_atual
            if st.button(
                rotulo,
                key=f"menu_{chave}",
                icon=icone,
                use_container_width=True,
                type="primary" if selecionado else "secondary",
            ):
                st.session_state[auth_service.CHAVE_PAGINA] = chave
                st.rerun()

        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        _rodape_usuario(usuario["nome"])

        if st.button(
            "Sair",
            key="menu_sair",
            icon=":material/logout:",
            use_container_width=True,
        ):
            auth_service.encerrar_sessao()
            st.rerun()

    return st.session_state.get(auth_service.CHAVE_PAGINA, "dashboard")
