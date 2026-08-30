# Informe de dependencias del curso

> Artefacto generado por `framework/_build/pedagogy_reports.py` a partir de `pedagogy/`. No editar a mano.

## Resumen verificable

- Registry de conceptos: **93**.
- Registry de APIs: **78**.
- Registry de notación: **14**.
- Requisitos sin origen anterior: **0**.
- Requisitos procedentes solo de OPTIONAL: **0**.

## Aristas por lesson

| Lesson | Requiere conceptos | Requiere APIs | Requiere notación | Recalls | Siguiente necesidad |
|---|---|---|---|---|---|
| L1 | — | — | — | — | L2: Las funciones y un único book compartido convierten la repetición en recetas reutilizables. |
| L2 | `python.variables`, `python.collections`, `python.control_flow`, `python.fstring`, `python.dict_get`, `microstructure.spread`, `microstructure.mid` | — | `notation.spread`, `notation.mid` | `python.control_flow`, `python.fstring`, `python.dict_get` | L3: Los módulos, imports y errores de dominio hacen reutilizable el libro funcional. |
| L3 | `python.functions`, `functional.order_book`, `python.fstring`, `python.generator_expression` | `functional.make_order`, `functional.add_order`, `functional.cancel_order`, `functional.best_bid`, `functional.best_ask`, `functional.spread`, `functional.mid`, `functional.imbalance` | — | `python.functions` | L4: Order y Fill vinculan los datos de mercado con comportamiento e invariantes. |
| L4 | `python.variables`, `python.functions`, `python.modules`, `python.fstring`, `python.generator_expression` | — | — | `python.functions` | L5: La composición crea fronteras controladas para el estado de mercado y la contabilidad. |
| L5 | `oop.classes`, `exchange.order`, `exchange.fill`, `python.lambda`, `python.sorted_key`, `python.fstring`, `python.generator_expression` | `order.constructor`, `fill.constructor`, `fill.cash_flow` | `notation.spread`, `notation.mid`, `notation.cash_flow` | `oop.classes` | L6: La herencia y un contrato abstracto conservan el esqueleto mientras cambia la decisión. |
| L6 | `oop.classes`, `oop.composition`, `python.generator_expression` | `orderbook.imbalance` | `notation.imbalance` | `oop.composition` | L7: Level y OrderBook convierten snapshots externos en una frontera de dominio estable. |
| L7 | `oop.classes`, `oop.composition`, `oop.computed_property`, `python.modules`, `python.type_hints`, `python.lambda`, `python.sorted_key`, `python.fstring`, `python.dict_get`, `python.generator_expression` | `orderbook.constructor`, `orderbook.best_bid`, `orderbook.best_ask`, `orderbook.spread`, `orderbook.mid`, `orderbook.imbalance` | `notation.spread`, `notation.mid`, `notation.imbalance` | `oop.classes` | L8: MatchingEngine añade dinámica mediante PLAN, VALIDATE y COMMIT. |
| L8 | `exchange.order`, `exchange.fill`, `market.book_metrics`, `python.type_hints`, `python.union_types`, `python.fstring`, `python.generator_expression` | `side.type`, `order_type.type`, `order.constructor`, `fill.constructor`, `orderbook.constructor`, `orderbook.best_bid`, `orderbook.best_ask`, `orderbook.mid` | `notation.mid` | `exchange.order`, `exchange.fill` | L9: Market compone estado, dinámica y tiempo sin duplicar el matching. |
| L9 | `matching.plan_validate_commit`, `exchange.orderbook`, `oop.composition`, `market.external_boundary`, `python.fstring`, `python.dict_get`, `python.generator_expression` | `matching.constructor`, `matching.process`, `orderbook.from_snapshot`, `tracker.constructor`, `tracker.position`, `tracker.apply_fill`, `tracker.equity` | — | `oop.composition` | L10: Un contrato Strategy de producción devuelve acciones y Backtest se responsabiliza de ejecutarlas. |
| L10 | `oop.polymorphism`, `oop.abstract_base_class`, `strategy.toy_contract`, `engine.market`, `matching.plan_validate_commit`, `metrics.equity_curve`, `python.fstring` | `toy_strategy.decide`, `market.sample`, `market.snapshots`, `market.step`, `market.submit`, `market.reset`, `tracker.apply_fill`, `tracker.equity` | — | `oop.polymorphism`, `oop.abstract_base_class`, `strategy.toy_contract` | L11: Los benchmarks y el slippage con signo convierten el resultado en evidencia. |
| L11 | `framework.strategy_contract`, `backtest.runner`, `microstructure.spread_cost`, `metrics.equity_curve`, `python.fstring` | `market.sample`, `market.step`, `new_order.constructor`, `order.constructor`, `orderbook.imbalance`, `orderbook.mid`, `strategy.on_book_update`, `strategy.on_fill`, `backtest.constructor`, `backtest.run`, `backtest_result.fills`, `backtest_result.equity_curve`, `backtest_result.final_position`, `backtest_result.final_equity`, `backtest_result.n_steps`, `backtest_result.n_fills`, `tracker.equity` | `notation.equity`, `notation.spread` | `microstructure.spread_cost` | L12: El slicing reparte el objetivo en el tiempo con TWAP y VWAP. |
| L12 | `framework.strategy_contract`, `metrics.arrival_price`, `metrics.slippage`, `execution.market_impact`, `python.fstring`, `python.generator_expression` | `market.sample`, `new_order.constructor`, `order.constructor`, `strategy.on_book_update`, `backtest.constructor`, `backtest.run`, `backtest_result.fills` | `notation.slippage_signed` | `execution.market_impact` | L13: Un market maker ofrece quotes, cobra el spread y controla el inventario. |
| L13 | `framework.strategy_contract`, `microstructure.spread_cost`, `metrics.inventory_exposure`, `architecture.execution_feedback`, `python.fstring`, `python.generator_expression` | `level.constructor`, `orderbook.constructor`, `orderbook.mid`, `new_order.constructor`, `strategy.on_book_update`, `strategy.on_fill` | `notation.spread`, `notation.equity` | `microstructure.spread_cost`, `architecture.execution_feedback` | L14: Avellaneda–Stoikov da parámetros interpretables al centro y a la anchura. |
| L14 | `framework.strategy_contract`, `inventory.risk`, `inventory.skew`, `market_making.heuristic_reservation_price`, `market_making.cara_utility`, `market_making.fill_intensity`, `python.fstring` | `level.constructor`, `orderbook.constructor`, `orderbook.mid`, `new_order.constructor`, `strategy.on_book_update`, `strategy.on_fill`, `market_maker.constructor`, `market_maker.half_spread`, `market_maker.inventory`, `market_maker.inventory_skew`, `market_maker.reservation_price`, `market_maker.quotes`, `mm_simulation.constructor`, `mm_simulation.run`, `sim_result.final_pnl`, `sim_result.max_inventory` | `notation.inventory`, `notation.heuristic_reservation`, `notation.cara_utility`, `notation.fill_intensity` | `market_making.heuristic_reservation_price`, `framework.strategy_contract`, `market_making.cara_utility`, `market_making.fill_intensity` | L15: La práctica pública de L15 muestrea razonamiento acumulativo; la evaluación oficial permanece bloqueada: sus bancos deberán crearse de nuevo y entregarse exclusivamente desde la futura fuente privada autorizada. |
| L15 | `python.control_flow`, `python.generator_expression`, `oop.polymorphism`, `matching.atomicity`, `framework.strategy_contract`, `metrics.slippage`, `execution.vwap`, `inventory.skew`, `as.reservation_price`, `as.optimal_spread` | `matching.process`, `strategy.on_book_update`, `backtest.run` | `notation.slippage_signed`, `notation.vwap`, `notation.as_reservation_price`, `notation.as_optimal_spread` | — | — |

