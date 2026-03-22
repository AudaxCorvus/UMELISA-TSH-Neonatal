## Análisis Comparativo de Métodos de Interpolación para TSH Neonatal

### Evaluación en Dos Placas

---

### 1. Resumen General

Se evaluaron **9 métodos** de interpolación en dos placas independientes (15 muestras cada una). Todos los métodos coincidieron en la clasificación clínica (Elevado/Normal) para la totalidad de las muestras, confirmando su validez diagnóstica.

---

### 2. Comportamiento de los Métodos

| Método | Placa A (vs Semilog) | Placa B (vs Semilog) | Clasificación |
|--------|---------------------|---------------------|---------------|
| **Semilog Piecewise** | Referencia | Referencia | ✅ |
| **Linear Piecewise** | Prácticamente idéntico | Prácticamente idéntico | ✅ |
| **Linear Extrapolation** | Idéntico a Linear Piecewise | Idéntico a Linear Piecewise | ✅ |
| **Polynomial Degree 2** | **Inaceptable**: valores erráticos (muestra 2: +980%, muestra 4: -18%) | **Inaceptable**: muestra 2: +380% | ⚠️ **No recomendar** |
| **Polynomial Degree 3** | Oscilaciones en muestras medias | Similar a Semilog Piecewise | ⚠️ Usar con precaución |
| **Akima Spline** | Muy cercano a Semilog Piecewise | Muy cercano a Semilog Piecewise | ✅ Recomendable |
| **Cubic Spline** | Muy cercano a Semilog Piecewise | Muy cercano a Semilog Piecewise | ✅ Recomendable |
| **Model 4PL** | Estable, ligeramente superior en muestras medias (+5-10%) | Estable, ligeramente superior | ✅ **Recomendado** |
| **Model 5PL** | Subestima en muestras muy altas (muestra 7: -7%) | Similar a Model 4PL | ⚠️ Evaluar más |

---

### 3. Problemas Identificados

| Método | Problema | Gravedad |
|--------|----------|----------|
| **Polynomial Degree 2** | Sobreestima gravemente en muestras bajas, subestima en medias | ❌ Crítico |
| **Polynomial Degree 3** | Oscilaciones en zona media | ⚠️ Moderado |
| **Model 5PL** | Subestima en muestras >150 mUI/L | ⚠️ Leve |

---

### 4. Recomendaciones Finales

| Prioridad | Método | Justificación |
|-----------|--------|---------------|
| **1** | **Model 4PL** | Estable en todo el rango, comportamiento suave, estándar industrial en inmunoensayos |
| **2** | **Semilog Piecewise** | Método histórico SUMA, validado clínicamente, excelente para compatibilidad retrospectiva |
| **3** | **Akima Spline / Cubic Spline** | Alternativas robustas, muy cercanas a Semilog Piecewise |
| **No recomendar** | **Polynomial Degree 2** | Comportamiento errático, valores fuera de rango en muestras bajas |

---

### 5. Conclusión

**Model 4PL** es la mejor opción por su estabilidad y comportamiento suave en todo el rango de concentraciones. **Semilog Piecewise** sigue siendo una alternativa válida para mantener compatibilidad con resultados históricos. **Polynomial Degree 2 debe evitarse** por su comportamiento errático, especialmente en muestras con baja fluorescencia.

## Análisis de Curvas de Calibración - Placa A

### Comparativa Visual de los 9 Métodos

---

### 1. Curva Base (Semilog Piecewise)

**Imagen sugerida:** `A_semilog.png`

**Observaciones:**
- Curva suave y monótona creciente
- Transición adecuada entre el primer calibrador (A=0.52 mUI/L, fluo=1.82) y el segundo (B=10.75 mUI/L, fluo=10.73)
- La curva se ajusta bien a los puntos calibradores en todo el rango
- Presenta la curvatura típica de una sigmoide, con crecimiento más pronunciado entre 25-100 mUI/L
- El último punto (F=194 mUI/L, fluo=156.32) marca adecuadamente el límite superior

**Valoración:** ✅ Excelente - Referencia

---

### 2. Linear Piecewise

**Imagen sugerida:** `A_lineal.png`

**Observaciones:**
- Curva formada por segmentos rectos que conectan directamente los calibradores
- Entre A y B: pendiente baja, adecuada para zona de baja concentración
- Entre B y C: pendiente más pronunciada
- Entre C y D: pendiente similar
- Entre D y E: pendiente se estabiliza
- Entre E y F: pendiente disminuye notablemente (señal de saturación)

**Comparación con Semilog:** Visualmente muy similar, ya que los puntos están bien distribuidos. La diferencia principal es que en la zona entre E y F (96-194 mUI/L) la pendiente es ligeramente diferente.

**Valoración:** ✅ Adecuado

---

### 3. Linear Extrapolation

**Imagen sugerida:** `A_lineal_extra.png`

**Observaciones:**
- Prácticamente idéntica a Linear Piecewise en el rango de calibradores
- No se observa extrapolación en esta gráfica porque todas las muestras están dentro del rango
- La línea de extrapolación más allá de F no se visualiza porque el eje X termina en 200

**Valoración:** ✅ Adecuado (similar a Linear Piecewise)

---

### 4. Polynomial Degree 2

**Imagen sugerida:** `A_poli_2.png`

