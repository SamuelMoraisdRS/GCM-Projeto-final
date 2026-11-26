"""Camada API REST (backend) responsável apenas por repassar requisições à camada de serviço."""

import re
from typing import Any

from flask import Flask, jsonify, request

from loja.exceptions import (
    DadosInvalidosError,
    ProdutoJaExisteError,
    ProdutoNaoEncontradoError,
)
from loja.service import LojaService


def _parse_codigo_path(raw_codigo: str) -> int:
    if not re.fullmatch(r"-?\d+", raw_codigo):
        raise DadosInvalidosError("Campo 'codigo' deve ser um número inteiro.")
    return int(raw_codigo)


def _get_json_object() -> dict[str, Any]:
    data = request.get_json(force=True, silent=True)
    if not isinstance(data, dict):
        raise DadosInvalidosError("Corpo da requisição deve ser um objeto JSON válido.")
    return data


def create_app(service: LojaService | None = None) -> Flask:
    """Cria e configura a aplicação Flask conectada à camada de serviço."""
    app = Flask(__name__)
    loja_service = service if service is not None else LojaService()

    @app.errorhandler(DadosInvalidosError)
    def handle_bad_request(err: DadosInvalidosError):
        return jsonify({"erro": str(err)}), 400

    @app.errorhandler(ProdutoNaoEncontradoError)
    def handle_not_found(err: ProdutoNaoEncontradoError):
        return jsonify({"erro": str(err)}), 404

    @app.errorhandler(ProdutoJaExisteError)
    def handle_conflict(err: ProdutoJaExisteError):
        return jsonify({"erro": str(err)}), 409

    @app.post("/loja/produto")
    def cadastrar_produto():
        dados = _get_json_object()
        produto = loja_service.cadastrar_produto(
            codigo=dados.get("codigo"),
            preco=dados.get("preco"),
        )
        return (
            jsonify(
                {
                    "codigo": produto.codigo,
                    "preco": produto.preco,
                    "estoque": produto.estoque,
                }
            ),
            201,
        )

    @app.get("/loja/produto/<codigo>/estoque")
    def consultar_estoque(codigo: str):
        codigo_int = _parse_codigo_path(codigo)
        estoque = loja_service.consultar_estoque(codigo_int)
        return jsonify({"codigo": codigo_int, "estoque": estoque}), 200

    @app.put("/loja/produto/<codigo>/entrada")
    def entrada_estoque(codigo: str):
        codigo_int = _parse_codigo_path(codigo)
        dados = _get_json_object()
        produto = loja_service.entrada_estoque(
            codigo=codigo_int,
            quantidade=dados.get("quantidade"),
        )
        return jsonify({"codigo": produto.codigo, "estoque": produto.estoque}), 200

    @app.put("/loja/produto/<codigo>/saida")
    def saida_estoque(codigo: str):
        codigo_int = _parse_codigo_path(codigo)
        dados = _get_json_object()
        produto = loja_service.saida_estoque(
            codigo=codigo_int,
            quantidade=dados.get("quantidade"),
        )
        return jsonify({"codigo": produto.codigo, "estoque": produto.estoque}), 200

    @app.post("/loja/venda")
    def realizar_venda():
        dados = _get_json_object()
        resultado = loja_service.realizar_venda(dados.get("itens"))
        return jsonify(resultado), 201

    return app
