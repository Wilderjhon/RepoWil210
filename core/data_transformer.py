"""
Lee el Excel, limpia los datos y exporta a CSV.
"""
import pandas as pd


class DataTransformer:
    """Transforma datos de Excel."""

    def __init__(self):
        self.df = None
        self.file_path = ""
        self.config_loader = None

    def set_config(self, config_loader):
        self.config_loader = config_loader

    def load_excel(self, file_path):
        try:
            self.df = pd.read_excel(file_path, header=0)
            self.df.columns = [str(c).strip() for c in self.df.columns]
            self.file_path = file_path
            return True, f"Excel cargado: {len(self.df)} filas, {len(self.df.columns)} columnas."
        except Exception as e:
            return False, f"Error al leer el Excel: {str(e)}"

    def clean_data(self):
        """Rellena vacíos según el tipo de dato de cada columna."""
        if self.df is None:
            return False, "No hay datos cargados."

        for col in self.df.columns:
            col_lower = str(col).lower()
            serie = self.df[col]
            dtype = serie.dtype

            es_fecha = (
                any(p in col_lower for p in ['fecha', 'date', 'nacimiento']) or
                pd.api.types.is_datetime64_any_dtype(dtype)
            )
            es_numerica = (
                any(p in col_lower for p in ['dni', 'legajo', 'celular', 'telefono', 'año']) or
                pd.api.types.is_numeric_dtype(dtype)
            )

            if es_fecha:
                try:
                    self.df[col] = pd.to_datetime(serie, errors='coerce')
                    self.df[col] = self.df[col].fillna(pd.Timestamp('1900-01-01'))
                    self.df[col] = self.df[col].dt.strftime('%Y-%m-%d')
                except Exception:
                    self.df[col] = serie.fillna('1900-01-01')
            elif es_numerica:
                self.df[col] = pd.to_numeric(serie, errors='coerce').fillna(0)
                try:
                    if self.df[col].apply(lambda x: float(x).is_integer()).all():
                        self.df[col] = self.df[col].astype(int)
                except Exception:
                    pass
            else:
                self.df[col] = serie.fillna("VACIO")

        return True, "Datos limpiados."

    def export_to_csv(self, output_path):
        if self.df is None:
            return False, "No hay datos para exportar."
        try:
            self.df.to_csv(output_path, index=False, encoding='utf-8-sig', sep=';')
            return True, f"CSV guardado en: {output_path}"
        except Exception as e:
            return False, f"Error al guardar CSV: {str(e)}"

    def buscar_columna(self, excel_col_name):
        """Busca una columna en el Excel por nombre exacto (case-insensitive)."""
        if self.df is None:
            return None
        for c in self.df.columns:
            if str(c).strip().lower() == str(excel_col_name).strip().lower():
                return c
        return None