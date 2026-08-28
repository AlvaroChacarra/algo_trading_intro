# Auditoría del recorrido del alumno — L1 → L15

> Artefacto generado por `framework/_build/pedagogy_reports.py` a partir del contrato ejecutable. No editar a mano.

## Resultado de continuidad

- Dependencias sin introducción previa: **0**.
- Dependencias obligatorias cuyo único origen es OPTIONAL: **0**.
- Lessons educativas con rutas explícitas: **14/14**.
- L15 conserva una experiencia lineal de assessment y no se fuerza al renderer de escenas.

La entrada de cada lesson se calcula solo con introducciones LIVE + REQUIRED anteriores. Los nombres entre `backticks` son identificadores estables del contrato.

## L01 — Python I — Dato, cálculo y decisión

- **Entrada — qué sabe:** Inicio del recorrido; no presupone conocimiento del curso.
- **Recuperación:** No requiere un recall distante; la continuidad es inmediata o la lesson inicia el curso.
- **Introduce:** LIVE: `python.execution_model`, `python.variables`, `python.collections`, `python.list`, `python.dict`, `python.control_flow`, `market.order_record`, `microstructure.spread`, `microstructure.mid`, `notation.spread`, `notation.mid`; REQUIRED: `python.fstring`, `python.dict_get`
- **Continuidad de API:** Sin cambio de API pública visible.
- **Práctica guiada:** escenas `l01-challenge`, `l01-execution`, `l01-variables`, `l01-loops`, `l01-order-data`, `l01-decision`; 5 ejercicios · 19 min — build: 1. Enciende el mercado; build: 2. Spread y mid; build: 3. Una lista de mids; aux: A1. Ticks enteros; aux: A2. Redondea como un exchange.
- **REQUIRED:** escenas `l01-errors`, `l01-recap`; introducciones `python.fstring`, `python.dict_get`; 21 ejercicios · 58 min.
- **OPTIONAL:** escenas `l01-execution/machine-code`; introducciones —; 14 ejercicios · 44 min. No entra en KNOWN ni en assessment.
- **Pieza acumulativa:** no expone una API nueva del paquete; consolida la pieza ya disponible o el trabajo previo al paquete.
- **Necesidad de L2:** Un segundo símbolo duplica datos y cálculos. → Las funciones y un único book compartido convierten la repetición en recetas reutilizables.

## L02 — Python II — Funciones y libro compartido

- **Entrada — qué sabe:** concepts: `python.variables` (L1), `python.collections` (L1), `python.control_flow` (L1), `python.fstring` (L1), `python.dict_get` (L1), `microstructure.spread` (L1), `microstructure.mid` (L1); notation: `notation.spread` (L1), `notation.mid` (L1)
- **Recuperación:** `python.control_flow` (L1): Una condición inline decide una sola vez. → Una función aplica la misma decisión a cada book.; `python.fstring` (L1): Una f-string inserta valores y controla su formato dentro de un ticket. → El calentamiento construye una lectura compacta del mid con el mismo patrón.; `python.dict_get` (L1): dict.get(clave, default) evita un KeyError cuando aún no existe una posición. → El calentamiento recupera ETH con valor cero antes de actualizar la cartera.
- **Introduce:** LIVE: `python.functions`, `python.shared_state`, `functional.order_book`, `microstructure.imbalance`, `functional.best_bid`, `functional.best_ask`, `functional.spread`, `functional.mid`, `functional.imbalance`, `notation.imbalance`; REQUIRED: `python.tuple`, `python.comprehension`, `python.generator_expression`, `python.lambda`, `python.sorted_key`, `python.default_arguments`
- **Continuidad de API:** Superficie nueva: `lesson02.order_book.best_bid`, `lesson02.order_book.best_ask`, `lesson02.order_book.spread`, `lesson02.order_book.mid`, `lesson02.order_book.imbalance`
- **Práctica guiada:** escenas `l02-challenge`, `l02-build-functions`, `l02-live-book`, `l02-bridge`; 6 ejercicios · 18 min — build: 1. Tu fábrica de órdenes; build: 2. Añade al libro; build: 3. Cancela una orden, paso a paso; aux: C1. Spread, mid y ticket; aux: C2. Ventana y media; aux: C3. Posición con red.
- **REQUIRED:** escenas `l02-recall`, `l02-sort-and-signal`, `l02-quiz`, `l02-build-functions/imbalance`; introducciones `python.tuple`, `python.comprehension`, `python.generator_expression`, `python.lambda`, `python.sorted_key`, `python.default_arguments`; 13 ejercicios · 58 min.
- **OPTIONAL:** escenas —; introducciones —; 19 ejercicios · 41 min. No entra en KNOWN ni en assessment.
- **Pieza acumulativa:** APIs `lesson02.order_book.best_bid`, `lesson02.order_book.best_ask`, `lesson02.order_book.spread`, `lesson02.order_book.mid`, `lesson02.order_book.imbalance`; snapshots comprobados —.
- **Necesidad de L3:** Las funciones todavía viven dentro de un notebook. → Los módulos, imports y errores de dominio hacen reutilizable el libro funcional.

## L03 — Python III — Módulos y errores de dominio

