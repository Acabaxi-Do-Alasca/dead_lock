# Simulador do Algoritmo do Banqueiro

Simulador em Python (Tkinter + matplotlib + networkx) do Algoritmo do
Banqueiro para alocação de recursos e prevenção de deadlock. Mostra
visualmente o grafo de alocação de recursos, as matrizes de estado
(Allocation, Max, Need, Available) e um log detalhado do raciocínio do
algoritmo a cada requisição.

## Requisitos

- Python 3.10+
- `matplotlib` e `networkx` (verifique com `pip show matplotlib networkx`;
  se faltar, instale com `pip install matplotlib networkx`)
- `tkinter` (já vem com a instalação padrão do Python no Windows)

## Como executar

```bash
python main.py
```

## Como rodar os testes

```bash
python -m unittest discover -s tests -v
```

## Abas da aplicação

- **Configuração**: cadastro manual de recursos e processos (Allocation
  sempre começa zerada).
- **Simulação**: grafo de alocação de recursos, matrizes Allocation/Need/
  Available e formulário para fazer requisições, finalizar processos e
  alternar entre modo Protegido (com verificação de segurança) e Livre (sem
  prevenção, para demonstrar deadlock de verdade).
- **Log / Histórico**: raciocínio passo a passo do algoritmo (Safety
  Algorithm, Resource-Request Algorithm, detecção de deadlock) e uma linha do
  tempo com snapshots do estado.
- **Cenários prontos**: três cenários pré-configurados --
  A) estado seguro clássico, B) uma requisição negada por levar a estado
  inseguro, C) deadlock real por espera circular em modo Livre.
- **Ajuda**: a analogia do corredor estreito da escola e as 4 condições
  necessárias para deadlock.

## Estrutura do projeto

```
core/         lógica pura do Algoritmo do Banqueiro (sem GUI)
simulation/   motor de simulação (modos Protegido/Livre, histórico)
scenarios/    definição e carregamento dos 3 cenários prontos
gui/          interface Tkinter
tests/        suíte de testes unitários
```
