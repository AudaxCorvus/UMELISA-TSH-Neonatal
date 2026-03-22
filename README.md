# UMELISA TSH Neonatal - Sistema de Análisis de Curvas de Calibración

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Scipy](https://img.shields.io/badge/scipy-1.7%2B-orange.svg)](https://scipy.org)

Sistema de escritorio para el procesamiento y análisis de curvas de calibración en ensayos UMELISA TSH Neonatal para el pesquisaje de Hipotiroidismo Congénito. Implementa nueve métodos de interpolación/regresión para evaluar precisión, estabilidad y coherencia diagnóstica.

## 📋 Tabla de Contenidos
- [Descripción General](#descripción-general)
- [Características](#características)
- [Métodos Implementados](#métodos-implementados)
- [Requisitos del Sistema](#requisitos-del-sistema)
- [Instalación](#instalación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Guía de Uso](#guía-de-uso)
- [Formato de Archivos](#formato-de-archivos)
- [Procesamiento de Datos](#procesamiento-de-datos)
- [Configuración de Parámetros](#configuración-de-parámetros)
- [Exportación de Resultados](#exportación-de-resultados)
- [Validación de Calidad](#validación-de-calidad)
- [Solución de Problemas](#solución-de-problemas)
- [Referencias Técnicas](#referencias-técnicas)
- [Contribución](#contribución)
- [Licencia](#licencia)

## 🎯 Descripción General

UMELISA TSH Neonatal es una aplicación desarrollada para laboratorios que utilizan el sistema UMELISA para la detección de Hipotiroidismo Congénito en recién nacidos. Tradicionalmente, el lector SUMA utiliza interpolación lineal en escala semilogarítmica para convertir fluorescencia en concentración de TSH. Este software amplía las capacidades del sistema implementando múltiples métodos de interpolación/regresión, permitiendo evaluar cuál ofrece el mejor desempeño en términos de precisión, estabilidad y coherencia diagnóstica.

### Flujo de Trabajo
1. Carga del archivo `.flu` con valores de fluorescencia (96 pozos)
2. Extracción automática de calibradores (A-F) y control
3. Validación de la curva de calibración (monotonía creciente)
4. Validación del control según límites configurables
5. Selección del método de interpolación/regresión
6. Cálculo de concentraciones para todas las muestras
7. Interpretación según punto de corte
8. Visualización de resultados (placa, tabla, curva)
9. Exportación de datos en múltiples formatos

## ✨ Características

| Característica | Descripción |
|----------------|-------------|
| **9 Métodos de Calibración** | Lineal punto a punto, semilog piecewise, polinomios grado 2 y 3, splines cúbicos y Akima, modelos 4PL y 5PL |
| **Validación Automática** | Verifica monotonía de la curva y rangos de control |
| **Punto de Corte Configurable** | Valor por defecto 30.0 mUI/L, totalmente ajustable |
| **Límites de Control Personalizables** | Permite establecer rangos de aceptación para el suero control |
| **Concentraciones de Calibradores Editables** | Modificar valores de calibradores A-F según lote de reactivos |
| **Visualización Interactiva** | Placa coloreada, tabla de resultados, curva de calibración con todos los métodos |
| **Múltiples Formatos de Exportación** | CSV, HTML, PNG para resultados, placa y curva |
| **Interfaz Intuitiva** | Barra de herramientas con selector de métodos y opciones de exportación |
| **Procesamiento en Tiempo Real** | Recalculo inmediato al cambiar método o parámetros |

## 🔬 Métodos Implementados

| Método | ID | Descripción | Aplicación |
|--------|-----|-------------|------------|
| **Lineal punto a punto** | `linear_piecewise` | Interpolación lineal entre calibradores consecutivos | Referencia básica |
| **Semilog piecewise** | `semilog_piecewise` | Entre A-B lineal-lineal, resto interpolación lineal en log(concentración) | **Método tradicional SUMA** |
| **Lineal con extrapolación** | `linear_extrapolation` | Lineal con extrapolación más allá del último calibrador | Muestras con alta fluorescencia |
| **Polinomio grado 2** | `polynomial_degree2` | Polinomio de segundo grado (parabólico) | Ajuste simple |
| **Polinomio grado 3** | `polynomial_degree3` | Polinomio de tercer grado (cúbico) | Mayor flexibilidad |
| **Spline cúbico** | `cubic_spline` | Spline cúbico con extrapolación | Curva suave que pasa por todos los puntos |
| **Akima spline** | `akima_spline` | Spline de Akima | Menos oscilaciones que spline cúbico |
| **Modelo 4PL** | `model_4pl` | Modelo logístico de 4 parámetros | Fundamento biológico, comportamiento suave |
| **Modelo 5PL** | `model_5pl` | Modelo logístico de 5 parámetros | Asimetría adicional en la curva |

### Fórmulas de los Modelos Logísticos

**Modelo 4PL:**
```
y = D + (A - D) / (1 + (C / x)^B)
```
- **A**: Asíntota superior (fluorescencia máxima)
- **B**: Pendiente (coeficiente de Hill)
- **C**: Punto de inflexión (EC50, concentración media efectiva)
- **D**: Asíntota inferior (fluorescencia mínima)

**Modelo 5PL:**
```
y = D + (A - D) / (1 + (C / x)^B)^F
```
- **A, B, C, D**: Mismos parámetros que 4PL
- **F**: Factor de asimetría (permite curvas no simétricas)

### Algoritmos de Interpolación

#### Semilog Piecewise (Método Tradicional)
```
Zona A-B: Interpolación lineal-lineal
    conc = conc_A + (fluor - fluor_A) * (conc_B - conc_A) / (fluor_B - fluor_A)

Zona B-F: Interpolación lineal en espacio log(conc)
    log_conc = log_conc_i + (fluor - fluor_i) * (log_conc_{i+1} - log_conc_i) / (fluor_{i+1} - fluor_i)
    conc = 10^log_conc

Extrapolación superior: Lineal en log(conc) extendido
```

#### Splines
- **Cúbico**: Función interpolante de tercer grado con continuidad hasta segunda derivada
- **Akima**: Spline local que evita oscilaciones excesivas

## 💻 Requisitos del Sistema

### Software
- **Python**: 3.8 o superior
- **Sistema operativo**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 11+

### Dependencias
```txt
numpy >= 1.21.0          # Operaciones numéricas y arrays
scipy >= 1.7.0           # Splines, curve_fit y optimización
matplotlib >= 3.5.0      # Visualización de curvas
pandas >= 1.3.0          # Exportación de datos a CSV/HTML
tkinter                  # Interfaz gráfica (incluido con Python)
```

### Hardware Recomendado
| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| Procesador | 2 cores @ 1.5 GHz | 4 cores @ 2.0 GHz |
| RAM | 2 GB | 4 GB |
| Almacenamiento | 100 MB | 500 MB |
| Resolución | 1024x768 | 1920x1080 |

## 📦 Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/umelisa-tsh-neonatal.git
cd umelisa-tsh-neonatal
```

### 2. Crear Entorno Virtual (Recomendado)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install --upgrade pip
pip install numpy scipy matplotlib pandas
```

### 4. Verificar Instalación
```bash
python -c "import numpy, scipy, matplotlib, pandas; print('✅ Todas las dependencias instaladas correctamente')"
```

### 5. Generar archivo requirements.txt (opcional)
```bash
python requeriments.py
```

### 6. Ejecutar la Aplicación
```bash
python main.py
```

Para Windows también puedes usar el script:
```cmd
run.bat
```

## 📁 Estructura del Proyecto

```
umelisa-tsh-neonatal/
│
├── main.py                      # Aplicación principal (GUI)
├── requeriments.py              # Utilidad para generar requirements.txt
├── run.bat                      # Script de inicio para Windows
│
├── models/                      # Capa de datos
│   ├── __init__.py
│   ├── plate_model.py          # Modelo de placa (96 pozos)
│   └── assay_model.py          # Modelo de ensayo (9 métodos, validaciones)
│
├── controllers/                 # Capa de lógica de negocio
│   ├── __init__.py
│   └── assay_controller.py     # Controlador de ensayos (carga, cálculo, interpretación)
│
└── views/                       # Capa de presentación
    ├── __init__.py
    ├── assay_view.py           # Vista principal (placa, resultados, curva, exportaciones)
    └── config_view.py          # Ventana de configuración (parámetros del ensayo)
```

## 🖥️ Guía de Uso

### Menú Archivo
| Opción | Atajo | Descripción |
|--------|-------|-------------|
| Abrir placa | `Ctrl+O` | Carga archivo `.flu` con valores de fluorescencia |
| Salir | `Ctrl+Q` | Cierra la aplicación |

### Menú Configuración
| Opción | Descripción |
|--------|-------------|
| Editar parámetros | Configura punto de corte, límites de control y concentraciones de calibradores |

### Barra de Herramientas
| Botón/Control | Descripción |
|---------------|-------------|
| **Ver Placa** | Muestra los 96 pozos con códigos de colores según resultado |
| **Ver Resultados** | Tabla con fluor1, fluor2, media, concentración e interpretación |
| **Ver Curva** | Gráfico de la curva de calibración con el método seleccionado |
| **Método (Combo)** | Selector desplegable con los 9 métodos disponibles |
| **Exportar** | Menú desplegable con opciones de exportación (CSV, PNG, HTML) |

### Códigos de Color en la Placa

| Color | Código HEX | Significado |
|-------|------------|-------------|
| 🔵 Azul claro | `#ADD8E6` | Elevado (concentración ≥ cutoff) |
| 🟡 Amarillo | `#FFFF00` | Repetir (inconsistencia en duplicados) |
| ⚪ Gris | `#C0C0C0` | > Último punto (sobrepasa calibrador F) |
| ⚪ Blanco | `#FFFFFF` | Negativo (concentración < cutoff) |
| 🟡 Amarillo claro | `#FEFEC1` | Calibradores A, B |
| 🔵 Azul | `#84E0F9` | Calibradores C, D |
| 🟤 Marrón | `#997070` | Calibradores E, F |
| 🟢 Verde | `#90EE90` | Control |
| 🌸 Rosa | `#FFB6C1` | Calibrador E (A2) |
| 🟣 Ciruela | `#DDA0DD` | Calibrador F (B2) |
| 🔵 Azul cielo | `#87CEEB` | Control (E2, F2) |

### Códigos de Color en la Tabla de Resultados

| Color | Significado |
|-------|-------------|
| 🔵 Azul claro | Elevado |
| 🟡 Amarillo | Repetir |
| ⚪ Gris | > Último punto |
| ⚪ Blanco | Negativo |

## 📄 Formato de Archivos

### Archivo `.flu` (Fluorescencia)
El archivo debe contener 96 valores numéricos, uno por línea, ordenados por **columna primero** (columna 1, luego columna 2, etc.):

```
# Columna 1 (pozos A1, B1, C1, ..., H1)
120.45
118.32
85.67
82.34
45.12
43.89
22.34
21.56

# Columna 2 (pozos A2, B2, ..., H2)
115.23
112.87
...
```

**Posiciones estándar de la placa (96 pozos):**

| Posición | Contenido | Descripción |
|----------|-----------|-------------|
| A1, B1 | Calibrador A | 0.520 mUI/L |
| C1, D1 | Calibrador B | 10.750 mUI/L |
| E1, F1 | Calibrador C | 25.200 mUI/L |
| G1, H1 | Calibrador D | 49.850 mUI/L |
| A2, B2 | Calibrador E | 96.150 mUI/L |
| C2, D2 | Calibrador F | 194.000 mUI/L |
| E2, F2 | Control | Suero control |
| G2 - H12 | Muestras | Duplicados consecutivos |

**Características soportadas:**
- Separador decimal: punto (.) o coma (,)
- Comentarios: líneas que comienzan con `#` se ignoran
- Líneas vacías: se omiten automáticamente
- Valores no numéricos: se reemplazan con 0.0
- Archivos con menos de 96 valores: se completan con 0.0
- Archivos con más de 96 valores: se truncan

### Ejemplo de Archivo Válido
```
120.45
118.32
85.67
82.34
45.12
43.89
22.34
21.56
115.23
112.87
# ... continuar hasta 96 valores
```

## 🔬 Procesamiento de Datos

### Calibradores y Control

| Calibrador | Concentración (mUI/L) | Log10(Conc) | Posiciones |
|------------|----------------------|-------------|------------|
| A | 0.520 | -0.284 | A1, B1 |
| B | 10.750 | 1.031 | C1, D1 |
| C | 25.200 | 1.401 | E1, F1 |
| D | 49.850 | 1.698 | G1, H1 |
| E | 96.150 | 1.983 | A2, B2 |
| F | 194.000 | 2.288 | C2, D2 |
| Control | - | - | E2, F2 |

### Cálculos Internos

| Variable | Fórmula | Descripción |
|----------|---------|-------------|
| **Fluor medio calibrador** | (well1 + well2) / 2 | Promedio de duplicados |
| **Fluor medio control** | (well1 + well2) / 2 | Promedio del suero control |
| **Curva de calibración** | Conc = f(Fluor) | Según método seleccionado |
| **Concentración muestra** | f(mean_fluor) | Aplicación de la función |

### Validaciones

#### 1. Validación de Curva de Calibración
- **Condición**: Fluor(A) < Fluor(B) < Fluor(C) < Fluor(D) < Fluor(E) < Fluor(F)
- **Si falla**: `"CURVA DE CALIBRACIÓN RECHAZADA, REPITA EL ENSAYO"`
- **Consecuencia**: No se calculan concentraciones

#### 2. Validación de Control
- **Condición**: media_control ∈ [control_lower, control_upper]
- **Si falla**: `"SUERO CONTROL FUERA DE RANGO. SUGERIMOS REPETIR EL ENSAYO"`
- **Nota**: Si ambos límites son 0, la validación se desactiva

### Interpretación de Muestras

| Condición | Resultado | Concentración |
|-----------|-----------|---------------|
| mean_fluor > fluor(F) | "> Ult. Punto" | None (no calculable) |
| concentración < cutoff | "" (Negativo) | Valor calculado |
| concentración ≥ cutoff | "Elevado" | Valor calculado |
| Error en cálculo | "ERROR" | None |

## ⚙️ Configuración de Parámetros

La ventana de configuración (`ConfigView`) permite editar todos los parámetros del ensayo:

### Punto de Corte
| Parámetro | Valor por defecto | Descripción |
|-----------|------------------|-------------|
| Valor (mUI/L) | 30.0 | Umbral para clasificar como Elevado |

### Límites del Control
| Parámetro | Valor por defecto | Descripción |
|-----------|------------------|-------------|
| Límite inferior | 20.0 | Valor mínimo aceptable para el control |
| Límite superior | 30.0 | Valor máximo aceptable para el control |
| Nota | 0 = sin validación | Desactiva la validación si ambos son 0 |

### Concentraciones de Calibradores
| Calibrador | Valor por defecto (mUI/L) | Rango típico |
|------------|--------------------------|--------------|
| A | 0.520 | 0.4 - 0.7 |
| B | 10.750 | 9.0 - 12.5 |
| C | 25.200 | 22.0 - 28.0 |
| D | 49.850 | 45.0 - 55.0 |
| E | 96.150 | 90.0 - 105.0 |
| F | 194.000 | 180.0 - 210.0 |

## 📊 Exportación de Resultados

| Formato | Contenido | Archivo por defecto | Uso |
|---------|-----------|---------------------|-----|
| **CSV (Placa)** | Matriz 8x12 con valores de fluorescencia | `placa_YYYYMMDD_HHMMSS.csv` | Análisis externo, hojas de cálculo |
| **CSV (Resultados)** | Tabla con N°, fluor1, fluor2, media, concentración, resultado | `resultados_YYYYMMDD_HHMMSS.csv` | Procesamiento posterior, estadísticas |
| **CSV (Curva)** | Puntos de calibración (concentración, fluorescencia) | `curva_YYYYMMDD_HHMMSS.csv` | Verificación de calibración |
| **PNG** | Imagen de la curva de calibración (DPI 150) | `curva_YYYYMMDD_HHMMSS.png` | Reportes, presentaciones |
| **HTML** | Tabla de resultados con formato y colores | `resultados_YYYYMMDD_HHMMSS.html` | Documentación, archivo independiente |

### Estructura del CSV de Resultados
```csv
N.,Código,Fluor1,Fluor2,Media,mUVL (mUI/L),Resultado
1,,120.45,118.32,119.38,2.34,
2,,85.67,82.34,84.01,15.67,
3,,45.12,43.89,44.51,45.23,Elevado
4,,22.34,21.56,21.95,78.90,Elevado
```

### Estructura del HTML Exportado
- Incluye estilos CSS embebidos
- Tablas con código de colores
- Fecha y hora de exportación
- Método utilizado
- Estado de validaciones

## ✅ Validación de Calidad

### Criterios de Aceptación del Ensayo

| Criterio | Condición | Acción |
|----------|-----------|--------|
| Curva monótona | Fluor(A) < Fluor(B) < ... < Fluor(F) | Permite cálculo |
| Curva no monótona | Cualquier calibrador fuera de orden | Rechaza ensayo, no calcula |
| Control en rango | media_control ∈ [lower, upper] | Resultados válidos |
| Control fuera de rango | media_control ∉ [lower, upper] | Advertencia, resultados como referencia |

### Recomendaciones

1. **Antes de procesar**: Verificar que todos los calibradores tengan valores positivos y crecientes
2. **Selección de método**: Para compatibilidad retrospectiva usar `semilog_piecewise`
3. **Alta precisión**: Usar `model_4pl` o `cubic_spline`
4. **Muestras fuera de rango**: Considerar dilución si aparecen como "> Ult. Punto"

## 🔧 Solución de Problemas

### Error: "No module named 'tkinter'"
**Solución:** Instalar tkinter según sistema operativo:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (con Homebrew)
brew install python-tk
```

### Error: "CURVA DE CALIBRACIÓN RECHAZADA"
**Causa:** Los valores de fluorescencia de los calibradores no son estrictamente crecientes.
**Solución:**
1. Verificar que A < B < C < D < E < F en términos de fluorescencia
2. Revisar si hay errores de lectura en el equipo SUMA
3. Verificar la calidad de los reactivos calibradores

### Error: "SUERO CONTROL FUERA DE RANGO"
**Causa:** La media del control (E2, F2) está fuera de los límites configurados.
**Solución:**
1. Verificar límites en Configuración (menú Configuración → Editar parámetros)
2. Si los límites son correctos, repetir el ensayo con nuevo control
3. Temporalmente se pueden desactivar límites (poner ambos en 0)

### Error: Valores de concentración negativos
**Causa:** Fluorescencia por debajo del calibrador A.
**Solución:** Se asignan automáticamente a 0.0 mUI/L (no afecta interpretación)

### Error: Muestras marcadas como "> Ult. Punto"
**Causa:** Fluorescencia superior al calibrador F (194 mUI/L).
**Solución:** Diluir la muestra y repetir el ensayo

### Error: "ValueError: La placa está vacía"
**Causa:** El archivo .flu no contiene datos o todos los valores son 0.
**Solución:** Verificar que el archivo tenga al menos 96 líneas con valores numéricos

### La curva no se muestra correctamente
**Verificar:**
1. Que todos los calibradores tengan valores positivos
2. Que la curva sea monótona creciente
3. Probar con otro método de interpolación
4. Verificar consola por errores de ajuste en 4PL/5PL

### El ajuste 4PL/5PL falla
**Causa:** Datos no sigmoidales o valores extremos.
**Solución:** Usar otros métodos como `cubic_spline` o `semilog_piecewise`

## 📚 Referencias Técnicas

1. **UMELISA TSH Neonatal**: Procedimiento operativo estándar, Centro de Inmunoensayo, La Habana, Cuba.

2. **Modelo 4PL/5PL**: 
   - Findlay, J. W., & Dillard, R. F. (2007). Appropriate calibration curve fitting in ligand binding assays. *The AAPS Journal*, 9(2), E260-E267.
   - DeLean, A., Munson, P. J., & Rodbard, D. (1978). Simultaneous analysis of families of sigmoidal curves. *American Journal of Physiology*, 235(2), E97-E102.

3. **Splines en Curvas de Calibración**:
   - Akima, H. (1970). A new method of interpolation and smooth curve fitting based on local procedures. *Journal of the ACM*, 17(4), 589-602.

4. **Validación de Ensayos**:
   - Clinical and Laboratory Standards Institute (CLSI). Evaluation of the Linearity of Quantitative Measurement Procedures. EP06-A.

5. **Hipotiroidismo Congénito**:
   - American Academy of Pediatrics. (2006). Newborn screening for congenital hypothyroidism. *Pediatrics*, 117(6), 2290-2303.

## 🤝 Contribución

### Reportar Issues
1. Verificar si el issue ya existe en GitHub Issues
2. Incluir mensaje de error completo
3. Adjuntar archivo `.flu` de ejemplo si es posible
4. Indicar método utilizado y configuración
5. Describir pasos para reproducir el error

### Pull Requests
1. Fork el repositorio
2. Crear rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abrir Pull Request describiendo los cambios

### Estilo de Código
- Seguir PEP 8
- Documentar funciones con docstrings
- Incluir type hints
- Mantener nombres en español para variables de negocio

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.