- **Entrada — qué sabe:** concepts: `python.functions` (L2), `functional.order_book` (L2), `python.fstring` (L1), `python.generator_expression` (L2); apis: `functional.best_bid` (L2), `functional.spread` (L2)
- **Recuperación:** `python.functions` (L2): Las funciones eliminan duplicación dentro de un notebook. → Los imports reutilizan esas mismas funciones entre archivos.
- **Introduce:** LIVE: `python.modules`, `python.imports`, `python.exceptions`, `python.domain_errors`; REQUIRED: `python.main_guard`
- **Continuidad de API:** Sin cambio de API pública visible.
- **Práctica guiada:** escenas `l03-challenge`, `l03-module-build`, `l03-errors`, `l03-bridge`; 6 ejercicios · 18 min — build: 1. Importa una función del módulo; build: 2. Importa el módulo entero; build: 3. Blinda con try/except; aux: C1. Medio spread; aux: C2. Tamaños compradores; aux: C3. Desempaqueta.
- **REQUIRED:** escenas `l03-import-recall`, `l03-main-guard`, `l03-quiz`, `l03-module-build/two-lives`, `l03-module-build/robust-library`; introducciones `python.main_guard`; 16 ejercicios · 52 min.
- **OPTIONAL:** escenas —; introducciones —; 1 ejercicios · 5 min. No entra en KNOWN ni en assessment.
- **Pieza acumulativa:** no expone una API nueva del paquete; consolida la pieza ya disponible o el trabajo previo al paquete.
- **Necesidad de L4:** Los diccionarios sin estructura mantienen separados los datos y el comportamiento. → Order y Fill vinculan los datos de mercado con comportamiento e invariantes.

## L04 — OOP I — Order y Fill

- **Entrada — qué sabe:** concepts: `python.variables` (L1), `python.functions` (L2), `python.modules` (L3), `python.fstring` (L1), `python.generator_expression` (L2)
- **Recuperación:** `python.functions` (L2): Una función recibe un diccionario de orden. → Un método lee el estado que ya contiene self.
- **Introduce:** LIVE: `oop.classes`, `oop.self`, `oop.methods`, `exchange.order`, `exchange.fill`, `side.type`, `order_type.type`, `order.constructor`, `fill.constructor`, `order.notional`, `fill.cash_flow`, `notation.cash_flow`; REQUIRED: `python.type_hints`
- **Continuidad de API:** `pedagogical.OrderMini.__init__` → `order.constructor` (La versión mínima hace visible self; la versión canónica estabiliza Side, OrderType, defaults e id antes de reutilizarse.); `pedagogical.FillMini.__init__` → `fill.constructor` (La versión canónica conserva la idea de ejecución e incorpora timestamp y tipos estables.)
- **Práctica guiada:** escenas `l04-challenge`, `l04-class-build`, `l04-order-workshop`, `l04-bridge`; 4 ejercicios · 20 min — build: 1. La clase Order; build: 2. Un método: notional; build: 3. __repr__: que sepa describirse; build: 4. La clase Fill y su cash_flow.
- **REQUIRED:** escenas `l04-function-recall`, `l04-fill-cash-flow`, `l04-quiz`, `l04-class-build/fill`; introducciones `python.type_hints`; 14 ejercicios · 36 min.
- **OPTIONAL:** escenas —; introducciones —; 4 ejercicios · 20 min. No entra en KNOWN ni en assessment.
- **Pieza acumulativa:** APIs `exchange.orders.Side`, `exchange.orders.OrderType`, `exchange.orders.Order`, `exchange.trades.Fill`, `exchange.orders.Order.notional`, `exchange.trades.Fill.cash_flow`; snapshots comprobados `04-oop-i-order-trade/exercises/exchange/orders.py`, `04-oop-i-order-trade/exercises/exchange/trades.py`.
- **Necesidad de L5:** Los objetos de dominio individuales no poseen todavía un estado coherente de libro o cartera. → La composición crea fronteras controladas para el estado de mercado y la contabilidad.

## L05 — OOP II — OrderBook y PositionTracker

