"""Exceções de domínio da camada de serviço."""


class LojaError(Exception):
    """Exceção base para erros de negócio da loja."""


class DadosInvalidosError(LojaError):
    """Lançada quando dados obrigatórios estão ausentes ou têm tipo/valor inválido."""


class ProdutoNaoEncontradoError(LojaError):
    """Lançada quando o produto informado não existe."""


class ProdutoJaExisteError(LojaError):
    """Lançada ao tentar cadastrar um produto com código já existente."""


class EstoqueInsuficienteError(DadosInvalidosError):
    """Lançada quando não há estoque suficiente para a operação solicitada."""
