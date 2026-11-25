"""Camada de serviço (negócio) independente da API REST e do front-end."""

from decimal import Decimal
import math
from typing import Any

from loja.exceptions import (
    DadosInvalidosError,
    EstoqueInsuficienteError,
    ProdutoJaExisteError,
    ProdutoNaoEncontradoError,
)
from loja.models import Produto
from loja.repository import ProdutoRepository


class LojaService:
    """Implementa todas as regras de negócio de produtos, estoque e vendas."""

    def __init__(self, repository: ProdutoRepository | None = None) -> None:
        self._repository = repository if repository is not None else ProdutoRepository()

    @staticmethod
    def _validar_inteiro(valor: Any, campo: str, minimo: int = 0) -> int:
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise DadosInvalidosError(f"Campo '{campo}' deve ser um número inteiro.")
        if valor < minimo:
            raise DadosInvalidosError(
                f"Campo '{campo}' deve ser maior ou igual a {minimo}."
            )
        return valor

    @staticmethod
    def _validar_preco(valor: Any) -> float:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise DadosInvalidosError("Campo 'preco' deve ser um número decimal.")
        preco_float = float(valor)
        if not math.isfinite(preco_float) or preco_float <= 0:
            raise DadosInvalidosError("Campo 'preco' deve ser um número positivo.")
        return preco_float

    @staticmethod
    def _copiar_produto(produto: Produto) -> Produto:
        return Produto(
            codigo=produto.codigo,
            preco=produto.preco,
            estoque=produto.estoque,
        )

    def cadastrar_produto(self, codigo: Any, preco: Any) -> Produto:
        """Cadastra um novo produto com estoque inicial igual a zero."""
        codigo_valido = self._validar_inteiro(codigo, "codigo", minimo=0)
        preco_valido = self._validar_preco(preco)

        with self._repository.lock:
            if self._repository.existe(codigo_valido):
                raise ProdutoJaExisteError(
                    f"Já existe um produto cadastrado com o código {codigo_valido}."
                )
            produto = Produto(codigo=codigo_valido, preco=preco_valido, estoque=0)
            self._repository.salvar(produto)
            return self._copiar_produto(produto)
