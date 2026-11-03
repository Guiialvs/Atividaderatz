"""
ARQUIVO: test_api.py
O QUE FAZ: testa a API de ponta a ponta (testes de integração).
Usa o "cliente de teste" do Flask, que faz pedidos HTTP de verdade ao app,
mas com um banco de dados TEMPORÁRIO. O banco real nunca é tocado.

Para rodar todos os testes:  python -m unittest discover -v
"""

import os
import shutil
import tempfile
import unittest

from app import create_app


def tarefa_valida(**mudancas):
    """Devolve uma tarefa correta. Dá para trocar campos: tarefa_valida(prioridade='baixa')."""
    dados = {
        "atividade": "Entregar relatório",
        "prazo": "2026-12-01",
        "prioridade": "alta",
        "status": "pendente",
    }
    dados.update(mudancas)
    return dados


class TestApi(unittest.TestCase):
    def setUp(self):
        """Roda ANTES de cada teste: cria um app com banco temporário novo.
        Assim, um teste nunca atrapalha o outro."""
        self.pasta = tempfile.mkdtemp()
        self.app = create_app(
            {"TESTING": True, "DATABASE": os.path.join(self.pasta, "teste.sqlite3")}
        )
        self.client = self.app.test_client()

    def tearDown(self):
        """Roda DEPOIS de cada teste: apaga o banco temporário."""
        shutil.rmtree(self.pasta, ignore_errors=True)

    def criar(self, **mudancas):
        """Atalho: cadastra uma tarefa pela API e devolve a resposta."""
        return self.client.post("/api/tarefas", json=tarefa_valida(**mudancas))

    # ------------------------------ POST ------------------------------

    def test_post_cria_tarefa_e_responde_201(self):
        resposta = self.criar()
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.get_json()["id"], 1)
        self.assertEqual(resposta.get_json()["atividade"], "Entregar relatório")

    def test_post_usa_status_pendente_como_padrao(self):
        dados = tarefa_valida()
        del dados["status"]
        resposta = self.client.post("/api/tarefas", json=dados)
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.get_json()["status"], "pendente")

    def test_post_sem_atividade_responde_400(self):
        resposta = self.criar(atividade="")
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("O nome da atividade é obrigatório.", resposta.get_json()["erros"])

    def test_post_com_prazo_invalido_responde_400(self):
        self.assertEqual(self.criar(prazo="amanhã").status_code, 400)

    def test_post_com_json_quebrado_responde_400(self):
        resposta = self.client.post(
            "/api/tarefas", data="{quebrado", content_type="application/json"
        )
        self.assertEqual(resposta.status_code, 400)

    def test_post_sem_corpo_responde_400(self):
        self.assertEqual(self.client.post("/api/tarefas").status_code, 400)

    # ------------------------------ GET -------------------------------

    def test_get_lista_tarefas(self):
        self.criar(atividade="A")
        self.criar(atividade="B")
        resposta = self.client.get("/api/tarefas")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(resposta.get_json()), 2)

    def test_get_lista_vazia_responde_200(self):
        resposta = self.client.get("/api/tarefas")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json(), [])

    def test_get_filtra_por_status(self):
        self.criar(atividade="A", status="concluida")
        self.criar(atividade="B", status="pendente")
        resposta = self.client.get("/api/tarefas?status=concluida")
        self.assertEqual(len(resposta.get_json()), 1)
        self.assertEqual(resposta.get_json()[0]["atividade"], "A")

    def test_get_com_filtro_invalido_responde_400(self):
        self.assertEqual(self.client.get("/api/tarefas?status=xyz").status_code, 400)

    def test_get_uma_tarefa_pelo_id(self):
        self.criar()
        resposta = self.client.get("/api/tarefas/1")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["prioridade"], "alta")

    def test_get_tarefa_inexistente_responde_404(self):
        self.assertEqual(self.client.get("/api/tarefas/999").status_code, 404)

    # ------------------------------ PUT -------------------------------

    def test_put_atualiza_tarefa(self):
        self.criar()
        resposta = self.client.put(
            "/api/tarefas/1", json=tarefa_valida(status="concluida")
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["status"], "concluida")
        # Confere se a mudança foi mesmo gravada no banco.
        self.assertEqual(self.client.get("/api/tarefas/1").get_json()["status"], "concluida")

    def test_put_tarefa_inexistente_responde_404(self):
        resposta = self.client.put("/api/tarefas/999", json=tarefa_valida())
        self.assertEqual(resposta.status_code, 404)

    def test_put_com_dados_invalidos_responde_400(self):
        self.criar()
        resposta = self.client.put("/api/tarefas/1", json=tarefa_valida(prioridade="x"))
        self.assertEqual(resposta.status_code, 400)

    # ----------------------------- DELETE -----------------------------

    def test_delete_apaga_tarefa_e_responde_204(self):
        self.criar()
        self.assertEqual(self.client.delete("/api/tarefas/1").status_code, 204)
        # Depois de apagar, a tarefa não existe mais.
        self.assertEqual(self.client.get("/api/tarefas/1").status_code, 404)

    def test_delete_tarefa_inexistente_responde_404(self):
        self.assertEqual(self.client.delete("/api/tarefas/999").status_code, 404)

    # ------------------------- ERROS EM GERAL -------------------------

    def test_rota_inexistente_da_api_responde_404_em_json(self):
        resposta = self.client.get("/api/outra-coisa")
        self.assertEqual(resposta.status_code, 404)
        self.assertEqual(resposta.get_json()["erro"], "Rota não encontrada.")

    def test_metodo_nao_permitido_responde_405_em_json(self):
        resposta = self.client.put("/api/tarefas", json=tarefa_valida())
        self.assertEqual(resposta.status_code, 405)

    # ------------------------------ PÁGINAS ---------------------------

    def test_paginas_html_carregam(self):
        for caminho in ("/", "/tarefas/nova", "/tarefas/1/editar"):
            self.assertEqual(self.client.get(caminho).status_code, 200, caminho)


if __name__ == "__main__":
    unittest.main()
