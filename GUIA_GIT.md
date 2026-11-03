# Guia de Git + TDD (para VOCÊ fazer)

O professor avalia o **processo**: o histórico do Git precisa mostrar **você escrevendo o teste ANTES do código**.
Por isso este guia não vem com o histórico pronto: ele só vale se for o seu histórico de verdade.

## 1. Configuração (uma vez só)
```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
```

## 2. Primeiro commit
```bash
git init
git add .
git commit -m "chore: projeto inicial com API REST, interface e testes"
```

## 3. Conectar ao GitHub
1. Crie um repositório **vazio** em github.com
2. Copie o endereço dele e rode:
```bash
git remote add origin ENDERECO_DO_REPOSITORIO
git branch -M main
git push -u origin main
```

## 4. Exercício de TDD: regra "prazo não pode estar no passado"
Esta regra **ainda não existe** no projeto. Implemente seguindo o ciclo:

```bash
git checkout -b feature/prazo-no-passado
```

**RED (teste que falha)**
1. Em `tests/test_validacao.py`, escreva um teste que diz: uma tarefa com prazo em uma data passada deve gerar um erro.
2. Rode `python -m unittest discover -v` e confirme que o teste **FALHA**.
```bash
git add tests/
git commit -m "test: rejeita tarefa com prazo no passado (red)"
```

**GREEN (código mínimo)**
3. Em `validacao.py`, escreva o mínimo de código para o teste passar.
4. Rode os testes e confirme que **TODOS passam**.
```bash
git add validacao.py
git commit -m "feat: valida prazo no passado (green)"
```

**REFACTOR (melhorar sem quebrar)**
5. Melhore o código (nomes, organização) e rode os testes de novo.
```bash
git add .
git commit -m "refactor: organiza validação de prazo (refactor)"
```

**Integrar**
```bash
git push -u origin feature/prazo-no-passado
```
No GitHub, abra um **Pull Request** e faça o **merge** na `main`. Depois:
```bash
git checkout main
git pull
```

Dica para pensar: ao criar essa regra, algum teste que já existe vai quebrar? Por quê?

## 5. Comandos úteis
| Comando | Para que serve |
|---|---|
| `git status` | Ver o que mudou |
| `git log --oneline` | Ver o histórico resumido |
| `git diff` | Ver as mudanças linha a linha |
| `git branch` | Listar as branches |
