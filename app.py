
import os
from datetime import date
from flask import Flask, flash, redirect, render_template, request, url_for

from database import close_db, init_db, get_db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "chave-de-desenvolvimento"
)

app.teardown_appcontext(close_db)


def valores_vazios():
    return {
        "atividade": "",
        "prazo": "",
        "prioridade": "",
        "status": "pendente"
    }


def buscar_tarefas():
    db = get_db()
    return db.execute("""
        SELECT id, atividade, prazo, prioridade, status
        FROM tarefas
        ORDER BY id DESC
    """).fetchall()


def buscar_tarefa(atividade_id):
    db = get_db()
    return db.execute("""
        SELECT id, atividade, prazo, prioridade, status
        FROM tarefas
        WHERE id = ?
    """, (atividade_id,)).fetchone()


def validar_tarefa(valores):
    if not all(valores.values()):
        return "Preencha todos os campos."

    try:
        date.fromisoformat(valores["prazo"])
    except ValueError:
        return "Informe um prazo válido."

    if valores["prioridade"] not in ("baixa", "media", "alta"):
        return "Selecione uma prioridade válida."

    if valores["status"] not in (
        "pendente", "em_andamento", "concluida"
    ):
        return "Selecione um status válido."

    return None


def ler_formulario():
    return {
        "atividade": request.form.get("atividade", "").strip(),
        "prazo": request.form.get("prazo", "").strip(),
        "prioridade": request.form.get("prioridade", "").strip(),
        "status": request.form.get("status", "").strip()
    }


@app.route("/")
def index():
    return render_template(
        "index.html",
        tarefas=buscar_tarefas(),
        valores=valores_vazios(),
        tarefa_edicao=None,
        mostrar_todas=False
    )


# Tela com todas as tarefas
@app.route("/tarefas")
def tarefas():
    return render_template(
        "index.html",
        tarefas=buscar_tarefas(),
        valores=valores_vazios(),
        tarefa_edicao=None,
        mostrar_todas=True
    )


# Abre o formulário e cadastra uma tarefa
@app.route("/criar", methods=["GET", "POST"])
def criar_tarefa():
    if request.method == "GET":
        return render_template(
            "formulario.html",
            valores=valores_vazios(),
            tarefa_edicao=None
        )

    valores = ler_formulario()
    erro = validar_tarefa(valores)

    if erro:
        flash(erro, "erro")
        return render_template(
            "formulario.html",
            valores=valores,
            tarefa_edicao=None
        )

    db = get_db()
    db.execute("""
        INSERT INTO tarefas
        (atividade, prazo, prioridade, status)
        VALUES (?, ?, ?, ?)
    """, (
        valores["atividade"],
        valores["prazo"],
        valores["prioridade"],
        valores["status"]
    ))
    db.commit()

    flash("Tarefa cadastrada com sucesso!", "sucesso")
    return redirect(url_for("index"))


# Exclui uma tarefa
@app.route("/excluir/<int:atividade_id>", methods=["POST"])
def excluir_tarefa(atividade_id):
    db = get_db()
    cursor = db.execute(
        "DELETE FROM tarefas WHERE id = ?",
        (atividade_id,)
    )
    db.commit()

    if cursor.rowcount == 0:
        flash("Tarefa não encontrada.", "erro")
    else:
        flash("Tarefa excluída com sucesso!", "sucesso")

    return redirect(url_for("index"))


# Abre o formulário e atualiza uma tarefa
@app.route("/editar/<int:atividade_id>", methods=["GET", "POST"])
def editar_tarefa(atividade_id):
    tarefa = buscar_tarefa(atividade_id)

    if tarefa is None:
        flash("Tarefa não encontrada.", "erro")
        return redirect(url_for("index"))

    valores = {
        "atividade": tarefa["atividade"],
        "prazo": tarefa["prazo"],
        "prioridade": tarefa["prioridade"],
        "status": tarefa["status"]
    }

    if request.method == "POST":
        valores = ler_formulario()
        erro = validar_tarefa(valores)

        if erro:
            flash(erro, "erro")
        else:
            db = get_db()
            db.execute("""
                UPDATE tarefas
                SET atividade = ?, prazo = ?,
                    prioridade = ?, status = ?
                WHERE id = ?
            """, (
                valores["atividade"],
                valores["prazo"],
                valores["prioridade"],
                valores["status"],
                atividade_id
            ))
            db.commit()

            flash("Tarefa atualizada com sucesso!", "sucesso")
            return redirect(url_for("index"))

    return render_template(
        "formulario.html",
        valores=valores,
        tarefa_edicao=tarefa
    )


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=True)
