# Proyecto: Filtro de Kalman para Estimación de Precios Financieros

## Objetivo General
Generar un Jupyter Notebook didáctico (45 minutos) que explique el filtro de Kalman aplicado a la estimación de precios de un activo financiero para estudiantes de finanzas con poco conocimiento de filtros, combinando:
- Explicaciones matemáticas con derivaciones paso a paso
- Gráficos que acompañen cada paso
- Implementación práctica

---

## 1. Generación de Datos Simulados (Microestructura de Mercado)

### Parámetros de simulación específicos:
- **Frecuencia temporal**: Cada minuto
- **Duración**: 300 ticks (5 horas de mercado)
- **Spread bid-ask**: Variable entre 0.05% - 0.5%
- **Volatilidad**: Variable, con apertura de spread durante períodos volátiles

### Componentes a simular para un único activo:
- **Bid y Ask**: Precios de compra y venta con spread dinámico
- **Volumen**: Cantidad disponible en cada lado del libro de órdenes
- **Mid Price**: Precio medio entre bid y ask
- **Trades**: Operaciones ejecutadas con:
  - Precios de ejecución
  - Volúmenes ejecutados (con pesos diferentes para el filtro)

### Dinámicas del mercado:
- Precio subyacente sigue un random walk
- Spread se amplía durante períodos de alta volatilidad
- Trades con mayor volumen tienen mayor impacto en la estimación

---

## 2. Aplicación del Filtro de Kalman

### Modelo de estado:
- **Random Walk**: El precio verdadero sigue un paseo aleatorio
- **Estado**: Precio verdadero del activo (no observable directamente)

### Observaciones del filtro:
1. **Mid Prices**: 
   - Error de estimación = spread actual en ese momento
   - Frecuencia: cada minuto
2. **Trades**:
   - Peso proporcional al volumen de la transacción
   - Mayor volumen = mayor confianza en la observación
   - Error inversamente proporcional al volumen

### Outputs a calcular y mostrar:
- **Estimación de Kalman** del precio verdadero
- **Error (varianza)** de la estimación en cada momento
- **Ganancia de Kalman** para cada observación
- **Confianza relativa** entre mid prices y trades

### Visualizaciones requeridas:
- Trayectoria del mid price vs. precio estimado por Kalman
- Evolución del error del filtro a lo largo del tiempo
- Impacto de trades de diferentes volúmenes en la estimación
- Evolución de la ganancia de Kalman

---

## 3. Explicaciones Matemáticas (Derivaciones Paso a Paso)

### 3.1 ¿Por qué necesitamos filtrar precios?

En mercados financieros, las observaciones de precios están contaminadas por **ruido de microestructura**:

- **Mid prices**: Afectados por spreads bid-ask amplios
- **Trades**: Influenciados por costos de transacción, inventarios de dealers, timing específico
- **Liquidez variable**: Durante períodos volátiles, la información se vuelve menos confiable

El **objetivo** es separar la señal (precio "verdadero") del ruido (fricciones del mercado), lo cual es exactamente lo que hace el filtro de Kalman bajo ciertas condiciones.

### 3.2 Modelo de Estado: Random Walk para el Precio Verdadero

Consideramos que el precio verdadero $p_t$ (no observable directamente) sigue un **paseo aleatorio**:

$$p_{t+1} = p_t + \epsilon_t, \quad \epsilon_t \sim N(0, \sigma_{\epsilon}^2)$$

**Interpretación financiera**:
- **Sin deriva**: El precio no tiene tendencia predecible (eficiencia del mercado)
- **Varianza proporcional al tiempo**: $\text{Var}[p_{t+\Delta t} - p_t] = \sigma_{\epsilon}^2 \Delta t$
- **Martingala**: $E[p_{t+1}|p_t] = p_t$ (el mejor predictor del precio futuro es el precio actual)

**En notación matricial**:
$$\mathbf{x}_{t+1} = \mathbf{F} \mathbf{x}_t + \mathbf{w}_t$$

donde:
- $\mathbf{x}_t = p_t$ (estado unidimensional)
- $\mathbf{F} = 1$ (matriz de transición)
- $\mathbf{w}_t \sim N(0, \mathbf{Q})$ con $\mathbf{Q} = \sigma_{\epsilon}^2$

### 3.3 Modelo de Observación: Mid Prices y Trades

Tenemos **dos tipos de observaciones** del precio verdadero:

#### 3.3.1 Mid Prices
$$z_{mid,t} = p_t + v_{mid,t}, \quad v_{mid,t} \sim N(0, \sigma_{mid,t}^2)$$