## Conceptos

| Concepto estable | Primera introducción | Reutilización | Recalls | Assessment |
|---|---|---|---|---|
| `python.execution_model` | L1 · LIVE | — | — | `l01-explain-execution` |
| `python.variables` | L1 · LIVE | L2, L4 | — | `l01-model-market-data` |
| `python.collections` | L1 · LIVE | L2 | — | — |
| `python.list` | L1 · LIVE | — | — | `l01-model-market-data` |
| `python.dict` | L1 · LIVE | — | — | `l01-model-market-data` |
| `python.fstring` | L1 · REQUIRED | L2, L3, L4, L5, L7, L8, L9, L10, L11, L12, L13, L14 | L2 | — |
| `python.dict_get` | L1 · REQUIRED | L2, L7, L9 | L2 | — |
| `python.control_flow` | L1 · LIVE | L2, L15 | L2 | `l01-turn-data-into-decision`, `l15-integrate-course` |
| `market.order_record` | L1 · LIVE | — | — | `l01-model-market-data` |
| `microstructure.spread` | L1 · LIVE | L2 | — | `l01-turn-data-into-decision` |
| `microstructure.mid` | L1 · LIVE | L2 | — | `l01-turn-data-into-decision` |
| `python.functions` | L2 · LIVE | L3, L4 | L3, L4 | `l02-extract-functions` |
| `python.shared_state` | L2 · LIVE | — | — | `l02-extract-functions` |
| `functional.order_book` | L2 · LIVE | L3 | — | `l02-read-functional-book` |
| `microstructure.imbalance` | L2 · LIVE | — | — | `l02-read-functional-book` |
| `python.tuple` | L2 · REQUIRED | — | — | — |
| `python.comprehension` | L2 · REQUIRED | — | — | `l02-read-sorting-tools` |
| `python.generator_expression` | L2 · REQUIRED | L3, L4, L5, L6, L7, L8, L9, L12, L13, L15 | — | `l02-read-sorting-tools` |
| `python.lambda` | L2 · REQUIRED | L5, L7 | — | `l02-read-sorting-tools` |
| `python.sorted_key` | L2 · REQUIRED | L5, L7 | — | `l02-read-sorting-tools` |
| `python.default_arguments` | L2 · REQUIRED | — | — | — |
| `python.modules` | L3 · LIVE | L4, L7 | — | `l03-reuse-module` |
| `python.imports` | L3 · LIVE | — | — | `l03-reuse-module` |
| `python.exceptions` | L3 · LIVE | — | — | `l03-handle-domain-errors` |
| `python.main_guard` | L3 · REQUIRED | — | — | `l03-separate-import-and-execution` |
| `python.domain_errors` | L3 · LIVE | — | — | `l03-separate-import-and-execution` |
| `oop.classes` | L4 · LIVE | L5, L6, L7 | L5, L7 | `l04-build-domain-objects` |
| `oop.self` | L4 · LIVE | — | — | `l04-build-domain-objects` |
| `oop.methods` | L4 · LIVE | — | — | — |
| `python.type_hints` | L4 · REQUIRED | L7, L8 | — | `l04-read-canonical-constructors` |
| `exchange.order` | L4 · LIVE | L5, L8 | L8 | `l04-build-domain-objects` |
| `exchange.fill` | L4 · LIVE | L5, L8 | L8 | `l04-build-domain-objects`, `l04-interpret-cash-flow` |
| `oop.composition` | L5 · LIVE | L6, L7, L9 | L6, L9 | `l05-compose-book`, `l09-compose-market` |
| `oop.encapsulation` | L5 · REQUIRED | — | — | `l05-protect-invariants` |
| `oop.computed_property` | L5 · LIVE | L7 | — | `l05-compose-book` |
| `exchange.orderbook` | L5 · LIVE | L9 | — | `l05-compose-book` |
| `exchange.position_tracker` | L5 · LIVE | — | — | `l05-account-for-fills` |
| `microstructure.spread_cost` | L5 · REQUIRED | L11, L13 | L11, L13 | `l05-protect-invariants` |
| `oop.inheritance` | L6 · LIVE | — | — | `l06-build-strategy-family` |
| `oop.override` | L6 · LIVE | — | — | `l06-build-strategy-family` |
| `oop.abstract_base_class` | L6 · LIVE | L10 | L10 | `l06-enforce-contract`, `l10-map-toy-to-production` |
| `oop.polymorphism` | L6 · LIVE | L10, L15 | L10 | `l06-explain-polymorphism`, `l10-map-toy-to-production`, `l15-integrate-course` |
| `oop.super` | L6 · REQUIRED | — | — | `l06-initialize-subclasses` |
| `strategy.toy_contract` | L6 · LIVE | L10 | L10 | `l06-build-strategy-family` |
| `python.dataclass` | L7 · LIVE | — | — | `l07-build-book` |
| `python.enum` | L7 · REQUIRED | — | — | `l07-build-stable-boundary` |
| `oop.classmethod` | L7 · REQUIRED | — | — | `l07-build-stable-boundary` |
| `python.union_types` | L7 · REQUIRED | L8 | — | `l07-build-stable-boundary` |
| `market.level` | L7 · LIVE | — | — | `l07-build-book` |
| `market.book_metrics` | L7 · LIVE | L8 | — | `l07-read-metrics` |
| `market.external_boundary` | L7 · LIVE | L9 | — | `l07-build-book` |
| `oop.staticmethod` | L8 · REQUIRED | — | — | `l08-compare-order-policies` |
| `matching.plan_validate_commit` | L8 · LIVE | L9, L10 | — | `l08-explain-atomicity` |
| `matching.atomicity` | L8 · LIVE | L15 | — | `l08-explain-atomicity`, `l15-integrate-course` |
| `matching.order_policies` | L8 · REQUIRED | — | — | `l08-compare-order-policies` |
| `execution.market_impact` | L8 · REQUIRED | L12 | L12 | `l08-connect-size-to-impact` |
| `engine.market` | L9 · LIVE | L10 | — | `l09-compose-market` |
| `engine.time_loop` | L9 · LIVE | — | — | `l09-run-time-loop` |
| `engine.delegation` | L9 · LIVE | — | — | `l09-compose-market` |
| `engine.lifecycle` | L9 · LIVE | — | — | `l09-reset-lifecycle` |
| `architecture.actions` | L10 · LIVE | — | — | `l10-separate-decision-execution` |
| `architecture.decision_execution_separation` | L10 · LIVE | — | — | `l10-separate-decision-execution` |
| `architecture.execution_feedback` | L10 · LIVE | L13 | L13 | `l10-close-feedback-loop` |
| `framework.strategy_contract` | L10 · LIVE | L11, L12, L13, L14, L15 | L14 | `l10-map-toy-to-production`, `l14-build-capstone`, `l15-integrate-course` |
| `framework.lifecycle` | L10 · REQUIRED | — | — | `l10-read-lifecycle` |
| `backtest.runner` | L10 · LIVE | L11 | — | `l10-read-lifecycle` |
| `metrics.arrival_price` | L11 · LIVE | L12 | — | `l11-benchmark-strategy` |
| `metrics.slippage` | L11 · LIVE | L12, L15 | — | `l11-interpret-slippage`, `l15-integrate-course` |
| `metrics.random_benchmark` | L11 · LIVE | — | — | `l11-benchmark-strategy` |
| `metrics.pnl_execution_separation` | L11 · LIVE | — | — | `l11-interpret-slippage` |
| `metrics.inventory_exposure` | L11 · LIVE | L13 | — | `l11-track-inventory-risk` |
| `metrics.equity_curve` | L9 · REQUIRED | L10, L11 | — | `l09-track-equity-over-time`, `l10-separate-decision-execution`, `l11-benchmark-strategy` |
| `execution.slicing` | L12 · LIVE | — | — | `l12-compare-schedules` |
| `execution.twap` | L12 · LIVE | — | — | `l12-compare-schedules` |
| `execution.vwap` | L12 · LIVE | L15 | — | `l12-compare-schedules`, `l15-integrate-course` |
| `execution.volume_profile` | L12 · LIVE | — | — | `l12-compare-schedules` |
| `strategy.vwap` | L12 · LIVE | — | — | `l12-run-vwap-strategy` |
| `execution.dynamic_volume_prediction` | L12 · OPTIONAL | — | — | — |
| `market_making.liquidity_provision` | L13 · LIVE | — | — | `l13-explain-liquidity-provision` |
| `market_making.quotes` | L13 · LIVE | — | — | `l13-explain-liquidity-provision`, `l13-inspect-pnl-path` |
| `market_making.adverse_selection` | L13 · LIVE | — | — | `l13-explain-liquidity-provision` |
| `inventory.risk` | L13 · LIVE | L14 | — | `l13-control-inventory` |
| `inventory.skew` | L13 · LIVE | L14, L15 | — | `l13-control-inventory`, `l14-build-capstone`, `l15-integrate-course` |
| `market_making.heuristic_reservation_price` | L13 · LIVE | L14 | L14 | `l13-control-inventory` |
| `market_making.cara_utility` | L13 · LIVE | L14 | L14 | `l13-prepare-risk-and-fills` |
| `market_making.fill_intensity` | L13 · LIVE | L14 | L14 | `l13-prepare-risk-and-fills` |
| `as.reservation_price` | L14 · LIVE | L15 | — | `l14-interpret-reservation-price`, `l15-integrate-course` |
| `as.optimal_spread` | L14 · LIVE | L15 | — | `l14-interpret-optimal-spread`, `l15-integrate-course` |
| `as.gamma` | L14 · LIVE | — | — | `l14-interpret-reservation-price`, `l14-run-parameter-lab` |
| `as.sigma` | L14 · LIVE | — | — | `l14-interpret-reservation-price` |
| `as.kappa` | L14 · LIVE | — | — | `l14-interpret-optimal-spread` |
| `as.time_horizon` | L14 · LIVE | — | — | `l14-interpret-reservation-price` |
| `simulation.parameter_sweep` | L14 · LIVE | — | — | `l14-run-parameter-lab` |

