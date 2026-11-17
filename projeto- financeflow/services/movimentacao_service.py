"""Regras de negócio das movimentações, com Pandas no tratamento dos dados."""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from config.settings import TIPO_RECEITA
from models import Movimentacao
from repositories.movimentacao_repository import MovimentacaoRepository
from utils.validations import ErroDeValidacao, validar_movimentacao

COLUNAS = [
    "id",
    "tipo",
    "categoria",
    "descricao",
    "valor",
    "data",
    "forma_pagamento",
    "observacao",
    "criado_em",
]

_repositorio = MovimentacaoRepository()


# --------------------------------------------------------------------------- #
# Leitura
# --------------------------------------------------------------------------- #
def carregar_dataframe(usuario_id: int) -> pd.DataFrame:
    """Carrega as movimentações do usuário em um DataFrame tipado."""
    registros = [m.para_dict() for m in _repositorio.listar_por_usuario(usuario_id)]
    df = pd.DataFrame(registros, columns=COLUNAS)

    if df.empty:
        df["data"] = pd.to_datetime(df["data"])
        df["valor"] = df["valor"].astype(float)
        df["valor_com_sinal"] = df["valor"]
        df["status"] = df["tipo"]
        df["mes"] = df["data"]
        return df

    df["data"] = pd.to_datetime(df["data"])
    df["valor"] = df["valor"].astype(float)
    df["valor_com_sinal"] = df["valor"].where(df["tipo"] == TIPO_RECEITA, -df["valor"])
    hoje = pd.Timestamp(date.today())
    df["status"] = pd.Series(
        ["Pendente" if d > hoje else "Concluído" for d in df["data"]], index=df.index
    )
    df["mes"] = df["data"].dt.to_period("M").dt.to_timestamp()
    return df.sort_values(["data", "id"], ascending=False).reset_index(drop=True)


def buscar(movimentacao_id: int, usuario_id: int) -> Movimentacao:
    """Busca uma movimentação específica do usuário."""
    movimentacao = _repositorio.buscar_por_id(movimentacao_id, usuario_id)
    if movimentacao is None:
        raise ErroDeValidacao("Movimentação não encontrada.")
    return movimentacao


# --------------------------------------------------------------------------- #
# Filtros (tela de Movimentações)
# --------------------------------------------------------------------------- #
PERIODOS: tuple[str, ...] = (
    "Todos os períodos",
    "Este mês",
    "Mês passado",
    "Últimos 3 meses",
    "Este ano",
)


def aplicar_filtros(
    df: pd.DataFrame,
    texto: str = "",
    periodo: str = "Todos os períodos",
    categoria: str = "Todas as categorias",
    tipo: str = "Todos",
) -> pd.DataFrame:
    """Aplica os filtros da tela de movimentações sobre o DataFrame."""
    if df.empty:
        return df

    filtrado = df.copy()

    if texto.strip():
        busca = texto.strip().lower()
        colunas_busca = ["descricao", "categoria", "forma_pagamento", "observacao"]
        mascara = pd.Series(False, index=filtrado.index)
        for coluna in colunas_busca:
            mascara |= (
                filtrado[coluna]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(busca, regex=False)
            )
        filtrado = filtrado[mascara]

    filtrado = _filtrar_por_periodo(filtrado, periodo)

    if categoria != "Todas as categorias":
        filtrado = filtrado[filtrado["categoria"] == categoria]

    if tipo != "Todos":
        filtrado = filtrado[filtrado["tipo"] == tipo]

    return filtrado.reset_index(drop=True)


def _filtrar_por_periodo(df: pd.DataFrame, periodo: str) -> pd.DataFrame:
    """Recorta o DataFrame conforme o período escolhido."""
    if periodo == "Todos os períodos" or df.empty:
        return df

    hoje = pd.Timestamp(date.today())
    inicio_mes = hoje.replace(day=1).normalize()

    if periodo == "Este mês":
        return df[df["mes"] == inicio_mes]
    if periodo == "Mês passado":
        mes_passado = (inicio_mes - pd.offsets.MonthBegin(1)).normalize()
        return df[df["mes"] == mes_passado]
    if periodo == "Últimos 3 meses":
        limite = (inicio_mes - pd.offsets.MonthBegin(2)).normalize()
        return df[df["mes"] >= limite]
    if periodo == "Este ano":
        return df[df["data"].dt.year == hoje.year]
    return df


def categorias_do_dataframe(df: pd.DataFrame) -> list[str]:
    """Lista as categorias presentes nos dados, em ordem alfabética."""
    if df.empty:
        return []
    return sorted(df["categoria"].dropna().unique().tolist())


# --------------------------------------------------------------------------- #
# Escrita
# --------------------------------------------------------------------------- #
def criar(usuario_id: int, dados: dict[str, Any]) -> Movimentacao:
    """Cria uma movimentação após validar os dados."""
    return _repositorio.criar(usuario_id, validar_movimentacao(dados))


def atualizar(
    movimentacao_id: int, usuario_id: int, dados: dict[str, Any]
) -> Movimentacao:
    """Atualiza uma movimentação após validar os dados."""
    atualizada = _repositorio.atualizar(
        movimentacao_id, usuario_id, validar_movimentacao(dados)
    )
    if atualizada is None:
        raise ErroDeValidacao("Movimentação não encontrada.")
    return atualizada


def excluir(movimentacao_id: int, usuario_id: int) -> None:
    """Exclui uma movimentação do usuário."""
    if not _repositorio.excluir(movimentacao_id, usuario_id):
        raise ErroDeValidacao("Movimentação não encontrada.")


# --------------------------------------------------------------------------- #
# Exportação
# --------------------------------------------------------------------------- #
def exportar_csv(df: pd.DataFrame) -> bytes:
    """Gera o CSV das movimentações para download."""
    colunas = [
        "data",
        "tipo",
        "categoria",
        "descricao",
        "valor",
        "forma_pagamento",
        "observacao",
    ]
    if df.empty:
        return pd.DataFrame(columns=colunas).to_csv(index=False).encode("utf-8-sig")

    exportavel = df[colunas].copy()
    exportavel["data"] = exportavel["data"].dt.strftime("%d/%m/%Y")
    return exportavel.to_csv(index=False, sep=";").encode("utf-8-sig")
