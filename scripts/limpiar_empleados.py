"""
Limpieza y enriquecimiento del dataset de empleados (Employee.csv de Kaggle).

Uso (desde la raiz del proyecto, con el venv activo):
    python scripts/limpiar_empleados.py
    python scripts/limpiar_empleados.py ruta/entrada.csv ruta/salida.csv

Entrada : data/raw/Empleados.csv
Salida  : data/clean/empleados_limpio.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw/Empleados.csv")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/clean/empleados_limpio.csv")

COLUMNAS = {
    "Education": "educacion",
    "JoiningYear": "anio_ingreso",
    "City": "ciudad",
    "PaymentTier": "nivel_pago",
    "Age": "edad",
    "Gender": "genero",
    "EverBenched": "estuvo_en_banca",
    "ExperienceInCurrentDomain": "experiencia_anios",
    "LeaveOrNot": "salida_2_anios",
}
EDUCACION = {"Bachelors": "Licenciatura", "Masters": "Maestría", "PHD": "Doctorado"}
GENERO = {"Male": "Masculino", "Female": "Femenino"}
BANCA = {"Yes": "Sí", "No": "No"}
# SUPUESTO (confirmar en la descripcion del dataset en Kaggle): 1 = nivel de pago mas alto, 3 = mas bajo
NIVEL_PAGO = {1: "Alto", 2: "Medio", 3: "Bajo"}


def limpiar(ruta_raw=RAW):
    log = []  # (paso, descripcion, afectadas, filas_restantes)

    df = pd.read_csv(ruta_raw).rename(columns=COLUMNAS)
    n0 = len(df)
    log.append(("0. Carga", "Filas originales (9 columnas)", n0, n0))

    # 1. Texto uniforme
    cambios = 0
    for col in ["educacion", "ciudad", "genero", "estuvo_en_banca"]:
        limpio = df[col].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
        cambios += int((limpio != df[col]).sum())
        df[col] = limpio
    log.append(("1. Texto", "Valores con espacios sobrantes corregidos", cambios, len(df)))

    # 2. Nulos
    nulos = int(df.isnull().sum().sum())
    log.append(("2. Nulos", "Valores vacios encontrados (no hubo que imputar)", nulos, len(df)))

    # 3. Valores fuera de rango
    fuera = int(((df["edad"] < 18) | (df["edad"] > 70)).sum()
                + (~df["nivel_pago"].isin([1, 2, 3])).sum()
                + (~df["salida_2_anios"].isin([0, 1])).sum()
                + (df["experiencia_anios"] < 0).sum()
                + ((df["edad"] - df["experiencia_anios"]) < 18).sum())
    log.append(("3. Rangos", "Edad fuera de 18-70, nivel de pago fuera de 1-3, salida distinta de 0/1, experiencia negativa o edad menos experiencia menor a 18", fuera, len(df)))

    # 4. Filas repetidas: se IDENTIFICAN pero se CONSERVAN (el dataset no trae ID)
    originales = ["educacion", "anio_ingreso", "ciudad", "nivel_pago", "edad", "genero",
                  "estuvo_en_banca", "experiencia_anios", "salida_2_anios"]
    n_rep = df.groupby(originales)["edad"].transform("size")
    es_primera = (~df.duplicated(subset=originales)).astype(int)
    repetidas = int((es_primera == 0).sum())
    log.append(("4. Filas repetidas", "Filas identicas a otra en las 9 columnas: se conservan y se marcan con n_repeticiones y es_primera_aparicion", repetidas, len(df)))

    # 5. Identificador
    df.insert(0, "id_empleado", ["E%04d" % i for i in range(1, len(df) + 1)])
    log.append(("5. Identificador", "id_empleado creado (el dataset original no trae ID)", len(df), len(df)))

    # 6. Traducciones
    df["educacion"] = df["educacion"].map(EDUCACION).fillna(df["educacion"])
    df["genero"] = df["genero"].map(GENERO).fillna(df["genero"])
    df["estuvo_en_banca"] = df["estuvo_en_banca"].map(BANCA).fillna(df["estuvo_en_banca"])
    log.append(("6. Traducciones", "Educacion, genero y estuvo_en_banca traducidos al espanol", len(df), len(df)))

    # 7. Columnas derivadas
    anio_ref = int(df["anio_ingreso"].max())
    df["antiguedad_anios"] = anio_ref - df["anio_ingreso"]
    df["nivel_pago_texto"] = df["nivel_pago"].map(NIVEL_PAGO)
    df["estuvo_en_banca_num"] = (df["estuvo_en_banca"] == "Sí").astype(int)
    df["estatus_2_anios"] = np.where(df["salida_2_anios"] == 1, "Se va", "Se queda")
    df["rango_edad"] = pd.cut(df["edad"], [17, 25, 30, 35, 40, 70],
                              labels=["18-25", "26-30", "31-35", "36-40", "41+"]).astype(str)
    df["rango_experiencia"] = pd.cut(df["experiencia_anios"], [-1, 1, 3, 5, 100],
                                     labels=["0-1", "2-3", "4-5", "6+"]).astype(str)
    df["n_repeticiones"] = n_rep.values
    df["es_primera_aparicion"] = es_primera.values
    log.append(("7. Derivadas", f"Columnas nuevas agregadas (año de referencia = {anio_ref}, el último año de ingreso)", 8, len(df)))

    orden = ["id_empleado", "educacion", "ciudad", "genero", "edad", "rango_edad", "anio_ingreso",
             "antiguedad_anios", "nivel_pago", "nivel_pago_texto", "experiencia_anios",
             "rango_experiencia", "estuvo_en_banca", "estuvo_en_banca_num", "salida_2_anios",
             "estatus_2_anios", "n_repeticiones", "es_primera_aparicion"]
    return df[orden], log


if __name__ == "__main__":
    df, log = limpiar()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, encoding="utf-8-sig")
    for paso in log:
        print(" | ".join(str(x) for x in paso))
    sin_rep = df[df["es_primera_aparicion"] == 1]
    print("\nFilas y columnas:", df.shape, "| Total de datos:", df.size)
    print("Sin filas repetidas:", sin_rep.shape, "| Total de datos:", sin_rep.size)
    print("Guardado en:", OUT)
