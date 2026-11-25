"""Repositório em memória para armazenamento de produtos."""

from threading import RLock

from loja.models import Produto


class ProdutoRepository:
    """Armazena e gerencia produtos em memória sem limite de quantidade."""

    def __init__(self) -> None:
        self._produtos: dict[int, Produto] = {}
        self._lock = RLock()

    @property
    def lock(self) -> RLock:
        """Retorna o lock para garantir operações compostas atômicas."""
        return self._lock

    def existe(self, codigo: int) -> bool:
        """Verifica se existe produto cadastrado com o código informado."""
        with self._lock:
            return codigo in self._produtos

    def obter(self, codigo: int) -> Produto | None:
        """Retorna o produto pelo código ou None caso não exista."""
        with self._lock:
            return self._produtos.get(codigo)

    def salvar(self, produto: Produto) -> None:
        """Persiste ou atualiza um produto no repositório."""
        with self._lock:
            self._produtos[produto.codigo] = produto
