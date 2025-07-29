from info_tools import InfoTools
from pandas_tools import PandasTools
from polars_tools import PolarsTools
from os_tools import OsTools
from singleton_tools import SingletonMeta
import datetime
import functools
import inspect
import polars as pl
import pandas as pd


class ConstantsAndTools(metaclass=SingletonMeta):
    def __init__(self):
        self.IT: InfoTools = InfoTools()
        self.PdT: PandasTools = PandasTools()
        self.PlT: PolarsTools = PolarsTools()
        self.OT: OsTools = OsTools()

        # -- Creacion de paths
        self.data_path, self.input_path, self.output_path = self.create_data_directories()

    def create_data_directories(self, root_path: str = "./") -> tuple:
        """
        Metodo que crea la carpeta data con subcarpetas input_data y output_data y retorna las 3 rutas
        :param root_path:
        :return:
        """

        # -- Carpeta data
        self.OT.create_folder_if_not_exists(f"{root_path}data")

        # -- Carpeta input_data
        self.OT.create_folder_if_not_exists(f"{root_path}data/input_data")

        # -- Carpeta output_data
        self.OT.create_folder_if_not_exists(f"{root_path}data/output_data")

        return f"{root_path}data", f"{root_path}data/input_data", f"{root_path}data/output_data"

    @staticmethod
    def hx_info_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            IT: InfoTools = InfoTools()
            start_time = datetime.datetime.now()
            IT.intro_print(f"[INFO DECORATOR] Ejecutando función / método: {func.__name__}")
            IT.info_print(f"🕒 Inicio: {start_time}", "light_magenta")

            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            IT.sub_intro_print("Parámetros:")
            for name, value in bound_args.arguments.items():
                IT.info_print(f"{name} = {value}")

            try:
                result = func(*args, **kwargs)
                if isinstance(result, pl.DataFrame) or isinstance(result, pd.DataFrame):
                    IT.info_print(f"No se pinta el resultado porque es un dataframe")
                else:
                    IT.info_print(f"✅ Resultado: {result}" if result is not None else "ℹ️ La función no devuelve nada")
            except Exception as e:
                IT.warning_print(f"❌ Error durante la ejecución: {e}")
                raise

            end_time = datetime.datetime.now()
            duration = end_time - start_time
            IT.sub_intro_print("Ejecucion correcta")
            IT.info_print(f"🕒 Tiempo de ejecución: {duration.total_seconds():.6f} segundos", "light_magenta")
            return result

        return wrapper