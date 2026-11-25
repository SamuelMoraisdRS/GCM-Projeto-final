"""Ponto de entrada para execução do servidor da API REST."""

from loja.api import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
