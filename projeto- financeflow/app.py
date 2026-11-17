"""FinanceFlow - ponto de entrada da aplicacao Streamlit.

Responsabilidades deste arquivo: configurar a pagina, inicializar o banco,
aplicar o tema e decidir qual tela renderizar. Nenhuma regra de negocio
mora aqui.
"""

from __future__ import annotations

from typing import Callable

import streamlit as st

from components.estilos import aplicar_estilos
from components.sidebar import render_sidebar
from config.database import inicializar_banco
from config.settings import APP_ICONE, APP_NOME
from pages import configuracoes, dashboard, login, movimentacoes
from services import auth_service

TELAS: dict[str, tuple[str, Callable[[], None]]] = {
    "dashboard": ("Dashboard", dashboard.render),
    "movimentacoes": ("Movimentações", movimentacoes.render),
    "configuracoes": ("Configurações", configuracoes.render),
}


@st.cache_resource(show_spinner=False)
def _preparar_banco() -> bool:
    """Cria o schema uma unica vez por processo."""
    inicializar_banco()
    return True


def _executar(tela: Callable[[], None], titulo: str, rota: str) -> None:
    """Executa a tela escolhida.

    Usamos st.navigation com a navegacao oculta para manter o menu lateral
    customizado e desativar a navegacao automatica da pasta `pages/`.
    """
    pagina = st.Page(tela, title=f"{titulo} | {APP_NOME}", url_path=rota, default=True)
    try:
        st.navigation([pagina], position="hidden").run()
    except TypeError:  # compatibilidade com versoes antigas do Streamlit
        tela()


def main() -> None:
    """Fluxo principal da aplicacao."""
    st.set_page_config(
        page_title=APP_NOME,
        page_icon=APP_ICONE,
        layout="wide",
        initial_sidebar_state="auto",
    )

    _preparar_banco()
    auth_service.inicializar_sessao()
    aplicar_estilos(auth_service.tema_atual())

    if not auth_service.esta_autenticado():
        _executar(login.render, "Entrar", "login")
        return

    rota = render_sidebar()
    titulo, tela = TELAS.get(rota, TELAS["dashboard"])
    _executar(tela, titulo, rota)


if __name__ == "__main__":
    main()
