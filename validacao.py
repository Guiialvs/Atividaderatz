"""
ARQUIVO: validacao.py
O QUE FAZ: guarda as REGRAS DE NEGÓCIO da tarefa.

Aqui só decidimos se os dados recebidos são aceitos ou não.
Não tem Flask nem banco de dados neste arquivo, e por isso é fácil de testar.
"""

from datetime import datetime

# Valores permitidos nos campos de escolha.
PRIORIDADES_VALIDAS = ("baixa", "media", "alta")
STATUS_VALIDOS = ("pendente", "em_andamento", "concluida")


def validar_tarefa(dados):
    """Confere os dados de uma tarefa.

    Devolve uma LISTA de mensagens de erro.
    Se a lista voltar vazia, os dados estão corretos.
    """
    erros = []

    # Se nem veio um objeto (ex.: veio um texto ou uma lista), para por aqui.
    if not isinstance(dados, dict):
        return ["Os dados da tarefa precisam ser enviados como um objeto JSON."]

    # REGRA 1: o nome da atividade é obrigatório e não pode ser só espaços.
    atividade = dados.get("atividade")
    if not isinstance(atividade, str) or atividade.strip() == "":
        erros.append("O nome da atividade é obrigatório.")
    # REGRA 2: o nome não pode ser gigante.
    elif len(atividade.strip()) > 100:
        erros.append("O nome da atividade pode ter no máximo 100 caracteres.")

    # REGRA 3: o prazo é obrigatório e precisa ser uma data real (AAAA-MM-DD).
    prazo = dados.get("prazo")
    if not isinstance(prazo, str) or prazo.strip() == "":
        erros.append("O prazo é obrigatório.")
    else:
        try:
            datetime.strptime(prazo.strip(), "%Y-%m-%d")
        except ValueError:
            erros.append("Informe um prazo válido no formato AAAA-MM-DD.")

    # REGRA 4: a prioridade é obrigatória e precisa ser uma das 3 opções.
    prioridade = dados.get("prioridade")
    if prioridade is None or prioridade == "":
        erros.append("A prioridade é obrigatória.")
    elif prioridade not in PRIORIDADES_VALIDAS:
        erros.append("A prioridade deve ser: baixa, media ou alta.")

    # REGRA 5: o status é opcional (o padrão é "pendente"),
    # mas se vier precisa ser um dos 3 valores válidos.
    status = dados.get("status")
    if status is not None and status not in STATUS_VALIDOS:
        erros.append("O status deve ser: pendente, em_andamento ou concluida.")

    return erros


def normalizar_tarefa(dados):
    """Arruma os dados já validados: tira espaços e coloca o status padrão."""
    return {
        "atividade": dados["atividade"].strip(),
        "prazo": dados["prazo"].strip(),
        "prioridade": dados["prioridade"],
        "status": dados.get("status") or "pendente",
    }
