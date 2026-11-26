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

    def _obter_produto_existente(self, codigo: int) -> Produto:
        produto = self._repository.obter(codigo)
        if produto is None:
            raise ProdutoNaoEncontradoError(
                f"Produto com código {codigo} não encontrado."
            )
        return produto

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

    def consultar_estoque(self, codigo: Any) -> int:
        """Retorna a quantidade atual em estoque do produto informado."""
        codigo_valido = self._validar_inteiro(codigo, "codigo", minimo=0)
        with self._repository.lock:
            produto = self._obter_produto_existente(codigo_valido)
            return produto.estoque

    def entrada_estoque(self, codigo: Any, quantidade: Any) -> Produto:
        """Acrescenta a quantidade informada ao estoque do produto."""
        codigo_valido = self._validar_inteiro(codigo, "codigo", minimo=0)
        qtd_valida = self._validar_inteiro(quantidade, "quantidade", minimo=1)

        with self._repository.lock:
            produto = self._obter_produto_existente(codigo_valido)
            produto.estoque += qtd_valida
            return self._copiar_produto(produto)

    def saida_estoque(self, codigo: Any, quantidade: Any) -> Produto:
        """Subtrai a quantidade informada do estoque do produto."""
        codigo_valido = self._validar_inteiro(codigo, "codigo", minimo=0)
        qtd_valida = self._validar_inteiro(quantidade, "quantidade", minimo=1)

        with self._repository.lock:
            produto = self._obter_produto_existente(codigo_valido)
            if qtd_valida > produto.estoque:
                raise EstoqueInsuficienteError(
                    f"Estoque insuficiente para o produto {codigo_valido}."
                )
            produto.estoque -= qtd_valida
            return self._copiar_produto(produto)

    def realizar_venda(self, itens: Any) -> dict[str, Any]:
        """Realiza uma venda atômica de uma lista de itens."""
        if not isinstance(itens, list) or len(itens) == 0:
            raise DadosInvalidosError(
                "Campo 'itens' é obrigatório e deve ser uma lista não vazia."
            )

        itens_validados: list[tuple[int, int]] = []
        demanda_por_codigo: dict[int, int] = {}

        for item in itens:
            if not isinstance(item, dict):
                raise DadosInvalidosError("Cada item da venda deve ser um objeto.")
            codigo_valido = self._validar_inteiro(item.get("codigo"), "codigo", minimo=0)
            qtd_valida = self._validar_inteiro(
                item.get("quantidade"), "quantidade", minimo=1
            )
            itens_validados.append((codigo_valido, qtd_valida))
            demanda_por_codigo[codigo_valido] = (
                demanda_por_codigo.get(codigo_valido, 0) + qtd_valida
            )

        with self._repository.lock:
            produtos: dict[int, Produto] = {}
            for codigo_item in demanda_por_codigo:
                produtos[codigo_item] = self._obter_produto_existente(codigo_item)

            for codigo_item, qtd_total in demanda_por_codigo.items():
                if qtd_total > produtos[codigo_item].estoque:
                    raise EstoqueInsuficienteError(
                        f"Estoque insuficiente para o produto {codigo_item}."
                    )

            total_venda = Decimal("0")
            itens_resposta: list[dict[str, Any]] = []

            for codigo_item, qtd_item in itens_validados:
                produto = produtos[codigo_item]
                produto.estoque -= qtd_item
                subtotal = Decimal(str(produto.preco)) * Decimal(qtd_item)
                total_venda += subtotal
                itens_resposta.append(
                    {
                        "codigo": codigo_item,
                        "quantidade": qtd_item,
                        "subtotal": float(subtotal),
                        "estoque": produto.estoque,
                    }
                )

            return {
                "total": float(total_venda),
                "itens": itens_resposta,
            }
