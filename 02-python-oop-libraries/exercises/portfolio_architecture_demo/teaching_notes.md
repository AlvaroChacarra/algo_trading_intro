# Guion pedagogico - Portfolio Architecture Demo

Este mini repo esta pensado para ensenar una idea clave de OOP:

**No todo problema vive en `main`. Cada clase tiene una frontera, una responsabilidad y un lugar natural donde depurar.**

## Que ensena este ejercicio

- modularidad: separar el sistema en piezas pequenas
- encapsulacion: cada clase protege su propia logica
- ownership: cada error tiene un hogar mas probable
- DRY: no repetir validaciones o calculos en varios sitios
- lectura arquitectonica: entender un sistema sin meter todo en un archivo

## Mapa de clases

### `AssetUniverse`

Responsabilidad:

- definir que activos existen
- agruparlos por categoria

No debe:

- preguntar al usuario
- descargar datos
- calcular pesos

### `UnderlyingSelector`

Responsabilidad:

- mostrar el universo disponible
- recoger o simular la seleccion
- validar tickers, duplicados y tamano de la cesta

No debe:

- conocer la logica del modelo
- decidir pesos

### `YahooFinanceDataProvider`

Responsabilidad:

- devolver un snapshot de mercado por ticker
- simular una capa de datos tipo Yahoo Finance
- lanzar errores claros si falta un dato

No debe:

- validar la seleccion del usuario
- calcular la cartera final

### `PortfolioOptimizerModel`

Responsabilidad:

- transformar datos en pesos
- aplicar la regla `score = expected_return / volatility`
- normalizar pesos para que sumen 1

No debe:

- preguntar nada al usuario
- saber de que fuente vienen los datos

### `PortfolioOptimizerApp`

Responsabilidad:

- orquestar el flujo completo
- capturar errores y explicarlos
- presentar el resultado

No debe:

- esconder toda la logica de negocio
- duplicar validaciones del selector
- recalcular dentro del app lo que ya hace el modelo

## Flujo de ejecucion

1. `run_demo.py` crea la app y selecciona un escenario.
2. La app prepara una seleccion preset o interactiva.
3. `UnderlyingSelector` valida la seleccion.
4. `YahooFinanceDataProvider` devuelve metricas por ticker.
5. `PortfolioOptimizerModel` convierte esas metricas en pesos.
6. La app imprime resultado o explica donde buscar el error.

## Preguntas de debugging por ownership

### Si falla la extraccion del dato, irias a la clase del modelo?

No. Primero miraria `data_provider.py`, porque esa clase es la que posee la responsabilidad de traer y validar el snapshot de mercado.

### Donde buscarias primero y por que?

Primero en `data_provider.py`, porque si el dato no llega o llega mal, el modelo todavia no ha empezado su trabajo real.

### Si el usuario mete un ticker que no existe, que clase deberia detectarlo?

`UnderlyingSelector`, porque esa clase es la frontera entre input humano y sistema interno.

### Si los pesos no suman 1, donde esta el problema mas probable?

Primero en `model.py`, porque la normalizacion de pesos pertenece al modelo.

### Si el menu de activos esta mal, mirarias el selector o el universo?

Primero `universe.py`, porque el universo define que activos existen y como se agrupan.

## Como usarlo en clase

### Escenario 1: `happy`

Objetivo:

- mostrar el flujo normal
- ver la separacion limpia entre modulos

Que decir:

- "El selector valida."
- "El proveedor trae datos."
- "El modelo calcula."
- "La app conecta."

### Escenario 2: `data_fail`

Objetivo:

- ensenar debugging por ownership

Que decir:

- "El fallo no esta en el modelo."
- "Todavia no tiene sentido mirar pesos si el snapshot ya falla."

### Escenario 3: `bad_selection`

Objetivo:

- mostrar que los errores deben pararse pronto

Que decir:

- "No llames al proveedor si la entrada ya es invalida."
- "Validar pronto simplifica el resto del sistema."

### Escenario 4: `model_fail`

Objetivo:

- mostrar un error que si pertenece al modelo

Que decir:

- "Aqui si tiene sentido mirar `model.py`."
- "El sistema de datos ha entregado algo, pero el modelo no puede construir pesos utiles."

## Extensiones sugeridas

- anadir un `RiskReport` como modulo nuevo
- sustituir el proveedor mock por uno real con la misma interfaz
- dejar que el usuario seleccione un perfil conservador o agresivo
- exportar los resultados a CSV
- meter una clase `PortfolioReportFormatter` para separar aun mas la salida

## Mensaje final para el alumno

Cuando el codigo crece, la pregunta importante deja de ser "funciona o no funciona" y pasa a ser:

**"Que pieza es responsable de esto?"**