donde el **error de observación** depende del spread:
$$\sigma_{mid,t}^2 = \left(\frac{\text{spread}_t}{2}\right)^2$$

**Intuición**: Un spread amplio indica mayor incertidumbre sobre el precio verdadero.

#### 3.3.2 Trades
$$z_{trade,t} = p_t + v_{trade,t}, \quad v_{trade,t} \sim N(0, \sigma_{trade,t}^2)$$

donde el **error depende del volumen** de la transacción:
$$\sigma_{trade,t}^2 = \sigma_p^2 \frac{v_0}{v_t}$$

**Parámetros**:
- $v_t$: Volumen del trade
- $v_0$: Volumen de referencia
- $\sigma_p$: Error base

**Intuición**: Trades grandes ($v_t \gg v_0$) proporcionan más información → menor error de observación.

### 3.4 Algoritmo de Kalman: Derivaciones Paso a Paso

#### Paso 1: Predicción del Estado

**Ecuación**:
$$\hat{p}_{t|t-1} = \hat{p}_{t-1|t-1}$$

**Derivación**: Como $\mathbf{F} = 1$ y $E[\mathbf{w}_t] = 0$:
$$E[p_t | \text{info}_{t-1}] = E[p_{t-1} + \epsilon_{t-1} | \text{info}_{t-1}] = p_{t-1|t-1}$$

#### Paso 2: Predicción de la Varianza

**Ecuación**:
$$P_{t|t-1} = P_{t-1|t-1} + \sigma_{\epsilon}^2$$

**Derivación**: La varianza se propaga según:
$$\text{Var}[p_t | \text{info}_{t-1}] = \text{Var}[p_{t-1} | \text{info}_{t-1}] + \text{Var}[\epsilon_{t-1}]$$

**Interpretación**: La incertidumbre **aumenta** con el tiempo debido al ruido del proceso.

#### Paso 3: Ganancia de Kalman

**Ecuación**:
$$K_t = \frac{P_{t|t-1}}{P_{t|t-1} + \sigma_{obs,t}^2}$$

donde $\sigma_{obs,t}^2$ es el error de la observación actual (mid price o trade).

**Derivación** (minimización del error cuadrático medio):

Queremos minimizar $E[(p_t - \hat{p}_{t|t})^2]$ donde:
$$\hat{p}_{t|t} = \hat{p}_{t|t-1} + K_t(z_t - \hat{p}_{t|t-1})$$

Desarrollando el error cuadrático y tomando la derivada respecto a $K_t$:
$$\frac{\partial}{\partial K_t} E[(p_t - \hat{p}_{t|t})^2] = 0$$

Esto lleva a:
$$K_t = \frac{P_{t|t-1}}{P_{t|t-1} + \sigma_{obs,t}^2}$$

**Interpretación de la Ganancia**:
- Si $\sigma_{obs,t}^2 \ll P_{t|t-1}$ → $K_t \approx 1$ → Confiamos más en la observación
- Si $\sigma_{obs,t}^2 \gg P_{t|t-1}$ → $K_t \approx 0$ → Ignoramos la observación ruidosa

#### Paso 4: Actualización del Estado

**Ecuación**:
$$\hat{p}_{t|t} = \hat{p}_{t|t-1} + K_t(z_t - \hat{p}_{t|t-1})$$

**Derivación**: Combinación óptima de:
- **Predicción**: $\hat{p}_{t|t-1}$ (basada en el modelo)
- **Innovación**: $z_t - \hat{p}_{t|t-1}$ (nueva información)

La ganancia $K_t$ pondera ambas fuentes de información según su **confiabilidad relativa**.

#### Paso 5: Actualización de la Varianza

**Ecuación**:
$$P_{t|t} = (1 - K_t) P_{t|t-1}$$

**Derivación**: La nueva varianza es:
$$P_{t|t} = \text{Var}[p_t - \hat{p}_{t|t}]$$

Sustituyendo la ecuación de actualización y usando propiedades de la varianza:
$$P_{t|t} = (1 - K_t)^2 P_{t|t-1} + K_t^2 \sigma_{obs,t}^2$$

Simplificando con la definición de $K_t$:
$$P_{t|t} = (1 - K_t) P_{t|t-1}$$

**Interpretación**: La varianza **siempre disminuye** tras una observación ($P_{t|t} < P_{t|t-1}$).

### 3.5 Caso Especial: Ponderación por Volumen en Trades

Para trades, el **error de observación variable** afecta directamente la ganancia de Kalman:

$$K_{trade,t} = \frac{P_{t|t-1}}{P_{t|t-1} + \sigma_p^2 \frac{v_0}{v_t}}$$

**Impacto del volumen**:
- **Trade pequeño** ($v_t \ll v_0$): $\sigma_{trade,t}^2$ grande → $K_{trade,t}$ pequeña → Poco impacto
- **Trade grande** ($v_t \gg v_0$): $\sigma_{trade,t}^2$ pequeña → $K_{trade,t}$ grande → Gran impacto

**Ejemplo numérico**:
Si $P_{t|t-1} = 0.1$, $\sigma_p^2 = 1$, $v_0 = 1000$:
- Trade de 100 acciones: $K_t = 0.1/(0.1 + 10) = 0.01$ (casi se ignora)
- Trade de 10,000 acciones: $K_t = 0.1/(0.1 + 0.1) = 0.5$ (impacto significativo)

---

## 4. Estructura del Notebook (45 minutos)

### Secciones con tiempos estimados:
1. **Introducción** (5 min): Problema de estimación de precios en microestructura con ruido
2. **Simulación de datos** (10 min): Generación y visualización de datos de mercado con spread variable
3. **Teoría matemática** (15 min): Derivaciones paso a paso del filtro de Kalman para random walk
4. **Implementación** (10 min): Aplicación del filtro con ponderación por volumen
5. **Resultados y análisis** (5 min): Visualización y conclusiones

### Enfoque pedagógico:
- **Para estudiantes de finanzas** sin background en filtros
- **Derivaciones matemáticas completas** pero explicadas intuitivamente
- **Conexión constante** entre teoría y aplicación financiera
- **Ejemplos numéricos** en cada paso matemático
- **Progresión lógica**: Del problema financiero a la solución matemática

### Flujo narrativo:
1. **Motivación financiera**: ¿Por qué los precios observados son ruidosos?
2. **Modelado matemático**: Cómo traducir el problema a ecuaciones
3. **Algoritmo de Kalman**: Derivaciones paso a paso con interpretación financiera
4. **Implementación**: Código Python que materializa la teoría
5. **Validación**: Gráficos que muestran la efectividad del filtro

---

## 5. Requisitos Técnicos

### Librerías de Python:
- `numpy`: Cálculos numéricos y álgebra lineal
- `pandas`: Manipulación de datos de mercado
- `plotly`: Visualizaciones interactivas de series temporales

### Implementación específica:
- **Simulación realista** de microestructura con spread variable
- **Filtro de Kalman adaptativo** con errores dependientes del volumen
- **Visualizaciones dinámicas** que muestren la evolución temporal
- **Código modular** para facilitar el entendimiento paso a paso

---

## 6. Aspectos Específicos de Implementación

### Generación de datos:
- Precio subyacente: Random walk con volatilidad variable
- Spread dinámico: 0.05% - 0.5% correlacionado con volatilidad
- Trades: Frecuencia y volumen realistas
- 300 observaciones (5 horas de mercado)

### Filtro de Kalman personalizado:
- **Modelo de estado**: Random walk simple ($p_{t+1} = p_t + \epsilon_t$)
- **Observaciones duales**: Mid prices (error = spread/2) y trades (error ∝ 1/volumen)
- **Lógica de prioridad**: Si hay trade, usar trade; si no, usar mid price
- **Ponderación adaptativa**: Trades grandes tienen mayor impacto en la estimación
- **Ganancia variable**: Kalman gain se adapta automáticamente al tipo y calidad de observación

### Métricas de evaluación:
- **Error cuadrático medio**: Comparación entre precio estimado y "verdadero"
- **Evolución de la incertidumbre**: Cómo disminuye $P_{t|t}$ con cada observación
- **Análisis de la ganancia**: $K_t$ como indicador de confianza en observaciones
- **Comparación con benchmarks**: Filtro vs. media móvil simple
- **Impacto del volumen**: Correlación entre tamaño de trade y actualización del filtro

### Conexión teoría-práctica:
- **Cada ecuación** se implementa directamente en código Python
- **Visualizaciones** muestran el comportamiento matemático predicho
- **Parámetros realistas** basados en microestructura de mercados reales
- **Interpretación financiera** de cada componente del algoritmo

---

## Notas Adicionales
- **Enfoque didáctico** con progresión lógica desde conceptos básicos
- **Balance entre rigor matemático** y comprensibilidad para finanzas
- **Aplicación práctica** con datos realistas de microestructura
- **Tiempo total**: 45 minutos de lectura y ejecución