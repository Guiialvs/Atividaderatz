import os
import sqlite3
from flask import current_app, g


def get_db():

    if "db" not in g:
        caminho_banco = current_app.config["DATABASE"]

        os.makedirs(os.path.dirname(caminho_banco), exist_ok=True)

        g.db = sqlite3.connect(caminho_banco)

        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(exception=None):

    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            atividade TEXT NOT NULL,
            prazo TEXT NOT NULL,
            prioridade TEXT NOT NULL
                CHECK (prioridade IN ('baixa', 'media', 'alta')),
            status TEXT NOT NULL DEFAULT 'pendente'
                CHECK (status IN (
                    'pendente',
                    'em_andamento',
                    'concluida'
                ))
        )
        """
    )
    db.commit()
