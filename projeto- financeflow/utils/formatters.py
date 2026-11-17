"""Formatação de valores para exibição (padrão pt-BR, sem depender de locale)."""

from __future__ import annotations

from datetime import date, datetime

MESES_ABREVIADOS: tuple[str, ...] = (
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez",
)

MESES_EXTENSO: tuple[str, ...] = (
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
)

DIAS_SEMANA: tuple[str, ...] = (
    "Segunda-feira", "Terça-feira", "Quarta-feira",
    "Quinta-feira", "Sexta-feira", "Sábado", "Domingo",
)


def formatar_numero(valor: float, casas: int = 2) -> str:
    """Formata um número no padrão brasileiro: 1.234,56."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", " ").replace(".", ",").replace(" ", ".")


def formatar_moeda(valor: float, simbolo: str = "R$", com_sinal: bool = False) -> str:
    """Formata um valor monetário: R$ 1.234,56."""
    sinal = ""
    if com_sinal:
        sinal = "+ " if valor >= 0 else "- "
    return f"{sinal}{simbolo} {formatar_numero(abs(valor))}"


def formatar_percentual(valor: float, casas: int = 0) -> str:
    """Formata um percentual já calculado: 12% ou -4%."""
    sinal = "+" if valor > 0 else ""
    return f"{sinal}{formatar_numero(valor, casas)}%"


def formatar_data(valor: date | datetime | None) -> str:
    """Formata uma data como 05/10/2026."""
    if valor is None:
        return "-"
    return valor.strftime("%d/%m/%Y")


def formatar_data_extenso(valor: date | None = None) -> str:
    """Formata uma data como 'Domingo, 11 de outubro'."""
    referencia = valor or date.today()
    dia_semana = DIAS_SEMANA[referencia.weekday()]
    mes = MESES_EXTENSO[referencia.month - 1]
    return f"{dia_semana}, {referencia.day} de {mes}"


def formatar_mes_ano(valor: date) -> str:
    """Formata um mês como 'Out/26'."""
    return f"{MESES_ABREVIADOS[valor.month - 1]}/{valor.strftime('%y')}"


def primeiro_nome(nome: str) -> str:
    """Devolve apenas o primeiro nome da pessoa."""
    return nome.strip().split(" ")[0] if nome.strip() else "Visitante"


def iniciais(nome: str) -> str:
    """Devolve até duas iniciais do nome (usado no avatar)."""
    partes = [parte for parte in nome.strip().split(" ") if parte]
    if not partes:
        return "?"
    if len(partes) == 1:
        return partes[0][:2].upper()
    return (partes[0][0] + partes[-1][0]).upper()
