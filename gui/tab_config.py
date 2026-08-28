"""Aba de Configuração: cadastro manual de recursos e processos.

Guarda os dados em listas simples em memória (`app.config_resources` /
`app.config_processes`) até o usuário clicar em "Iniciar Simulação", quando
um `SystemState`/`SimulationEngine` são construídos com Allocation = 0.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from core.models import Process, ResourceType
from core.state import SystemState
from simulation.engine import Mode, SimulationEngine


class ConfigTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.app.config_resources = []  # list[dict(name, total)]
        self.app.config_processes = []  # list[dict(name, max=list[int])]

        self._build_resource_section()
        self._build_process_section()
        self._build_start_section()

    # -- recursos -------------------------------------------------------------

    def _build_resource_section(self):
        frame = ttk.LabelFrame(self, text="Recursos")
        frame.pack(fill="x", padx=10, pady=8)

        form = ttk.Frame(frame)
        form.pack(fill="x", padx=8, pady=6)
        ttk.Label(form, text="Nome:").grid(row=0, column=0, sticky="w")
        self.resource_name_entry = ttk.Entry(form, width=12)
        self.resource_name_entry.grid(row=0, column=1, padx=4)
        ttk.Label(form, text="Instâncias totais:").grid(row=0, column=2, sticky="w")
        self.resource_total_entry = ttk.Spinbox(form, from_=1, to=99, width=6)
        self.resource_total_entry.set(1)
        self.resource_total_entry.grid(row=0, column=3, padx=4)
        ttk.Button(form, text="Adicionar Recurso", command=self._add_resource).grid(
            row=0, column=4, padx=8
        )

        self.resource_tree = ttk.Treeview(
            frame, columns=("name", "total"), show="headings", height=4
        )
        self.resource_tree.heading("name", text="Nome")
        self.resource_tree.heading("total", text="Total de instâncias")
        self.resource_tree.pack(fill="x", padx=8, pady=(0, 6))

        ttk.Button(frame, text="Remover selecionado", command=self._remove_resource).pack(
            anchor="e", padx=8, pady=(0, 8)
        )

    def _add_resource(self):
        name = self.resource_name_entry.get().strip()
        if not name:
            messagebox.showerror("Erro", "Informe um nome para o recurso.")
            return
        if any(r["name"] == name for r in self.app.config_resources):
            messagebox.showerror("Erro", f"Já existe um recurso chamado '{name}'.")
            return
        try:
            total = int(self.resource_total_entry.get())
            if total < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Instâncias totais deve ser um inteiro >= 1.")
            return

        self.app.config_resources.append({"name": name, "total": total})
        for p in self.app.config_processes:
            p["max"].append(0)

        self.resource_name_entry.delete(0, tk.END)
        self._refresh_resource_tree()
        self._rebuild_process_form()
        self._refresh_process_tree()

    def _remove_resource(self):
        selection = self.resource_tree.selection()
        if not selection:
            return
        index = self.resource_tree.index(selection[0])
        del self.app.config_resources[index]
        for p in self.app.config_processes:
            del p["max"][index]
        self._refresh_resource_tree()
        self._rebuild_process_form()
        self._refresh_process_tree()

    def _refresh_resource_tree(self):
        self.resource_tree.delete(*self.resource_tree.get_children())
        for r in self.app.config_resources:
            self.resource_tree.insert("", "end", values=(r["name"], r["total"]))

    # -- processos --------------------------------------------------------------

    def _build_process_section(self):
        self.process_frame = ttk.LabelFrame(self, text="Processos")
        self.process_frame.pack(fill="x", padx=10, pady=8)

        self.process_form_container = ttk.Frame(self.process_frame)
        self.process_form_container.pack(fill="x", padx=8, pady=6)
        self._rebuild_process_form()

        self.process_tree = ttk.Treeview(
            self.process_frame, columns=("name", "max"), show="headings", height=5
        )
        self.process_tree.heading("name", text="Nome")
        self.process_tree.heading("max", text="Max (uma coluna por recurso)")
        self.process_tree.pack(fill="x", padx=8, pady=(0, 6))

        ttk.Button(
            self.process_frame, text="Remover selecionado", command=self._remove_process
        ).pack(anchor="e", padx=8, pady=(0, 8))

    def _rebuild_process_form(self):
        for child in self.process_form_container.winfo_children():
            child.destroy()

        ttk.Label(self.process_form_container, text="Nome:").grid(row=0, column=0, sticky="w")
        self.process_name_entry = ttk.Entry(self.process_form_container, width=12)
        self.process_name_entry.grid(row=0, column=1, padx=4)

        self.max_entries: list[ttk.Spinbox] = []
        col = 2
        if not self.app.config_resources:
            ttk.Label(
                self.process_form_container,
                text="(cadastre ao menos um recurso antes de adicionar processos)",
                foreground="#777",
            ).grid(row=0, column=2, columnspan=3, sticky="w", padx=8)
            col = 5
        else:
            for r in self.app.config_resources:
                ttk.Label(self.process_form_container, text=f"Max {r['name']}:").grid(
                    row=0, column=col, sticky="w"
                )
                spin = ttk.Spinbox(self.process_form_container, from_=0, to=99, width=5)
                spin.set(0)
                spin.grid(row=0, column=col + 1, padx=4)
                self.max_entries.append(spin)
                col += 2

        ttk.Button(
            self.process_form_container, text="Adicionar Processo", command=self._add_process
        ).grid(row=0, column=col, padx=8)

    def _add_process(self):
        name = self.process_name_entry.get().strip()
        if not name:
            messagebox.showerror("Erro", "Informe um nome para o processo.")
            return
        if any(p["name"] == name for p in self.app.config_processes):
            messagebox.showerror("Erro", f"Já existe um processo chamado '{name}'.")
            return
        if not self.app.config_resources:
            messagebox.showerror("Erro", "Cadastre ao menos um recurso primeiro.")
            return

        try:
            max_vector = [int(s.get()) for s in self.max_entries]
            if any(v < 0 for v in max_vector):
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Os valores de Max devem ser inteiros >= 0.")
            return

        self.app.config_processes.append({"name": name, "max": max_vector})
        self.process_name_entry.delete(0, tk.END)
        for s in self.max_entries:
            s.set(0)
        self._refresh_process_tree()

    def _remove_process(self):
        selection = self.process_tree.selection()
        if not selection:
            return
        index = self.process_tree.index(selection[0])
        del self.app.config_processes[index]
        self._refresh_process_tree()

    def _refresh_process_tree(self):
        self.process_tree.delete(*self.process_tree.get_children())
        for p in self.app.config_processes:
            self.process_tree.insert("", "end", values=(p["name"], str(p["max"])))

    # -- iniciar simulação -------------------------------------------------------

    def _build_start_section(self):
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=12)
        ttk.Button(
            frame, text="Iniciar Simulação (Allocation = 0)", command=self._start_simulation
        ).pack(side="left")
        ttk.Label(
            frame,
            text="Todos os processos começam sem nenhum recurso alocado; use a "
            "aba Simulação para fazer requisições.",
            foreground="#555",
        ).pack(side="left", padx=12)

    def _start_simulation(self):
        if not self.app.config_resources:
            messagebox.showerror("Erro", "Cadastre ao menos um recurso.")
            return
        if not self.app.config_processes:
            messagebox.showerror("Erro", "Cadastre ao menos um processo.")
            return

        resources = [
            ResourceType(j, r["name"], r["total"])
            for j, r in enumerate(self.app.config_resources)
        ]
        processes = [Process(i, p["name"]) for i, p in enumerate(self.app.config_processes)]
        n_res = len(resources)
        allocation = [[0] * n_res for _ in processes]
        max_demand = [list(p["max"]) for p in self.app.config_processes]

        try:
            state = SystemState(processes, resources, allocation, max_demand)
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))
            return

        engine = SimulationEngine(state, mode=Mode.PROTECTED)
        engine.state.log("INFO", "Simulação manual iniciada a partir da aba Configuração.")
        self.app.set_engine(engine)
        self.app.show_simulation_tab()
