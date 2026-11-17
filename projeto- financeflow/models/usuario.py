"""Modelo de usuário."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base
from config.settings import TEMA_CLARO

if TYPE_CHECKING:  # pragma: no cover - apenas para type hints
    from models.movimentacao import Movimentacao


class Usuario(Base):
    """Representa uma pessoa que acessa o sistema."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(
        String(180), nullable=False, unique=True, index=True
    )
    senha: Mapped[str] = mapped_column(String(255), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    # Preferências de interface (telas de Configurações).
    tema: Mapped[str] = mapped_column(String(20), nullable=False, default=TEMA_CLARO)
    moeda: Mapped[str] = mapped_column(String(10), nullable=False, default="R$")
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)

    movimentacoes: Mapped[list["Movimentacao"]] = relationship(
        back_populates="usuario",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def para_dict(self) -> dict[str, Any]:
        """Converte o usuário em dicionário (usado na sessão do Streamlit)."""
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "tema": self.tema,
            "moeda": self.moeda,
            "telefone": self.telefone or "",
            "criado_em": self.criado_em,
        }

    def __repr__(self) -> str:  # pragma: no cover - auxílio em debug
        return f"<Usuario id={self.id} email={self.email!r}>"
