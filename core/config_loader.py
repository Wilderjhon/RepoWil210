"""
Carga y valida el archivo config.json.
"""
import json


class ConfigLoader:
    """Carga un archivo JSON de configuración."""

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = None

    def load(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return True, "Configuración cargada correctamente."
        except FileNotFoundError:
            return False, f"No se encontró el archivo: {self.config_path}"
        except json.JSONDecodeError as e:
            return False, f"El archivo JSON tiene errores: {str(e)}"
        except Exception as e:
            return False, f"Error al leer la configuración: {str(e)}"

    def get_tablas(self):
        return self.config.get("tablas", [])

    def get_prefijo(self):
        return self.config.get("prefijo_username", "")

    def get_nombre_proyecto(self):
        return self.config.get("nombre_proyecto", "Sin nombre")