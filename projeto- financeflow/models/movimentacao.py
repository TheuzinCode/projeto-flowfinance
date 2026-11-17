"""Modelo de movimentação financeira (receitas e despesas)."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base
from config.settings import TIPO_RECEITA

if TYPE_CHECKING:  # pragma: no cover - apenas para type hints
    from models.usuario import Usuario


class Movimentacao(Base):
    """Uma entrada (receita) ou saída (despesa) de dinheiro."""

    __tablename__ = "movimentacoes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    categoria: Mapped[str] = mapped_column(String(60), nullable=False)
    descricao: Mapped[str] = mapped_column(String(180), nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    forma_pagamento: Mapped[str] = mapped_column(String(40), nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="movimentacoes")

    @property
    def e_receita(self) -> bool:
        """Indica se a movimentação é uma receita."""
        return self.tipo == TIPO_RECEITA

    @property
    def valor_com_sinal(self) -> float:
        """Valor positivo para receitas e negativo para despesas."""
        return self.valor if self.e_receita else -self.valor

    @property
    def status(self) -> str:
        """Movimentações com data futura são consideradas pendentes."""
        return "Pendente" if self.data > date.today() else "Concluído"

    def para_dict(self) -> dict[str, Any]:
        """Converte a movimentação em dicionário (base dos DataFrames)."""
        return {
            "id": self.id,
            "tipo": self.tipo,
            "categoria": self.categoria,
            "descricao": self.descricao,
            "valor": float(self.valor),
            "data": self.data,
            "forma_pagamento": self.forma_pagamento,
            "observacao": self.observacao or "",
            "criado_em": self.criado_em,
        }

    def __repr__(self) -> str:  # pragma: no cover - auxílio em debug
        return f"<Movimentacao id={self.id} {self.tipo} {self.valor}>"
