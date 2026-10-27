"""
Funções responsáveis pelo acesso ao banco de dados SQLite.

Este banco armazena as tarefas acadêmicas em um arquivo local,
sem precisar instalar um servidor de banco de dados.
"""

import os
import sqlite3
from flask import current_app, g


def get_db():
    """Abre e reutiliza a conexão com o banco durante a requisição."""

    # Verifica se já existe uma conexão aberta nesta requisição.
    if "db" not in g:

        # Cria a pasta instance caso ela ainda não exista.
        os.makedirs(current_app.instance_path, exist_ok=True)

        # Define o caminho do arquivo do banco de dados.
        caminho_banco = os.path.join(
            current_app.instance_path,
            "tarefas.sqlite3"
        )

        # Conecta ao banco SQLite.
        g.db = sqlite3.connect(caminho_banco)

        # Permite acessar os dados pelo nome das colunas.
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(exception=None):
    """Fecha a conexão com o banco ao terminar a requisição."""

    # Recupera a conexão e remove a referência temporária.
    db = g.pop("db", None)

    # Fecha a conexão caso ela tenha sido aberta.
    if db is not None:
        db.close()


def init_db():
    """Cria a tabela de tarefas caso ela ainda não exista."""

    # Obtém a conexão com o banco de dados.
    db = get_db()

    # Cria a tabela que armazenará as tarefas acadêmicas.
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

    # Salva as alterações no banco de dados.
    db.commit()