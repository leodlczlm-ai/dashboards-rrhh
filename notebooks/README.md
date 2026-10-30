# Dashboards de RR.HH. y administración en Power BI

Proyecto final de **Herramientas de Visualización** · Ingeniería en Ciencia de Datos e Inteligencia Artificial · Universidad Politécnica de Gómez Palacio (UPGP)
**Autor:** Leonardo de Lara Calzada

## Objetivo

Recolectar, limpiar y analizar dos datasets (uno de empleados y uno de inventario) y presentarlos en dos dashboards de Power BI orientados a públicos distintos:

- **Dashboard de empleados:** perfil de la plantilla y tasa de salida a 2 años.
- **Dashboard administrativo:** inventario, descuentos y productos agotados.

## Datasets

| | Empleados | Administrativo (inventario) |
|---|---|---|
| Archivo original | `data/raw/Empleados.csv` | `data/raw/zepto_v1.xlsx` |
| Fuente | Kaggle · *[completar autor y enlace]* | Kaggle · *[completar autor y enlace]* |
| Licencia | *[completar]* | *[completar]* |
| Fecha de descarga | *[completar]* | *[completar]* |
| Filas × columnas originales | 4,653 × 9 | 3,732 × 9 |
| **Datos originales** | **41,877** | **33,588** |
| Dataset limpio | 4,653 × 18 = 83,754 datos | 3,729 × 20 = 74,580 datos |

**Requisito de volumen (mínimo 15,000 datos):** se cumple en ambos datasets, tanto en los originales como en los limpios. En el dataset de empleados, aun quitando las filas repetidas (2,764 filas × 9 columnas) quedan 24,876 datos.

## Estructura del repositorio

```
├── data/
│   ├── raw/          Datos originales, sin modificar
│   └── clean/        Datos limpios que consume Power BI
├── notebooks/        01_empleados.ipynb · 02_administrativo.ipynb
├── scripts/          limpiar_empleados.py · limpiar_administrativo.py
├── dashboards/       dashboard_empleados.pbix · dashboard_administrativo.pbix
├── docs/             Capturas de los dashboards y libros de Excel con estadísticas, diccionario y registro de limpieza
├── requirements.txt
└── README.md
```

## Cómo reproducir

```powershell
git clone https://github.com/USUARIO/REPOSITORIO.git
cd REPOSITORIO
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python scripts\limpiar_empleados.py
python scripts\limpiar_administrativo.py
```

Los notebooks se abren en VS Code con el kernel `venv` y se ejecutan desde la carpeta `notebooks/`. Los dos `.pbix` se abren con Power BI Desktop.

## Limpieza

### Empleados (4,653 filas)

| Paso | Resultado |
|---|---|
| Espacios sobrantes en texto | 0 valores |
| Valores nulos | 0 |
| Valores fuera de rango (edad, nivel de pago, salida, experiencia) | 0 |
| Filas idénticas a otra | 1,889 identificadas y **conservadas** (marcadas con `n_repeticiones` y `es_primera_aparicion`) |
| Nuevas columnas | 9: `id_empleado`, `rango_edad`, `antiguedad_anios`, `nivel_pago_texto`, `rango_experiencia`, `estuvo_en_banca_num`, `estatus_2_anios`, `n_repeticiones`, `es_primera_aparicion` |
| Filas finales | 4,653 |

**Decisión sobre filas repetidas:** el dataset no trae ID y sus columnas toman pocos valores, así que las filas idénticas pueden ser personas distintas. Se conservaron. La decisión cambia la tasa de salida global de 34.4 % (todas las filas) a 39.4 % (sin repetidas); ambas versiones se comparan en el notebook y en `docs/empleados_limpio.xlsx`.

### Administrativo (3,732 filas)

| Paso | Filas afectadas | Filas restantes |
|---|---|---|
| Nombres con espacios sobrantes corregidos | 337 | 3,732 |
| Filas idénticas en todas las columnas eliminadas | 2 | 3,730 |
| Filas con precio de lista o de venta en 0 eliminadas | 1 | 3,729 |
| `peso_gramos` en 0 dejado vacío | 4 | 3,729 |
| `cantidad_paquete` en 0 dejado vacío | 6 | 3,729 |
| Precios de paise a rupias (÷ 100) | todos | 3,729 |
| Nuevas columnas | 11 | 3,729 |

**Hallazgo clave:** varias categorías contienen exactamente los mismos productos con los mismos valores (por ejemplo, *Cooking Essentials* y *Munchies*; *Chocolates & Candies*, *Ice Cream & Desserts* y *Packaged Food*; *Paan Corner* y *Personal Care*). Hay 3,729 filas pero solo **1,800 productos únicos**. Sumar sobre todas las filas infla el valor del inventario 2.12 veces (₹2.24 M frente a ₹1.06 M), por lo que se crearon `id_producto` y `es_listado_principal` para calcular los totales sin duplicar productos.