- **Entrada — qué sabe:** concepts: `oop.classes` (L4), `exchange.order` (L4), `exchange.fill` (L4), `python.lambda` (L2), `python.sorted_key` (L2), `python.fstring` (L1), `python.generator_expression` (L2); apis: `order.constructor` (L4), `fill.constructor` (L4), `fill.cash_flow` (L4); notation: `notation.spread` (L1), `notation.mid` (L1), `notation.cash_flow` (L4)
- **Recuperación:** `oop.classes` (L4): Order y Fill vinculan un registro con comportamiento. → Los contenedores protegen muchos objetos de dominio y su estado compartido.
- **Introduce:** LIVE: `oop.composition`, `oop.computed_property`, `exchange.orderbook`, `exchange.position_tracker`, `orderbook.constructor`, `level.constructor`, `orderbook.best_bid`, `orderbook.best_ask`, `orderbook.spread`, `orderbook.mid`, `orderbook.imbalance`, `tracker.constructor`, `tracker.position`, `tracker.apply_fill`, `tracker.equity`, `notation.equity`; REQUIRED: `oop.encapsulation`, `microstructure.spread_cost`
- **Continuidad de API:** Superficie nueva: `exchange.book.OrderBook`, `exchange.book.Level`, `exchange.book.OrderBook.best_bid`, `exchange.book.OrderBook.best_ask`, `exchange.book.OrderBook.spread`, `exchange.book.OrderBook.mid`, `exchange.book.OrderBook.imbalance`, `exchange.portfolio.PositionTracker`, `exchange.portfolio.PositionTracker.position`, `exchange.portfolio.PositionTracker.apply_fill`, `exchange.portfolio.PositionTracker.equity`
- **Práctica guiada:** escenas `l05-challenge`, `l05-composition`, `l05-book-api`, `l05-tracker`, `l05-bridge`; 7 ejercicios · 20 min — build: 1. OrderBook: un objeto que contiene niveles; build: 2. best_bid / best_ask / spread / mid; build: 3. imbalance() del nivel 1; aux: C1. Order exprés; aux: C2. __repr__ exprés; aux: C3. Caja exprés; aux: A2. best_bid y best_ask como properties.
- **REQUIRED:** escenas `l05-encapsulation`, `l05-quiz`, `l05-composition/tracker`, `l05-composition/equity`; introducciones `oop.encapsulation`, `microstructure.spread_cost`; 11 ejercicios · 34 min.
- **OPTIONAL:** escenas —; introducciones —; 3 ejercicios · 15 min. No entra en KNOWN ni en assessment.
- **Pieza acumulativa:** APIs `exchange.book.OrderBook`, `exchange.book.Level`, `exchange.book.OrderBook.best_bid`, `exchange.book.OrderBook.best_ask`, `exchange.book.OrderBook.spread`, `exchange.book.OrderBook.mid`, `exchange.book.OrderBook.imbalance`, `exchange.portfolio.PositionTracker`, `exchange.portfolio.PositionTracker.position`, `exchange.portfolio.PositionTracker.apply_fill`, `exchange.portfolio.PositionTracker.equity`; snapshots comprobados `05-oop-ii-book-portfolio/exercises/exchange/book.py`, `05-oop-ii-book-portfolio/exercises/exchange/orders.py`, `05-oop-ii-book-portfolio/exercises/exchange/portfolio.py`, `05-oop-ii-book-portfolio/exercises/exchange/trades.py`.
- **Necesidad de L6:** Duplicar una clase completa por estrategia repite estructura y ciclo de vida. → La herencia y un contrato abstracto conservan el esqueleto mientras cambia la decisión.

## L06 — OOP III — Herencia, ABC y polimorfismo

- **Entrada — qué sabe:** concepts: `oop.classes` (L4), `oop.composition` (L5), `python.generator_expression` (L2); apis: `orderbook.imbalance` (L5); notation: `notation.imbalance` (L2)
- **Recuperación:** `oop.composition` (L5): La composición combina responsabilidades distintas. → La herencia comparte un único contrato de comportamiento.
- **Introduce:** LIVE: `oop.inheritance`, `oop.override`, `oop.abstract_base_class`, `oop.polymorphism`, `strategy.toy_contract`, `toy_strategy.decide`; REQUIRED: `oop.super`
- **Continuidad de API:** Superficie nueva: `strategies_toy.Strategy.decide`
- **Práctica guiada:** escenas `l06-challenge`, `l06-family-build`, `l06-polymorphism`, `l06-bridge`; 4 ejercicios · 20 min — build: 1. Una clase base con un método; build: 2. Hereda y sobrescribe; build: 3. El contrato: clase abstracta; build: 4. Polimorfismo.
- **REQUIRED:** escenas `l06-super`, `l06-abc`, `l06-quiz`; introducciones `oop.super`; 18 ejercicios · 52 min.
- **OPTIONAL:** escenas —; introducciones —; 2 ejercicios · 10 min. No entra en KNOWN ni en assessment.
- **Pieza acumulativa:** APIs `strategies_toy.Strategy.decide`; snapshots comprobados —.
- **Necesidad de L7:** La familia Strategy aún consume un escalar de juguete, no un estado de mercado protegido. → Level y OrderBook convierten snapshots externos en una frontera de dominio estable.

## L07 — Del snapshot real al OrderBook

- **Entrada — qué sabe:** concepts: `oop.classes` (L4), `oop.composition` (L5), `oop.computed_property` (L5), `python.modules` (L3), `python.type_hints` (L4), `python.lambda` (L2), `python.sorted_key` (L2), `python.fstring` (L1), `python.dict_get` (L1), `python.generator_expression` (L2); apis: `orderbook.constructor` (L5), `orderbook.best_bid` (L5), `orderbook.best_ask` (L5), `orderbook.spread` (L5), `orderbook.mid` (L5), `orderbook.imbalance` (L5); notation: `notation.spread` (L1), `notation.mid` (L1), `notation.imbalance` (L2)
- **Recuperación:** `oop.classes` (L4): Una clase agrupa datos y comportamiento. → Level y OrderBook protegen las invariantes del estado de mercado.
- **Introduce:** LIVE: `python.dataclass`, `market.level`, `market.book_metrics`, `market.external_boundary`, `orderbook.from_snapshot`, `orderbook.microprice`; REQUIRED: `python.enum`, `oop.classmethod`, `python.union_types`, `orderbook.depth`
- **Continuidad de API:** Superficie nueva: `exchange.book.OrderBook.from_snapshot`, `exchange.book.OrderBook.depth`, `exchange.book.OrderBook.microprice`
- **Práctica guiada:** escenas `l07-challenge`, `l07-build`, `l07-scrubber`, `l07-bridge`; 6 ejercicios · 19 min — build: B1 · Construye Level; build: B2 · Ordena bids y asks; build: B3 · Raw snapshot → niveles; aux: C1. Override exprés; aux: C2. El bucle exprés; aux: A1. La primera foto.
- **REQUIRED:** escenas `l07-signal`, `l07-quiz`, `l07-build/constructors`, `l07-build/factory`, `l07-build/api`; introducciones `python.enum`, `oop.classmethod`, `python.union_types`, `orderbook.depth`; 9 ejercicios · 42 min.
- **OPTIONAL:** escenas —; introducciones —; 2 ejercicios · 10 min. No entra en KNOWN ni en assessment.
- **Pieza acumulativa:** APIs `exchange.book.OrderBook.from_snapshot`, `exchange.book.OrderBook.depth`, `exchange.book.OrderBook.microprice`; snapshots comprobados `07-microstructure-reading-book/exercises/exchange/book.py`.
- **Necesidad de L8:** OrderBook responde preguntas, pero no puede ejecutar una intención. → MatchingEngine añade dinámica mediante PLAN, VALIDATE y COMMIT.

