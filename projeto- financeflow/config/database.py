"""Criação da engine, da sessão e do schema do banco.

A troca SQLite -> PostgreSQL acontece apenas pela variável DATABASE_URL.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config.settings import DATABASE_URL


class Base(DeclarativeBase):
    """Classe base de todos os modelos ORM."""


def _criar_engine() -> Engine:
    """Cria a engine aplicando os ajustes necessários para cada banco."""
    parametros: dict[str, Any] = {"echo": False, "future": True}
    if DATABASE_URL.startswith("sqlite"):
        # Necessário porque o Streamlit executa o script em threads distintas.
        parametros["connect_args"] = {"check_same_thread": False}
    else:
        parametros["pool_pre_ping"] = True
    return create_engine(DATABASE_URL, **parametros)


engine: Engine = _criar_engine()

# expire_on_commit=False permite usar os objetos depois que a sessão fecha.
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)


@contextmanager
def obter_sessao() -> Iterator[Session]:
    """Abre uma sessão transacional com commit/rollback automáticos."""
    sessao = SessionLocal()
    try:
        yield sessao
        sessao.commit()
    except Exception:
        sessao.rollback()
        raise
    finally:
        sessao.close()


def inicializar_banco() -> None:
    """Cria as tabelas caso ainda não existam."""
    import models  # noqa: F401  (registra as entidades no metadata)

    Base.metadata.create_all(bind=engine)
