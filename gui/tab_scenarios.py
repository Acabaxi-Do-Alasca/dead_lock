"""Aba de Cenários prontos: carrega um dos 3 cenários pré-definidos com um clique."""

import tkinter as tk
from tkinter import messagebox, ttk

from scenarios.loader import build_engine_from_scenario
from scenarios.scenario_definitions import ALL_SCENARIOS


class ScenariosTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(
            self,
            text="Carregue um cenário pronto para ver o Algoritmo do Banqueiro em ação. "
            "Isso substitui a simulação atual.",
            wraplength=700,
        ).pack(anchor="w", padx=10, pady=(10, 6))

        for scenario in ALL_SCENARIOS:
            self._build_scenario_card(scenario)

    def _build_scenario_card(self, scenario):
        card = ttk.LabelFrame(self, text=scenario["title"])
        card.pack(fill="x", padx=10, pady=6)

        ttk.Label(card, text=scenario["description"], wraplength=680, justify="left").pack(
            anchor="w", padx=8, pady=6
        )

        if scenario["suggested_requests"]:
            steps = ", ".join(f"{name}->{req}" for name, req in scenario["suggested_requests"])
            ttk.Label(
                card, text=f"Requisições sugeridas: {steps}", foreground="#555"
            ).pack(anchor="w", padx=8, pady=(0, 6))

        ttk.Button(
            card,
            text=f"Carregar Cenário {scenario['key']}",
            command=lambda key=scenario["key"]: self._load(key),
        ).pack(anchor="e", padx=8, pady=(0, 8))

    def _load(self, key):
        try:
            engine = build_engine_from_scenario(key)
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))
            return
        self.app.set_engine(engine)
        self.app.show_simulation_tab()