## APIs visibles

| API estable | Primera introducción | Reutilización | Assessment | Nombre público |
|---|---|---|---|---|
| `functional.make_order` | L2 · LIVE | L3 | `l02-extract-functions`, `l03-reuse-module` | `lesson02.order_book.make_order` |
| `functional.add_order` | L2 · LIVE | L3 | `l02-extract-functions`, `l03-reuse-module` | `lesson02.order_book.add_order` |
| `functional.cancel_order` | L2 · LIVE | L3 | `l02-extract-functions`, `l03-reuse-module` | `lesson02.order_book.cancel_order` |
| `functional.best_bid` | L2 · LIVE | L3 | `l02-extract-functions`, `l03-reuse-module` | `lesson02.order_book.best_bid` |
| `functional.best_ask` | L2 · LIVE | L3 | `l02-extract-functions`, `l03-reuse-module` | `lesson02.order_book.best_ask` |
| `functional.spread` | L2 · LIVE | L3 | `l02-read-functional-book`, `l03-reuse-module` | `lesson02.order_book.spread` |
| `functional.mid` | L2 · LIVE | L3 | `l02-read-functional-book`, `l03-reuse-module` | `lesson02.order_book.mid` |
| `functional.imbalance` | L2 · LIVE | L3 | `l02-read-functional-book`, `l03-reuse-module` | `lesson02.order_book.imbalance` |
| `side.type` | L4 · LIVE | L8 | `l04-read-canonical-constructors` | `exchange.orders.Side` |
| `order_type.type` | L4 · LIVE | L8 | `l04-read-canonical-constructors` | `exchange.orders.OrderType` |
| `order.constructor` | L4 · LIVE | L5, L8, L11, L12 | `l04-read-canonical-constructors` | `exchange.orders.Order` |
| `fill.constructor` | L4 · LIVE | L5, L8 | `l04-read-canonical-constructors` | `exchange.trades.Fill` |
| `order.notional` | L4 · LIVE | — | `l04-build-domain-objects` | `exchange.orders.Order.notional` |
| `fill.cash_flow` | L4 · LIVE | L5 | `l04-build-domain-objects`, `l04-interpret-cash-flow` | `exchange.trades.Fill.cash_flow` |
| `orderbook.constructor` | L5 · LIVE | L7, L8, L13, L14 | `l05-compose-book` | `exchange.book.OrderBook` |
| `level.constructor` | L5 · LIVE | L13, L14 | `l05-compose-book` | `exchange.book.Level` |
| `orderbook.best_bid` | L5 · LIVE | L7, L8 | `l05-compose-book`, `l07-read-metrics` | `exchange.book.OrderBook.best_bid` |
| `orderbook.best_ask` | L5 · LIVE | L7, L8 | `l05-compose-book`, `l07-read-metrics` | `exchange.book.OrderBook.best_ask` |
| `orderbook.spread` | L5 · LIVE | L7 | `l05-compose-book` | `exchange.book.OrderBook.spread` |
| `orderbook.mid` | L5 · LIVE | L7, L8, L11, L13, L14 | `l05-compose-book`, `l07-read-metrics` | `exchange.book.OrderBook.mid` |
| `orderbook.imbalance` | L5 · LIVE | L6, L7, L11 | `l05-compose-book` | `exchange.book.OrderBook.imbalance` |
| `tracker.apply_fill` | L5 · LIVE | L9, L10 | `l05-account-for-fills`, `l09-track-equity-over-time` | `exchange.portfolio.PositionTracker.apply_fill` |
| `tracker.constructor` | L5 · LIVE | L9 | `l05-account-for-fills`, `l09-track-equity-over-time` | `exchange.portfolio.PositionTracker` |
| `tracker.position` | L5 · LIVE | L9 | `l05-account-for-fills`, `l09-track-equity-over-time` | `exchange.portfolio.PositionTracker.position` |
| `tracker.equity` | L5 · LIVE | L9, L10, L11 | `l05-account-for-fills`, `l09-track-equity-over-time` | `exchange.portfolio.PositionTracker.equity` |
| `toy_strategy.decide` | L6 · LIVE | L10 | `l06-build-strategy-family`, `l10-map-toy-to-production` | `strategies_toy.Strategy.decide` |
| `orderbook.from_snapshot` | L7 · LIVE | L9 | `l07-build-stable-boundary` | `exchange.book.OrderBook.from_snapshot` |
| `orderbook.depth` | L7 · REQUIRED | — | `l07-build-stable-boundary` | `exchange.book.OrderBook.depth` |
| `orderbook.microprice` | L7 · LIVE | — | `l07-build-stable-boundary` | `exchange.book.OrderBook.microprice` |
| `orderbook.reduce` | L8 · LIVE | — | `l08-explain-atomicity` | `exchange.book.OrderBook.reduce` |
| `orderbook.add_limit` | L8 · REQUIRED | — | `l08-compare-order-policies` | `exchange.book.OrderBook.add_limit` |
| `side.opposite` | L8 · REQUIRED | — | `l08-compare-order-policies` | `exchange.orders.Side.opposite` |
| `matching.process` | L8 · LIVE | L9, L15 | `l08-explain-atomicity`, `l15-integrate-course` | `exchange.matching.MatchingEngine.process` |
| `matching.constructor` | L8 · LIVE | L9 | `l08-explain-atomicity` | `exchange.matching.MatchingEngine` |
| `market.constructor` | L9 · LIVE | — | `l09-compose-market` | `exchange.market.Market` |
| `market.from_csv` | L9 · REQUIRED | — | `l09-reset-lifecycle` | `exchange.market.Market.from_csv` |
| `market.sample` | L9 · REQUIRED | L10, L11, L12 | `l09-reset-lifecycle`, `l11-benchmark-strategy`, `l12-run-vwap-strategy` | `exchange.market.Market.sample` |
| `market.snapshots` | L9 · REQUIRED | L10 | `l09-reset-lifecycle` | `exchange.market.Market.snapshots` |
| `market.book` | L9 · LIVE | — | `l09-compose-market` | `exchange.market.Market.book` |
| `market.step` | L9 · LIVE | L10, L11 | `l09-compose-market`, `l09-run-time-loop` | `exchange.market.Market.step` |
| `market.submit` | L9 · LIVE | L10 | `l09-compose-market` | `exchange.market.Market.submit` |
| `market.timestamp` | L9 · REQUIRED | — | `l09-reset-lifecycle` | `exchange.market.Market.timestamp` |
| `market.reset` | L9 · REQUIRED | L10 | `l09-reset-lifecycle` | `exchange.market.Market.reset` |
| `strategy.type` | L10 · LIVE | — | `l10-map-toy-to-production` | `exchange.strategy.Strategy` |
| `strategy.on_start` | L10 · REQUIRED | — | `l10-read-lifecycle` | `exchange.strategy.Strategy.on_start` |
| `new_order.constructor` | L10 · LIVE | L11, L12, L13, L14 | `l10-separate-decision-execution`, `l11-benchmark-strategy`, `l12-run-vwap-strategy` | `exchange.strategy.NewOrder` |
| `cancel.constructor` | L10 · LIVE | — | `l10-separate-decision-execution` | `exchange.strategy.Cancel` |
| `action.type` | L10 · LIVE | — | `l10-separate-decision-execution` | `exchange.strategy.Action` |
| `strategy.on_book_update` | L10 · LIVE | L11, L12, L13, L14, L15 | `l10-map-toy-to-production`, `l10-separate-decision-execution`, `l12-run-vwap-strategy`, `l14-build-capstone`, `l15-integrate-course` | `exchange.strategy.Strategy.on_book_update` |
| `strategy.on_fill` | L10 · LIVE | L11, L13, L14 | `l10-close-feedback-loop`, `l14-build-capstone` | `exchange.strategy.Strategy.on_fill` |
| `strategy.on_end` | L10 · REQUIRED | — | `l10-read-lifecycle` | `exchange.strategy.Strategy.on_end` |
| `backtest.constructor` | L10 · LIVE | L11, L12 | `l10-separate-decision-execution`, `l11-benchmark-strategy`, `l12-run-vwap-strategy` | `exchange.backtest.Backtest` |
| `backtest.run` | L10 · LIVE | L11, L12, L15 | `l10-separate-decision-execution`, `l11-benchmark-strategy`, `l12-run-vwap-strategy`, `l15-integrate-course` | `exchange.backtest.Backtest.run` |
| `backtest_result.type` | L10 · LIVE | — | `l10-separate-decision-execution` | `exchange.backtest.BacktestResult` |
| `backtest_result.fills` | L10 · LIVE | L11, L12 | `l10-close-feedback-loop`, `l11-interpret-slippage`, `l12-run-vwap-strategy` | `exchange.backtest.BacktestResult.fills` |
| `backtest_result.equity_curve` | L10 · LIVE | L11 | `l10-separate-decision-execution` | `exchange.backtest.BacktestResult.equity_curve` |
| `backtest_result.final_position` | L10 · LIVE | L11 | `l10-separate-decision-execution`, `l11-track-inventory-risk` | `exchange.backtest.BacktestResult.final_position` |
| `backtest_result.final_equity` | L10 · LIVE | L11 | `l10-separate-decision-execution`, `l11-benchmark-strategy` | `exchange.backtest.BacktestResult.final_equity` |
| `backtest_result.n_steps` | L10 · LIVE | L11 | `l10-separate-decision-execution`, `l11-benchmark-strategy` | `exchange.backtest.BacktestResult.n_steps` |
| `backtest_result.n_fills` | L10 · LIVE | L11 | `l10-close-feedback-loop`, `l11-interpret-slippage` | `exchange.backtest.BacktestResult.n_fills` |
| `vwap_strategy.constructor` | L12 · LIVE | — | `l12-run-vwap-strategy` | `exchange.strategies.vwap.VWAPStrategy` |
| `market_maker.constructor` | L13 · LIVE | L14 | `l13-explain-liquidity-provision`, `l14-build-capstone` | `exchange.strategies.market_maker.MarketMaker` |
| `market_maker.inventory` | L13 · LIVE | L14 | `l13-control-inventory`, `l13-explain-liquidity-provision`, `l14-build-capstone`, `l14-interpret-reservation-price` | `exchange.strategies.market_maker.MarketMaker.inventory` |
| `market_maker.half_spread` | L13 · LIVE | L14 | `l13-explain-liquidity-provision`, `l14-build-capstone` | `exchange.strategies.market_maker.MarketMaker.half_spread` |
| `market_maker.inventory_skew` | L13 · LIVE | L14 | `l13-explain-liquidity-provision`, `l14-build-capstone` | `exchange.strategies.market_maker.MarketMaker.inventory_skew` |
| `market_maker.reservation_price` | L13 · LIVE | L14 | `l13-control-inventory` | `exchange.strategies.market_maker.MarketMaker.reservation_price` |
| `market_maker.quotes` | L13 · LIVE | L14 | `l13-explain-liquidity-provision`, `l14-build-capstone` | `exchange.strategies.market_maker.MarketMaker.quotes` |
| `mm_simulation.constructor` | L13 · LIVE | L14 | `l13-explain-liquidity-provision`, `l14-run-parameter-lab` | `exchange.simulation.MMSimulation` |
| `mm_simulation.run` | L13 · LIVE | L14 | `l13-explain-liquidity-provision`, `l14-run-parameter-lab` | `exchange.simulation.MMSimulation.run` |
| `sim_result.type` | L13 · LIVE | — | `l13-explain-liquidity-provision` | `exchange.simulation.SimResult` |
| `sim_result.final_pnl` | L13 · LIVE | L14 | `l13-explain-liquidity-provision`, `l14-run-parameter-lab` | `exchange.simulation.SimResult.final_pnl` |
| `sim_result.pnl` | L13 · REQUIRED | — | `l13-inspect-pnl-path` | `exchange.simulation.SimResult.pnl` |
| `sim_result.max_inventory` | L13 · LIVE | L14 | `l13-explain-liquidity-provision`, `l14-run-parameter-lab` | `exchange.simulation.SimResult.max_inventory` |
| `avellaneda_stoikov.constructor` | L14 · LIVE | — | `l14-interpret-reservation-price`, `l14-run-parameter-lab` | `exchange.strategies.avellaneda_stoikov.AvellanedaStoikov` |
| `avellaneda_stoikov.time` | L14 · LIVE | — | `l14-interpret-reservation-price` | `exchange.strategies.avellaneda_stoikov.AvellanedaStoikov.time` |
| `avellaneda_stoikov.reservation_price` | L14 · LIVE | — | `l14-interpret-reservation-price` | `exchange.strategies.avellaneda_stoikov.AvellanedaStoikov.reservation_price` |
| `avellaneda_stoikov.optimal_spread` | L14 · LIVE | — | `l14-interpret-optimal-spread` | `exchange.strategies.avellaneda_stoikov.AvellanedaStoikov.optimal_spread` |
| `avellaneda_stoikov.quotes` | L14 · LIVE | — | `l14-run-parameter-lab` | `exchange.strategies.avellaneda_stoikov.AvellanedaStoikov.quotes` |