## L08 — Construir MatchingEngine

- **Entrada — qué sabe:** concepts: `exchange.order` (L4), `exchange.fill` (L4), `market.book_metrics` (L7), `python.type_hints` (L4), `python.union_types` (L7), `python.fstring` (L1), `python.generator_expression` (L2); apis: `side.type` (L4), `order_type.type` (L4), `order.constructor` (L4), `fill.constructor` (L4), `orderbook.constructor` (L5), `orderbook.best_bid` (L5), `orderbook.best_ask` (L5), `orderbook.mid` (L5); notation: `notation.mid` (L1)
- **Recuperación:** `exchange.order` (L4): Order representa una intención. → MatchingEngine interpreta esa intención contra la liquidez.; `exchange.fill` (L4): Fill representa una ejecución. → COMMIT emite un Fill por cada nivel consumido.
- **Introduce:** LIVE: `matching.plan_validate_commit`, `matching.atomicity`, `orderbook.reduce`, `matching.constructor`, `matching.process`; REQUIRED: `oop.staticmethod`, `matching.order_policies`, `execution.market_impact`, `orderbook.add_limit`, `side.opposite`
- **Continuidad de API:** Superficie nueva: `exchange.book.OrderBook.reduce`, `exchange.book.OrderBook.add_limit`, `exchange.orders.Side.opposite`, `exchange.matching.MatchingEngine`, `exchange.matching.MatchingEngine.process`
- **Práctica guiada:** escenas `l08-challenge`, `l08-plan-validate-commit`, `l08-simulator`, `l08-bridge`; 3 ejercicios · 19 min — build: B1 · ¿Qué lado consumo?; build: B2 · remaining + take; build: B3 · Primera MARKET completa.
- **REQUIRED:** escenas `l08-order-policies`, `l08-quiz`, `l08-plan-validate-commit/remainder`; introducciones `oop.staticmethod`, `matching.order_policies`, `execution.market_impact`, `orderbook.add_limit`, `side.opposite`; 13 ejercicios · 56 min.
- **OPTIONAL:** escenas —; introducciones —; 2 ejercicios · 15 min. No entra en KNOWN ni en assessment.
- **Pieza acumulativa:** APIs `exchange.book.OrderBook.reduce`, `exchange.book.OrderBook.add_limit`, `exchange.orders.Side.opposite`, `exchange.matching.MatchingEngine`, `exchange.matching.MatchingEngine.process`; snapshots comprobados `08-order-types-matching/exercises/exchange/book.py`, `08-order-types-matching/exercises/exchange/matching.py`, `08-order-types-matching/exercises/exchange/orders.py`, `08-order-types-matching/exercises/exchange/trades.py`.
- **Necesidad de L9:** MatchingEngine cambia un snapshot, pero no posee ni el tiempo de replay ni el estado actual. → Market compone estado, dinámica y tiempo sin duplicar el matching.

## L09 — Market — Estado, dinámica y tiempo

