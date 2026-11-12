"""Gera o Guia de Apresentação (manual de uso + roteiro de fala) em .docx/.pdf.

Material de apoio do grupo para a apresentação -- não é a documentação formal
de entrega (essa é gerada por build_documentacao.py).

Uso: python docs/build_manual.py
Gera: Manual_Simulador_Banqueiro.docx e .pdf na raiz do projeto.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docx.shared import Pt  # noqa: E402

from docx_helpers import (  # noqa: E402
    CAPA_CAMPOS, PROJECT_DIR, add_bullets, add_code_block, add_heading, add_image, add_para, add_qa,
    add_steps, add_summary, add_table, add_title_page, capture_terminal_log_of_scenario_c,
    new_doc, save_with_pdf,
)

OUT_PATH = os.path.join(PROJECT_DIR, "Manual_Simulador_Banqueiro.docx")

doc = new_doc()
add_title_page(
    doc,
    "Simulador do Algoritmo do Banqueiro",
    "Manual de Uso e Guia de Apresentação",
    "Prevenção de deadlock por alocação de recursos: como o simulador funciona, "
    "como operá-lo e um roteiro pronto para apresentar em sala.",
    CAPA_CAMPOS,
)

add_summary(doc, [
    "1. Introdução",
    "2. Conceitos fundamentais (deadlock e o Algoritmo do Banqueiro)",
    "3. Visão geral do programa",
    "4. Guia de uso passo a passo",
    "5. Demonstração guiada dos três cenários prontos",
    "6. Roteiro sugerido para a apresentação",
    "7. Perguntas frequentes esperadas",
    "8. Detalhes técnicos do projeto",
    "9. Conclusão",
])

# 1. Introdução -------------------------------------------------------------
add_heading(doc, "1. Introdução")
add_para(
    doc,
    "Em um sistema operacional, vários processos disputam recursos limitados "
    "(memória, arquivos, impressoras, e assim por diante). Quando um processo "
    "retém um recurso e espera por outro que está retido por um segundo "
    "processo -- que por sua vez espera por algo retido pelo primeiro -- "
    "nenhum dos dois consegue prosseguir. Esse travamento permanente é "
    "chamado de deadlock (impasse)."
)
add_para(
    doc,
    "Este projeto implementa e visualiza o Algoritmo do Banqueiro, uma "
    "estratégia clássica (Dijkstra) para prevenir deadlocks: antes de "
    "conceder qualquer requisição de recurso, o algoritmo simula a alocação "
    "e verifica se ainda existe uma sequência em que todos os processos "
    "conseguem terminar. Se não existir, a requisição é negada."
)
add_para(
    doc,
    "Este documento serve para duas coisas: (1) ensinar a operar o "
    "simulador passo a passo, com telas reais do programa, e (2) fornecer "
    "um roteiro pronto -- com explicações, ordem sugerida e perguntas "
    "esperadas -- para apresentar o trabalho em sala de aula."
)

# 2. Conceitos fundamentais --------------------------------------------------
add_heading(doc, "2. Conceitos Fundamentais")

add_heading(doc, "2.1 A analogia do corredor estreito", level=2)
add_para(
    doc,
    "Imagine um corredor estreito da escola, largo o bastante para uma "
    "pessoa por vez. Dois grupos de amigos entram em direções opostas. Se "
    "cada grupo segurar sua posição esperando o outro \"dar espaço\", os "
    "dois ficam parados -- cada um esperando um recurso (o espaço livre do "
    "corredor) que só o outro pode liberar. Ninguém andou errado sozinho: o "
    "problema é a combinação das decisões de todos. É exatamente essa a "
    "situação que o Algoritmo do Banqueiro evita entre processos e recursos."
)

add_heading(doc, "2.2 As quatro condições necessárias para deadlock", level=2)
add_para(doc, "Um deadlock só ocorre se estas quatro condições estiverem presentes ao mesmo tempo:")
add_bullets(doc, [
    "Exclusão mútua -- o recurso só pode ser usado por um processo por vez.",
    "Posse e espera -- um processo mantém o que já tem enquanto espera por mais.",
    "Não preempção -- ninguém pode tomar à força um recurso de outro processo.",
    "Espera circular -- existe uma cadeia circular de processos, cada um esperando um recurso retido pelo próximo.",
], numbered=True)
add_para(
    doc,
    "O Algoritmo do Banqueiro ataca diretamente a condição de espera "
    "circular: ele nunca concede uma requisição que possa, no futuro, levar "
    "a essa cadeia fechada."
)

add_heading(doc, "2.3 Estado seguro, estado inseguro e deadlock", level=2)
add_bullets(doc, [
    "Estado seguro: existe pelo menos uma ordem em que todos os processos conseguem terminar.",
    "Estado inseguro: não há garantia dessa ordem -- ainda não é um deadlock, mas já é arriscado o suficiente para o Banqueiro recusar a próxima requisição perigosa.",
    "Deadlock: a espera circular já aconteceu de fato -- os processos envolvidos nunca mais progridem sozinhos.",
])

add_heading(doc, "2.4 As matrizes do algoritmo", level=2)
add_bullets(doc, [
    "Allocation -- quanto cada processo já está segurando de cada recurso.",
    "Max -- o máximo que cada processo pode vir a pedir (declarado no início).",
    "Need = Max − Allocation -- quanto cada processo ainda pode precisar.",
    "Available -- quanto sobrou livre de cada recurso.",
])
add_para(
    doc,
    "A cada requisição, o simulador testa, para cada processo ainda não "
    "finalizado, se Need <= Work (o que está livre no momento do teste). Se "
    "sim, aquele processo poderia terminar e devolver tudo que tem, "
    "aumentando o Work disponível para os próximos. Se, no final da "
    "varredura, todos os processos puderem ser encaixados nessa ordem, o "
    "estado é seguro."
)

add_image(doc, "13_ajuda.png", "Aba Ajuda do simulador, com a analogia do corredor e as 4 condições de deadlock.")

# 3. Visão geral --------------------------------------------------------------
doc.add_page_break()
add_heading(doc, "3. Visão Geral do Programa")
add_para(
    doc,
    "O simulador é um programa Python de janela única (Tkinter), com o "
    "grafo desenhado via matplotlib/networkx, organizado em 5 abas:"
)
add_table(doc, ["Aba", "O que faz"], [
    ["Configuração", "Cadastro manual de recursos e processos; inicia uma simulação do zero (Allocation = 0)."],
    ["Simulação", "Grafo de alocação de recursos, matrizes Allocation/Need/Available e formulário de requisição."],
    ["Log / Histórico", "Raciocínio passo a passo do algoritmo e uma linha do tempo com snapshots do estado."],
    ["Cenários prontos", "Três cenários pré-configurados para carregar com um clique (A, B e C)."],
    ["Ajuda", "A analogia do corredor e a explicação das condições de deadlock."],
], col_widths_cm=[4, 12])
add_para(
    doc,
    "Além da janela, o próprio terminal onde o programa foi aberto funciona "
    "como terminal de log: cada passo do algoritmo é impresso ali, em tempo "
    "real e com cores por categoria (ver seções 4.3 e 5.3)."
)

add_heading(doc, "Como executar", level=2)
add_para(
    doc,
    "Abra um terminal (Prompt de Comando, PowerShell ou o terminal do "
    "PyCharm/VS Code) dentro da pasta do projeto, com Python 3.10+ instalado, e rode:"
)
p = doc.add_paragraph()
run = p.add_run("python main.py")
run.font.name = "Consolas"
run.font.size = Pt(11)
add_para(
    doc,
    "A janela do simulador abre e o terminal passa a mostrar o log. Deixe os "
    "dois lado a lado durante a apresentação. Uma cópia do log também é "
    "gravada em logs/simulacao.log (recriado a cada execução)."
)
add_para(
    doc,
    "É necessário ter as bibliotecas matplotlib e networkx instaladas "
    "(tkinter já vem com o Python no Windows). Para rodar os testes "
    "automatizados do algoritmo:"
)
p = doc.add_paragraph()
run = p.add_run("python -m unittest discover -s tests -v")
run.font.name = "Consolas"
run.font.size = Pt(11)

# 4. Guia de uso ----------------------------------------------------------
doc.add_page_break()
add_heading(doc, "4. Guia de Uso Passo a Passo")

add_heading(doc, "4.1 Aba Configuração -- montando uma simulação do zero", level=2)
add_para(doc, "A aba começa vazia, com um formulário para recursos e outro para processos:")
add_image(doc, "01_config_vazia.png", "Aba Configuração, ainda vazia.")

add_para(doc, "1. Cadastre um recurso: digite um nome e a quantidade total de instâncias, e clique em \"Adicionar Recurso\".")
add_image(doc, "02_config_recursos.png", "Dois recursos (A e B) já cadastrados.")

add_para(doc, "2. Cadastre um processo: digite um nome e, para cada recurso já cadastrado, o máximo que esse processo pode vir a pedir. Clique em \"Adicionar Processo\".")
add_image(doc, "03_config_processos.png", "Dois processos (P0 e P1) já cadastrados, cada um com seu vetor Max.")

add_para(doc, "3. Clique em \"Iniciar Simulação (Allocation = 0)\". O programa monta o estado inicial -- todos os processos começam sem nenhum recurso alocado -- e leva você para a aba Simulação.")
add_image(doc, "04_simulacao_manual_iniciada.png", "Simulação recém-iniciada: Allocation zerada, grafo sem nenhuma seta ainda.")

add_heading(doc, "4.2 Aba Simulação -- o grafo, as matrizes e o formulário de requisição", level=2)
add_para(doc, "É a tela principal, dividida em duas partes:")
add_bullets(doc, [
    "À esquerda: o Grafo de Alocação de Recursos. Círculos são processos, quadrados são recursos (com \"livre/total\" escrito dentro). Setas pretas cheias indicam alocação (recurso -> processo); setas vermelhas tracejadas indicam um pedido pendente ou negado (processo -> recurso).",
    "À direita: as tabelas Allocation, Need e Available, sempre atualizadas, e o formulário para escolher um processo, digitar quanto de cada recurso ele está pedindo, e clicar em \"Solicitar\".",
])
add_para(
    doc,
    "As cores dos processos também têm significado: verde é pronto/executando, "
    "amarelo é bloqueado (esperando um recurso), cinza é terminado e "
    "vermelho é abortado (vítima escolhida para quebrar um deadlock)."
)
add_image(doc, "05_simulacao_manual_pedido.png", "Depois de um pedido concedido: a Allocation do processo escolhido aumentou e o Available diminuiu.")
add_para(
    doc,
    "Repare também nos dois botões de rádio \"Protegido (com Banqueiro)\" e "
    "\"Livre (sem prevenção)\": eles alternam se o simulador vai verificar "
    "segurança antes de conceder cada pedido ou não -- isso é essencial para "
    "o Cenário C, explicado adiante."
)

add_heading(doc, "4.3 O log do algoritmo -- aba Log / Histórico e terminal de log", level=2)
add_para(
    doc,
    "Toda vez que algo acontece (um pedido, uma negação, uma detecção ou um "
    "tratamento de deadlock), o programa registra cada etapa do raciocínio: "
    "quais comparações Need <= Work foram feitas, se cada processo pôde "
    "prosseguir, e a conclusão final. Esse mesmo registro aparece em dois "
    "lugares:"
)
add_bullets(doc, [
    "Na aba Log / Histórico, em forma de tabela, com filtro por categoria. Do lado direito fica a linha do tempo (timeline): clicando em um evento, é possível ver como as matrizes estavam naquele momento.",
    "No terminal onde o programa foi aberto (terminal de log), linha por linha e em tempo real, no formato [passo] CATEGORIA | mensagem, com uma cor por categoria e uma linha separadora a cada nova requisição. Um exemplo real está na seção 5.3.",
])
add_table(doc, ["Categoria", "Significado"], [
    ["REQUEST", "Um processo pediu recursos."],
    ["SAFETY_CHECK", "Safety Algorithm testando Need[i] <= Work para um processo."],
    ["RELEASE", "Processo terminaria (na simulação) e devolveria seus recursos ao Work."],
    ["RESULT", "Conclusão de uma verificação: estado seguro/inseguro, deadlock ou não."],
    ["GRANT / DENY", "Requisição concedida / não atendida no momento."],
    ["ROLLBACK", "Alocação tentativa desfeita porque levaria a estado inseguro (prevenção)."],
    ["DEADLOCK_CHECK", "Algoritmo de detecção testando o pedido pendente de um processo."],
    ["RECOVERY / ABORT", "Tratamento do deadlock: escolha da vítima e aborto do processo."],
], col_widths_cm=[4, 12])

add_heading(doc, "4.4 Aba Cenários prontos", level=2)
add_para(
    doc,
    "A forma mais rápida de demonstrar o simulador: três botões, cada um "
    "carregando uma situação já configurada (explicados em detalhe na "
    "seção 5)."
)

add_heading(doc, "4.5 Aba Ajuda", level=2)
add_para(doc, "Contém a analogia do corredor e a explicação das quatro condições de deadlock, útil para consultar durante a apresentação (ver Figura 1).")

# 5. Cenários ----------------------------------------------------------------
doc.add_page_break()
add_heading(doc, "5. Demonstração Guiada dos Três Cenários")
add_para(
    doc,
    "Esta é a parte mais importante para a apresentação: os três cenários "
    "prontos mostram, na prática, um estado seguro, uma negação (prevenção) "
    "e um deadlock real sendo forçado, detectado e tratado."
)

add_heading(doc, "5.1 Cenário A -- Estado seguro (exemplo clássico)", level=2)
add_para(
    doc,
    "5 processos disputando 3 tipos de recursos (A=10, B=5, C=7). Ao "
    "carregar, o estado já é seguro: existe uma sequência de execução -- "
    "<P1, P3, P4, P0, P2> -- em que todos os processos conseguem terminar "
    "sem travar. Esse é o exemplo clássico do livro de Sistemas "
    "Operacionais (Silberschatz)."
)
add_image(doc, "06_cenario_a.png", "Cenário A carregado: grafo, matrizes Allocation/Need/Available e status \"pronto\" para todos os processos.")
add_para(doc, "O que dizer na apresentação: mesmo com vários processos precisando de bastante recurso (veja a coluna Need), sempre existe alguém que pode terminar primeiro e devolver o que usou, destravando os próximos -- por isso o estado é seguro.")

add_heading(doc, "5.2 Cenário B -- Requisição negada (estado inseguro)", level=2)
add_para(
    doc,
    "3 processos disputando 2 recursos (A=3, B=3). O estado inicial é "
    "seguro, mas a descrição do cenário sugere um pedido perigoso: o "
    "processo P1 solicitando (1, 0)."
)
add_image(doc, "07_cenario_b_inicial.png", "Cenário B logo após carregar -- ainda em estado seguro.")
add_para(doc, "Ao ir na aba Simulação, escolher P1, digitar 1 no primeiro recurso e 0 no segundo, e clicar em Solicitar, o pedido é negado:")
add_image(doc, "08_cenario_b_negado.png", "Pedido de P1 negado: a Allocation voltou exatamente ao que era antes (rollback), P1 aparece bloqueado (amarelo) com uma seta vermelha tracejada pendente.")
add_para(doc, "Na aba Log, é possível mostrar o motivo exato:")
add_image(doc, "09_cenario_b_log.png", "Log do Cenário B: cada comparação Need <= Work aparece, terminando em \"Estado INSEGURO\" e \"ROLLBACK\".")
add_para(doc, "O que dizer na apresentação: mesmo havendo recurso disponível na hora do pedido, o Banqueiro enxerga à frente e percebe que, se conceder, ninguém mais conseguiria progredir depois -- por isso prefere negar e desfazer a alocação (rollback) a arriscar um travamento.")

add_heading(doc, "5.3 Cenário C -- Deadlock real por espera circular (modo Livre)", level=2)
add_para(
    doc,
    "3 processos e 3 recursos de instância única, cada um já alocado por "
    "um processo diferente. Esse cenário carrega automaticamente em modo "
    "Livre -- ou seja, sem a proteção do Banqueiro -- exatamente para "
    "mostrar o que aconteceria sem o algoritmo."
)
add_image(doc, "10_cenario_c_inicial.png", "Cenário C recém-carregado: cada processo já segura um recurso, Available = 0 em tudo.")
add_para(
    doc,
    "Seguindo os pedidos sugeridos na descrição do cenário (P0 pede o "
    "recurso de P1, P1 pede o de P2, e P2 pede o de P0), as três "
    "requisições ficam pendentes e fecham um ciclo:"
)
add_image(doc, "11_cenario_c_ciclo.png", "As três requisições fecham um ciclo -- destacado em vermelho no grafo -- e o título já avisa \"CICLO DETECTADO\".")

add_heading(doc, "Detecção", level=3)
add_para(
    doc,
    "Clicando em \"Verificar Deadlock (detecção)\" (role o painel da "
    "direita até o fim para ver os botões), o algoritmo de detecção "
    "(core/detection.py) confirma formalmente o travamento. Ele parte do que "
    "está livre (Work = Available = [0, 0, 0]) e testa, para cada processo, "
    "se o pedido pendente cabe em Work. Nenhum cabe, então nenhum processo "
    "pode ser atendido, terminar e liberar o que segura: os três ficam com "
    "Finish = False -- DEADLOCK detectado em P0, P1 e P2."
)

add_heading(doc, "Tratamento", level=3)
add_para(
    doc,
    "Clicando em \"Recuperar do Deadlock (abortar vítima)\", o simulador "
    "trata a situação por recuperação por término de processo "
    "(recover_from_deadlock, em simulation/engine.py):"
)
add_steps(doc, [
    "Detecta de novo quais processos estão em deadlock.",
    "Escolhe uma vítima: o processo em deadlock que retém MENOS recursos (menor custo para abortar). Como os três retêm 1 recurso cada, o desempate é pelo menor índice: P0.",
    "Aborta P0: o recurso R0 que ele segurava volta para Available.",
    "Reavalia os processos bloqueados: P2 esperava justamente R0, então recebe o recurso e volta a executar.",
    "Detecta de novo: agora P2 pode terminar e liberar R2, que é o que P1 espera -- não há mais ciclo. Se ainda houvesse deadlock, o processo se repetiria com uma nova vítima.",
])
add_image(doc, "14_cenario_c_recuperado.png", "Depois do tratamento: P0 abortado (vermelho, sem recursos), P2 executando com R0 e R2, P1 apenas esperando R2 -- o ciclo foi quebrado.")
add_image(doc, "12_cenario_c_log.png", "Aba Log após o tratamento: detecção, escolha da vítima, aborto, repasse do recurso e a nova verificação concluindo \"Nenhum deadlock detectado\".")

add_heading(doc, "O mesmo raciocínio no terminal de log", level=3)
add_para(
    doc,
    "Esta é a saída real do terminal para o Cenário C inteiro -- forçar o "
    "deadlock, detectar e tratar (gerada executando o próprio simulador):"
)
add_code_block(doc, capture_terminal_log_of_scenario_c())

add_para(
    doc,
    "O que dizer na apresentação: aqui aparecem as três estratégias contra "
    "deadlock. Em modo Protegido o Banqueiro PREVINE -- a segunda ou "
    "terceira requisição teria sido negada antes de o ciclo se fechar, como "
    "no Cenário B. Em modo Livre o deadlock acontece, o algoritmo de "
    "detecção o IDENTIFICA (ninguém consegue ser atendido) e a recuperação o "
    "TRATA abortando o processo mais barato e repassando seus recursos."
)

# 6. Roteiro -------------------------------------------------------------------
doc.add_page_break()
add_heading(doc, "6. Roteiro Sugerido para a Apresentação")
add_para(
    doc,
    "O trabalho será avaliado em dois pontos: (1) os logs e o código -- "
    "código bem documentado e um terminal de log mostrando o algoritmo passo "
    "a passo; e (2) a apresentação -- rodar o simulador, forçar um deadlock e "
    "explicar como o código o detectou e tratou. O roteiro abaixo (cerca de "
    "10 a 12 minutos) cobre os dois."
)
add_para(
    doc,
    "Antes de começar: abra um terminal na pasta do projeto, rode python "
    "main.py e deixe o terminal visível ao lado da janela do simulador.",
    bold=True,
)
add_table(doc, ["Tempo", "O que fazer", "O que falar"], [
    ["~1 min", "Abrir na aba Ajuda", "Contar a analogia do corredor e citar as 4 condições de deadlock."],
    ["~2 min", "Carregar Cenário A", "Explicar Allocation/Max/Need/Available e por que esse estado é seguro."],
    ["~2 min", "Carregar Cenário B e fazer o pedido de P1 (1, 0)", "Mostrar a negação no grafo e o raciocínio linha a linha no terminal de log: PREVENÇÃO pelo Banqueiro (rollback)."],
    ["~3 min", "Carregar Cenário C, fazer os 3 pedidos, clicar em Verificar Deadlock e depois em Recuperar do Deadlock", "Forçar o deadlock (ciclo em vermelho), mostrar a DETECÇÃO no terminal (ninguém cabe em Work) e o TRATAMENTO (vítima P0 abortada, R0 repassado a P2, ciclo quebrado)."],
    ["~2 min", "Mostrar o código (seção 8)", "Abrir core/banker.py, core/detection.py e recover_from_deadlock em simulation/engine.py; apontar os comentários Passo 1, Passo 2... que seguem o livro-texto."],
    ["~1 min", "Encerramento", "Resumir: em modo Protegido o Banqueiro nunca deixa o deadlock acontecer; sem proteção, o sistema detecta e se recupera dele."],
], col_widths_cm=[2.2, 6.3, 7.5])
add_para(doc, "Dica: pratique a sequência de cliques antes da apresentação (Cenários prontos -> Simulação -> Log) para não perder tempo procurando os botões na hora. Os botões de detecção e recuperação só aparecem no modo Livre, no fim do painel da direita (role para baixo).")

# 7. Perguntas frequentes -------------------------------------------------------
doc.add_page_break()
add_heading(doc, "7. Perguntas Frequentes Esperadas")
add_qa(doc,
    "Por que o Banqueiro nega um pedido se, naquele instante, existe recurso disponível?",
    "Porque \"ter disponível agora\" não é suficiente -- o algoritmo simula a concessão e verifica se, depois dela, ainda existe alguma ordem em que todos os processos conseguem terminar. Se não existir, é arriscado demais conceder.")
add_qa(doc,
    "Qual a diferença entre estado inseguro e deadlock?",
    "Estado inseguro é quando não há garantia de uma sequência segura -- pode ou não terminar em deadlock, dependendo do que cada processo pedir depois. Deadlock é quando a espera circular já aconteceu de fato e ninguém mais progride sozinho.")
add_qa(doc,
    "Como o simulador consegue mostrar um deadlock de verdade, se o Banqueiro sempre previne?",
    "Existe um modo \"Livre\", usado no Cenário C, que desliga a verificação de segurança de propósito, só para fins didáticos -- assim é possível ver a espera circular se formando e sendo confirmada por um algoritmo de detecção separado.")
add_qa(doc,
    "Depois de detectar o deadlock, como o código trata a situação?",
    "Por recuperação por término de processo: escolhe uma vítima entre os processos em deadlock, aborta-a (os recursos dela voltam para Available), repassa esses recursos a quem estava bloqueado esperando por eles e roda a detecção de novo. Se ainda houver deadlock, escolhe outra vítima; se não, o tratamento termina.")
add_qa(doc,
    "Por que a vítima foi o P0?",
    "O critério é abortar o processo que retém menos recursos, ou seja, o de menor custo. No Cenário C os três retêm 1 recurso cada, então o desempate é pelo menor índice. Abortar um só já basta, porque isso quebra o ciclo.")
add_qa(doc,
    "Abortar um processo não é perder trabalho?",
    "Sim, por isso a recuperação é o último recurso e o critério tenta minimizar a perda. É justamente a vantagem do Banqueiro: em modo Protegido o deadlock nunca chega a acontecer, então ninguém precisa ser abortado.")
add_qa(doc,
    "O que acontece quando uma requisição é negada -- os recursos ficam perdidos?",
    "Não. O simulador testa a alocação, e se o resultado for inseguro, desfaz exatamente essa tentativa (rollback) -- as matrizes voltam a ser idênticas ao estado anterior ao pedido.")
add_qa(doc,
    "Esse algoritmo é usado em sistemas operacionais reais?",
    "O Algoritmo do Banqueiro é mais um modelo teórico/didático (proposto por Edsger Dijkstra) do que uma solução usada diretamente em SOs de propósito geral, porque exige saber de antemão o máximo que cada processo vai precisar -- algo raramente conhecido na prática. Sistemas reais tendem a usar outras estratégias, como detecção e recuperação, ou simplesmente evitar ciclos de espera por convenção (ex.: sempre pedir recursos em uma mesma ordem).")
add_qa(doc,
    "Por que as matrizes usam o vetor Need em vez de Max diretamente?",
    "Need = Max − Allocation representa o que falta, que é exatamente o que interessa para saber se um processo consegue terminar com o que ainda está disponível (Work).")

# 8. Detalhes técnicos ------------------------------------------------------
doc.add_page_break()
add_heading(doc, "8. Detalhes Técnicos do Projeto")
add_para(doc, "Para quem quiser (ou for perguntado sobre) a implementação:")
add_bullets(doc, [
    "Linguagem: Python 3, interface gráfica com Tkinter.",
    "Grafo de alocação: matplotlib + networkx, embutido na janela.",
    "core/ -- lógica pura do algoritmo (Safety Algorithm, Resource-Request Algorithm, detecção de deadlock), sem nenhuma dependência de interface gráfica.",
    "simulation/ -- motor de simulação: modos Protegido e Livre, tratamento (recuperação) de deadlock, histórico de eventos e o terminal de log.",
    "scenarios/ -- definição dos três cenários prontos (A, B e C).",
    "gui/ -- as cinco abas da interface.",
    "tests/ -- 41 testes automatizados cobrindo o algoritmo (incluindo o caso clássico do livro-texto, o teste de rollback exato, a recuperação do Cenário C e a prova de que o Banqueiro impede esse ciclo).",
])
add_para(doc, "Para rodar toda a suíte de testes e ver cada verificação passando:")
p = doc.add_paragraph()
run = p.add_run("python -m unittest discover -s tests -v")
run.font.name = "Consolas"
run.font.size = Pt(11)

add_heading(doc, "Mapa do código: onde está cada parte", level=2)
add_para(doc, "Use esta tabela para abrir o arquivo certo quando perguntarem \"onde no código isso acontece?\":")
add_table(doc, ["O que", "Onde no código"], [
    ["Prevenção (Algoritmo do Banqueiro)", "core/banker.py -- request_algorithm() (Passos 1 a 5b) e safety_algorithm() (Passos 1 a 4)"],
    ["Rollback de uma requisição insegura", "core/banker.py -- Passo 5b (state.restore) e core/state.py -- clone() / restore()"],
    ["Detecção de deadlock", "core/detection.py -- detect_deadlock() (Passos 1 a 4); chamado por check_deadlock() em simulation/engine.py"],
    ["Tratamento (recuperação)", "simulation/engine.py -- recover_from_deadlock(), _choose_victim(), _abort_process() e _retry_pending()"],
    ["Modo Livre (forçar deadlock)", "simulation/engine.py -- _request_free()"],
    ["Terminal de log", "simulation/terminal_log.py (formato e cores) e core/state.py -- _append(), que envia cada passo ao logger"],
    ["Grafo e destaque do ciclo", "gui/graph_view.py -- draw_rag() e _find_cycle_edges()"],
], col_widths_cm=[5, 11])
add_para(
    doc,
    "Todos os módulos têm um texto de abertura (docstring) explicando seu "
    "papel, e os algoritmos têm comentários Passo 1, Passo 2... que "
    "seguem a numeração do livro-texto (Silberschatz)."
)

# 9. Conclusão ------------------------------------------------------------------
doc.add_page_break()
add_heading(doc, "9. Conclusão")
add_para(
    doc,
    "O simulador cobre, de ponta a ponta, o ciclo pedido pelo trabalho: "
    "simular múltiplos processos disputando recursos, implementar o "
    "Algoritmo do Banqueiro completo (incluindo o Safety Algorithm), "
    "visualizar o grafo de alocação, representar as matrizes de estado, "
    "demonstrar cenários que levam a deadlock e como são prevenidos, "
    "detectar e tratar um deadlock real, e registrar no terminal de log o "
    "raciocínio de cada decisão."
)
add_para(
    doc,
    "Para a apresentação, o caminho mais direto é: Ajuda -> Cenário A -> "
    "Cenário B (prevenção: pedido negado) -> Cenário C (deadlock forçado, "
    "detectado e tratado) -> código. Esse percurso, acompanhado do terminal "
    "de log, já conta toda a história do algoritmo."
)

save_with_pdf(doc, OUT_PATH)
