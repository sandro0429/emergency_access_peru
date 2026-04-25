"""
Funciones para cargar los conjuntos de datos originales desde data/raw/.
Cada función retorna el objeto sin procesar (raw), sin modificaciones.

Archivos esperados en data/raw/:
- CCPP_IGN100K.shp (+ .dbf, .prj, .shx...) — centros poblados (IGN)
- DISTRITOS.shp (+ archivos auxiliares) — límites de distrito
- IPRESS.csv — registro de centros de salud de SUSALUD
- ConsultaC1_2025_v20.csv — producción de atención de emergencia (MINSA C1)
"""

from pathlib import Path
import pandas as pd
import geopandas as gpd

# Esta ruta debería resolver a:
# D:\Data_science_Python_2026\emergency_access_peru\data\raw
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def load_districts(filename: str = "DISTRITOS.shp") -> gpd.GeoDataFrame:
    """Carga el shapefile de límites distritales."""
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de distritos: {path}")
    return gpd.read_file(path)


def load_populated_centers(filename: str = "CCPP_IGN100K.shp") -> gpd.GeoDataFrame:
    """Carga el shapefile de centros poblados."""
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de centros poblados: {path}")
    return gpd.read_file(path)


def _read_tabular(path: Path) -> pd.DataFrame:
    """Lee archivos tabulares .csv o .xlsx."""
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo tabular: {path}")

    suffix = path.suffix.lower()

    if suffix in [".xlsx", ".xls"]:
        return pd.read_excel(path)

    if suffix == ".csv":
        attempts = [
            {"sep": ",", "encoding": "utf-8"},
            {"sep": ";", "encoding": "utf-8"},
            {"sep": ",", "encoding": "latin1"},
            {"sep": ";", "encoding": "latin1"},
        ]

        last_error = None
        for params in attempts:
            try:
                df = pd.read_csv(path, low_memory=False, **params)
                if df.shape[1] > 1:
                    return df
            except Exception as e:
                last_error = e

        raise ValueError(f"No se pudo leer el CSV {path}. Último error: {last_error}")

    raise ValueError(f"Formato no soportado: {path.suffix}")


def load_ipress(filename: str = "IPRESS.csv") -> pd.DataFrame:
    """Carga la base de establecimientos de salud IPRESS."""
    path = RAW_DIR / filename
    return _read_tabular(path)


def load_emergency_activity(filename: str = "ConsultaC1_2025_v20.csv") -> pd.DataFrame:
    """Carga la base de producción asistencial de emergencia."""
    path = RAW_DIR / filename
    return _read_tabular(path)


def load_all() -> dict:
    """Carga los cuatro datasets requeridos."""
    return {
        "districts": load_districts(),
        "ccpp": load_populated_centers(),
        "ipress": load_ipress(),
        "emergency": load_emergency_activity(),
    }


if __name__ == "__main__":
    print(f"RAW_DIR detectado: {RAW_DIR}")

    datasets = load_all()

    for name, obj in datasets.items():
        print(f"\nDataset: {name}")
        print(f"Tipo: {type(obj)}")
        print(f"Shape: {obj.shape}")

        if hasattr(obj, "crs"):
            print(f"CRS: {obj.crs}")

        print("Primeras columnas:")
        print(list(obj.columns[:10]))