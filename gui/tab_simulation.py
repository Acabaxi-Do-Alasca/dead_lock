"""Aba de Simulação: grafo de alocação, matrizes e formulário de requisição."""

import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from gui import graph_view
from gui.widgets import MatrixTable, ScrollableFrame, Tooltip
from simulation.engine import Mode

STATE_LABELS = {
    "READY": "pronto",
    "RUNNING": "executando",
    "BLOCKED": "bloqueado",
    "FINISHED": "terminado",
}


class SimulationTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left = ttk.Frame(paned)
        right = ttk.Frame(paned)
        paned.add(left, weight=3)
        paned.add(right, weight=2)

        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=left)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas, left)
        toolbar.update()

        self.status_label = ttk.Label(left, text="", foreground="#555")
        self.status_label.pack(anchor="w", padx=6, pady=(0, 4))

        scrollable = ScrollableFrame(right)
        scrollable.pack(fill="both", expand=True)
        right_content = scrollable.inner

        self.tables_container = ttk.Frame(right_content)
        self.tables_container.pack(fill="x", padx=8, pady=6)

        self.form_frame = ttk.LabelFrame(right_content, text="Fazer Requisição / Ação")
        self.form_frame.pack(fill="x", padx=8, pady=6)
        self.form_inner = ttk.Frame(self.form_frame)
        self.form_inner.pack(fill="x", padx=6, pady=6)

        self.placeholder = ttk.Label(
            right_content,
            text="Nenhuma simulação ativa. Configure processos/recursos na aba "
            "Configuração ou carregue um cenário pronto.",
            foreground="#777",
            wraplength=280,
        )

    # -- ciclo de atualização -----------------------------------------------------

    def refresh(self):
        engine = self.app.engine
        for child in self.tables_container.winfo_children():
            child.destroy()
        for child in self.form_inner.winfo_children():
            child.destroy()

        if engine is None:
            self.ax.clear()
            self.ax.axis("off")
            self.canvas.draw_idle()
            self.status_label.config(text="")
            self.placeholder.pack(anchor="w")
            return
        self.placeholder.pack_forget()

        has_cycle = graph_view.draw_rag(self.ax, engine)
        self.canvas.draw_idle()

        state = engine.state
        status_bits = [
            f"{p.name}: {STATE_LABELS.get(p.state.name, p.state.name)}" for p in state.processes
        ]
        prefix = "MODO LIVRE (sem prevenção) -- " if engine.mode == Mode.FREE else "Modo Protegido -- "
        self.status_label.config(
            text=prefix + " | ".join(status_bits) + ("  [CICLO NO GRAFO]" if has_cycle else "")
        )

        self._build_tables(state)
        self._build_form(engine)

    def _build_tables(self, state):
        res_labels = [r.name for r in state.resources]
        proc_labels = [p.name for p in state.processes]

        alloc_table = MatrixTable(self.tables_container, "Allocation", res_labels)
        alloc_table.update_rows(proc_labels, state.allocation)
        alloc_table.pack(fill="x", pady=4)

        need_table = MatrixTable(self.tables_container, "Need (Max - Allocation)", res_labels)
        need_table.update_rows(proc_labels, state.need)
        need_table.pack(fill="x", pady=4)
        Tooltip(need_table, "Need indica quanto cada processo ainda PODE vir a pedir no futuro.")

        avail_table = MatrixTable(self.tables_container, "Available", res_labels)
        avail_table.update_vector("livres", state.available)
        avail_table.pack(fill="x", pady=4)
        Tooltip(avail_table, "Available é o que sobrou de cada recurso, livre para alocação.")

    def _build_form(self, engine):
        state = engine.state

        ttk.Label(self.form_inner, text="Processo:").grid(row=0, column=0, sticky="w")
        self.process_var = tk.StringVar()
        combo = ttk.Combobox(
            self.form_inner,
            textvariable=self.process_var,
            values=[p.name for p in state.processes],
            state="readonly",
            width=10,
        )
        combo.grid(row=0, column=1, padx=4)
        if state.processes:
            combo.current(0)

        # Campos de requisição (um Spinbox por recurso), no máximo 2 por linha,
        # para não estourar a largura fixa do painel quando há muitos recursos.
        RESOURCES_PER_ROW = 2
        self.request_entries = []
        for idx, r in enumerate(state.resources):
            row = 1 + idx // RESOURCES_PER_ROW
            col = (idx % RESOURCES_PER_ROW) * 2
            ttk.Label(self.form_inner, text=f"{r.name}:").grid(
                row=row, column=col, sticky="w", pady=2
            )
            spin = ttk.Spinbox(self.form_inner, from_=0, to=99, width=6)
            spin.set(0)
            spin.grid(row=row, column=col + 1, padx=4, sticky="w")
            self.request_entries.append(spin)

        next_row = 1 + (len(state.resources) + RESOURCES_PER_ROW - 1) // RESOURCES_PER_ROW

        self.mode_var = tk.StringVar(value=engine.mode.name)
        mode_frame = ttk.Frame(self.form_inner)
        mode_frame.grid(row=next_row, column=0, columnspan=4, sticky="w", pady=(8, 0))
        ttk.Radiobutton(
            mode_frame, text="Protegido (com Banqueiro)", value="PROTECTED",
            variable=self.mode_var, command=self._on_mode_change,
        ).pack(anchor="w")
        ttk.Radiobutton(
            mode_frame, text="Livre (sem prevenção)", value="FREE",
            variable=self.mode_var, command=self._on_mode_change,
        ).pack(anchor="w")

        button_frame = ttk.Frame(self.form_inner)
        button_frame.grid(row=next_row + 1, column=0, columnspan=4, sticky="w", pady=(8, 0))
        ttk.Button(button_frame, text="Solicitar", command=self._on_request).pack(
            side="top", anchor="w", pady=2, fill="x"
        )
        ttk.Button(
            button_frame, text="Finalizar processo (libera tudo)", command=self._on_finish
        ).pack(side="top", anchor="w", pady=2, fill="x")
        if engine.mode == Mode.FREE:
            ttk.Button(
                button_frame, text="Verificar Deadlock", command=self._on_check_deadlock
            ).pack(side="top", anchor="w", pady=2, fill="x")

    # -- ações ------------------------------------------------------------------

    def _selected_process(self, engine):
        name = self.process_var.get()
        return next((p for p in engine.state.processes if p.name == name), None)

    def _read_request_vector(self):
        return [int(s.get()) for s in self.request_entries]

    def _on_mode_change(self):
        engine = self.app.engine
        if engine is None:
            return
        engine.set_mode(Mode.PROTECTED if self.mode_var.get() == "PROTECTED" else Mode.FREE)
        self.app.refresh_all()

    def _on_request(self):
        engine = self.app.engine
        if engine is None:
            return
        proc = self._selected_process(engine)
        if proc is None:
            return
        try:
            vector = self._read_request_vector()
        except ValueError:
            messagebox.showerror("Erro", "Valores de requisição inválidos.")
            return

        try:
            result = engine.request(proc.pid, vector)
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))
            return

        self.app.refresh_all()
        if engine.mode == Mode.PROTECTED:
            if result.granted:
                messagebox.showinfo("Requisição concedida", f"Requisição de {proc.name} foi concedida -- veja o log para o raciocínio completo.")
            else:
                messagebox.showwarning(
                    "Requisição negada",
                    f"Requisição de {proc.name} foi negada ({result.reason}). Veja a aba Log para o raciocínio do Banqueiro.",
                )
        else:
            if not result:
                messagebox.showwarning(
                    "Requisição pendente",
                    f"{proc.name} ficou bloqueado aguardando recursos (modo Livre, sem verificação de segurança).",
                )

    def _on_finish(self):
        engine = self.app.engine
        if engine is None:
            return
        proc = self._selected_process(engine)
        if proc is None:
            return
        engine.finish_process(proc.pid)
        self.app.refresh_all()

    def _on_check_deadlock(self):
        engine = self.app.engine
        if engine is None:
            return
        result = engine.check_deadlock()
        self.app.refresh_all()
        if result.deadlocked_processes:
            names = ", ".join(engine.state.processes[i].name for i in result.deadlocked_processes)
            messagebox.showerror("Deadlock detectado", f"Processos em deadlock: {names}. Veja o log para a análise completa.")
        else:
            messagebox.showinfo("Sem deadlock", "Nenhum deadlock foi detectado no estado atual.")