- **Entrada — qué sabe:** concepts: `matching.plan_validate_commit` (L8), `exchange.orderbook` (L5), `oop.composition` (L5), `market.external_boundary` (L7), `python.fstring` (L1), `python.dict_get` (L1), `python.generator_expression` (L2); apis: `matching.constructor` (L8), `matching.process` (L8), `orderbook.from_snapshot` (L7), `tracker.constructor` (L5), `tracker.position` (L5), `tracker.apply_fill` (L5), `tracker.equity` (L5)
- **Recuperación:** `oop.composition` (L5): OrderBook contiene una colección de niveles. → Market contiene un MatchingEngine y un OrderBook activo.
- **Introduce:** LIVE: `engine.market`, `engine.time_loop`, `engine.delegation`, `engine.lifecycle`, `market.constructor`, `market.book`, `market.step`, `market.submit`; REQUIRED: `metrics.equity_curve`, `market.sample`, `market.snapshots`, `market.timestamp`, `market.reset`
- **Continuidad de API:** Superficie nueva: `exchange.market.Market`, `exchange.market.Market.sample`, `exchange.market.Market.snapshots`, `exchange.market.Market.book`, `exchange.market.Market.step`, `exchange.market.Market.submit`, `exchange.market.Market.timestamp`, `exchange.market.Market.reset`
- **Práctica guiada:** escenas `l09-challenge`, `l09-composition-recall`, `l09-market-api`, `l09-day-loop`, `l09-bridge`; 5 ejercicios · 20 min — build: B1 · Estado inicial; build: B2 · Implementa step(); build: B3 · Final de datos; build: B4 · submit() sin book: fail fast; build: B5 · Delega al MatchingEngine.
- **REQUIRED:** escenas `l09-quiz`, `l09-market-api/timestamp`, `l09-market-api/reset`; introducciones `metrics.equity_curve`, `market.sample`, `market.snapshots`, `market.timestamp`, `market.reset`; 10 ejercicios · 34 min.
- **OPTIONAL:** escenas —; introducciones —; 2 ejercicios · 10 min. No entra en KNOWN ni en assessment.
- **Pieza acumulativa:** APIs `exchange.market.Market`, `exchange.market.Market.sample`, `exchange.market.Market.snapshots`, `exchange.market.Market.book`, `exchange.market.Market.step`, `exchange.market.Market.submit`, `exchange.market.Market.timestamp`, `exchange.market.Market.reset`; snapshots comprobados `09-market-simulation-loop/exercises/exchange/book.py`, `09-market-simulation-loop/exercises/exchange/market.py`, `09-market-simulation-loop/exercises/exchange/matching.py`, `09-market-simulation-loop/exercises/exchange/portfolio.py`.
- **Necesidad de L10:** El loop incrusta una decisión y no puede intercambiar estrategias con seguridad. → Un contrato Strategy de producción devuelve acciones y Backtest se responsabiliza de ejecutarlas.

## L10 — El framework — Strategy + Backtest

- **Entrada — qué sabe:** concepts: `oop.polymorphism` (L6), `oop.abstract_base_class` (L6), `strategy.toy_contract` (L6), `engine.market` (L9), `matching.plan_validate_commit` (L8), `metrics.equity_curve` (L9), `python.fstring` (L1); apis: `toy_strategy.decide` (L6), `market.sample` (L9), `market.snapshots` (L9), `market.step` (L9), `market.submit` (L9), `market.reset` (L9), `tracker.apply_fill` (L5), `tracker.equity` (L5)
- **Recuperación:** `oop.polymorphism` (L6): decide(imbalance) devuelve una etiqueta. → on_book_update(book) devuelve una lista de Action.; `oop.abstract_base_class` (L6): La ABC obliga a cada estrategia de juguete a decidir. → La ABC Strategy conserva un único contrato para el runner.; `strategy.toy_contract` (L6): Un callable devuelve una etiqueta. → Un callable devuelve acciones tipadas sin ejecutarlas.
- **Introduce:** LIVE: `architecture.actions`, `architecture.decision_execution_separation`, `architecture.execution_feedback`, `framework.strategy_contract`, `backtest.runner`, `strategy.type`, `new_order.constructor`, `cancel.constructor`, `action.type`, `strategy.on_book_update`, `strategy.on_fill`, `backtest.constructor`, `backtest.run`, `backtest_result.type`, `backtest_result.equity_curve`, `backtest_result.fills`, `backtest_result.final_position`, `backtest_result.final_equity`, `backtest_result.n_steps`, `backtest_result.n_fills`; REQUIRED: `framework.lifecycle`, `strategy.on_start`, `strategy.on_end`
- **Continuidad de API:** `toy_strategy.decide` → `strategy.on_book_update` (the runner needs full state and typed actions)
- **Práctica guiada:** escenas `l10-challenge`, `l10-contract`, `l10-live-runner`, `l10-bridge`; 7 ejercicios · 21 min — build: 1. Tu primera estrategia; build: 2. Corre el Backtest; build: 3. Reacciona a tus fills; aux: C1. El día exprés; aux: C2. equity exprés; aux: A1. La estrategia que no hace nada; aux: A2. Una acción de verdad.
- **REQUIRED:** escenas `l10-first-strategy`, `l10-quiz`; introducciones `framework.lifecycle`, `strategy.on_start`, `strategy.on_end`; 4 ejercicios · 12 min.
- **OPTIONAL:** escenas —; introducciones —; 1 ejercicios · 5 min. No entra en KNOWN ni en assessment.
- **Pieza acumulativa:** APIs `exchange.strategy.Strategy`, `exchange.strategy.Strategy.on_start`, `exchange.strategy.NewOrder`, `exchange.strategy.Cancel`, `exchange.strategy.Action`, `exchange.strategy.Strategy.on_book_update`, `exchange.strategy.Strategy.on_fill`, `exchange.strategy.Strategy.on_end`, `exchange.backtest.Backtest`, `exchange.backtest.Backtest.run`, `exchange.backtest.BacktestResult`, `exchange.backtest.BacktestResult.equity_curve`, `exchange.backtest.BacktestResult.fills`, `exchange.backtest.BacktestResult.final_position`, `exchange.backtest.BacktestResult.final_equity`, `exchange.backtest.BacktestResult.n_steps`, `exchange.backtest.BacktestResult.n_fills`; snapshots comprobados `06-oop-iii-inheritance/exercises/strategies_toy.py`, `10-strategy-framework/exercises/exchange/backtest.py`, `10-strategy-framework/exercises/exchange/market.py`, `10-strategy-framework/exercises/exchange/portfolio.py`, `10-strategy-framework/exercises/exchange/strategy.py`.
- **Necesidad de L11:** La equity final no permite separar señal, coste de ejecución e inventario. → Los benchmarks y el slippage con signo convierten el resultado en evidencia.

