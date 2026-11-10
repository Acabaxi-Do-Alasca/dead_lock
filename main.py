"""Ponto de entrada do simulador do Algoritmo do Banqueiro.

Uso (de preferência a partir de um terminal, para acompanhar o log):
    python main.py

A janela do simulador abre e, no terminal onde o comando foi executado,
cada passo do algoritmo é impresso em tempo real (terminal de log). Uma
cópia do log também é gravada em logs/simulacao.log.
"""

import os
import tkinter as tk

from gui.app import App
from simulation.terminal_log import print_banner, setup_terminal_log

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    setup_terminal_log(log_dir=os.path.join(PROJECT_DIR, "logs"))
    print_banner()
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
