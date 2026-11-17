"""Acesso a dados de usuários. Nenhuma regra de negócio mora aqui."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select

from config.database import obter_sessao
from models import Usuario


class UsuarioRepository:
    """Operações de persistência da entidade Usuario."""

    def criar(self, nome: str, email: str, senha_hash: str) -> Usuario:
        """Insere um novo usuário e devolve o registro criado."""
        usuario = Usuario(nome=nome, email=email, senha=senha_hash)
        with obter_sessao() as sessao:
            sessao.add(usuario)
            sessao.flush()
        return usuario

    def buscar_por_email(self, email: str) -> Usuario | None:
        """Busca um usuário pelo e-mail (case-insensitive)."""
        with obter_sessao() as sessao:
            comando = select(Usuario).where(Usuario.email == email.strip().lower())
            return sessao.scalars(comando).first()

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        """Busca um usuário pelo identificador."""
        with obter_sessao() as sessao:
            return sessao.get(Usuario, usuario_id)

    def email_em_uso(self, email: str, ignorar_id: int | None = None) -> bool:
        """Informa se o e-mail já pertence a outro usuário."""
        with obter_sessao() as sessao:
            comando = select(Usuario.id).where(Usuario.email == email.strip().lower())
            if ignorar_id is not None:
                comando = comando.where(Usuario.id != ignorar_id)
            return sessao.scalars(comando).first() is not None

    def atualizar(self, usuario_id: int, **campos: Any) -> Usuario | None:
        """Atualiza os campos informados e devolve o usuário atualizado."""
        with obter_sessao() as sessao:
            usuario = sessao.get(Usuario, usuario_id)
            if usuario is None:
                return None
            for campo, valor in campos.items():
                if hasattr(usuario, campo):
                    setattr(usuario, campo, valor)
            sessao.flush()
            return usuario

    def excluir(self, usuario_id: int) -> bool:
        """Remove o usuário e todas as suas movimentações."""
        with obter_sessao() as sessao:
            usuario = sessao.get(Usuario, usuario_id)
            if usuario is None:
                return False
            sessao.delete(usuario)
            return True
