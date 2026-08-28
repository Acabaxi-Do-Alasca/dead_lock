"""Widgets Tkinter reutilizáveis: tabela de matriz e tooltip."""

import tkinter as tk
from tkinter import ttk


class MatrixTable(ttk.Frame):
    """Exibe uma matriz (ou vetor) numérica em uma Treeview, com título."""

    def __init__(self, parent, title: str, col_labels: list[str]):
        super().__init__(parent)
        self.col_labels = col_labels

        ttk.Label(self, text=title, font=("Segoe UI", 9, "bold")).pack(anchor="w")

        columns = ["proc"] + col_labels
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=6)
        self.tree.heading("proc", text="")
        self.tree.column("proc", width=50, anchor="center")
        for col in col_labels:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=50, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def update_rows(self, row_labels: list[str], matrix: list[list[int]]):
        self.tree.delete(*self.tree.get_children())
        for label, row in zip(row_labels, matrix):
            self.tree.insert("", "end", values=[label] + list(row))

    def update_vector(self, label: str, vector: list[int]):
        self.tree.delete(*self.tree.get_children())
        self.tree.insert("", "end", values=[label] + list(vector))


class ScrollableFrame(ttk.Frame):
    """Frame com rolagem vertical -- usado quando o conteúdo (matrizes +
    formulário) pode ficar mais alto do que a janela, dependendo de quantos
    processos/recursos o cenário tiver."""

    def __init__(self, parent):
        super().__init__(parent)
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.inner = ttk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=self.inner, anchor="nw")

        def on_inner_configure(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfigure(window_id, width=event.width)

        self.inner.bind("<Configure>", on_inner_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda _e: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda _e: canvas.unbind_all("<MouseWheel>"))


class Tooltip:
    """Tooltip simples: mostra um balão de texto ao passar o mouse sobre um widget."""

    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _event=None):
        if self.tip_window is not None:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 8),
            wraplength=320,
            padx=6,
            pady=4,
        )
        label.pack()

    def _hide(self, _event=None):
        if self.tip_window is not None:
            self.tip_window.destroy()
            self.tip_window = None
