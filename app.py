import os
from datetime import date
from flask import Flask, flash, redirect, render_template, request, url_for

from database import close_db, init_db, get_db

app = Flask(__name__)

# Chave usada pelo Flask para gerenciar mensagens e sessões.
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "chave-de-desenvolvimento-troque-em-producao"
)

# Fecha a conexão com o banco ao terminar a requisição.
app.teardown_appcontext(close_db)


@app.route("/", methods=["GET"])
def index():

    db = get_db()

    # Busca as tarefas cadastradas.
    tarefas = db.execute(
        """
        SELECT id, atividade, prazo, prioridade, status
        FROM tarefas
        ORDER BY id DESC
        """
    ).fetchall()

    # Exibe o formulário e a lista de tarefas no mesmo HTML.
    return render_template(
        "index.html",
        tarefas=tarefas,
        valores=valores
    )

@app.route("/criar", methods=["POST"])
def criar_tarefa():
    
    db = get_db()

# Valores iniciais do formulário.
    valores = {
        "atividade": "",
        "prazo": "",
        "prioridade": "",
        "status": ""
    }

    # Verifica se o formulário foi enviado.
    if request.method == "POST":

        # Recebe os dados preenchidos no HTML.
        valores = {
            "atividade": request.form.get("atividade", "").strip(),
            "prazo": request.form.get("prazo", "").strip(),
            "prioridade": request.form.get("prioridade", "").strip(),
            "status": request.form.get("status", "").strip()
        }

        # Verifica se todos os campos foram preenchidos.
        if not all(valores.values()):
            flash("Preencha todos os campos.", "erro")

        else:
            # Verifica se a data informada é válida.
            try:
                date.fromisoformat(valores["prazo"])
            except ValueError:
                flash("Informe um prazo válido.", "erro")

            else:
                # Verifica se a prioridade é permitida.
                if valores["prioridade"] not in ("baixa", "media", "alta"):
                    flash("Selecione uma prioridade válida.", "erro")

                # Verifica se o status é permitido.
                elif valores["status"] not in (
                    "pendente", "em_andamento", "concluida"
                ):
                    flash("Selecione um status válido.", "erro")

                else:
                    # Salva a tarefa no banco de dados.
                    db.execute(
                        """
                        INSERT INTO tarefas
                        (atividade, prazo, prioridade, status)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            valores["atividade"],
                            valores["prazo"],
                            valores["prioridade"],
                            valores["status"]
                        )
                    )

                    # Confirma a gravação dos dados.
                    db.commit()

                    flash("Tarefa cadastrada com sucesso!", "sucesso")

                    # Volta para a página inicial.
                    return redirect(url_for("index"))


@app.route("/excluir/<int:atividade_id>", methods=["POST"])
def excluir_atividade(atividade_id):

    db = get_db()
    cursor = db.execute("DELETE FROM tarefas WHERE id = ?", (atividade_id,))
    db.commit()

    if cursor.rowcount == 0:
        flash("Essa tarefa não existe ou já foi excluído.", "erro")
    else:
        flash("tarefa excluída com sucesso.", "sucesso")

    return redirect(url_for("index"))

@app.route("/editar/<int:atividade_id>", methods=["GET", "POST"])
def editar_atividade(atividade_id):

    db = get_db()

    # Busca a tarefa que será editada.
    tarefa = db.execute(
        "SELECT * FROM tarefas WHERE id = ?",
        (atividade_id,)
    ).fetchone()

    # Verifica se a tarefa existe.
    if tarefa is None:
        flash("Tarefa não encontrada.", "erro")
        return redirect(url_for("index"))

    # Preenche o formulário com os dados atuais.
    valores = {
        "atividade": tarefa["atividade"],
        "prazo": tarefa["prazo"],
        "prioridade": tarefa["prioridade"],
        "status": tarefa["status"]
    }

    # Verifica se o formulário de edição foi enviado.
    if request.method == "POST":

        valores = {
            "atividade": request.form.get("atividade", "").strip(),
            "prazo": request.form.get("prazo", "").strip(),
            "prioridade": request.form.get("prioridade", "").strip(),
            "status": request.form.get("status", "").strip()
        }

        if not all(valores.values()):
            flash("Preencha todos os campos.", "erro")

        else:
            try:
                date.fromisoformat(valores["prazo"])
            except ValueError:
                flash("Informe um prazo válido.", "erro")

            else:
                if valores["prioridade"] not in ("baixa", "media", "alta"):
                    flash("Prioridade inválida.", "erro")

                elif valores["status"] not in (
                    "pendente", "em_andamento", "concluida"
                ):
                    flash("Status inválido.", "erro")

                else:
                    # Atualiza os dados da tarefa no banco.
                    db.execute(
                        """
                        UPDATE tarefas
                        SET atividade = ?, prazo = ?, prioridade = ?, status = ?
                        WHERE id = ?
                        """,
                        (
                            valores["atividade"],
                            valores["prazo"],
                            valores["prioridade"],
                            valores["status"],
                            atividade_id
                        )
                    )

                    db.commit()

                    flash("Tarefa atualizada com sucesso!", "sucesso")
                    return redirect(url_for("index"))

    # Busca todas as tarefas para manter a listagem na página.
    tarefas = db.execute(
        """
        SELECT id, atividade, prazo, prioridade, status
        FROM tarefas
        ORDER BY id DESC
        """
    ).fetchall()

    # Reutiliza o mesmo HTML para editar e listar.
    return render_template(
        "index.html",
        tarefas=tarefas,
        valores=valores,
        tarefa_edicao=None
    )

# Cria a tabela caso ela ainda não exista.
with app.app_context():
    init_db()


# Inicia o servidor Flask.
if __name__ == "__main__":
    app.run(debug=True)