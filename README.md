# Simulador do Algoritmo do Banqueiro

Simulador em Python (Tkinter + matplotlib + networkx) de um gerenciador de
deadlocks focado no Algoritmo do Banqueiro. Mostra visualmente o grafo de
alocação de recursos, as matrizes de estado (Allocation, Max, Need,
Available) e, num terminal de log, o raciocínio do algoritmo passo a passo.

O simulador cobre as três estratégias contra deadlock:

- **Prevenção**: em modo Protegido, o Banqueiro só concede uma requisição se
  o estado continuar seguro. Caso contrário, desfaz a alocação (rollback).
- **Detecção**: em modo Livre o deadlock pode acontecer de verdade, e o
  algoritmo de detecção identifica quais processos estão presos.
- **Tratamento**: a recuperação escolhe um processo-vítima, o aborta e repassa
  os recursos liberados a quem esperava, quebrando o ciclo.

## Requisitos

- Python 3.10+
- `matplotlib` e `networkx` (verifique com `pip show matplotlib networkx`;
  se faltar, instale com `pip install matplotlib networkx`)
- `tkinter` (já vem com a instalação padrão do Python no Windows)

## Como executar

Rode a partir de um terminal para acompanhar o log:

```bash
python main.py
```

A janela do simulador abre e o terminal mostra cada passo do algoritmo em
tempo real, no formato `[passo] CATEGORIA | mensagem`, com uma cor por
categoria. Uma cópia do log é gravada em `logs/simulacao.log`.

## Como rodar os testes

```bash
python -m unittest discover -s tests -v
```

## Como forçar e tratar um deadlock (Cenário C)

1. Aba **Cenários prontos** → **Carregar Cenário C** (ele abre em modo Livre).
2. Na aba **Simulação**, faça os pedidos: P0 → (0,1,0), P1 → (0,0,1),
   P2 → (1,0,0). O ciclo aparece em vermelho no grafo.
3. **Verificar Deadlock (detecção)**: confirma P0, P1 e P2 em deadlock.
4. **Recuperar do Deadlock (abortar vítima)**: aborta P0, repassa R0 para P2
   e o ciclo some.

## Abas da aplicação

- **Configuração**: cadastro manual de recursos e processos (Allocation
  sempre começa zerada).
- **Simulação**: grafo de alocação de recursos, matrizes Allocation/Need/
  Available e formulário para fazer requisições, finalizar processos e
  alternar entre modo Protegido e Livre. No modo Livre aparecem os botões
  de detecção e de recuperação.
- **Log / Histórico**: o mesmo raciocínio do terminal de log, em tabela, e
  uma linha do tempo com snapshots do estado.
- **Cenários prontos**: A) estado seguro clássico, B) requisição negada por
  levar a estado inseguro, C) deadlock real forçado em modo Livre.
- **Ajuda**: a analogia do corredor estreito da escola e as 4 condições
  necessárias para deadlock.

## Onde está cada parte no código

| O que | Onde |
|---|---|
| Prevenção (Banqueiro) | `core/banker.py` com `request_algorithm()` e `safety_algorithm()` |
| Detecção | `core/detection.py` com `detect_deadlock()` |
| Tratamento | `simulation/engine.py` com `recover_from_deadlock()` |
| Terminal de log | `simulation/terminal_log.py` |

```
core/         lógica pura do Algoritmo do Banqueiro e da detecção (sem GUI)
simulation/   motor de simulação (modos, recuperação, histórico, terminal de log)
scenarios/    definição e carregamento dos 3 cenários prontos
gui/          interface Tkinter
tests/        suíte de testes unitários
docs/         script e imagens do manual (Manual_Simulador_Banqueiro.docx)
```
