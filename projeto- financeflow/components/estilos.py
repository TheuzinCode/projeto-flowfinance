"""Tema visual da aplicacao: paletas, variaveis CSS e injecao da folha de estilo."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import streamlit as st

from config.settings import ARQUIVO_CSS, ARQUIVO_LOGO, TEMA_ESCURO

PALETA_CLARA: dict[str, str] = {
    "fundo": "#F6F8FB",
    "superficie": "#FFFFFF",
    "superficie-2": "#F1F5F9",
    "borda": "#E6EBF2",
    "texto": "#0F172A",
    "texto-suave": "#64748B",
    "primaria": "#2563EB",
    "primaria-suave": "#EAF1FE",
    "verde": "#16A34A",
    "verde-suave": "#E7F7EE",
    "vermelho": "#DC2626",
    "vermelho-suave": "#FDECEC",
    "alerta": "#B45309",
    "alerta-suave": "#FEF3C7",
    "sombra": "0 1px 2px rgba(16,24,40,0.04), 0 8px 24px rgba(16,24,40,0.05)",
}

PALETA_ESCURA: dict[str, str] = {
    "fundo": "#0B1120",
    "superficie": "#111A2E",
    "superficie-2": "#17223A",
    "borda": "#243149",
    "texto": "#E8EDF7",
    "texto-suave": "#94A3B8",
    "primaria": "#3B82F6",
    "primaria-suave": "#1B2B4D",
    "verde": "#34D399",
    "verde-suave": "#12302A",
    "vermelho": "#F87171",
    "vermelho-suave": "#3A1A1E",
    "alerta": "#FBBF24",
    "alerta-suave": "#3A2F11",
    "sombra": "0 1px 2px rgba(0,0,0,0.25), 0 10px 28px rgba(0,0,0,0.30)",
}


def sem_indentacao(marcacao: str) -> str:
    """Remove a indentacao do HTML antes de enviar ao Streamlit.

    Sem isso, o Markdown interpreta linhas recuadas como bloco de codigo
    e o HTML aparece na tela como texto.
    """
    return " ".join(linha.strip() for linha in marcacao.strip().splitlines())


def paleta(tema: str) -> dict[str, str]:
    """Devolve a paleta de cores do tema selecionado."""
    return PALETA_ESCURA if tema == TEMA_ESCURO else PALETA_CLARA


def _folha_de_estilo() -> str:
    """Le o arquivo CSS (sem cache, para permitir ajustes com o app no ar)."""
    try:
        return ARQUIVO_CSS.read_text(encoding="utf-8")
    except OSError:
        return ""


@lru_cache(maxsize=1)
def logo_svg() -> str:
    """Le o SVG do logo em uma unica linha (com fallback se o arquivo sumir)."""
    try:
        return sem_indentacao(ARQUIVO_LOGO.read_text(encoding="utf-8"))
    except OSError:
        return "<span>FF</span>"


def _variaveis_css(tema: str) -> str:
    """Monta o bloco :root com as variaveis do tema."""
    linhas = [f"    --ff-{nome}: {valor};" for nome, valor in paleta(tema).items()]
    return ":root {\n" + "\n".join(linhas) + "\n}"


def aplicar_estilos(tema: str) -> None:
    """Injeta as variaveis do tema e a folha de estilo na pagina."""
    css = f"<style>\n{_variaveis_css(tema)}\n{_folha_de_estilo()}\n</style>"
    st.markdown(css, unsafe_allow_html=True)


def cores_grafico(tema: str) -> dict[str, Any]:
    """Configuracao de cores usada pelos graficos Plotly."""
    cores = paleta(tema)
    return {
        "template": "plotly_dark" if tema == TEMA_ESCURO else "plotly_white",
        "texto": cores["texto-suave"],
        "grade": cores["borda"],
        "receita": cores["verde"],
        "despesa": cores["vermelho"],
        "saldo": cores["primaria"],
        "sequencia": [
            cores["primaria"],
            "#22C55E",
            "#F59E0B",
            "#06B6D4",
            "#EF4444",
            "#14B8A6",
            "#94A3B8",
            "#A855F7",
        ],
    }