## L11 — Primera estrategia + métricas

- **Entrada — qué sabe:** concepts: `framework.strategy_contract` (L10), `backtest.runner` (L10), `microstructure.spread_cost` (L5), `metrics.equity_curve` (L9), `python.fstring` (L1); apis: `market.sample` (L9), `market.step` (L9), `new_order.constructor` (L10), `order.constructor` (L4), `orderbook.imbalance` (L5), `orderbook.mid` (L5), `strategy.on_book_update` (L10), `strategy.on_fill` (L10), `backtest.constructor` (L10), `backtest.run` (L10), `backtest_result.fills` (L10), `backtest_result.equity_curve` (L10), `backtest_result.final_position` (L10), `backtest_result.final_equity` (L10), `backtest_result.n_steps` (L10), `backtest_result.n_fills` (L10), `tracker.equity` (L5); notation: `notation.equity` (L5), `notation.spread` (L1)
- **Recuperación:** `microstructure.spread_cost` (L5): Cruzar el spread crea un coste inmediato de ida y vuelta. → El slippage con signo aísla la calidad de ejecución del PnL.
- **Introduce:** LIVE: `metrics.arrival_price`, `metrics.slippage`, `metrics.random_benchmark`, `metrics.pnl_execution_separation`, `metrics.inventory_exposure`, `notation.slippage_signed`
- **Continuidad de API:** Sin cambio de API pública visible.
- **Práctica guiada:** escenas `l11-challenge`, `l11-three-judges`, `l11-random-benchmark`, `l11-bridge`; 4 ejercicios · 20 min — build: 1. Estrategia de imbalance; build: 2. Mídela; build: 3. Parent arrival; build: 4. Riesgo escondido.
- **REQUIRED:** escenas `l11-cost-autopsy`, `l11-quiz`, `l11-three-judges/verdict`; introducciones —; 7 ejercicios · 14 min.
- **OPTIONAL:** escenas —; introducciones —; 2 ejercicios · 10 min. No entra en KNOWN ni en assessment.
- **Pieza acumulativa:** no expone una API nueva del paquete; consolida la pieza ya disponible o el trabajo previo al paquete.
- **Necesidad de L12:** Una única orden de mercado grande concentra el impacto. → El slicing reparte el objetivo en el tiempo con TWAP y VWAP.

## L12 — VWAP — Ejecución por tramos

- **Entrada — qué sabe:** concepts: `framework.strategy_contract` (L10), `metrics.arrival_price` (L11), `metrics.slippage` (L11), `execution.market_impact` (L8), `python.fstring` (L1), `python.generator_expression` (L2); apis: `market.sample` (L9), `new_order.constructor` (L10), `order.constructor` (L4), `strategy.on_book_update` (L10), `backtest.constructor` (L10), `backtest.run` (L10), `backtest_result.fills` (L10); notation: `notation.slippage_signed` (L11)
- **Recuperación:** `execution.market_impact` (L8): Las órdenes grandes consumen más niveles. → El slicing controla cuánto impacto se expone en cada paso temporal.
- **Introduce:** LIVE: `execution.slicing`, `execution.twap`, `execution.vwap`, `execution.volume_profile`, `strategy.vwap`, `vwap_strategy.constructor`, `notation.twap`, `notation.vwap`; OPTIONAL: `execution.dynamic_volume_prediction`
- **Continuidad de API:** Superficie nueva: `exchange.strategies.vwap.VWAPStrategy`
- **Práctica guiada:** escenas `l12-challenge`, `l12-slicing`, `l12-schedule-duel`, `l12-vwap-strategy`, `l12-bridge`; 4 ejercicios · 20 min — build: 1. Schedule TWAP; build: 2. Lanza un VWAPStrategy; build: 3. Perfil VWAP a medida; build: 4. Precio medio de ejecución.
- **REQUIRED:** escenas `l12-quiz`; introducciones —; 7 ejercicios · 14 min.
- **OPTIONAL:** escenas `l12-dynamic-profile`; introducciones `execution.dynamic_volume_prediction`; 7 ejercicios · 35 min. No entra en KNOWN ni en assessment.
- **Pieza acumulativa:** APIs `exchange.strategies.vwap.VWAPStrategy`; snapshots comprobados `12-vwap-execution/exercises/exchange/backtest.py`, `12-vwap-execution/exercises/exchange/market.py`, `12-vwap-execution/exercises/exchange/orders.py`, `12-vwap-execution/exercises/exchange/strategies/vwap.py`, `12-vwap-execution/exercises/exchange/strategy.py`.
- **Necesidad de L13:** Las estrategias de ejecución pagan el spread para demandar liquidez. → Un market maker ofrece quotes, cobra el spread y controla el inventario.

## L13 — Market making — Spread, inventario y skew

