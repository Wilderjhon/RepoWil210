"""
Pantalla para armar la configuración visualmente.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import pandas as pd

from ui.colors import (
    COLOR_FONDO, COLOR_TEXTO, COLOR_GRIS,
    COLOR_ENTRADA, COLOR_BORDE, COLOR_OK, COLOR_ERROR,
    FUENTE_TITULO, FUENTE_SECCION, FUENTE_NORMAL, FUENTE_PEQUENA
)
from ui.widgets import BotonVerde


class ConfigBuilder(tk.Toplevel):
    """Ventana para construir un config.json visualmente."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Configuración del Proyecto")
        self.geometry("950x700")
        self.configure(bg=COLOR_FONDO)

        self.columnas_excel = []
        self.tablas_ui = []

        self._create_widgets()

    # ========================================================
    # UI
    # ========================================================
    def _create_widgets(self):
        # Título
        tk.Label(self, text="CONFIGURACIÓN DEL PROYECTO",
                 font=FUENTE_TITULO, bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=(15, 10))

        # --- Datos generales ---
        frame_gen = tk.Frame(self, bg=COLOR_FONDO)
        frame_gen.pack(padx=20, pady=5, fill="x")

        tk.Label(frame_gen, text="Nombre del proyecto:", font=FUENTE_NORMAL,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).grid(row=0, column=0, sticky="w", pady=3)
        self.entry_nombre = tk.Entry(frame_gen, font=FUENTE_NORMAL,
                                      bg=COLOR_ENTRADA, fg=COLOR_TEXTO,
                                      insertbackground=COLOR_TEXTO, relief="flat", bd=5)
        self.entry_nombre.grid(row=0, column=1, sticky="ew", padx=(10, 30), ipady=3)
        self.entry_nombre.insert(0, "Mi Proyecto")

        tk.Label(frame_gen, text="Prefijo username:", font=FUENTE_NORMAL,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).grid(row=0, column=2, sticky="w", pady=3)
        self.entry_prefijo = tk.Entry(frame_gen, font=FUENTE_NORMAL,
                                       bg=COLOR_ENTRADA, fg=COLOR_TEXTO,
                                       insertbackground=COLOR_TEXTO, relief="flat", bd=5)
        self.entry_prefijo.grid(row=0, column=3, sticky="ew", padx=(10, 0), ipady=3)
        self.entry_prefijo.insert(0, "est_")

        frame_gen.columnconfigure(1, weight=1)
        frame_gen.columnconfigure(3, weight=1)

        # --- Cargar Excel ---
        frame_excel = tk.Frame(self, bg=COLOR_FONDO)
        frame_excel.pack(padx=20, pady=10, fill="x")

        BotonVerde(frame_excel, text="📊  Cargar Excel (para leer columnas)",
                   command=self.cargar_excel, width=35).pack(side="left")

        self.lbl_excel = tk.Label(frame_excel, text="Sin Excel cargado",
                                   font=FUENTE_PEQUENA, bg=COLOR_FONDO, fg=COLOR_GRIS)
        self.lbl_excel.pack(side="left", padx=(10, 0))

        # --- Tablas ---
        tk.Label(self, text="TABLAS", font=FUENTE_SECCION,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=(15, 5))

        self.frame_tablas_container = tk.Frame(self, bg=COLOR_FONDO)
        self.frame_tablas_container.pack(fill="both", expand=True, padx=20)

        self.canvas = tk.Canvas(self.frame_tablas_container, bg=COLOR_FONDO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame_tablas_container, orient="vertical", command=self.canvas.yview)
        self.frame_tablas = tk.Frame(self.canvas, bg=COLOR_FONDO)

        self.frame_tablas.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.frame_tablas, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Botones inferiores ---
        frame_botones = tk.Frame(self, bg=COLOR_FONDO)
        frame_botones.pack(pady=15, fill="x")

        BotonVerde(frame_botones, text="+ Agregar tabla",
                   command=self.agregar_tabla, width=18).pack(side="left", padx=10)
        BotonVerde(frame_botones, text="💾 Guardar config.json",
                   command=self.guardar_config, width=20).pack(side="right", padx=10)

    # ========================================================
    # CARGA EXCEL
    # ========================================================
    def cargar_excel(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar Excel",
            filetypes=(("Excel", "*.xlsx *.xls"), ("Todos", "*.*"))
        )
        if not filename:
            return

        try:
            df = pd.read_excel(filename, nrows=5)
            self.columnas_excel = [str(c).strip() for c in df.columns]
            self.lbl_excel.config(
                text=f"✓ {os.path.basename(filename)} — {len(self.columnas_excel)} columnas",
                fg=COLOR_OK
            )
            messagebox.showinfo("Excel cargado",
                                "Columnas detectadas:\n" + "\n".join(self.columnas_excel))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el Excel: {e}")

    # ========================================================
    # TABLAS
    # ========================================================
    def agregar_tabla(self):
        idx = len(self.tablas_ui)

        frame_tabla = tk.LabelFrame(
            self.frame_tablas,
            text=f"Tabla {idx + 1}",
            font=FUENTE_NORMAL,
            bg=COLOR_FONDO, fg=COLOR_TEXTO,
            bd=2, relief="groove",
            labelanchor="nw"
        )
        frame_tabla.pack(fill="x", padx=5, pady=10)

        # Nombre + esquema
        frame_top = tk.Frame(frame_tabla, bg=COLOR_FONDO)
        frame_top.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_top, text="Nombre SQL:", font=FUENTE_PEQUENA,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left")
        entry_nombre = tk.Entry(frame_top, font=FUENTE_PEQUENA,
                                 bg=COLOR_ENTRADA, fg=COLOR_TEXTO,
                                 insertbackground=COLOR_TEXTO, relief="flat", bd=3)
        entry_nombre.pack(side="left", padx=(5, 15), ipady=2)
        entry_nombre.insert(0, "mi_tabla")

        tk.Label(frame_top, text="Esquema:", font=FUENTE_PEQUENA,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left")
        entry_esquema = tk.Entry(frame_top, font=FUENTE_PEQUENA,
                                  bg=COLOR_ENTRADA, fg=COLOR_TEXTO,
                                  insertbackground=COLOR_TEXTO, relief="flat", bd=3, width=10)
        entry_esquema.pack(side="left", padx=5, ipady=2)
        entry_esquema.insert(0, "public")

        tk.Label(frame_top, text="ON CONFLICT:", font=FUENTE_PEQUENA,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left", padx=(15, 5))
        entry_onconflict = tk.Entry(frame_top, font=FUENTE_PEQUENA,
                                     bg=COLOR_ENTRADA, fg=COLOR_TEXTO,
                                     insertbackground=COLOR_TEXTO, relief="flat", bd=3, width=15)
        entry_onconflict.pack(side="left", ipady=2)
        entry_onconflict.insert(0, "DO NOTHING")

        # Contenedor de columnas
        frame_columnas = tk.Frame(frame_tabla, bg=COLOR_FONDO)
        frame_columnas.pack(fill="x", padx=10, pady=5)

        # Referencias
        tabla_ref = {
            "frame": frame_tabla,
            "nombre": entry_nombre,
            "esquema": entry_esquema,
            "on_conflict": entry_onconflict,
            "frame_columnas": frame_columnas,
            "columnas": []
        }
        self.tablas_ui.append(tabla_ref)

        # Botones de la tabla
        frame_botones_tabla = tk.Frame(frame_tabla, bg=COLOR_FONDO)
        frame_botones_tabla.pack(fill="x", padx=10, pady=(0, 8))

        BotonVerde(frame_botones_tabla, text="+ Columna",
                   command=lambda t=tabla_ref: self.agregar_columna(t),
                   width=12).pack(side="left", padx=5)
        BotonVerde(frame_botones_tabla, text="🗑 Eliminar tabla",
                   command=lambda t=tabla_ref: self.eliminar_tabla(t),
                   width=15).pack(side="right", padx=5)

    def agregar_columna(self, tabla_ref):
        frame_col = tk.Frame(tabla_ref["frame_columnas"], bg=COLOR_FONDO)
        frame_col.pack(fill="x", pady=2)

        # Combo: columna del Excel
        combo_excel = ttk.Combobox(frame_col, values=self.columnas_excel,
                                    font=FUENTE_PEQUENA, width=22)
        combo_excel.pack(side="left", padx=2)
        if self.columnas_excel:
            combo_excel.set(self.columnas_excel[0])
        else:
            combo_excel.set("(cargá un Excel)")

        tk.Label(frame_col, text="→", font=FUENTE_PEQUENA,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left", padx=2)

        # Entry: nombre SQL
        entry_sql = tk.Entry(frame_col, font=FUENTE_PEQUENA,
                              bg=COLOR_ENTRADA, fg=COLOR_TEXTO,
                              insertbackground=COLOR_TEXTO, relief="flat", bd=3, width=20)
        entry_sql.pack(side="left", padx=2, ipady=2)
        entry_sql.insert(0, "columna_sql")

        # Combo: tipo
        tk.Label(frame_col, text="Tipo:", font=FUENTE_PEQUENA,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left", padx=(8, 2))
        combo_tipo = ttk.Combobox(frame_col, values=["texto", "numero", "fecha", "bool"],
                                   font=FUENTE_PEQUENA, width=8, state="readonly")
        combo_tipo.pack(side="left", padx=2)
        combo_tipo.set("texto")

        # Combo: transformación
        tk.Label(frame_col, text="Transform.:", font=FUENTE_PEQUENA,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left", padx=(8, 2))
        combo_transform = ttk.Combobox(frame_col, values=["", "prefijo"],
                                        font=FUENTE_PEQUENA, width=8, state="readonly")
        combo_transform.pack(side="left", padx=2)
        combo_transform.set("")

        BotonVerde(frame_col, text="✖",
                   command=lambda: self._eliminar_columna(tabla_ref, frame_col),
                   width=3).pack(side="left", padx=5)

        tabla_ref["columnas"].append({
            "frame": frame_col,
            "excel": combo_excel,
            "sql": entry_sql,
            "tipo": combo_tipo,
            "transform": combo_transform
        })

    def _eliminar_columna(self, tabla_ref, frame_col):
        tabla_ref["columnas"] = [c for c in tabla_ref["columnas"] if c["frame"] != frame_col]
        frame_col.destroy()

    def eliminar_tabla(self, tabla_ref):
        if tabla_ref in self.tablas_ui:
            self.tablas_ui.remove(tabla_ref)
        tabla_ref["frame"].destroy()

    # ========================================================
    # GUARDAR
    # ========================================================
    def guardar_config(self):
        if not self.tablas_ui:
            messagebox.showerror("Error", "Agregá al menos una tabla.")
            return

        config = {
            "nombre_proyecto": self.entry_nombre.get().strip(),
            "prefijo_username": self.entry_prefijo.get().strip(),
            "tablas": []
        }

        for tabla in self.tablas_ui:
            tabla_dict = {
                "nombre": tabla["nombre"].get().strip(),
                "esquema": tabla["esquema"].get().strip() or "public",
                "columnas": []
            }
            oc = tabla["on_conflict"].get().strip()
            if oc:
                tabla_dict["on_conflict"] = oc

            for col in tabla["columnas"]:
                col_dict = {
                    "columna_sql": col["sql"].get().strip(),
                    "columna_excel": col["excel"].get().strip(),
                }
                tipo = col["tipo"].get().strip()
                transform = col["transform"].get().strip()
                if tipo and tipo != "texto":
                    col_dict["tipo"] = tipo
                if transform:
                    col_dict["transformacion"] = transform
                tabla_dict["columnas"].append(col_dict)

            config["tablas"].append(tabla_dict)

        output_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile="config.json",
            filetypes=[("JSON", "*.json")]
        )
        if not output_path:
            return

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Éxito", f"Config guardada en:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")