"""Validações de entrada com mensagens de erro amigáveis."""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from config.settings import (
    CATEGORIAS_DESPESA,
    CATEGORIAS_RECEITA,
    FORMAS_PAGAMENTO,
    TAMANHO_MINIMO_SENHA,
    TIPO_RECEITA,
    TIPOS,
)

PADRAO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")


class ErroDeValidacao(Exception):
    """Erro de regra de entrada, exibido diretamente para o usuário."""


def validar_nome(nome: str) -> str:
    """Valida e normaliza o nome informado."""
    nome = (nome or "").strip()
    if len(nome) < 3:
        raise ErroDeValidacao("Informe um nome com pelo menos 3 caracteres.")
    return nome


def validar_email(email: str) -> str:
    """Valida e normaliza o e-mail informado."""
    email = (email or "").strip().lower()
    if not PADRAO_EMAIL.match(email):
        raise ErroDeValidacao("Informe um e-mail válido, por exemplo: nome@email.com.")
    return email


def validar_senha(senha: str, confirmacao: str | None = None) -> str:
    """Valida a senha e, quando informada, a confirmação."""
    senha = senha or ""
    if len(senha) < TAMANHO_MINIMO_SENHA:
        raise ErroDeValidacao(
            f"A senha precisa ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres."
        )
    if confirmacao is not None and senha != confirmacao:
        raise ErroDeValidacao("As senhas informadas não são iguais.")
    return senha


def categorias_do_tipo(tipo: str) -> tuple[str, ...]:
    """Devolve as categorias válidas para um tipo de movimentação."""
    return CATEGORIAS_RECEITA if tipo == TIPO_RECEITA else CATEGORIAS_DESPESA


def validar_movimentacao(dados: dict[str, Any]) -> dict[str, Any]:
    """Valida os dados do formulário de movimentação e devolve-os normalizados."""
    tipo = dados.get("tipo")
    if tipo not in TIPOS:
        raise ErroDeValidacao("Selecione um tipo válido: Receita ou Despesa.")

    categoria = (dados.get("categoria") or "").strip()
    if categoria not in categorias_do_tipo(tipo):
        raise ErroDeValidacao("Selecione uma categoria válida para esse tipo.")

    descricao = (dados.get("descricao") or "").strip()
    if len(descricao) < 3:
        raise ErroDeValidacao("A descrição precisa ter pelo menos 3 caracteres.")

    try:
        valor = float(dados.get("valor") or 0)
    except (TypeError, ValueError) as erro:
        raise ErroDeValidacao("Informe um valor numérico válido.") from erro
    if valor <= 0:
        raise ErroDeValidacao("O valor precisa ser maior que zero.")

    data_movimentacao = dados.get("data")
    if not isinstance(data_movimentacao, date):
        raise ErroDeValidacao("Informe uma data válida.")

    forma_pagamento = (dados.get("forma_pagamento") or "").strip()
    if forma_pagamento not in FORMAS_PAGAMENTO:
        raise ErroDeValidacao("Selecione uma forma de pagamento válida.")

    return {
        "tipo": tipo,
        "categoria": categoria,
        "descricao": descricao,
        "valor": round(valor, 2),
        "data": data_movimentacao,
        "forma_pagamento": forma_pagamento,
        "observacao": (dados.get("observacao") or "").strip() or None,
    }
