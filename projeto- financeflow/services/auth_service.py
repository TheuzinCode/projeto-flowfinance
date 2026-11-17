"""Regras de autenticação: cadastro, login, logout e sessão."""

from __future__ import annotations

from typing import Any

import bcrypt
import streamlit as st

from config.settings import TEMA_CLARO
from models import Usuario
from repositories.usuario_repository import UsuarioRepository
from utils.validations import (
    ErroDeValidacao,
    validar_email,
    validar_nome,
    validar_senha,
)

CHAVE_USUARIO = "usuario"
CHAVE_PAGINA = "pagina"

_repositorio = UsuarioRepository()


# --------------------------------------------------------------------------- #
# Senhas
# --------------------------------------------------------------------------- #
def gerar_hash(senha: str) -> str:
    """Gera o hash bcrypt de uma senha."""
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def senha_confere(senha: str, senha_hash: str) -> bool:
    """Compara a senha digitada com o hash armazenado."""
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
    except ValueError:
        return False


# --------------------------------------------------------------------------- #
# Cadastro e login
# --------------------------------------------------------------------------- #
def registrar(nome: str, email: str, senha: str, confirmacao: str) -> Usuario:
    """Cadastra um novo usuário validando os dados informados."""
    nome = validar_nome(nome)
    email = validar_email(email)
    senha = validar_senha(senha, confirmacao)

    if _repositorio.email_em_uso(email):
        raise ErroDeValidacao("Este e-mail já está cadastrado. Faça login.")

    return _repositorio.criar(nome=nome, email=email, senha_hash=gerar_hash(senha))


def autenticar(email: str, senha: str) -> Usuario:
    """Valida as credenciais e devolve o usuário autenticado."""
    if not email or not senha:
        raise ErroDeValidacao("Informe e-mail e senha para entrar.")

    usuario = _repositorio.buscar_por_email(email)
    if usuario is None or not senha_confere(senha, usuario.senha):
        raise ErroDeValidacao("E-mail ou senha incorretos.")
    return usuario


# --------------------------------------------------------------------------- #
# Sessão (st.session_state)
# --------------------------------------------------------------------------- #
def inicializar_sessao() -> None:
    """Garante que as chaves usadas pela aplicação existam."""
    st.session_state.setdefault(CHAVE_USUARIO, None)
    st.session_state.setdefault(CHAVE_PAGINA, "dashboard")


def iniciar_sessao(usuario: Usuario) -> None:
    """Salva o usuário autenticado na sessão."""
    st.session_state[CHAVE_USUARIO] = usuario.para_dict()
    st.session_state[CHAVE_PAGINA] = "dashboard"


def encerrar_sessao() -> None:
    """Faz logout limpando os dados da sessão."""
    st.session_state[CHAVE_USUARIO] = None
    st.session_state[CHAVE_PAGINA] = "dashboard"


def esta_autenticado() -> bool:
    """Informa se existe um usuário logado."""
    return st.session_state.get(CHAVE_USUARIO) is not None


def usuario_logado() -> dict[str, Any]:
    """Devolve os dados do usuário logado."""
    usuario = st.session_state.get(CHAVE_USUARIO)
    if usuario is None:
        raise ErroDeValidacao("Sessão expirada. Faça login novamente.")
    return usuario


def usuario_id() -> int:
    """Atalho para o id do usuário logado."""
    return int(usuario_logado()["id"])


def tema_atual() -> str:
    """Tema escolhido pelo usuário (ou o padrão, quando não há login)."""
    usuario = st.session_state.get(CHAVE_USUARIO)
    return usuario["tema"] if usuario else TEMA_CLARO


def moeda_atual() -> str:
    """Símbolo da moeda escolhida pelo usuário."""
    usuario = st.session_state.get(CHAVE_USUARIO)
    return usuario["moeda"] if usuario else "R$"


# --------------------------------------------------------------------------- #
# Atualização de perfil
# --------------------------------------------------------------------------- #
def atualizar_perfil(
    usuario_id_atual: int, nome: str, email: str, telefone: str
) -> Usuario:
    """Atualiza nome, e-mail e telefone do usuário."""
    nome = validar_nome(nome)
    email = validar_email(email)

    if _repositorio.email_em_uso(email, ignorar_id=usuario_id_atual):
        raise ErroDeValidacao("Este e-mail já está sendo usado por outra conta.")

    usuario = _repositorio.atualizar(
        usuario_id_atual, nome=nome, email=email, telefone=telefone.strip() or None
    )
    if usuario is None:
        raise ErroDeValidacao("Usuário não encontrado.")
    _sincronizar_sessao(usuario)
    return usuario


def atualizar_preferencias(
    usuario_id_atual: int, tema: str, moeda: str
) -> Usuario:
    """Atualiza tema e moeda do usuário."""
    usuario = _repositorio.atualizar(usuario_id_atual, tema=tema, moeda=moeda)
    if usuario is None:
        raise ErroDeValidacao("Usuário não encontrado.")
    _sincronizar_sessao(usuario)
    return usuario


def alterar_senha(usuario_id_atual: int, nova_senha: str, confirmacao: str) -> None:
    """Troca a senha do usuário."""
    nova_senha = validar_senha(nova_senha, confirmacao)
    usuario = _repositorio.atualizar(
        usuario_id_atual, senha=gerar_hash(nova_senha)
    )
    if usuario is None:
        raise ErroDeValidacao("Usuário não encontrado.")


def _sincronizar_sessao(usuario: Usuario) -> None:
    """Mantém os dados da sessão iguais aos do banco."""
    st.session_state[CHAVE_USUARIO] = usuario.para_dict()
