"""Modelos de domínio do sistema de loja."""

from dataclasses import dataclass


@dataclass
class Produto:
    """Representa um produto da loja com código, preço e estoque."""

    codigo: int
    preco: float
    estoque: int = 0
