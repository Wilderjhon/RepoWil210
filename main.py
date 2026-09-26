"""
Punto de entrada de la aplicación.
"""
import tkinter as tk

from ui.app_window import AppUI


def main():
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()