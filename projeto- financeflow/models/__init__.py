"""Modelos ORM.

Importar o pacote registra todas as entidades no mapeador do SQLAlchemy.
Sem isso, usar apenas um dos modelos faria o relacionamento entre eles falhar.
"""

from models.movimentacao import Movimentacao
from models.usuario import Usuario

__all__ = ["Movimentacao", "Usuario"]
