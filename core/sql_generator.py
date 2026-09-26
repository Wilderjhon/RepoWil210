"""
Genera las sentencias INSERT SQL a partir del DataFrame y la configuración.
"""
import pandas as pd


class SQLGenerator:
    """Genera SQL configurable según el JSON."""

    def __init__(self, transformer, config_loader):
        self.transformer = transformer
        self.config_loader = config_loader

    def _esc(self, v):
        """Escapa comillas simples para SQL."""
        return str(v).replace("'", "''")

    def _valor_sql(self, valor, tipo):
        """Convierte un valor Python en expresión SQL."""
        if valor is None:
            return "NULL"
        v_str = str(valor).strip()
        if v_str in ("", "VACIO", "NaT", "nan"):
            return "NULL"

        if tipo == "numero":
            try:
                return str(int(float(v_str)))
            except ValueError:
                return "0"
        elif tipo == "fecha":
            if v_str == "1900-01-01":
                return "NULL"
            return f"'{self._esc(v_str)}'::date"
        elif tipo == "bool":
            return "true" if v_str.lower() in ("true", "1", "si", "sí", "yes") else "false"
        else:
            return f"'{self._esc(v_str)}'"

    def generate(self, prefijo_override=None):
        """Genera el SQL completo."""
        df = self.transformer.df
        if df is None:
            return False, "No hay datos cargados."

        if self.config_loader is None or self.config_loader.config is None:
            return False, "No hay configuración cargada."

        config = self.config_loader.config
        prefijo = (prefijo_override or config.get("prefijo_username", "")).strip()

        lineas = []
        lineas.append(f"-- Proyecto: {config.get('nombre_proyecto', 'Sin nombre')}")
        lineas.append(f"-- Registros en Excel: {len(df)}")
        lineas.append("")

        tablas = config.get("tablas", [])
        resumen = []

        for tabla in tablas:
            nombre_tabla = tabla["nombre"]
            esquema = tabla.get("esquema", "public")
            columnas_config = tabla.get("columnas", [])
            on_conflict = tabla.get("on_conflict", "")

            # Validar columnas requeridas
            faltantes = []
            for col_cfg in columnas_config:
                if "columna_excel" in col_cfg:
                    if self.transformer.buscar_columna(col_cfg["columna_excel"]) is None:
                        faltantes.append(col_cfg["columna_excel"])

            if faltantes:
                return False, (
                    f"En la tabla '{nombre_tabla}', no se encontraron estas columnas:\n"
                    f"  - " + "\n  - ".join(faltantes)
                )

            lineas.append("-- ==========================================================")
            lineas.append(f"-- TABLA: {esquema}.{nombre_tabla}")
            lineas.append("-- ==========================================================")

            nombres_sql = [c["columna_sql"] for c in columnas_config]
            cols_str = ", ".join(f'"{n}"' for n in nombres_sql)

            valores_filas = []
            for _, row in df.iterrows():
                valores = []
                for col_cfg in columnas_config:
                    # 1) Valor fijo
                    if "valor_fijo" in col_cfg:
                        vf = col_cfg["valor_fijo"]
                        if isinstance(vf, bool):
                            valores.append("true" if vf else "false")
                        elif isinstance(vf, (int, float)):
                            valores.append(str(vf))
                        else:
                            valores.append(f"'{self._esc(vf)}'")
                        continue

                    # 2) Subconsulta
                    if "subconsulta" in col_cfg:
                        sub = col_cfg["subconsulta"]
                        col_match = self.transformer.buscar_columna(sub["columna_excel_match"])
                        if col_match is None:
                            valores.append("NULL")
                            continue
                        v_match = str(row[col_match]).strip()
                        if sub.get("transformacion") == "prefijo":
                            v_match = f"{prefijo}{v_match}"
                        valores.append(
                            f'(SELECT "{sub["columna_busqueda"]}" FROM '
                            f'"{sub["tabla"]}" WHERE "{sub["columna_busqueda"]}" = '
                            f"'{self._esc(v_match)}' LIMIT 1)"
                        )
                        continue

                    # 3) Valor desde Excel
                    col_excel = self.transformer.buscar_columna(col_cfg["columna_excel"])
                    if col_excel is None:
                        valores.append("NULL")
                        continue

                    v = row[col_excel]
                    tipo = col_cfg.get("tipo", "texto")

                    if col_cfg.get("transformacion") == "prefijo":
                        v = f"{prefijo}{v}"
                        tipo = "texto"

                    valores.append(self._valor_sql(v, tipo))

                valores_filas.append("    (" + ", ".join(valores) + ")")

            lineas.append(f'INSERT INTO "{esquema}"."{nombre_tabla}" ({cols_str})')
            lineas.append("VALUES")
            lineas.append(",\n".join(valores_filas))
            if on_conflict:
                lineas.append(f"ON CONFLICT {on_conflict};")
            else:
                lineas.append(";")
            lineas.append("")

            resumen.append(f"  - {nombre_tabla}: {len(valores_filas)} filas")

        lineas.append("-- ==========================================================")
        lineas.append("-- RESUMEN")
        lineas.append("-- ==========================================================")
        lineas.extend(resumen)

        return True, "\n".join(lineas)