- **Entrada — qué sabe:** concepts: `framework.strategy_contract` (L10), `microstructure.spread_cost` (L5), `metrics.inventory_exposure` (L11), `architecture.execution_feedback` (L10), `python.fstring` (L1), `python.generator_expression` (L2); apis: `level.constructor` (L5), `orderbook.constructor` (L5), `orderbook.mid` (L5), `new_order.constructor` (L10), `strategy.on_book_update` (L10), `strategy.on_fill` (L10); notation: `notation.spread` (L1), `notation.equity` (L5)
- **Recuperación:** `microstructure.spread_cost` (L5): Un taker pierde el spread en una ida y vuelta. → Un provider intenta cobrar ese spread.; `architecture.execution_feedback` (L10): on_fill cierra el bucle de feedback. → El mismo hook actualiza el inventario.
- **Introduce:** LIVE: `market_making.liquidity_provision`, `market_making.quotes`, `market_making.adverse_selection`, `inventory.risk`, `inventory.skew`, `market_making.heuristic_reservation_price`, `market_making.cara_utility`, `market_making.fill_intensity`, `market_maker.constructor`, `market_maker.half_spread`, `market_maker.inventory`, `market_maker.inventory_skew`, `market_maker.reservation_price`, `market_maker.quotes`, `mm_simulation.constructor`, `mm_simulation.run`, `sim_result.type`, `sim_result.final_pnl`, `sim_result.max_inventory`, `notation.inventory`, `notation.heuristic_reservation`, `notation.cara_utility`, `notation.fill_intensity`; REQUIRED: `sim_result.pnl`
- **Continuidad de API:** Superficie nueva: `exchange.strategies.market_maker.MarketMaker`, `exchange.strategies.market_maker.MarketMaker.half_spread`, `exchange.strategies.market_maker.MarketMaker.inventory`, `exchange.strategies.market_maker.MarketMaker.inventory_skew`, `exchange.strategies.market_maker.MarketMaker.reservation_price`, `exchange.strategies.market_maker.MarketMaker.quotes`, `exchange.simulation.MMSimulation`, `exchange.simulation.MMSimulation.run`, `exchange.simulation.SimResult`, `exchange.simulation.SimResult.pnl`, `exchange.simulation.SimResult.final_pnl`, `exchange.simulation.SimResult.max_inventory`
- **Práctica guiada:** escenas `l13-challenge`, `l13-business-and-risk`, `l13-mm-simulator`, `l13-quotes`, `l13-bridge`; 4 ejercicios · 20 min — build: 1. Cotiza alrededor del mid; build: 2. El skew baja las cotizaciones si estás largo; build: 3. Reservation price; build: 4. Simula al market maker.
- **REQUIRED:** escenas `l13-quiz`; introducciones `sim_result.pnl`; 9 ejercicios · 19 min.
- **OPTIONAL:** escenas —; introducciones —; 0 ejercicios · 0 min. No entra en KNOWN ni en assessment.
- **Pieza acumulativa:** APIs `exchange.strategies.market_maker.MarketMaker`, `exchange.strategies.market_maker.MarketMaker.half_spread`, `exchange.strategies.market_maker.MarketMaker.inventory`, `exchange.strategies.market_maker.MarketMaker.inventory_skew`, `exchange.strategies.market_maker.MarketMaker.reservation_price`, `exchange.strategies.market_maker.MarketMaker.quotes`, `exchange.simulation.MMSimulation`, `exchange.simulation.MMSimulation.run`, `exchange.simulation.SimResult`, `exchange.simulation.SimResult.pnl`, `exchange.simulation.SimResult.final_pnl`, `exchange.simulation.SimResult.max_inventory`; snapshots comprobados `13-market-making-intro/exercises/exchange/book.py`, `13-market-making-intro/exercises/exchange/simulation.py`, `13-market-making-intro/exercises/exchange/strategies/market_maker.py`, `13-market-making-intro/exercises/exchange/strategy.py`.
- **Necesidad de L14:** Un skew ajustado a mano no conecta de forma explícita volatilidad, horizonte e intensidad de fills. → Avellaneda–Stoikov da parámetros interpretables al centro y a la anchura.

## L14 — Avellaneda–Stoikov — Modelo y simulación