## Notación

| Notación estable | Primera introducción | Reutilización | Assessment |
|---|---|---|---|
| `notation.spread` | L1 · LIVE | L2, L5, L7, L11, L13 | `l01-model-market-data` |
| `notation.mid` | L1 · LIVE | L2, L5, L7, L8 | `l01-model-market-data` |
| `notation.imbalance` | L2 · LIVE | L6, L7 | `l02-read-functional-book` |
| `notation.cash_flow` | L4 · LIVE | L5 | `l04-interpret-cash-flow` |
| `notation.equity` | L5 · LIVE | L11, L13 | `l05-account-for-fills`, `l13-inspect-pnl-path` |
| `notation.slippage_signed` | L11 · LIVE | L12, L15 | `l11-interpret-slippage`, `l15-integrate-course` |
| `notation.twap` | L12 · LIVE | — | `l12-compare-schedules` |
| `notation.vwap` | L12 · LIVE | L15 | `l12-compare-schedules`, `l15-integrate-course` |
| `notation.inventory` | L13 · LIVE | L14 | `l13-control-inventory` |
| `notation.heuristic_reservation` | L13 · LIVE | L14 | `l13-control-inventory` |
| `notation.cara_utility` | L13 · LIVE | L14 | `l13-prepare-risk-and-fills`, `l14-interpret-reservation-price` |
| `notation.fill_intensity` | L13 · LIVE | L14 | `l13-prepare-risk-and-fills`, `l14-interpret-optimal-spread` |
| `notation.as_reservation_price` | L14 · LIVE | L15 | `l14-interpret-reservation-price`, `l15-integrate-course` |
| `notation.as_optimal_spread` | L14 · LIVE | L15 | `l14-interpret-optimal-spread`, `l15-integrate-course` |

