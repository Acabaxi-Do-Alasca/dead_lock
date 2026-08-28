"""Aba de Ajuda: analogia do corredor estreito e explicação conceitual."""

import tkinter as tk
from tkinter import ttk

HELP_TEXT = """\
A analogia do corredor estreito da escola
------------------------------------------
Imagine um corredor estreito da escola, largo o bastante para uma pessoa por
vez. Dois grupos de amigos entram em direções opostas. Se cada grupo avançar
segurando sua posição e esperando o outro "dar espaço", os dois grupos ficam
parados, cada um esperando um recurso (o espaço livre do corredor) que só o
outro pode liberar. Ninguém andou errado sozinho -- o problema é a combinação
das decisões de todos.

Esse é exatamente o cenário de deadlock em um sistema operacional: processos
(os grupos de amigos) disputam recursos (o espaço do corredor) e cada um
segura o que já tem enquanto espera o que falta. O Algoritmo do Banqueiro é
como um monitor no corredor que, antes de deixar alguém avançar, verifica se
ainda existe uma forma de todo mundo terminar de passar sem travar. Se não
existir, ele barra a pessoa ali mesmo -- mesmo que nesse instante o corredor
pareça ter espaço.

As 4 condições necessárias para deadlock
------------------------------------------
Um deadlock só pode ocorrer se as quatro condições abaixo estiverem
presentes ao mesmo tempo:

1. Exclusão mútua -- o recurso só pode ser usado por um processo por vez
   (só cabe uma pessoa de cada vez num certo trecho do corredor).
2. Posse e espera -- um processo mantém os recursos que já tem enquanto
   espera por outros (o grupo não recua, fica parado onde está segurando o
   espaço que já ocupou).
3. Não preempção -- um recurso não pode ser tomado à força de um processo,
   só ele pode liberá-lo voluntariamente (ninguém pode empurrar o outro
   grupo para trás).
4. Espera circular -- existe uma cadeia circular de processos, cada um
   esperando um recurso retido pelo próximo da cadeia (grupo A espera o
   espaço do grupo B, que espera o espaço do grupo A).

O Algoritmo do Banqueiro previne o deadlock atacando a condição de espera
circular: antes de conceder uma requisição, ele simula a alocação e roda o
Safety Algorithm para garantir que sempre existirá uma ordem em que todos os
processos conseguem terminar. Se a requisição levaria a um estado onde
nenhuma ordem assim existe (estado inseguro), ela é negada e desfeita.

Estado seguro vs. inseguro vs. deadlock
------------------------------------------
- Estado seguro: existe pelo menos uma sequência de execução em que todos os
  processos conseguem obter o que faltam e terminar.
- Estado inseguro: não existe garantia de tal sequência -- não significa que
  já há deadlock, mas que ele se tornou possível dependendo do que cada
  processo pedir a seguir. É por isso que o Banqueiro nega requisições que
  levam a um estado inseguro, mesmo sem haver deadlock ainda.
- Deadlock: uma espera circular já se formou de fato -- os processos
  envolvidos nunca mais progridem sozinhos.

Neste simulador, o modo "Protegido" nunca deixa o sistema chegar a um
deadlock, pois recusa qualquer requisição que levaria a um estado inseguro.
O modo "Livre" desliga essa proteção para você poder observar, na aba
Cenários (Cenário C), uma espera circular real se formando e sendo
confirmada pelo algoritmo de detecção de deadlock.
"""


class HelpTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        text_frame = ttk.Frame(self)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        text = tk.Text(text_frame, wrap="word", padx=10, pady=10, font=("Segoe UI", 10))
        vsb = ttk.Scrollbar(text_frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=vsb.set)
        text.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        text.insert("1.0", HELP_TEXT)
        text.configure(state="disabled")