- **Entrada — qué sabe:** concepts: `framework.strategy_contract` (L10), `inventory.risk` (L13), `inventory.skew` (L13), `market_making.heuristic_reservation_price` (L13), `market_making.cara_utility` (L13), `market_making.fill_intensity` (L13), `python.fstring` (L1); apis: `level.constructor` (L5), `orderbook.constructor` (L5), `orderbook.mid` (L5), `new_order.constructor` (L10), `strategy.on_book_update` (L10), `strategy.on_fill` (L10), `market_maker.constructor` (L13), `market_maker.half_spread` (L13), `market_maker.inventory` (L13), `market_maker.inventory_skew` (L13), `market_maker.reservation_price` (L13), `market_maker.quotes` (L13), `mm_simulation.constructor` (L13), `mm_simulation.run` (L13), `sim_result.final_pnl` (L13), `sim_result.max_inventory` (L13); notation: `notation.inventory` (L13), `notation.heuristic_reservation` (L13), `notation.cara_utility` (L13), `notation.fill_intensity` (L13)
- **Recuperación:** `market_making.heuristic_reservation_price` (L13): r = mid - skew_heurístico × inventario → r = s - q γ σ² τ expresa el mismo control con unidades.; `framework.strategy_contract` (L10): on_book_update devuelve acciones y on_fill actualiza el estado. → A-S cambia las fórmulas dentro del mismo ciclo de vida.; `market_making.cara_utility` (L13): CARA dio a γ el significado de aversión al riesgo. → γ controla cuánto desplazan riesgo e inventario el centro A-S.; `market_making.fill_intensity` (L13): λ(δ)=A·exp(−κδ) hizo visible la caída de fills con la distancia. → κ entra en el ancho óptimo y cuantifica ese mismo trade-off.
- **Introduce:** LIVE: `as.reservation_price`, `as.optimal_spread`, `as.gamma`, `as.sigma`, `as.kappa`, `as.time_horizon`, `simulation.parameter_sweep`, `avellaneda_stoikov.constructor`, `avellaneda_stoikov.time`, `avellaneda_stoikov.reservation_price`, `avellaneda_stoikov.optimal_spread`, `avellaneda_stoikov.quotes`, `notation.as_reservation_price`, `notation.as_optimal_spread`
- **Continuidad de API:** `market_maker.constructor` → `avellaneda_stoikov.constructor` (La subclase conserva symbol y quote_size, y sustituye los parámetros heurísticos por γ, σ, κ y horizonte explícitos.); `market_maker.reservation_price` → `avellaneda_stoikov.reservation_price` (La firma permanece estable, pero el centro deja el skew fijo y pasa a qγσ²τ; el contrato separado impide ocultar ese cambio de responsabilidad.); `market_maker.quotes` → `avellaneda_stoikov.quotes` (El retorno sigue siendo bid/ask, pero ahora usa el reservation price y el ancho óptimo de A-S.)
- **Práctica guiada:** escenas `l14-challenge`, `l14-formulas`, `l14-lab`, `l14-recap`; 7 ejercicios · 21 min — build: 1. Reservation price con inventario; build: 2. Optimal spread positivo; build: 3. Cotizaciones A-S; aux: C1. Reservation exprés; aux: C2. La vuelta exprés; aux: A1. Reservation A-S a mano; aux: A2. Optimal spread a mano.
- **REQUIRED:** escenas `l14-capstone`, `l14-quiz`; introducciones —; 8 ejercicios · 35 min.
- **OPTIONAL:** escenas —; introducciones —; 2 ejercicios · 10 min. No entra en KNOWN ni en assessment.
- **Pieza acumulativa:** APIs `exchange.strategies.avellaneda_stoikov.AvellanedaStoikov`, `exchange.strategies.avellaneda_stoikov.AvellanedaStoikov.time`, `exchange.strategies.avellaneda_stoikov.AvellanedaStoikov.reservation_price`, `exchange.strategies.avellaneda_stoikov.AvellanedaStoikov.optimal_spread`, `exchange.strategies.avellaneda_stoikov.AvellanedaStoikov.quotes`; snapshots comprobados `14-avellaneda-stoikov/exercises/exchange/book.py`, `14-avellaneda-stoikov/exercises/exchange/simulation.py`, `14-avellaneda-stoikov/exercises/exchange/strategies/avellaneda_stoikov.py`, `14-avellaneda-stoikov/exercises/exchange/strategies/market_maker.py`, `14-avellaneda-stoikov/exercises/exchange/strategy.py`.
- **Necesidad de L15:** El exchange completo aún no se ha demostrado bajo restricciones de evaluación. → La evaluación final muestrea razonamiento acumulativo de todos los bloques.

## L15 — Assessment final acumulativo

- **Entrada — qué sabe:** concepts: `python.control_flow` (L1), `python.generator_expression` (L2), `oop.polymorphism` (L6), `matching.atomicity` (L8), `framework.strategy_contract` (L10), `metrics.slippage` (L11), `execution.vwap` (L12), `inventory.skew` (L13), `as.reservation_price` (L14), `as.optimal_spread` (L14); apis: `matching.process` (L8), `strategy.on_book_update` (L10), `backtest.run` (L10); notation: `notation.slippage_signed` (L11), `notation.vwap` (L12), `notation.as_reservation_price` (L14), `notation.as_optimal_spread` (L14)
- **Recuperación:** No requiere un recall distante; la continuidad es inmediata o la lesson inicia el curso.
- **Introduce:** No añade conceptos: integra el curso en la evaluación final.
- **Continuidad de API:** Sin cambio de API pública visible.
- **Práctica guiada:** escenas —; 0 ejercicios · 0 min.
- **REQUIRED:** escenas `l15-official-assessment`; introducciones —; 0 ejercicios · 0 min.
- **OPTIONAL:** escenas —; introducciones —; 0 ejercicios · 0 min. No entra en KNOWN ni en assessment.
- **Pieza acumulativa:** APIs —; snapshots comprobados `14-avellaneda-stoikov/exercises/exchange/backtest.py`, `14-avellaneda-stoikov/exercises/exchange/matching.py`, `14-avellaneda-stoikov/exercises/exchange/strategy.py`.
- **Salida:** assessment acumulativo; cierra el recorrido sin prometer una lesson inexistente.

## Cierre

El cálculo machine-readable arroja cero dependencias pendientes y cero fugas OPTIONAL → REQUIRED. La revisión cualitativa y la evidencia visual se registran por separado en `docs/work2-full-course-scaleout.md`.
