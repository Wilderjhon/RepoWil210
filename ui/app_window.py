"""
Ventana principal de la aplicación.
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import base64
import tempfile

from core.config_loader import ConfigLoader
from core.data_transformer import DataTransformer
from core.sql_generator import SQLGenerator

from ui.colors import (
    COLOR_FONDO, COLOR_TEXTO, COLOR_GRIS,
    COLOR_ENTRADA, COLOR_BORDE, COLOR_OK, COLOR_ERROR,
    FUENTE_TITULO, FUENTE_SUBTITULO, FUENTE_SECCION,
    FUENTE_NORMAL, FUENTE_PEQUENA
)
from ui.widgets import BotonVerde
from ui.config_builder import ConfigBuilder


def resource_path(relative_path):
    """Ruta de un archivo, funciona en modo script y en .exe."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def cargar_icono_base64():
    """Lee b64.txt y devuelve el contenido."""
    try:
        ruta = resource_path('b64.txt')
        with open(ruta, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"No se pudo leer b64.txt: {e}")
        return ""


class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Transformador Excel → SQL/CSV")
        self.root.geometry("600x650")
        self.root.configure(bg=COLOR_FONDO)

        self._set_window_icon()

        self.transformer = DataTransformer()
        self.sql_generator = None
        self.config_loader = None
        self.current_excel_path = ""
        self.current_config_path = ""

        self._create_widgets()

    def _set_window_icon(self):
        try:
            b64 = cargar_icono_base64()
            if not b64:
                return
            icon_bytes = base64.b64decode(b64)
            temp_icon = os.path.join(tempfile.gettempdir(), 'app_icon_temp.ico')
            with open(temp_icon, 'wb') as f:
                f.write(icon_bytes)
            self.root.iconbitmap(temp_icon)
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")

    def _create_widgets(self):
        # Título
        tk.Label(self.root, text="CONVERTIDOR DE DATOS",
                 font=FUENTE_TITULO, bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=(15, 5))
        tk.Label(self.root, text="Configurable para cualquier Excel",
                 font=FUENTE_SUBTITULO, bg=COLOR_FONDO, fg=COLOR_GRIS).pack(pady=(0, 15))

        # PASO 1
        tk.Label(self.root, text="PASO 1 — Cargar configuración",
                 font=FUENTE_SECCION, bg=COLOR_FONDO, fg=COLOR_TEXTO, anchor="w").pack(fill="x", padx=20, pady=(10, 5))

        self.btn_config = BotonVerde(self.root, text="📂  Seleccionar config.json",
                                      command=self.select_config, width=30)
        self.btn_config.pack(pady=5)

        BotonVerde(self.root, text="🛠  Armar nueva configuración",
                   command=self.abrir_config_builder, width=30).pack(pady=5)

        self.lbl_config = tk.Label(self.root, text="Ninguna configuración cargada",
                                    font=FUENTE_PEQUENA, bg=COLOR_FONDO, fg=COLOR_GRIS, wraplength=550)
        self.lbl_config.pack(pady=(0, 15))

        # PASO 2
        tk.Label(self.root, text="PASO 2 — Cargar Excel",
                 font=FUENTE_SECCION, bg=COLOR_FONDO, fg=COLOR_TEXTO, anchor="w").pack(fill="x", padx=20, pady=(10, 5))

        self.btn_excel = BotonVerde(self.root, text="📊  Seleccionar Excel",
                                     command=self.select_excel, width=30, state="disabled")
        self.btn_excel.pack(pady=5)

        self.lbl_file = tk.Label(self.root, text="Ningún archivo seleccionado",
                                  font=FUENTE_PEQUENA, bg=COLOR_FONDO, fg=COLOR_GRIS, wraplength=550)
        self.lbl_file.pack(pady=(0, 15))

        # PASO 3
        tk.Label(self.root, text="PASO 3 — Exportar resultados",
                 font=FUENTE_SECCION, bg=COLOR_FONDO, fg=COLOR_TEXTO, anchor="w").pack(fill="x", padx=20, pady=(10, 5))

        frame_exp = tk.Frame(self.root, bg=COLOR_FONDO)
        frame_exp.pack(pady=10)

        self.btn_csv = BotonVerde(frame_exp, text="Exportar CSV",
                                   command=self.export_csv, width=18, state="disabled")
        self.btn_csv.pack(side="left", padx=5)

        self.btn_sql = BotonVerde(frame_exp, text="Generar SQL",
                                   command=self.generate_sql, width=18, state="disabled")
        self.btn_sql.pack(side="left", padx=5)

        # Separador
        tk.Frame(self.root, height=2, bg=COLOR_BORDE).pack(fill="x", padx=40, pady=15)

        # Prefijo
        frame_pref = tk.Frame(self.root, bg=COLOR_FONDO)
        frame_pref.pack(pady=5, padx=40, fill="x")
        tk.Label(frame_pref, text="Prefijo username:", font=FUENTE_NORMAL,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left")
        self.entry_prefijo = tk.Entry(frame_pref, font=FUENTE_NORMAL,
                                       bg=COLOR_ENTRADA, fg=COLOR_TEXTO,
                                       insertbackground=COLOR_TEXTO, relief="flat", bd=5)
        self.entry_prefijo.pack(side="right", fill="x", expand=True, ipady=3, padx=(10, 0))

        # Status
        self.lbl_status = tk.Label(self.root, text="", font=FUENTE_PEQUENA,
                                    bg=COLOR_FONDO, fg=COLOR_GRIS, wraplength=560, justify="left")
        self.lbl_status.pack(pady=(15, 10), padx=20)

    # --------------------------------------------------------
    # ACCIONES
    # --------------------------------------------------------
    def abrir_config_builder(self):
        """Abre la ventana para armar un config.json visualmente."""
        builder = ConfigBuilder(self.root)
        builder.grab_set()  # modal

    def select_config(self):
        filetypes = (("Archivos JSON", "*.json"), ("Todos los archivos", "*.*"))
        filename = filedialog.askopenfilename(title="Seleccionar config.json", filetypes=filetypes)
        if not filename:
            return

        self.config_loader = ConfigLoader(filename)
        success, message = self.config_loader.load()
        if not success:
            messagebox.showerror("Error", message)
            return

        self.current_config_path = filename
        nombre = self.config_loader.get_nombre_proyecto()
        n_tablas = len(self.config_loader.get_tablas())

        self.lbl_config.config(
            text=f"✓ {os.path.basename(filename)} — '{nombre}' ({n_tablas} tablas)",
            fg=COLOR_OK
        )
        self.entry_prefijo.delete(0, tk.END)
        self.entry_prefijo.insert(0, self.config_loader.get_prefijo())

        self.transformer.set_config(self.config_loader)
        self.sql_generator = SQLGenerator(self.transformer, self.config_loader)

        self.btn_excel.config(state="normal")
        self.lbl_status.config(text="Configuración lista. Ahora seleccioná el Excel.",
                                fg=COLOR_TEXTO)

    def select_excel(self):
        filetypes = (("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*"))
        filename = filedialog.askopenfilename(title="Seleccionar Excel", filetypes=filetypes)
        if not filename:
            return

        success, message = self.transformer.load_excel(filename)
        if not success:
            messagebox.showerror("Error", message)
            return

        self.current_excel_path = filename
        self.transformer.clean_data()

        self.lbl_file.config(text=f"✓ {os.path.basename(filename)} — {message}", fg=COLOR_OK)
        self.btn_csv.config(state="normal")
        self.btn_sql.config(state="normal")
        self.lbl_status.config(
            text=f"Excel cargado. {len(self.transformer.df)} filas listas para exportar.",
            fg=COLOR_TEXTO
        )

    def export_csv(self):
        if not self.current_excel_path:
            return
        base_name = os.path.splitext(os.path.basename(self.current_excel_path))[0]
        output_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"{base_name}_convertido.csv",
            filetypes=[("CSV", "*.csv")]
        )
        if not output_path:
            return
        success, message = self.transformer.export_to_csv(output_path)
        if success:
            self.lbl_status.config(text=f"✓ {message}", fg=COLOR_OK)
            messagebox.showinfo("Éxito", message)
        else:
            self.lbl_status.config(text=f"✗ {message}", fg=COLOR_ERROR)
            messagebox.showerror("Error", message)

    def generate_sql(self):
        prefijo = self.entry_prefijo.get().strip()
        success, result = self.sql_generator.generate(prefijo)
        if not success:
            self.lbl_status.config(text=f"✗ {result}", fg=COLOR_ERROR)
            messagebox.showerror("Error", result)
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".sql",
            initialfile="inserts_generados.sql",
            filetypes=[("SQL Script", "*.sql"), ("Text", "*.txt")]
        )
        if not output_path:
            return
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result)
            self.lbl_status.config(text=f"✓ SQL guardado en: {output_path}", fg=COLOR_OK)
            messagebox.showinfo("Éxito", f"Script SQL generado:\n{output_path}")
        except Exception as e:
            self.lbl_status.config(text=f"✗ Error al guardar: {e}", fg=COLOR_ERROR)
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")