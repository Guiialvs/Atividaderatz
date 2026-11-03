"""
ARQUIVO: test_validacao.py
O QUE FAZ: testa as REGRAS DE NEGÓCIO (validacao.py) sozinhas,
sem servidor e sem banco de dados. São testes de unidade: rápidos e simples.

Para rodar todos os testes:  python -m unittest discover -v
"""

import unittest

from validacao import normalizar_tarefa, validar_tarefa


def tarefa_valida():
    """Devolve uma tarefa correta, usada como base nos testes."""
    return {
        "atividade": "Entregar relatório",
        "prazo": "2026-12-01",
        "prioridade": "alta",
        "status": "pendente",
    }


class TestValidarTarefa(unittest.TestCase):
    def test_aceita_tarefa_valida(self):
        self.assertEqual(validar_tarefa(tarefa_valida()), [])

    def test_rejeita_tarefa_sem_atividade(self):
        dados = tarefa_valida()
        dados["atividade"] = ""
        self.assertIn("O nome da atividade é obrigatório.", validar_tarefa(dados))

    def test_rejeita_atividade_so_com_espacos(self):
        dados = tarefa_valida()
        dados["atividade"] = "    "
        self.assertIn("O nome da atividade é obrigatório.", validar_tarefa(dados))

    def test_rejeita_atividade_com_mais_de_100_caracteres(self):
        dados = tarefa_valida()
        dados["atividade"] = "a" * 101
        self.assertIn(
            "O nome da atividade pode ter no máximo 100 caracteres.",
            validar_tarefa(dados),
        )

    def test_rejeita_tarefa_sem_prazo(self):
        dados = tarefa_valida()
        del dados["prazo"]
        self.assertIn("O prazo é obrigatório.", validar_tarefa(dados))

    def test_rejeita_prazo_que_nao_e_data_real(self):
        dados = tarefa_valida()
        dados["prazo"] = "2026-02-31"  # fevereiro não tem dia 31
        self.assertIn(
            "Informe um prazo válido no formato AAAA-MM-DD.", validar_tarefa(dados)
        )

    def test_rejeita_prioridade_invalida(self):
        dados = tarefa_valida()
        dados["prioridade"] = "urgentissima"
        self.assertIn(
            "A prioridade deve ser: baixa, media ou alta.", validar_tarefa(dados)
        )

    def test_rejeita_tarefa_sem_prioridade(self):
        dados = tarefa_valida()
        del dados["prioridade"]
        self.assertIn("A prioridade é obrigatória.", validar_tarefa(dados))

    def test_rejeita_status_invalido(self):
        dados = tarefa_valida()
        dados["status"] = "abandonada"
        self.assertIn(
            "O status deve ser: pendente, em_andamento ou concluida.",
            validar_tarefa(dados),
        )

    def test_status_e_opcional(self):
        dados = tarefa_valida()
        del dados["status"]
        self.assertEqual(validar_tarefa(dados), [])

    def test_rejeita_dados_que_nao_sao_um_objeto(self):
        self.assertEqual(len(validar_tarefa(["lista"])), 1)


class TestNormalizarTarefa(unittest.TestCase):
    def test_tira_espacos_e_usa_status_padrao(self):
        resultado = normalizar_tarefa(
            {"atividade": "  Estudar  ", "prazo": " 2026-12-01 ", "prioridade": "baixa"}
        )
        self.assertEqual(
            resultado,
            {
                "atividade": "Estudar",
                "prazo": "2026-12-01",
                "prioridade": "baixa",
                "status": "pendente",
            },
        )


if __name__ == "__main__":
    unittest.main()
