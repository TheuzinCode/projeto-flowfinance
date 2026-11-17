"""Acesso a dados de movimentações financeiras."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select

from config.database import obter_sessao
from models import Movimentacao


class MovimentacaoRepository:
    """Operações de persistência da entidade Movimentacao."""

    def listar_por_usuario(self, usuario_id: int) -> list[Movimentacao]:
        """Lista todas as movimentações do usuário, da mais recente à mais antiga."""
        with obter_sessao() as sessao:
            comando = (
                select(Movimentacao)
                .where(Movimentacao.usuario_id == usuario_id)
                .order_by(Movimentacao.data.desc(), Movimentacao.id.desc())
            )
            return list(sessao.scalars(comando).all())

    def buscar_por_id(
        self, movimentacao_id: int, usuario_id: int
    ) -> Movimentacao | None:
        """Busca uma movimentação garantindo que ela pertence ao usuário."""
        with obter_sessao() as sessao:
            comando = select(Movimentacao).where(
                Movimentacao.id == movimentacao_id,
                Movimentacao.usuario_id == usuario_id,
            )
            return sessao.scalars(comando).first()

    def criar(self, usuario_id: int, dados: dict[str, Any]) -> Movimentacao:
        """Insere uma nova movimentação."""
        movimentacao = Movimentacao(usuario_id=usuario_id, **dados)
        with obter_sessao() as sessao:
            sessao.add(movimentacao)
            sessao.flush()
        return movimentacao

    def atualizar(
        self, movimentacao_id: int, usuario_id: int, dados: dict[str, Any]
    ) -> Movimentacao | None:
        """Atualiza uma movimentação existente do usuário."""
        with obter_sessao() as sessao:
            movimentacao = sessao.get(Movimentacao, movimentacao_id)
            if movimentacao is None or movimentacao.usuario_id != usuario_id:
                return None
            for campo, valor in dados.items():
                setattr(movimentacao, campo, valor)
            sessao.flush()
            return movimentacao

    def excluir(self, movimentacao_id: int, usuario_id: int) -> bool:
        """Remove uma movimentação do usuário."""
        with obter_sessao() as sessao:
            movimentacao = sessao.get(Movimentacao, movimentacao_id)
            if movimentacao is None or movimentacao.usuario_id != usuario_id:
                return False
            sessao.delete(movimentacao)
            return True

    def contar(self, usuario_id: int) -> int:
        """Conta quantas movimentações o usuário possui."""
        with obter_sessao() as sessao:
            comando = select(Movimentacao.id).where(
                Movimentacao.usuario_id == usuario_id
            )
            return len(list(sessao.scalars(comando).all()))
