"""Janela raiz da aplicação: monta o Notebook com as 5 abas."""

import tkinter as tk
from tkinter import ttk

from gui.tab_config import ConfigTab
from gui.tab_help import HelpTab
from gui.tab_log import LogTab
from gui.tab_scenarios import ScenariosTab
from gui.tab_simulation import SimulationTab


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.engine = None  # SimulationEngine ativo (None até configurar ou carregar cenário)

        root.title("Simulador do Algoritmo do Banqueiro -- Prevenção de Deadlock")
        root.geometry("1200x750")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_config = ConfigTab(self.notebook, self)
        self.tab_simulation = SimulationTab(self.notebook, self)
        self.tab_log = LogTab(self.notebook, self)
        self.tab_scenarios = ScenariosTab(self.notebook, self)
        self.tab_help = HelpTab(self.notebook, self)

        self.notebook.add(self.tab_config, text="Configuração")
        self.notebook.add(self.tab_simulation, text="Simulação")
        self.notebook.add(self.tab_log, text="Log / Histórico")
        self.notebook.add(self.tab_scenarios, text="Cenários prontos")
        self.notebook.add(self.tab_help, text="Ajuda")

        self.refresh_all()

    def set_engine(self, engine) -> None:
        self.engine = engine
        self.refresh_all()

    def refresh_all(self) -> None:
        self.tab_simulation.refresh()
        self.tab_log.refresh()

    def show_simulation_tab(self) -> None:
        self.notebook.select(self.tab_simulation)