## Objetivos de assessment

El blueprint conserva únicamente trazabilidad y distribución; no contiene enunciados ni soluciones.

| Lesson | Objetivo | Ruta | Evaluable | Distribución declarada |
|---|---|---|---|---|
| L1 | `l01-explain-execution` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L1 | `l01-model-market-data` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L1 | `l01-turn-data-into-decision` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L2 | `l02-extract-functions` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L2 | `l02-read-functional-book` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L2 | `l02-read-sorting-tools` | REQUIRED | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L3 | `l03-reuse-module` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L3 | `l03-handle-domain-errors` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L3 | `l03-separate-import-and-execution` | REQUIRED | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L4 | `l04-build-domain-objects` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L4 | `l04-read-canonical-constructors` | REQUIRED | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L4 | `l04-interpret-cash-flow` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L5 | `l05-compose-book` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L5 | `l05-account-for-fills` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L5 | `l05-protect-invariants` | REQUIRED | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L6 | `l06-build-strategy-family` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L6 | `l06-explain-polymorphism` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L6 | `l06-enforce-contract` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L6 | `l06-initialize-subclasses` | REQUIRED | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L7 | `l07-build-book` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L7 | `l07-read-metrics` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L7 | `l07-build-stable-boundary` | REQUIRED | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L8 | `l08-explain-atomicity` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L8 | `l08-compare-order-policies` | REQUIRED | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L8 | `l08-connect-size-to-impact` | REQUIRED | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L9 | `l09-compose-market` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L9 | `l09-run-time-loop` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L9 | `l09-reset-lifecycle` | REQUIRED | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L9 | `l09-track-equity-over-time` | REQUIRED | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L10 | `l10-map-toy-to-production` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L10 | `l10-separate-decision-execution` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L10 | `l10-close-feedback-loop` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L10 | `l10-read-lifecycle` | REQUIRED | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L11 | `l11-benchmark-strategy` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L11 | `l11-interpret-slippage` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L11 | `l11-track-inventory-risk` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L12 | `l12-compare-schedules` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L12 | `l12-run-vwap-strategy` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L13 | `l13-explain-liquidity-provision` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L13 | `l13-control-inventory` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L13 | `l13-prepare-risk-and-fills` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L13 | `l13-inspect-pnl-path` | REQUIRED | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L14 | `l14-interpret-reservation-price` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L14 | `l14-interpret-optimal-spread` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L14 | `l14-run-parameter-lab` | LIVE | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L14 | `l14-build-capstone` | REQUIRED | sí | code_reading=3, conceptual=2, debugging=2, financial_interpretation=2, integration=1 |
| L15 | `l15-integrate-course` | REQUIRED | sí | code_reading=8, conceptual=8, debugging=8, financial_interpretation=8, integration=8 |

## Fuente y mantenimiento

Las introducciones, reutilizaciones y recalls se derivan de `pedagogy/lessons/NN.yml`; las rutas de práctica proceden de `pedagogy/exercise_routes.yml`; la trazabilidad evaluativa procede de `pedagogy/assessment_blueprint.yml`. CI regenera ambos informes y falla si existe drift.
