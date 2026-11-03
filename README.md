# Agenda Acadêmica

Gerenciador de **tarefas acadêmicas**: cadastre atividades, defina prazos e prioridades e acompanhe o andamento.

Projeto da disciplina *Técnicas Avançadas de Programação Web e Mobile* (Fatec Araras), com **API REST**, **TDD** e **Git**.

## O que o sistema faz
- Cadastra, lista, edita e exclui tarefas (CRUD)
- Filtra a lista por status
- Mostra totais no dashboard (total, pendentes, em andamento, concluídas)

## Tecnologias
| Parte | Tecnologia |
|---|---|
| API REST (back-end) | Python + Flask |
| Banco de dados | SQLite (arquivo local, não precisa instalar servidor) |
| Interface | HTML + CSS + JavaScript puro, responsiva, consumindo a API com `fetch` |
| Testes | `unittest` (já vem no Python) |
| Versionamento | Git + GitHub |

## Instalação
Requisito: **Python 3.9 ou superior**.

```bash
# 1) (opcional, recomendado) criar ambiente virtual
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# 2) instalar as dependências
pip install -r requirements.txt
```

## Configuração
Nenhuma configuração é obrigatória. Opcionalmente, defina a variável de ambiente `SECRET_KEY`.
O banco é criado sozinho em `instance/tarefas.sqlite3` na primeira execução.
**Nunca coloque senhas ou chaves reais no repositório** (o arquivo `.env` já está no `.gitignore`).

## Como executar
```bash
python app.py
```
Abra http://localhost:5000 no navegador.

## Como rodar os testes
```bash
python -m unittest discover -v
```
Os testes usam um banco temporário, então não mexem nos seus dados reais.

## Endpoints da API
| Método | Rota | O que faz | Códigos |
|---|---|---|---|
| GET | `/api/tarefas` | Lista tarefas (`?status=pendente` filtra) | 200, 400 |
| GET | `/api/tarefas/<id>` | Mostra uma tarefa | 200, 404 |
| POST | `/api/tarefas` | Cria uma tarefa | 201, 400 |
| PUT | `/api/tarefas/<id>` | Atualiza uma tarefa | 200, 400, 404 |
| DELETE | `/api/tarefas/<id>` | Exclui uma tarefa | 204, 404 |

Erros inesperados do servidor respondem **500**. Todas as respostas de erro da API vêm em JSON.

### Exemplo: criar uma tarefa
Requisição `POST /api/tarefas`:
```json
{ "atividade": "Entregar relatório de BD", "prazo": "2026-12-01", "prioridade": "alta", "status": "pendente" }
```
Resposta `201 Created`:
```json
{ "id": 1, "atividade": "Entregar relatório de BD", "prazo": "2026-12-01", "prioridade": "alta", "status": "pendente" }
```

### Exemplo: erro de validação
Resposta `400 Bad Request`:
```json
{ "erros": ["O nome da atividade é obrigatório.", "A prioridade é obrigatória."] }
```

## Regras de negócio
1. Nome da atividade obrigatório (máximo 100 caracteres)
2. Prazo obrigatório e com data real, no formato `AAAA-MM-DD`
3. Prioridade obrigatória: `baixa`, `media` ou `alta`
4. Status opcional (padrão `pendente`): `pendente`, `em_andamento` ou `concluida`

## Estrutura do projeto
```
app.py            cria o app e define as rotas (API + páginas)
validacao.py      regras de negócio
repositorio.py    comandos SQL (acesso ao banco)
database.py       conexão com o SQLite e criação da tabela
templates/        páginas HTML
static/           CSS e JavaScript (que consome a API)
tests/            testes automatizados
```
