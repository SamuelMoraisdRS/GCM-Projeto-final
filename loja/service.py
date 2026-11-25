"""Camada de serviço (negócio) independente da API REST e do front-end."""

from ast import Tuple
from decimal import Decimal
import math
from typing import Any, Self

from loja import repository
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
    
    def consultar_estoque(self, codigo: int) -> tuple[int ,int]:
        """Retorna uma tupla (código de resposta, estoque)
           Se o produto não for encontrado a resposta será 404 e o segundo valor será -1"""
        
        prod = self._repository.obter(codigo) 
        if prod is not None:
            return (200, prod.estoque)
        else:
            return (400, -1)