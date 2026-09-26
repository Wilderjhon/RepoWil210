"""
Widgets personalizados (botones, etc).
"""
import tkinter as tk
from ui.colors import (
    COLOR_BOTON, COLOR_BOTON_HOVER, COLOR_TEXTO, FUENTE_BOTON
)


class BotonVerde(tk.Button):
    """Botón con efecto hover verde."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config(
            bg=COLOR_BOTON,
            fg=COLOR_TEXTO,
            activebackground=COLOR_BOTON_HOVER,
            activeforeground="#000000",
            relief="flat",
            bd=0,
            font=FUENTE_BOTON,
            cursor="hand2",
            padx=20,
            pady=10
        )
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, e):
        if self["state"] != "disabled":
            self.config(bg=COLOR_BOTON_HOVER, fg="#000000")

    def _on_leave(self, e):
        if self["state"] != "disabled":
            self.config(bg=COLOR_BOTON, fg=COLOR_TEXTO)
