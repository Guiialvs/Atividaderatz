// =====================================================================
// ARQUIVO: api.js
// O QUE FAZ: funções que todas as páginas usam para conversar com a API
// e mostrar mensagens ao usuário.
// =====================================================================

// Endereço base da nossa API.
const API = "/api/tarefas";

// Nomes bonitos para mostrar na tela (o banco guarda o valor "técnico").
const NOMES_STATUS = {
  pendente: "Pendente",
  em_andamento: "Em andamento",
  concluida: "Concluída",
};
const NOMES_PRIORIDADE = { baixa: "Baixa", media: "Média", alta: "Alta" };

// Mostra uma mensagem na caixa do topo. tipo = "sucesso" ou "erro".
// Se o texto vier vazio, esconde a caixa.
function mostrarMensagem(texto, tipo) {
  const caixa = document.getElementById("mensagem");
  if (!texto) {
    caixa.hidden = true;
    return;
  }
  caixa.textContent = texto; // textContent é seguro: não interpreta HTML
  caixa.className = "flash flash-" + tipo;
  caixa.hidden = false;
}

// Faz um pedido à API e devolve { ok, codigo, dados }.
//   ok     -> true se o código HTTP foi de sucesso (200, 201, 204...)
//   codigo -> o código HTTP (200, 400, 404...)
//   dados  -> a resposta já convertida de JSON (ou null se veio vazia)
async function chamarApi(url, metodo = "GET", corpo) {
  const opcoes = { method: metodo, headers: {} };

  // Se temos dados para enviar (POST/PUT), mandamos como JSON.
  if (corpo !== undefined) {
    opcoes.headers["Content-Type"] = "application/json";
    opcoes.body = JSON.stringify(corpo);
  }

  try {
    const resposta = await fetch(url, opcoes);
    const texto = await resposta.text();
    return {
      ok: resposta.ok,
      codigo: resposta.status,
      dados: texto ? JSON.parse(texto) : null,
    };
  } catch (erro) {
    // Cai aqui se o servidor estiver desligado ou a resposta não for JSON.
    return {
      ok: false,
      codigo: 0,
      dados: { erro: "Não foi possível se comunicar com o servidor." },
    };
  }
}

// Junta as mensagens de erro que a API mandou em um texto só.
// A API manda {"erros": [...]} (vários erros) ou {"erro": "..."} (um erro).
function textoDoErro(dados) {
  if (!dados) return "Algo deu errado.";
  return (dados.erros || [dados.erro]).join(" ");
}

// Troca a data de "2026-11-10" para "10/11/2026".
function formatarData(dataIso) {
  const [ano, mes, dia] = dataIso.split("-");
  return `${dia}/${mes}/${ano}`;
}
