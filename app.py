import os
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

import repositorio
from database import close_db, init_db
from validacao import STATUS_VALIDOS, normalizar_tarefa, validar_tarefa


def create_app(config=None):

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-de-desenvolvimento")
    app.config["DATABASE"] = os.path.join(app.instance_path, "tarefas.sqlite3")

    if config:
        app.config.update(config)

    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()

    def erro_json(codigo, mensagem):
        """Resposta de erro padronizada: {"erro": "mensagem"}."""
        return jsonify({"erro": mensagem}), codigo

    def ler_json():
        """Lê o JSON enviado pelo cliente. Devolve None se estiver quebrado."""
        return request.get_json(silent=True)

    @app.get("/api/tarefas")
    def api_listar():
        """GET /api/tarefas -> 200 com a lista (ou 400 se o filtro for inválido)."""
        status = request.args.get("status")
        if status and status not in STATUS_VALIDOS:
            return erro_json(400, "Status inválido no filtro.")
        return jsonify(repositorio.listar(status)), 200

    @app.get("/api/tarefas/<int:tarefa_id>")
    def api_buscar(tarefa_id):
        """GET /api/tarefas/3 -> 200 com a tarefa (ou 404 se não existe)."""
        tarefa = repositorio.buscar(tarefa_id)
        if tarefa is None:
            return erro_json(404, "Tarefa não encontrada.")
        return jsonify(tarefa), 200

    @app.post("/api/tarefas")
    def api_criar():
        """POST /api/tarefas -> 201 com a tarefa criada (ou 400 se tiver erro)."""
        dados = ler_json()
        if dados is None:
            return erro_json(400, "O corpo da requisição precisa ser um JSON válido.")

        erros = validar_tarefa(dados)
        if erros:
            return jsonify({"erros": erros}), 400

        tarefa = repositorio.criar(normalizar_tarefa(dados))
        return jsonify(tarefa), 201  

    @app.put("/api/tarefas/<int:tarefa_id>")
    def api_atualizar(tarefa_id):
        """PUT /api/tarefas/3 -> 200 com a tarefa atualizada (400 ou 404 se der erro)."""
        dados = ler_json()
        if dados is None:
            return erro_json(400, "O corpo da requisição precisa ser um JSON válido.")

        erros = validar_tarefa(dados)
        if erros:
            return jsonify({"erros": erros}), 400

        tarefa = repositorio.atualizar(tarefa_id, normalizar_tarefa(dados))
        if tarefa is None:
            return erro_json(404, "Tarefa não encontrada.")
        return jsonify(tarefa), 200

    @app.delete("/api/tarefas/<int:tarefa_id>")
    def api_excluir(tarefa_id):
        """DELETE /api/tarefas/3 -> 204 sem conteúdo (ou 404 se não existe)."""
        if not repositorio.excluir(tarefa_id):
            return erro_json(404, "Tarefa não encontrada.")
        return "", 204  

    @app.errorhandler(Exception)
    def tratar_erro(erro):
        """Pega qualquer erro. Nas rotas /api/ responde em JSON, como uma API deve."""
        e_da_api = request.path.startswith("/api/")

        if isinstance(erro, HTTPException):
            if not e_da_api:
                return erro
            mensagens = {404: "Rota não encontrada.", 405: "Método não permitido."}
            return erro_json(erro.code, mensagens.get(erro.code, erro.description))

        app.logger.exception(erro)
        if e_da_api:
            return erro_json(500, "Erro interno do servidor.")
        return "Erro interno do servidor.", 500

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/tarefas/nova")
    def pagina_nova():
        return render_template("formulario.html", tarefa_id=None)

    @app.get("/tarefas/<int:tarefa_id>/editar")
    def pagina_editar(tarefa_id):
        return render_template("formulario.html", tarefa_id=tarefa_id)

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
