"""
Limpieza y enriquecimiento del dataset administrativo (inventario Zepto).

Uso (desde la raiz del proyecto, con el venv activo):
    python scripts/limpiar_administrativo.py
    python scripts/limpiar_administrativo.py ruta/entrada.xlsx ruta/salida.csv

Entrada : data/raw/zepto_v1.xlsx
Salida  : data/clean/administrativo_limpio.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw/zepto_v1.xlsx")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/clean/administrativo_limpio.csv")

COLUMNAS = {
    "Category": "categoria",
    "name": "producto",
    "mrp": "precio_lista",
    "discountPercent": "descuento_pct",
    "availableQuantity": "cantidad_disponible",
    "discountedSellingPrice": "precio_venta",
    "weightInGms": "peso_gramos",
    "outOfStock": "agotado",
    "quantity": "cantidad_paquete",
}

# Clasificacion propia (supuesto): agrupa las 14 categorias en 3 grupos
GRUPOS = {
    "Cooking Essentials": "Alimentos y bebidas",
    "Munchies": "Alimentos y bebidas",
    "Packaged Food": "Alimentos y bebidas",
    "Biscuits": "Alimentos y bebidas",
    "Chocolates & Candies": "Alimentos y bebidas",
    "Ice Cream & Desserts": "Alimentos y bebidas",
    "Dairy, Bread & Batter": "Alimentos y bebidas",
    "Beverages": "Alimentos y bebidas",
    "Fruits & Vegetables": "Alimentos y bebidas",
    "Meats, Fish & Eggs": "Alimentos y bebidas",
    "Personal Care": "Cuidado personal y salud",
    "Health & Hygiene": "Cuidado personal y salud",
    "Paan Corner": "Cuidado personal y salud",
    "Home & Cleaning": "Hogar y limpieza",
}


def limpiar(ruta_raw=RAW):
    log = []  # (paso, descripcion, filas_afectadas, filas_restantes)

    df = pd.read_excel(ruta_raw).rename(columns=COLUMNAS)
    n0 = len(df)
    log.append(("0. Carga", "Filas y columnas originales", n0, n0))

    # 1. Texto uniforme
    cambios = 0
    for col in ["categoria", "producto"]:
        limpio = df[col].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
        cambios += int((limpio != df[col]).sum())
        df[col] = limpio
    log.append(("1. Texto", "Nombres con espacios sobrantes corregidos (categoria y producto)", cambios, len(df)))

    # 2. Duplicados exactos (misma categoria y mismos valores)
    n = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    log.append(("2. Duplicados", "Filas identicas en todas las columnas eliminadas", n - len(df), len(df)))

    # 3. Precios invalidos
    n = len(df)
    df = df[(df["precio_lista"] > 0) & (df["precio_venta"] > 0)].reset_index(drop=True)
    log.append(("3. Precios", "Filas con precio de lista o de venta en 0 eliminadas", n - len(df), len(df)))

    # 4. Ceros imposibles -> vacio (no se inventa el dato)
    cero_peso = int((df["peso_gramos"] == 0).sum())
    cero_paq = int((df["cantidad_paquete"] == 0).sum())
    df["peso_gramos"] = df["peso_gramos"].replace(0, np.nan)
    df["cantidad_paquete"] = df["cantidad_paquete"].replace(0, np.nan)
    log.append(("4. Ceros invalidos", "peso_gramos = 0 convertido a vacio", cero_peso, len(df)))
    log.append(("4. Ceros invalidos", "cantidad_paquete = 0 convertido a vacio", cero_paq, len(df)))

    # 5. Unidades: paise -> rupias
    df["precio_lista"] = (df["precio_lista"] / 100).round(2)
    df["precio_venta"] = (df["precio_venta"] / 100).round(2)
    log.append(("5. Unidades", "precio_lista y precio_venta divididos entre 100 (paise a rupias)", len(df), len(df)))

    # 6. Identificador de producto (el dataset no trae ID)
    clave = ["producto", "precio_lista", "descuento_pct", "cantidad_disponible",
             "precio_venta", "peso_gramos", "cantidad_paquete"]
    df["id_producto"] = ["P%04d" % (i + 1) for i in df.groupby(clave, sort=False, dropna=False).ngroup()]
    df["n_categorias"] = df.groupby("id_producto")["categoria"].transform("nunique")
    df["es_listado_principal"] = (~df["id_producto"].duplicated()).astype(int)
    log.append(("6. Identificador", "Productos unicos detectados (id_producto)", int(df["id_producto"].nunique()), len(df)))
    log.append(("6. Identificador", "Productos listados en 2 o mas categorias", int((df.groupby("id_producto")["categoria"].nunique() > 1).sum()), len(df)))

    # 7. Columnas derivadas
    df["agotado_num"] = df["agotado"].astype(int)
    df["ahorro_unitario"] = (df["precio_lista"] - df["precio_venta"]).round(2)
    df["valor_inventario"] = (df["precio_venta"] * df["cantidad_disponible"]).round(2)
    df["ahorro_potencial"] = (df["ahorro_unitario"] * df["cantidad_disponible"]).round(2)
    df["grupo"] = df["categoria"].map(GRUPOS)
    df["rango_precio"] = pd.cut(df["precio_lista"], [0, 50, 100, 200, 500, np.inf],
                                labels=["0-50", "51-100", "101-200", "201-500", "500+"]).astype(str)
    df["rango_descuento"] = pd.cut(df["descuento_pct"], [-1, 0, 10, 20, 100],
                                   labels=["Sin descuento", "1-10%", "11-20%", "21% o mas"]).astype(str)
    df["nivel_stock"] = pd.cut(df["cantidad_disponible"], [-1, 0, 2, 5, 6],
                               labels=["Agotado", "Bajo (1-2)", "Medio (3-5)", "Alto (6)"]).astype(str)
    log.append(("7. Derivadas", "Columnas nuevas agregadas", 11, len(df)))

    orden = ["id_producto", "categoria", "grupo", "producto", "precio_lista", "descuento_pct",
             "precio_venta", "ahorro_unitario", "cantidad_disponible", "agotado", "agotado_num",
             "nivel_stock", "valor_inventario", "ahorro_potencial", "peso_gramos", "cantidad_paquete",
             "rango_precio", "rango_descuento", "n_categorias", "es_listado_principal"]
    return df[orden], log


if __name__ == "__main__":
    df, log = limpiar()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    for paso in log:
        print(" | ".join(str(x) for x in paso))
    print("\nFilas y columnas:", df.shape, "| Total de datos:", df.size)
    print("Guardado en:", OUT)
