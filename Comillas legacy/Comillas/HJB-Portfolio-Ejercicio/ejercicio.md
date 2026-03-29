# Ejemplo 7.6 – Selección Óptima de Portafolio (Modelo tipo Merton)

## 1. Planteamiento del problema
**Activos:**
- Bono sin riesgo: $db = r b\,dt$.
- Acción riesgosa: $dS = R S\,dt + \sigma S\,dW$.

**Riqueza bajo controles (fracción en la acción y consumo):**
$$
 dX_t = \big[(1-\alpha_1)X_t r + \alpha_1 X_t R - \alpha_2\big] dt + \alpha_1 X_t \sigma\, dW_t.
$$
Donde:
- $\alpha_1(t)$: fracción de la riqueza invertida en la acción (resto en bono).
- $\alpha_2(t)$: tasa de consumo (flujo en unidades monetarias por unidad de tiempo).

**Función objetivo (solo utilidad de consumo intertemporal, sin utilidad terminal):**
$$
\max_{\{\alpha_1,\alpha_2\}} \; \mathbb{E}\Bigg[ \int_t^T e^{-\rho s} F(\alpha_2(s))\,ds \Bigg], \qquad F(c)=c^{\gamma}, \; 0<\gamma<1.
$$
La aversión relativa al riesgo (CRRA) es $1-\gamma$.

**Supuestos clave:**
- No hay utilidad de herencia: $u(x,T)=0$.
- No se permite apalancamiento/venta corta implícitamente (puede suceder $\alpha_1^*>1$).
- Consumo no negativo: $\alpha_2(t)\ge 0$.
- Parámetros constantes.

---

## 2. Ecuación HJB
La función de valor $u(x,t)$ satisface:
$$
 u_t + \max_{\alpha_1,\alpha_2} \Big\{\tfrac12 (\alpha_1 x \sigma)^2 u_{xx} + \big[(1-\alpha_1) x r + \alpha_1 x R - \alpha_2\big] u_x + e^{-\rho t} \alpha_2^{\gamma} \Big\} = 0,
$$
con condición terminal $u(x,T)=0$.

---

## 3. Controles óptimos
Buscamos una solución homogénea del tipo:
$$
 u(x,t) = g(t) x^{\gamma}.
$$
Derivadas:
$u_x = g(t) \gamma x^{\gamma-1}$, $u_{xx} = g(t) \gamma(\gamma-1) x^{\gamma-2}$.

Sustituyendo en la HJB y maximizando término a término:

### Inversión óptima (constante en el tiempo)
$$
 \alpha_1^* = \frac{R-r}{\sigma^2 (1-\gamma)}.
$$

### Consumo óptimo (proporcional a la riqueza)
$$
 \alpha_2^*(x,t) = \Big[e^{\rho t} g(t)\Big]^{\tfrac{1}{\gamma-1}} x.
$$
La propensión al consumo es $\alpha_2^*/X_t = k(t)$ con $k(t) = [e^{\rho t} g(t)]^{1/(\gamma-1)}$.

---

## 4. Dinámica de $g(t)$
El remplazo anterior produce la ODE (después de maximizar):
$$
 g'(t) + \nu \gamma g(t) + (1-\gamma) g(t) \big[e^{\rho t} g(t)\big]^{\tfrac{1}{\gamma-1}} = 0,
$$
con
$$
 \nu = \frac{(R-r)^2}{2\sigma^2 (1-\gamma)} + r.
$$

### Solución cerrada
Bajo la condición $\rho - \nu\gamma > 0$ (que garantiza finitud de la utilidad):
$$
 g(t) = e^{-\rho t} \left[ \frac{1-\gamma}{\rho - \nu \gamma} \Big(1 - e^{-(\rho - \nu \gamma)(T-t)}\Big) \right]^{1-\gamma}.
$$

De aquí se obtiene directamente $k(t)$ y por tanto el consumo óptimo.

---

## 5. Parámetros de ejemplo y cálculos
Valores base:

| Parámetro | Valor | Interpretación |
|-----------|-------|----------------|
| $r$ | 2% | Tasa libre de riesgo |
| $R$ | 6% | Rendimiento esperado de la acción |
| $\sigma$ | 0.2 | Volatilidad de la acción |
| $\gamma$ | 0.5 | Elasticidad utilidad (RRA = 0.5) |
| $\rho$ | 3% | Tasa de impaciencia |
| $T$ | 30 | Horizonte (años) |

Resultados:

- Fracción óptima en acciones:
  $$\alpha_1^* \approx 2.0 \quad (200\% \text{ de la riqueza } \Rightarrow \text{apalancamiento}).$$

- Propensión inicial al consumo (aprox.):
  $$\frac{\alpha_2^*}{X} \approx 0.125 \quad (12.5\% \text{ de la riqueza por año}).$$

---

## 6. Interpretación económica
- **Cartera:** $\alpha_1^*$ es constante; depende solo del exceso de retorno $(R-r)$, del riesgo $\sigma^2$ y de la aversión $1-\gamma$. No depende de $t$ ni de la riqueza: propiedad de homogeneidad CRRA.
- **Consumo:** proporcional a $X_t$; se ajusta automáticamente a subidas o bajadas de la riqueza. La tasa $k(t)$ varía con el tiempo vía $g(t)$ y converge al consumir más rápido conforme se acerca $T$ (si $\rho - \nu\gamma>0$).
- **Separación:** La decisión de cartera (riesgo) se separa de la de consumo (ahorro vs disfrute), característica del modelo de Merton.
- **Benchmark:** Proporciona una referencia teórica para comparar estrategias reales (fondos de pensiones, planes de retiro, reglas de retiro proporcional, etc.).
- **Apalancamiento:** Si $\alpha_1^*>1$ el modelo sugiere endeudarse para aumentar exposición a la acción; en la práctica hay límites regulatorios, márgenes y costos de financiamiento.

---

## 7. Condiciones y extensiones
- Condición de finitud típica: $\rho > \gamma \nu$.
- Si se añadiera utilidad terminal $B X_T^{\gamma}$ cambiaría la condición de frontera y la forma de $g(t)$.
- Con restricción $\alpha_1 \le 1$ el control de inversión dejaría de ser constante en general (aparece canto en la frontera).

---

## 8. Resumen
El problema produce reglas simples:
1. Asignación a la acción: $\alpha_1^* = (R-r)/[\sigma^2 (1-\gamma)]$.
2. Consumo proporcional: $c_t = k(t) X_t$ con $k(t)$ derivado de $g(t)$.
3. La estructura CRRA induce homogeneidad: duplicar la riqueza duplica el consumo óptimo y multiplica el valor por $2^{\gamma}$.

Estas propiedades facilitan calibración y comparación de políticas financieras en entornos de gestión patrimonial.
