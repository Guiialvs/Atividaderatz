// =====================================================================
// ARQUIVO: dashboard.js
// O QUE FAZ: na página inicial, busca as tarefas na API (GET),
// preenche os números e a tabela, e trata o botão "Excluir" (DELETE).
// =====================================================================

// Guarda os elementos da página em variáveis.
const corpoTabela = document.getElementById("corpo-tabela");
const areaTabela = document.getElementById("area-tabela");
const areaVazia = document.getElementById("area-vazia");
const contador = document.getElementById("contador");
const filtro = document.getElementById("filtro");

// Mensagens que podem chegar pela URL depois de criar/editar (ex.: /?msg=criada).
// Usamos uma lista fixa para nunca mostrar texto qualquer vindo da URL.
const MENSAGENS_DA_URL = {
  criada: "Tarefa cadastrada com sucesso!",
  atualizada: "Tarefa atualizada com sucesso!",
};

// Cria um elemento HTML com texto e classes (evita repetir código).
function criarElemento(tag, texto, classes) {
  const elemento = document.createElement(tag);
  if (texto !== undefined) elemento.textContent = texto;
  if (classes) elemento.className = classes;
  return elemento;
}

// Atualiza os 4 quadros de números a partir da lista COMPLETA de tarefas.
function atualizarNumeros(tarefas) {
  const contar = (status) => tarefas.filter((t) => t.status === status).length;
  document.getElementById("total").textContent = tarefas.length;
  document.getElementById("pendentes").textContent = contar("pendente");
  document.getElementById("andamento").textContent = contar("em_andamento");
  document.getElementById("concluidas").textContent = contar("concluida");
}

// Monta uma linha (<tr>) da tabela para uma tarefa.
function criarLinha(tarefa) {
  const linha = document.createElement("tr");

  // Coluna 1: nome da atividade e número da tarefa.
  const colunaNome = document.createElement("td");
  colunaNome.append(
    criarElemento("strong", tarefa.atividade),
    criarElemento("small", `Tarefa #${tarefa.id}`, "subline")
  );

  // Colunas 2, 3 e 4: prazo, prioridade e status.
  const colunaPrazo = criarElemento("td", formatarData(tarefa.prazo));
  const colunaPrioridade = document.createElement("td");
  colunaPrioridade.append(
    criarElemento("span", NOMES_PRIORIDADE[tarefa.prioridade], `pill priority-${tarefa.prioridade}`)
  );
  const colunaStatus = document.createElement("td");
  colunaStatus.append(
    criarElemento("span", NOMES_STATUS[tarefa.status], `pill status-${tarefa.status}`)
  );

  // Coluna 5: botões Editar (link para outra página) e Excluir (chama a API).
  const editar = criarElemento("a", "Editar", "button button-quiet button-small");
  editar.href = `/tarefas/${tarefa.id}/editar`;
  const excluir = criarElemento("button", "Excluir", "button button-danger button-small");
  excluir.type = "button";
  excluir.addEventListener("click", () => excluirTarefa(tarefa.id));
  const colunaAcoes = document.createElement("td");
  colunaAcoes.append(criarElemento("div", undefined, "actions"));
  colunaAcoes.firstChild.append(editar, excluir);

  linha.append(colunaNome, colunaPrazo, colunaPrioridade, colunaStatus, colunaAcoes);
  return linha;
}

// GET: busca as tarefas na API e desenha a tela.
async function carregarTarefas() {
  // 1) Lista completa: serve para os números do topo.
  const todas = await chamarApi(API);
  if (!todas.ok) {
    mostrarMensagem(textoDoErro(todas.dados), "erro");
    return;
  }
  atualizarNumeros(todas.dados);

  // 2) Lista da tabela: se há filtro, pede só aquele status (GET /api/tarefas?status=...).
  let tarefas = todas.dados;
  if (filtro.value) {
    const filtradas = await chamarApi(`${API}?status=${filtro.value}`);
    if (!filtradas.ok) {
      mostrarMensagem(textoDoErro(filtradas.dados), "erro");
      return;
    }
    tarefas = filtradas.dados;
  }

  // Desenha a tabela (ou a mensagem de "nenhuma tarefa").
  corpoTabela.innerHTML = "";
  tarefas.forEach((tarefa) => corpoTabela.append(criarLinha(tarefa)));
  areaTabela.hidden = tarefas.length === 0;
  areaVazia.hidden = tarefas.length !== 0;
  contador.textContent = `${tarefas.length} tarefa(s) exibida(s)`;
}

// DELETE: apaga uma tarefa depois de o usuário confirmar.
async function excluirTarefa(id) {
  if (!confirm("Tem certeza que deseja excluir esta tarefa?")) return;

  const resposta = await chamarApi(`${API}/${id}`, "DELETE");
  if (!resposta.ok) {
    mostrarMensagem(textoDoErro(resposta.dados), "erro");
    return;
  }
  mostrarMensagem("Tarefa excluída com sucesso!", "sucesso");
  carregarTarefas();
}

// Quando o filtro muda, recarrega a tabela.
filtro.addEventListener("change", carregarTarefas);

// Ao abrir a página: mostra a mensagem vinda da URL (se houver) e carrega os dados.
const mensagemUrl = new URLSearchParams(location.search).get("msg");
if (MENSAGENS_DA_URL[mensagemUrl]) {
  mostrarMensagem(MENSAGENS_DA_URL[mensagemUrl], "sucesso");
  history.replaceState(null, "", "/"); // limpa o "?msg=" do endereço
}
carregarTarefas();
