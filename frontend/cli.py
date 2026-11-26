"""Front-end de console simples que consome a API REST da loja."""

import os
from typing import Any

import requests

DEFAULT_API_URL = os.environ.get("LOJA_API_URL", "http://127.0.0.1:5000")


def _parse_input_number(raw: str, is_float: bool = False) -> Any:
    """Converte entrada quando numérica para envio tipado; caso contrário mantém string para validação da API."""
    texto = raw.strip()
    if not is_float:
        try:
            return int(texto)
        except ValueError:
            return texto
    try:
        return float(texto)
    except ValueError:
        return texto


def _exibir_resposta(resp: requests.Response) -> None:
    try:
        corpo = resp.json()
    except ValueError:
        corpo = resp.text
    print(f"[HTTP {resp.status_code}] {corpo}")


def _cadastrar_produto(base_url: str) -> None:
    codigo = _parse_input_number(input("Código do produto: "))
    preco = _parse_input_number(input("Preço do produto: "), is_float=True)
    resp = requests.post(
        f"{base_url}/loja/produto",
        json={"codigo": codigo, "preco": preco},
        timeout=5,
    )
    _exibir_resposta(resp)


def _consultar_estoque(base_url: str) -> None:
    codigo = input("Código do produto: ").strip()
    resp = requests.get(f"{base_url}/loja/produto/{codigo}/estoque", timeout=5)
    _exibir_resposta(resp)


def _movimentar_estoque(base_url: str, operacao: str) -> None:
    codigo = input("Código do produto: ").strip()
    quantidade = _parse_input_number(input("Quantidade: "))
    resp = requests.put(
        f"{base_url}/loja/produto/{codigo}/{operacao}",
        json={"quantidade": quantidade},
        timeout=5,
    )
    _exibir_resposta(resp)


def _realizar_venda(base_url: str) -> None:
    itens: list[dict[str, Any]] = []
    while True:
        codigo_raw = input("Código do produto (Enter para finalizar): ").strip()
        if not codigo_raw:
            break
        qtd_raw = input("Quantidade vendida: ")
        itens.append(
            {
                "codigo": _parse_input_number(codigo_raw),
                "quantidade": _parse_input_number(qtd_raw),
            }
        )
    resp = requests.post(
        f"{base_url}/loja/venda",
        json={"itens": itens},
        timeout=5,
    )
    _exibir_resposta(resp)


def main(base_url: str = DEFAULT_API_URL) -> None:
    """Loop interativo de menu no console."""
    opcoes = {
        "1": ("Cadastrar Produto", lambda: _cadastrar_produto(base_url)),
        "2": ("Consultar Estoque", lambda: _consultar_estoque(base_url)),
        "3": ("Entrada de Estoque", lambda: _movimentar_estoque(base_url, "entrada")),
        "4": ("Saída de Estoque", lambda: _movimentar_estoque(base_url, "saida")),
        "5": ("Venda", lambda: _realizar_venda(base_url)),
    }

    while True:
        print("\n=== Loja Virtual - Controle de Estoque ===")
        for chave, (rotulo, _) in opcoes.items():
            print(f"{chave}. {rotulo}")
        print("0. Sair")

        escolha = input("Escolha uma opção: ").strip()
        if escolha == "0":
            print("Encerrando...")
            break

        acao = opcoes.get(escolha)
        if acao is None:
            print("Opção inválida.")
            continue

        try:
            acao[1]()
        except requests.RequestException as exc:
            print(f"Erro ao comunicar com a API ({base_url}): {exc}")


if __name__ == "__main__":
    main()
