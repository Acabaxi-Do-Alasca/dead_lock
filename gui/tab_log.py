"""Aba de Log/Histórico: raciocínio passo a passo do algoritmo + timeline."""

import tkinter as tk
from tkinter import ttk


class LogTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left = ttk.Frame(paned)
        right = ttk.Frame(paned)
        paned.add(left, weight=3)
        paned.add(right, weight=1)

        filter_frame = ttk.Frame(left)
        filter_frame.pack(fill="x", padx=4, pady=4)
        ttk.Label(filter_frame, text="Filtrar categoria:").pack(side="left")
        self.category_var = tk.StringVar(value="Todas")
        self.category_combo = ttk.Combobox(
            filter_frame, textvariable=self.category_var, state="readonly", width=18,
            values=["Todas"],
        )
        self.category_combo.pack(side="left", padx=4)
        self.category_combo.bind("<<ComboboxSelected>>", lambda _e: self._populate_log())

        tree_frame = ttk.Frame(left)
        tree_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        columns = ("step", "categoria", "mensagem")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.heading("step", text="#")
        self.tree.column("step", width=40, anchor="center")
        self.tree.heading("categoria", text="Categoria")
        self.tree.column("categoria", width=120, anchor="center")
        self.tree.heading("mensagem", text="Mensagem (raciocínio do algoritmo)")
        self.tree.column("mensagem", width=520, anchor="w")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        ttk.Label(right, text="Linha do tempo (snapshots)", font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=4, pady=(4, 0)
        )
        self.timeline_list = tk.Listbox(right, width=34, exportselection=False)
        self.timeline_list.pack(fill="both", expand=True, padx=4, pady=4)
        self.timeline_list.bind("<<ListboxSelect>>", self._on_timeline_select)

        ttk.Label(right, text="Estado naquele momento:", font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=4
        )
        self.snapshot_detail = tk.Text(right, height=12, width=34, state="disabled", wrap="word")
        self.snapshot_detail.pack(fill="both", expand=False, padx=4, pady=4)

    def refresh(self):
        engine = self.app.engine
        if engine is None:
            self.tree.delete(*self.tree.get_children())
            self.timeline_list.delete(0, tk.END)
            self._set_detail_text("")
            return

        categories = sorted({e.category for e in engine.state.event_log})
        self.category_combo["values"] = ["Todas"] + categories
        if self.category_var.get() not in (["Todas"] + categories):
            self.category_var.set("Todas")

        self._populate_log()
        self._populate_timeline()

    def _populate_log(self):
        engine = self.app.engine
        self.tree.delete(*self.tree.get_children())
        if engine is None:
            return
        selected_category = self.category_var.get()
        for entry in engine.state.event_log:
            if selected_category != "Todas" and entry.category != selected_category:
                continue
            self.tree.insert("", "end", values=(entry.step, entry.category, entry.message))
        children = self.tree.get_children()
        if children:
            self.tree.see(children[-1])

    def _populate_timeline(self):
        engine = self.app.engine
        self.timeline_list.delete(0, tk.END)
        if engine is None:
            return
        for snap in engine.timeline:
            self.timeline_list.insert(tk.END, f"[{snap.step}] {snap.description}")
        if engine.timeline:
            last = len(engine.timeline) - 1
            self.timeline_list.selection_set(last)
            self.timeline_list.see(last)
            self._show_snapshot_detail(engine.timeline[last])

    def _on_timeline_select(self, _event):
        engine = self.app.engine
        if engine is None:
            return
        selection = self.timeline_list.curselection()
        if not selection:
            return
        self._show_snapshot_detail(engine.timeline[selection[0]])

    def _show_snapshot_detail(self, snap):
        lines = [f"Descrição: {snap.description}", "", "Allocation:"]
        lines.extend(str(row) for row in snap.allocation)
        lines.append("")
        lines.append("Need:")
        lines.extend(str(row) for row in snap.need)
        lines.append("")
        lines.append(f"Available: {snap.available}")
        self._set_detail_text("\n".join(lines))

    def _set_detail_text(self, text):
        self.snapshot_detail.configure(state="normal")
        self.snapshot_detail.delete("1.0", tk.END)
        self.snapshot_detail.insert("1.0", text)
        self.snapshot_detail.configure(state="disabled")
