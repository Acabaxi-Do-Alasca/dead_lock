"""Ponto de entrada do simulador do Algoritmo do Banqueiro.

Uso:
    python main.py
"""

import tkinter as tk

from gui.app import App


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
