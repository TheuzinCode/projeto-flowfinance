"""Conjunto de icones SVG em linha usados na interface.

Todos seguem o mesmo padrao visual (traco de 1.8, cantos arredondados,
grade de 24x24) e herdam a cor do elemento pai via `currentColor`,
funcionando nos temas claro e escuro sem nenhuma troca de arquivo.
"""

from __future__ import annotations

# Cada entrada guarda apenas o miolo do SVG; o invólucro é montado em `icone`.
ICONES: dict[str, str] = {
    # --- Indicadores do dashboard ---------------------------------------- #
    "carteira": (
        '<rect x="2.5" y="5.5" width="19" height="14" rx="3"/>'
        '<path d="M2.5 10h19"/><circle cx="17" cy="15" r="1.3"/>'
    ),
    "tendencia-alta": (
        '<polyline points="3 16.5 9.5 10 13.5 14 21 6.5"/>'
        '<polyline points="15.5 6.5 21 6.5 21 12"/>'
    ),
    "tendencia-baixa": (
        '<polyline points="3 7.5 9.5 14 13.5 10 21 17.5"/>'
        '<polyline points="15.5 17.5 21 17.5 21 12"/>'
    ),
    "cofre": (
        '<path d="M3 9.5 12 4l9 5.5"/><path d="M3 20h18"/>'
        '<path d="M5.5 9.8V20"/><path d="M9.8 9.8V20"/>'
        '<path d="M14.2 9.8V20"/><path d="M18.5 9.8V20"/>'
    ),
    # --- Apoio ------------------------------------------------------------ #
    "calendario": (
        '<rect x="3" y="5" width="18" height="16" rx="3"/>'
        '<path d="M8 3v4M16 3v4M3 10h18"/>'
    ),
    "lampada": (
        '<path d="M12 3a6 6 0 0 0-3.5 10.9V16h7v-2.1A6 6 0 0 0 12 3z"/>'
        '<path d="M9.5 19h5"/><path d="M10.5 21.5h3"/>'
    ),
    "banco-dados": (
        '<ellipse cx="12" cy="6" rx="8" ry="3.2"/>'
        '<path d="M4 6v6c0 1.8 3.6 3.2 8 3.2s8-1.4 8-3.2V6"/>'
        '<path d="M4 12v6c0 1.8 3.6 3.2 8 3.2s8-1.4 8-3.2v-6"/>'
    ),
    "seta-cima": '<path d="M12 19.5V4.5"/><polyline points="5.8 10.7 12 4.5 18.2 10.7"/>',
    "seta-baixo": '<path d="M12 4.5v15"/><polyline points="5.8 13.3 12 19.5 18.2 13.3"/>',
    # --- Categorias -------------------------------------------------------- #
    "casa": (
        '<path d="M3.5 10.5 12 4l8.5 6.5"/><path d="M5.5 9.8V20h13V9.8"/>'
        '<path d="M9.8 20v-5.2h4.4V20"/>'
    ),
    "talheres": (
        '<path d="M5 3v5a2 2 0 0 0 4 0V3"/><path d="M7 10v11"/>'
        '<path d="M16.8 3c-1.5 1.7-2.3 3.5-2.3 5.6 0 1.7.8 2.8 2.3 3.4V21"/>'
    ),
    "carro": (
        '<path d="M4 14l1.8-5A2 2 0 0 1 7.7 7.6h8.6a2 2 0 0 1 1.9 1.4L20 14"/>'
        '<rect x="3" y="14" width="18" height="5" rx="1.5"/>'
        '<path d="M6.5 19v1.5M17.5 19v1.5"/>'
    ),
    "filme": (
        '<rect x="2.5" y="5" width="19" height="14" rx="2.5"/>'
        '<path d="M7 5v14M17 5v14M2.5 12h19"/>'
    ),
    "pulso": '<path d="M3 12h4l2.2-5.5 4 12L15.5 12H21"/>',
    "formatura": (
        '<path d="M2.5 9 12 4.5 21.5 9 12 13.5z"/>'
        '<path d="M6.5 11.2V16c0 1.4 2.5 2.5 5.5 2.5s5.5-1.1 5.5-2.5v-4.8"/>'
    ),
    "tv": (
        '<rect x="2.5" y="7" width="19" height="13" rx="2.5"/>'
        '<path d="M8 3.5 12 7l4-3.5"/>'
    ),
    "caixa": (
        '<path d="M21 8.5 12 3.5 3 8.5v7l9 5 9-5z"/>'
        '<path d="M3 8.5 12 13.5l9-5"/><path d="M12 13.5v7"/>'
    ),
    "maleta": (
        '<rect x="2.5" y="7" width="19" height="13" rx="2.5"/>'
        '<path d="M8.5 7V5.5A1.5 1.5 0 0 1 10 4h4a1.5 1.5 0 0 1 1.5 1.5V7"/>'
        '<path d="M2.5 12.5h19"/>'
    ),
    "presente": (
        '<rect x="3" y="8.5" width="18" height="4" rx="1"/>'
        '<path d="M4.5 12.5V20h15v-7.5"/><path d="M12 8.5V20"/>'
        '<path d="M12 8.5S10.6 4 8.4 4a2.2 2.2 0 0 0 0 4.5z"/>'
        '<path d="M12 8.5S13.4 4 15.6 4a2.2 2.2 0 0 1 0 4.5z"/>'
    ),
    "grafico": (
        '<path d="M4 4v16h16"/><polyline points="7.5 15 11 11 14 13.5 19.5 7.5"/>'
    ),
    "etiqueta": (
        '<path d="M3 3.5h7.5L21 14l-7.5 7.5L3 11z"/><circle cx="7.5" cy="8" r="1.3"/>'
    ),
    "retorno": (
        '<path d="M4 10h11a5 5 0 0 1 0 10H8"/><polyline points="8 6 4 10 8 14"/>'
    ),
}

PADRAO = "caixa"


def icone(nome: str, tamanho: int = 18, traco: float = 1.8) -> str:
    """Devolve o SVG do icone em uma unica linha, pronto para o `st.markdown`."""
    corpo = ICONES.get(nome, ICONES[PADRAO])
    return (
        '<svg class="ff-icone" xmlns="http://www.w3.org/2000/svg" '
        f'width="{tamanho}" height="{tamanho}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="{traco}" stroke-linecap="round" '
        f'stroke-linejoin="round">{corpo}</svg>'
    )
