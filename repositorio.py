"""
ARQUIVO: repositorio.py
O QUE FAZ: conversa com o banco de dados (os comandos SQL ficam aqui).

Cada função faz UMA coisa: listar, buscar, criar, atualizar ou excluir.
As rotas da API usam essas funções e não precisam saber de SQL.
"""

from database import get_db

# Colunas que sempre buscamos, para não repetir o texto.
COLUNAS = "id, atividade, prazo, prioridade, status"


def _para_dict(linha):
    """Transforma a linha do banco em dicionário (que vira JSON fácil)."""
    return dict(linha) if linha is not None else None


def listar(status=None):
    """READ (lista): devolve todas as tarefas, da mais nova para a mais antiga.
    Se vier um status, devolve só as tarefas daquele status."""
    db = get_db()
    if status:
        linhas = db.execute(
            f"SELECT {COLUNAS} FROM tarefas WHERE status = ? ORDER BY id DESC",
            (status,),
        ).fetchall()
    else:
        linhas = db.execute(
            f"SELECT {COLUNAS} FROM tarefas ORDER BY id DESC"
        ).fetchall()
    return [_para_dict(linha) for linha in linhas]


def buscar(tarefa_id):
    """READ (uma só): procura pelo id. Devolve None se não achar."""
    db = get_db()
    linha = db.execute(
        f"SELECT {COLUNAS} FROM tarefas WHERE id = ?", (tarefa_id,)
    ).fetchone()
    return _para_dict(linha)


def criar(dados):
    """CREATE: grava uma tarefa nova e devolve ela já com o id."""
    db = get_db()
    cursor = db.execute(
        "INSERT INTO tarefas (atividade, prazo, prioridade, status) "
        "VALUES (?, ?, ?, ?)",
        (dados["atividade"], dados["prazo"], dados["prioridade"], dados["status"]),
    )
    db.commit()
    return buscar(cursor.lastrowid)


def atualizar(tarefa_id, dados):
    """UPDATE: troca os dados de uma tarefa.
    Devolve a tarefa atualizada, ou None se o id não existe."""
    db = get_db()
    cursor = db.execute(
        "UPDATE tarefas SET atividade = ?, prazo = ?, prioridade = ?, status = ? "
        "WHERE id = ?",
        (
            dados["atividade"],
            dados["prazo"],
            dados["prioridade"],
            dados["status"],
            tarefa_id,
        ),
    )
    db.commit()
    # rowcount = quantas linhas foram alteradas. Zero significa "id não existe".
    if cursor.rowcount == 0:
        return None
    return buscar(tarefa_id)


def excluir(tarefa_id):
    """DELETE: apaga a tarefa. Devolve True se apagou, False se não achou."""
    db = get_db()
    cursor = db.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
    db.commit()
    return cursor.rowcount > 0
