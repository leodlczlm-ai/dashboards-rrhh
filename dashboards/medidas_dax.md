# Medidas DAX de los dashboards

Guardar este archivo en `dashboards/`. Las cifras de validación salen de los scripts `scripts/estadisticas_empleados.py` y `scripts/estadisticas_administrativo.py` (pandas); las medidas se verifican en Power BI comparando contra ellas.

## Preparación en Power BI

1. **Obtener datos → Texto/CSV** y revisar `Origen del archivo = 65001: Unicode (UTF-8)`.
2. En **Transformar datos**, renombrar la consulta: `empleados` (en `dashboard_empleados.pbix`) o `inventario` (en `dashboard_administrativo.pbix`), para que las medidas funcionen tal cual.
3. Dar formato de porcentaje (en **Herramientas de medida**) a las medidas marcadas con `%`.

---

## Dashboard de empleados (tabla `empleados`)

```
Total Empleados = COUNTROWS(empleados)

Empleados Que Se Van = CALCULATE(COUNTROWS(empleados), empleados[salida_2_anios] = 1)

Tasa Salida = AVERAGE(empleados[salida_2_anios])                      -- %

Edad Promedio = AVERAGE(empleados[edad])

Experiencia Promedio = AVERAGE(empleados[experiencia_anios])

Pct En Banca = AVERAGE(empleados[estuvo_en_banca_num])                -- %
```

Estadísticas opcionales en DAX (la moda se calcula en Python, porque DAX no tiene una función de moda):

```
Edad Mediana = MEDIAN(empleados[edad])

Edad Desv Std = STDEV.S(empleados[edad])
```

Columnas de orden (Modelado → Nueva columna, y después **Ordenar por columna**):

```
Orden Educacion = SWITCH(empleados[educacion], "Licenciatura", 1, "Maestría", 2, "Doctorado", 3)
```

Además, ordenar `nivel_pago_texto` por `nivel_pago` para ver Alto, Medio y Bajo.

### Cifras de validación (todas las filas)

| Medida | Valor esperado |
|---|---|
| Total Empleados | 4,653 |
| Empleados Que Se Van | 1,600 |
| Tasa Salida | 34.4 % |
| Edad Promedio | 29.39 |
| Experiencia Promedio | 2.91 |
| Pct En Banca | 10.3 % |
| Edad Mediana | 28 |
| Edad Desv Std | 4.83 |
| Tasa Salida en Pune / New Delhi / Bangalore | 50.4 % / 31.6 % / 26.7 % |

---

## Dashboard administrativo (tabla `inventario`)

El dataset repite los mismos productos en varias categorías. Las medidas de **total** usan solo la primera aparición de cada producto (`es_listado_principal = 1`); las medidas **por categoría** usan todas las filas, para que cada categoría se vea completa.

```
-- Totales (productos únicos)
Productos Unicos = DISTINCTCOUNT(inventario[id_producto])

Valor Inventario = CALCULATE(SUM(inventario[valor_inventario]), inventario[es_listado_principal] = 1)

Productos Agotados = CALCULATE(COUNTROWS(inventario), inventario[es_listado_principal] = 1, inventario[agotado_num] = 1)

Pct Agotados = CALCULATE(AVERAGE(inventario[agotado_num]), inventario[es_listado_principal] = 1)          -- %

Descuento Promedio = CALCULATE(AVERAGE(inventario[descuento_pct]), inventario[es_listado_principal] = 1) / 100   -- %

Ahorro Potencial = CALCULATE(SUM(inventario[ahorro_potencial]), inventario[es_listado_principal] = 1)

Precio Mediano = CALCULATE(MEDIAN(inventario[precio_lista]), inventario[es_listado_principal] = 1)
```

```
-- Por categoría (todas las filas, sin el filtro de únicos)
Pct Agotados Categoria = AVERAGE(inventario[agotado_num])                                                  -- %

Descuento Promedio Categoria = AVERAGE(inventario[descuento_pct]) / 100                                    -- %
```

Columnas de orden (Modelado → Nueva columna, y después **Ordenar por columna**):

```
Orden Rango Precio = SWITCH(inventario[rango_precio], "0-50", 1, "51-100", 2, "101-200", 3, "201-500", 4, "500+", 5)

Orden Nivel Stock = SWITCH(inventario[nivel_stock], "Agotado", 1, "Bajo (1-2)", 2, "Medio (3-5)", 3, "Alto (6)", 4)
```

### Cifras de validación

| Medida | Valor esperado |
|---|---|
| Productos Unicos | 1,800 |
| Valor Inventario | 1,058,453.60 |
| Productos Agotados | 217 |
| Pct Agotados | 12.1 % |
| Descuento Promedio | 7.72 % |
| Ahorro Potencial | 115,512.40 |
| Precio Mediano | 105 |
| Pct Agotados Categoria: Biscuits / Beverages / Personal Care | 28.6 % / 21.7 % / 6.1 % |
| Descuento Promedio Categoria: Fruits & Vegetables / Home & Cleaning | 15.5 % / 5.7 % |

Si se suma `valor_inventario` sobre todas las filas (sin el filtro de únicos) da ₹2,241,460.60, es decir, 2.12 veces el valor real: por eso el filtro.

---

## Qué visual usa cada medida

| Dashboard | Visual | Medidas y campos |
|---|---|---|
| Empleados | 1. Tarjetas | Total Empleados · Empleados Que Se Van · Tasa Salida · Edad Promedio |
| Empleados | 2. Barras | Tasa Salida por `ciudad` |
| Empleados | 3. Columnas agrupadas | Tasa Salida por `educacion`, leyenda `nivel_pago_texto` |
| Empleados | 4. Líneas | Total Empleados por `anio_ingreso` |
| Empleados | 5. Columnas apiladas | Total Empleados por `rango_edad`, leyenda `genero` |
| Administrativo | 1. Tarjetas | Productos Unicos · Valor Inventario · Pct Agotados · Descuento Promedio |
| Administrativo | 2. Barras | Valor Inventario por `grupo` |
| Administrativo | 3. Barras | Descuento Promedio Categoria por `categoria` |
| Administrativo | 4. Columnas | Productos Unicos por `rango_precio` |
| Administrativo | 5. Barras | Pct Agotados Categoria por `categoria` |
