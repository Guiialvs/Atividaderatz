// =====================================================================
// ARQUIVO: formulario.js
// O QUE FAZ: no formulário, carrega a tarefa quando estamos editando
// (GET) e envia os dados à API ao salvar (POST para criar, PUT para editar).
// =====================================================================

const formulario = document.getElementById("formulario");
const campoAtividade = document.getElementById("atividade");
const campoPrazo = document.getElementById("prazo");
const campoPrioridade = document.getElementById("prioridade");
const campoStatus = document.getElementById("status");

// Se existir um id, estamos EDITANDO. Se vier vazio, estamos CADASTRANDO.
const idTarefa = formulario.dataset.tarefaId;

// GET: ao editar, busca a tarefa na API e preenche os campos.
async function carregarTarefa() {
  const resposta = await chamarApi(`${API}/${idTarefa}`);
  if (!resposta.ok) {
    mostrarMensagem(textoDoErro(resposta.dados), "erro");
    return;
  }
  campoAtividade.value = resposta.dados.atividade;
  campoPrazo.value = resposta.dados.prazo;
  campoPrioridade.value = resposta.dados.prioridade;
  campoStatus.value = resposta.dados.status;
}

// POST ou PUT: roda quando o usuário clica em salvar.
formulario.addEventListener("submit", async (evento) => {
  evento.preventDefault(); // impede a página de recarregar

  // Monta o objeto que será enviado como JSON.
  const tarefa = {
    atividade: campoAtividade.value,
    prazo: campoPrazo.value,
    prioridade: campoPrioridade.value,
    status: campoStatus.value,
  };

  // Editando -> PUT /api/tarefas/3   |   Cadastrando -> POST /api/tarefas
  const resposta = idTarefa
    ? await chamarApi(`${API}/${idTarefa}`, "PUT", tarefa)
    : await chamarApi(API, "POST", tarefa);

  // Se a API recusou (ex.: erro 400), mostramos o que ela mandou.
  if (!resposta.ok) {
    mostrarMensagem(textoDoErro(resposta.dados), "erro");
    return;
  }

  // Deu certo: volta ao dashboard com a mensagem de sucesso.
  location.href = idTarefa ? "/?msg=atualizada" : "/?msg=criada";
});

// Ao abrir a página, se for edição, carrega os dados da tarefa.
if (idTarefa) {
  carregarTarefa();
}