**Observaciones:**
- ❌ **Curva claramente inapropiada**
- La parábola no sigue la forma sigmoidal esperada
- Entre calibradores C (25.20) y D (49.85) la curva pasa **por debajo** de los puntos, subestimando
- Entre D y E (96.15) la curva se eleva bruscamente, sobreestimando
- El comportamiento parabólico no representa adecuadamente la saturación a altas concentraciones

**Problema fundamental:** Un polinomio de grado 2 tiene forma de U invertida o parábola, incapaz de modelar la sigmoide con asíntotas. Esto explica los valores erráticos observados en la tabla de resultados.

**Valoración:** ❌ **No recomendado**

---

### 5. Polynomial Degree 3

**Imagen sugerida:** `A_poli_3.png`

**Observaciones:**
- La curva cúbica sigue mejor los puntos que la cuadrática
- Presenta una ligera **oscilación** entre los calibradores C (25.20) y D (49.85), con la curva pasando por encima de los puntos
- En la zona entre E (96.15) y F (194.00) la curva se aplana adecuadamente, pero con una pequeña inflexión
- El comportamiento en los extremos es mejor que grado 2, pero aún presenta oscilaciones propias de polinomios de alto grado con pocos puntos

**Valoración:** ⚠️ Aceptable con precaución (oscilaciones)

---

### 6. Akima Spline

**Imagen sugerida:** `A_akima.png`

**Observaciones:**
- Curva muy suave que pasa **exactamente** por todos los puntos calibradores
- Excelente comportamiento en la zona entre E y F, sin oscilaciones
- La transición entre segmentos es natural y no introduce artefactos
- En la zona baja (A-B) mantiene la pendiente adecuada

**Ventaja:** Al ser un spline que evita oscilaciones excesivas, es ideal para conjuntos de puntos con distribución irregular.

**Valoración:** ✅ Excelente alternativa

---

### 7. Cubic Spline

**Imagen sugerida:** `A_cubic_spline.png`

**Observaciones:**
- Curva suave que pasa exactamente por todos los puntos calibradores
- Muy similar visualmente a Akima Spline
- Presenta una ligera curvatura más pronunciada entre algunos puntos, pero sin oscilaciones visibles
- Excelente ajuste en toda la curva

**Valoración:** ✅ Excelente

---

### 8. Model 4PL

**Imagen sugerida:** `A_4pl.png`

**Observaciones:**
- Curva sigmoidal perfecta, diseñada específicamente para inmunoensayos
- La curva **no pasa exactamente por todos los puntos**, sino que busca el mejor ajuste global
- Entre C (25.20) y D (49.85) la curva queda ligeramente por debajo de los puntos
- Entre D y E (96.15) la curva se ajusta mejor
- Presenta asíntota superior natural, modelando correctamente la saturación

**Ventaja fundamental:** El modelo 4PL incorpora la forma biológica real de la respuesta, con asíntotas inferior y superior. Esto explica su comportamiento estable en todo el rango.

**Valoración:** ⭐⭐⭐⭐⭐ **Óptimo - Recomendado**

---

### 9. Model 5PL

**Imagen sugerida:** `A_5pl.png`

**Observaciones:**
- Muy similar visualmente a 4PL
- La curva presenta una ligera asimetría adicional permitida por el quinto parámetro
- En esta placa específica, la diferencia con 4PL es mínima
- La curva muestra un ajuste ligeramente mejor en la zona de saturación (E-F)

**Valoración:** ✅ Excelente (similar a 4PL)

---

### 10. Resumen Visual de las Curvas

| Método | Forma de curva | Ajuste a puntos | Oscilaciones | Recomendación |
|--------|----------------|-----------------|--------------|---------------|
| **Semilog Piecewise** | Segmentos rectos en log | Exacto | No | ✅ Referencia |
| **Linear Piecewise** | Segmentos rectos | Exacto | No | ✅ |
| **Linear Extrapolation** | Segmentos rectos | Exacto | No | ✅ |
| **Polynomial Degree 2** | Parábola | Pobre | No | ❌ **No** |
| **Polynomial Degree 3** | Cúbica | Bueno | Leves | ⚠️ Precaución |
| **Akima Spline** | Suave | Exacto | No | ✅ |
| **Cubic Spline** | Suave | Exacto | No | ✅ |
| **Model 4PL** | Sigmoidal | Aproximado | No | ⭐⭐⭐⭐⭐ |
| **Model 5PL** | Sigmoidal asimétrica | Aproximado | No | ✅ |

---

### 11. Conclusión Visual

**Gráficamente, los métodos se agrupan en tres categorías:**

1. **Métodos de interpolación exacta** (Lineal Piecewise, Semilog Piecewise, Akima, Cubic Spline): Pasan por todos los puntos calibradores, ideales cuando se confía en la precisión de cada punto.

2. **Métodos de regresión** (4PL, 5PL): Buscan el mejor ajuste global, más robustos ante variaciones puntuales y con fundamento biológico.

3. **Métodos polinomiales** (Grado 2, Grado 3): Polynomial Degree 2 es claramente inadecuado; Polynomial Degree 3 puede usarse con precaución pero presenta oscilaciones.

**La curva Polynomial Degree 2 es la única que visualmente no se asemeja a una curva de calibración de TSH, confirmando los resultados numéricos que mostraban valores erráticos.**