## Estadística descriptiva

### Empleados (todas las filas, n = 4,653)

| Variable | Media | Mediana | Moda | Desv. estándar |
|---|---|---|---|---|
| Edad (años) | 29.39 | 28 | 26 | 4.83 |
| Experiencia (años) | 2.91 | 3 | 2 | 1.56 |
| Año de ingreso | 2015.06 | 2015 | 2017 | 1.86 |
| Antigüedad (años) | 2.94 | 3 | 1 | 1.86 |

La media de edad es mayor que la mediana (asimetría a la derecha): unos pocos empleados mayores elevan el promedio.

### Inventario (productos únicos, n = 1,800)

| Variable | Media | Mediana | Moda | Desv. estándar |
|---|---|---|---|---|
| Precio de lista (₹) | 153.16 | 105 | 60 | 162.71 |
| Precio de venta (₹) | 138.66 | 99 | 25 | 139.66 |
| Descuento (%) | 7.72 | 6 | 0 | 8.84 |
| Cantidad disponible | 4.00 | 5 | 6 | 2.20 |
| Valor de inventario (₹) | 588.03 | 378 | 0 | 747.99 |

La media del precio supera a la mediana y la desviación estándar es mayor que la media: pocos productos caros elevan el promedio.

El detalle completo (mínimos, máximos, coeficiente de variación y comparativas) está en `docs/empleados_limpio.xlsx` y `docs/administrativo_limpio.xlsx`, calculado con fórmulas.

## Dashboards

### Dashboard de empleados

![Dashboard de empleados](docs/captura_empleados.png)

| # | Visual | Medida |
|---|---|---|
| 1 | Tarjetas | Total de empleados · Edad promedio · Tasa de salida |
| 2 | Barras | Tasa de salida por ciudad |
| 3 | Columnas agrupadas | Tasa de salida por educación y nivel de pago |
| 4 | Líneas | Empleados por año de ingreso |
| 5 | Columnas apiladas | Empleados por rango de edad y género |

### Dashboard administrativo

![Dashboard administrativo](docs/captura_administrativo.png)

| # | Visual | Medida |
|---|---|---|
| 1 | Tarjetas | Productos únicos · Valor del inventario · % de agotados |
| 2 | Barras | Valor del inventario por grupo |
| 3 | Barras | Descuento promedio por categoría |
| 4 | Columnas | Productos por rango de precio |
| 5 | Barras | % de agotados por categoría |

### Medidas DAX

```
-- Empleados
Total Empleados = COUNTROWS(empleados)
Tasa Salida = AVERAGE(empleados[salida_2_anios])
Edad Promedio = AVERAGE(empleados[edad])

-- Inventario
Productos Unicos = DISTINCTCOUNT(inventario[id_producto])
Valor Inventario = CALCULATE(SUM(inventario[valor_inventario]), inventario[es_listado_principal] = 1)
Pct Agotados = CALCULATE(AVERAGE(inventario[agotado_num]), inventario[es_listado_principal] = 1)
Descuento Promedio = AVERAGE(inventario[descuento_pct]) / 100
```

## Hallazgos principales

- **Empleados:** la tasa de salida a 2 años es de 34.4 %. Es más alta en Pune (50.4 %) que en New Delhi (31.6 %) y Bangalore (26.7 %), en el nivel de pago medio (59.9 %) y entre quienes tienen maestría (48.8 %). Las correlaciones numéricas son débiles (la mayor es −0.20, con el nivel de pago).
- **Inventario:** el 12.1 % de los productos únicos está agotado y casi el 30 % no tiene descuento. *Biscuits* tiene el mayor porcentaje de agotados (28.6 %) y *Fruits & Vegetables* el mayor descuento promedio (15.5 %). Alimentos y bebidas concentra cerca del 59 % del valor del inventario.

## Limitaciones y supuestos

- `salida_2_anios` (`LeaveOrNot`) se interpreta como la salida del empleado en los siguientes 2 años; el nivel de pago 1 se interpreta como el más alto. *[confirmar en la descripción de Kaggle]*
- Casi todos los empleados que ingresaron en 2018 aparecen con salida = 1 (98.6 %): es un patrón del dataset, no una conclusión real.
- Las diferencias por género, ciudad y educación son asociaciones dentro de este dataset; no demuestran causa.
- Los precios del inventario se interpretaron como paise (÷ 100 para obtener rupias). *[confirmar en Kaggle]*
- `cantidad_disponible` llega como máximo a 6 y probablemente está topada; el valor del inventario es un indicador relativo.
- El inventario no tiene fecha, por lo que no incluye tendencias en el tiempo.
- La clasificación en tres grupos (`grupo`) es una agrupación propia de las 14 categorías.

## Tecnologías

Python 3 · pandas · NumPy · Matplotlib · Seaborn · Jupyter · Power BI Desktop · Git y GitHub · Visual Studio Code
