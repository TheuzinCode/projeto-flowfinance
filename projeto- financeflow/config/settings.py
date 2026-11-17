"""Configurações centrais do FinanceFlow.

Tudo que varia entre ambientes (banco, nome da aplicação, opções de domínio)
fica concentrado aqui para evitar valores mágicos espalhados pelo código.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR: Path = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# --------------------------------------------------------------------------- #
# Aplicação
# --------------------------------------------------------------------------- #
APP_NOME: str = "FinanceFlow"
APP_DESCRICAO: str = "Bem-vindo ao seu painel financeiro."
APP_ICONE: str = ":material/account_balance_wallet:"
ARQUIVO_LOGO: Path = BASE_DIR / "assets" / "logo.svg"
ARQUIVO_CSS: Path = BASE_DIR / "assets" / "styles.css"

# --------------------------------------------------------------------------- #
# Banco de dados
# --------------------------------------------------------------------------- #
# Em desenvolvimento usamos SQLite. Para produção basta definir DATABASE_URL
# no .env apontando para o PostgreSQL. Nenhuma outra linha precisa mudar.
DATABASE_URL: str = os.getenv(
    "DATABASE_URL", f"sqlite:///{BASE_DIR / 'financeflow.db'}"
)


def nome_do_banco() -> str:
    """Devolve o nome amigável do banco em uso (exibido em Configurações)."""
    if DATABASE_URL.startswith("sqlite"):
        return "SQLite (desenvolvimento)"
    if DATABASE_URL.startswith(("postgresql", "postgres")):
        return "PostgreSQL (produção)"
    return "Banco personalizado"


def resumo_conexao() -> str:
    """Devolve a string de conexão sem expor usuário e senha."""
    if "@" in DATABASE_URL:
        inicio, fim = DATABASE_URL.split("@", 1)
        protocolo = inicio.split("://", 1)[0]
        return f"{protocolo}://***@{fim}"
    return DATABASE_URL


# --------------------------------------------------------------------------- #
# Domínio
# --------------------------------------------------------------------------- #
TIPO_RECEITA: str = "Receita"
TIPO_DESPESA: str = "Despesa"
TIPOS: tuple[str, ...] = (TIPO_RECEITA, TIPO_DESPESA)

CATEGORIAS_RECEITA: tuple[str, ...] = (
    "Salário",
    "Extra",
    "Investimentos",
    "Vendas",
    "Reembolso",
    "Outros",
)

CATEGORIAS_DESPESA: tuple[str, ...] = (
    "Moradia",
    "Alimentação",
    "Transporte",
    "Lazer",
    "Saúde",
    "Educação",
    "Assinaturas",
    "Outros",
)

FORMAS_PAGAMENTO: tuple[str, ...] = (
    "Pix",
    "Dinheiro",
    "Cartão de crédito",
    "Cartão de débito",
    "Transferência",
    "Débito automático",
    "Boleto",
)

# Nome do icone (components/icones.py) usado por cada categoria.
ICONES_CATEGORIA: dict[str, str] = {
    "Salário": "maleta",
    "Extra": "presente",
    "Investimentos": "grafico",
    "Vendas": "etiqueta",
    "Reembolso": "retorno",
    "Moradia": "casa",
    "Alimentação": "talheres",
    "Transporte": "carro",
    "Lazer": "filme",
    "Saúde": "pulso",
    "Educação": "formatura",
    "Assinaturas": "tv",
    "Outros": "caixa",
}

MOEDAS: dict[str, str] = {
    "Real (R$)": "R$",
    "Dólar (US$)": "US$",
    "Euro (€)": "€",
}

IDIOMAS: tuple[str, ...] = ("Português (Brasil)",)

TEMA_CLARO: str = "Claro"
TEMA_ESCURO: str = "Escuro"
TEMAS: tuple[str, ...] = (TEMA_CLARO, TEMA_ESCURO)

# Regras simples de validação
TAMANHO_MINIMO_SENHA: int = 6
MESES_GRAFICO_EVOLUCAO: int = 6
QTD_ULTIMAS_MOVIMENTACOES: int = 5
