"""Specs de las lecciones de fundamentos (L1-L4).

Cada ejercicio: statement, (given), starter, validator (assert), solution.
Solo stdlib — cero dependencias, beginner-friendly.
"""

LESSONS = []

# ---------------------------------------------------------------------------
# L1 — Python I — El modelo de datos
# ---------------------------------------------------------------------------
LESSONS.append({
    "n": 1, "slug": "01-python-i-data-model",
    "title": "Python I — El modelo de datos",
    "piece": "order y snapshot como dicts",
    "objective": "De cero a entender que Python es texto que se ejecuta, y usarlo para guardar el primer dato de mercado: un snapshot y una orden.",
    "frase": "Un algoritmo es siempre lo mismo: dato <span class='dot'>→</span> cálculo <span class='dot'>→</span> decisión.",
    "concepts": [
        ("Tu código es texto que un programa ejecuta",
         "Un archivo .py no es magia: es texto. Python lo lee de arriba abajo y produce un resultado. Si algo falla, el error te dice exactamente dónde mirar — es información, no un castigo.",
         "bid = 99950\nask = 100000\nspread = ask - bid   # 50\nmid = (bid + ask) / 2  # 99975"),
        ("Datos con nombre: variables, listas y diccionarios",
         "Una variable guarda un valor. Una lista agrupa varios. Un diccionario agrupa piezas con significado — justo lo que es una orden: side, price, size.",
         "order = {\n  'symbol': 'BTCUSDT',\n  'side': 'buy',\n  'price': 99980,\n  'size': 0.10,\n}"),
        ("Del dato a la decisión: for e if",
         "Un for repite trabajo sobre muchos datos; un if convierte una observación en una decisión. Con esas dos piezas ya puedes recorrer un libro de órdenes y reaccionar.",
         "if spread <= 50:\n    market_state = 'tight'\nelse:\n    market_state = 'wide'"),
    ],
    "build": [
        {"title": "1. Enciende el mercado", "practice": "variables",
         "statement": "Guarda el snapshot en variables: `symbol = 'BTCUSDT'`, `bid = 99950`, `ask = 100000`.",
         "hint": "Tres asignaciones simples.",
         "starter": "# Escribe aquí\n",
         "validator": "assert symbol == 'BTCUSDT', 'symbol debe ser BTCUSDT'\nassert bid == 99950 and ask == 100000\nprint('ok')",
         "solution": "symbol = 'BTCUSDT'\nbid = 99950\nask = 100000"},
        {"title": "2. Spread y mid", "practice": "operaciones y tipos",
         "statement": "Calcula `spread = ask - bid` y `mid = (bid + ask) / 2`. Fíjate: la resta da entero; la división `/` siempre da decimal (`float`).",
         "given": "bid = 99950\nask = 100000\n",
         "starter": "# Escribe aquí\n",
         "validator": "assert spread == 50, 'spread debe ser 50'\nassert mid == 99975.0, 'mid debe ser 99975.0'\nassert isinstance(mid, float), 'mid es float: la division / siempre da float'\nprint('ok')",
         "solution": "spread = ask - bid\nmid = (bid + ask) / 2"},
        {"title": "3. Una lista de mids", "practice": "listas e indexing",
         "statement": "Dada `mids`, guarda el primero (`first_mid`), el último (`last_mid`) y cuántos hay (`n_mids`).",
         "hint": "`mids[0]` es el primero, `mids[-1]` el último, `len(mids)` cuántos hay.",
         "given": "mids = [99975, 99980, 99970, 99990, 100005]\n",
         "starter": "first_mid = None\nlast_mid = None\nn_mids = None\n",
         "validator": "assert first_mid == 99975\nassert last_mid == 100005\nassert n_mids == 5\nprint('ok')",
         "solution": "first_mid = mids[0]\nlast_mid = mids[-1]\nn_mids = len(mids)"},
        {"title": "4. Media con un bucle", "practice": "for y acumuladores",
         "statement": "Recorre `mids` con un `for`, ve sumando en `total` y calcula `average`.",
         "hint": "Empieza con `total = 0`; dentro del bucle, `total = total + m`.",
         "given": "mids = [99975, 99980, 99970, 99990, 100005]\n",
         "starter": "total = 0\n# recorre mids y calcula average\n",
         "validator": "assert abs(average - 99984.0) < 1e-9, 'la media debe ser 99984.0'\nprint('ok')",
         "solution": "total = 0\nfor m in mids:\n    total = total + m\naverage = total / len(mids)"},
        {"title": "5. Una orden, y cómo leerla", "practice": "diccionarios: crear y acceder",
         "statement": "Crea `order` con `symbol`, `side='buy'`, `price=99950`, `size=0.10`. Luego lee `order_side` (su lado) y calcula `order_notional` (precio × tamaño).",
         "hint": "Accedes a un campo con `order['campo']`.",
         "starter": "order = {\n    # completa\n}\norder_side = None\norder_notional = None\n",
         "validator": "assert isinstance(order, dict)\nfor k in ('symbol','side','price','size'):\n    assert k in order, f'falta el campo {k}'\nassert order_side == 'buy'\nassert abs(order_notional - 9995.0) < 1e-9, 'price * size = 9995.0'\nprint('ok')",
         "solution": "order = {'symbol': 'BTCUSDT', 'side': 'buy', 'price': 99950, 'size': 0.10}\norder_side = order['side']\norder_notional = order['price'] * order['size']"},
        {"title": "6. Clasifica el mercado", "practice": "if / elif / else",
         "statement": "Según el `spread`, guarda `market_state`: `'tight'` si es ≤ 20, `'normal'` si es ≤ 60, y `'wide'` en cualquier otro caso.",
         "hint": "Tres ramas: `if`, `elif`, `else`.",
         "given": "spread = 50\n",
         "starter": "# Escribe el if / elif / else\n",
         "validator": "assert market_state == 'normal', 'con spread 50 el mercado es normal'\nprint('ok ->', market_state)",
         "solution": "if spread <= 20:\n    market_state = 'tight'\nelif spread <= 60:\n    market_state = 'normal'\nelse:\n    market_state = 'wide'"},
        {"title": "7. Tu primer algoritmo", "practice": "dato → cálculo → decisión",
         "statement": "Júntalo todo. Desde `bid`/`ask` calcula `spread`, `mid` y `market_state`, y decide: `action = 'buy'` si `mid <= 100000`, si no `'hold'`. El spread es el *estado*; el mid, tu *señal*.",
         "hint": "Reutiliza lo de los ejercicios 2 y 6.",
         "given": "bid = 99950\nask = 100000\n",
         "starter": "# spread, mid, market_state y action\n",
         "validator": "assert spread == 50 and mid == 99975.0\nassert market_state == 'normal'\nassert action == 'buy'\nprint('ok  decision ->', action)",
         "solution": "spread = ask - bid\nmid = (bid + ask) / 2\n\nif spread <= 20:\n    market_state = 'tight'\nelif spread <= 60:\n    market_state = 'normal'\nelse:\n    market_state = 'wide'\n\nif mid <= 100000:\n    action = 'buy'\nelse:\n    action = 'hold'"},
    ],
    "aux": [
        {"section": "Gimnasio · Bloque 1 — Números y operadores del mercado",
         "blurb": "Los operadores que usarás cada día: división entera, resto, potencias, redondeos y agregados."},
        {"title": "A1. Ticks enteros", "practice": "// y % (división entera y resto)",
         "statement": "El spread mide 55 y el tick 10. ¿Cuántos ticks *enteros* caben (`ticks`) y qué resto queda (`resto`)?",
         "hint": "`//` da el cociente entero; `%` el resto.",
         "given": "spread = 55\ntick_size = 10\n",
         "starter": "ticks = None\nresto = None\n",
         "validator": "assert ticks == 5, 'en 55 caben 5 ticks de 10'\nassert resto == 5, 'y sobran 5'\nprint('ok ->', ticks, 'ticks y resto', resto)",
         "solution": "ticks = spread // tick_size\nresto = spread % tick_size"},
        {"title": "A2. Redondea como un exchange", "practice": "round",
         "statement": "Guarda `price_2dec` = `raw_price` redondeado a 2 decimales, y `size_whole` = `3.7` redondeado al entero más cercano.",
         "given": "raw_price = 99975.4567\n",
         "starter": "price_2dec = None\nsize_whole = None\n",
         "validator": "assert price_2dec == 99975.46, 'round(x, 2) redondea a 2 decimales'\nassert size_whole == 4\nprint('ok')",
         "solution": "price_2dec = round(raw_price, 2)\nsize_whole = round(3.7)"},
        {"title": "A3. PnL con signo", "practice": "abs y signo",
         "statement": "Compraste a `entry` y vendiste a `exit_price`, tamaño 2. Calcula `pnl = (exit_price - entry) * size` y su magnitud `pnl_abs`.",
         "given": "entry = 99950\nexit_price = 99920\nsize = 2\n",
         "starter": "pnl = None\npnl_abs = None\n",
         "validator": "assert pnl == -60, 'vendiste mas barato: el PnL es negativo'\nassert pnl_abs == 60\nprint('ok -> perdiste', pnl_abs)",
         "solution": "pnl = (exit_price - entry) * size\npnl_abs = abs(pnl)"},
        {"title": "A4. Interés compuesto", "practice": "** (potencias)",
         "statement": "Si BTC subiera un 1% al día durante 10 días, el multiplicador total es `(1 + 0.01) ** 10`. Guárdalo en `growth`.",
         "starter": "growth = None\n",
         "validator": "assert round(growth, 4) == 1.1046, 'mas que 1.10: el interes compuesto compone'\nprint('ok ->', round(growth, 4))",
         "solution": "growth = (1 + 0.01) ** 10"},
        {"title": "A5. Agregados de un vistazo", "practice": "min / max / sum",
         "statement": "De `mids`, guarda `lowest`, `highest` y `total` usando `min`, `max` y `sum` (sin bucles).",
         "given": "mids = [99975, 99980, 99970, 99990, 100005]\n",
         "starter": "lowest = None\nhighest = None\ntotal = None\n",
         "validator": "assert lowest == 99970 and highest == 100005\nassert total == 499920\nprint('ok')",
         "solution": "lowest = min(mids)\nhighest = max(mids)\ntotal = sum(mids)"},

        {"section": "Gimnasio · Bloque 2 — Strings: símbolos y tickets",
         "blurb": "Los datos de mercado llegan como texto: aprende a trocearlo, limpiarlo y formatearlo."},
        {"title": "A6. Base y quote", "practice": "slicing de strings",
         "statement": "De `symbol = 'BTCUSDT'` saca `base` (3 primeras letras) y `quote` (el resto) con slicing.",
         "hint": "Un string se trocea igual que una lista: `symbol[:3]`.",
         "given": "symbol = 'BTCUSDT'\n",
         "starter": "base = None\nquote = None\n",
         "validator": "assert base == 'BTC' and quote == 'USDT'\nprint('ok ->', base, '/', quote)",
         "solution": "base = symbol[:3]\nquote = symbol[3:]"},
        {"title": "A7. Limpia el input", "practice": "strip / upper / endswith",
         "statement": "`raw` llega sucio de un formulario. Guarda `clean` (sin espacios y en mayúsculas) y `is_usdt` (si termina en `'USDT'`).",
         "given": "raw = '  btcusdt '\n",
         "starter": "clean = None\nis_usdt = None\n",
         "validator": "assert clean == 'BTCUSDT', 'strip() quita espacios, upper() sube a mayusculas'\nassert is_usdt is True\nprint('ok')",
         "solution": "clean = raw.strip().upper()\nis_usdt = clean.endswith('USDT')"},
        {"title": "A8. Parsea una quote", "practice": "split + int",
         "statement": "El feed manda `'99950/100000'`. Sepáralo y guarda `bid` y `ask` como **enteros**.",
         "hint": "`.split('/')` devuelve una lista de trozos; `int(...)` convierte.",
         "given": "quote_str = '99950/100000'\n",
         "starter": "bid = None\nask = None\n",
         "validator": "assert bid == 99950 and ask == 100000\nassert isinstance(bid, int), 'convierte con int(): el feed manda texto'\nprint('ok')",
         "solution": "parts = quote_str.split('/')\nbid = int(parts[0])\nask = int(parts[1])"},
        {"title": "A9. El ticket perfecto", "practice": "f-strings con formato",
         "statement": "Construye `ticket` con una f-string: `'BUY 0.5 BTCUSDT @ 99950.00'` (lado en mayúsculas, precio con 2 decimales).",
         "hint": "`f\"{side.upper()} ... {price:.2f}\"`.",
         "given": "side = 'buy'\nsize = 0.5\nsymbol = 'BTCUSDT'\nprice = 99950\n",
         "starter": "ticket = None\n",
         "validator": "assert ticket == 'BUY 0.5 BTCUSDT @ 99950.00'\nprint('ok ->', ticket)",
         "solution": "ticket = f\"{side.upper()} {size} {symbol} @ {price:.2f}\""},

        {"section": "Gimnasio · Bloque 3 — Booleanos: condiciones de riesgo",
         "blurb": "Toda decisión de trading es al final un True/False. Componlos con and, or y not."},
        {"title": "A10. Dentro de banda", "practice": "comparaciones encadenadas",
         "statement": "Guarda `in_band` (si `mid` está entre `low` y `high`, ambos incluidos) y `outside` (lo contrario, usando `not`).",
         "given": "mid = 99975\nlow = 99900\nhigh = 100000\n",
         "starter": "in_band = None\noutside = None\n",
         "validator": "assert in_band is True and outside is False\nprint('ok')",
         "solution": "in_band = low <= mid <= high\noutside = not in_band"},
        {"title": "A11. ¿Puedo operar?", "practice": "and",
         "statement": "Solo operas si tienes caja, el mercado está abierto **y** el riesgo está OK. Calcula `can_trade`.",
         "given": "has_cash = True\nmarket_open = True\nrisk_ok = False\n",
         "starter": "can_trade = None\n",
         "validator": "assert can_trade is False, 'con risk_ok False no se opera: and exige que TODO sea True'\nprint('ok')",
         "solution": "can_trade = has_cash and market_open and risk_ok"},
        {"title": "A12. Señal y cautela", "practice": "and / or",
         "statement": "`signal` = spread estrecho (`< 20`) **y** imbalance alto (`> 0.6`). `caution` = spread ancho (`>= 60`) **o** imbalance flojo (`< 0.3`).",
         "given": "spread = 15\nimbalance = 0.7\n",
         "starter": "signal = None\ncaution = None\n",
         "validator": "assert signal is True\nassert caution is False\nprint('ok')",
         "solution": "signal = spread < 20 and imbalance > 0.6\ncaution = spread >= 60 or imbalance < 0.3"},

        {"section": "Gimnasio · Bloque 4 — Listas a fondo",
         "blurb": "La serie de precios es una lista. Trocéala, ordénala y pregúntale cosas."},
        {"title": "A13. Ventana de ticks", "practice": "slicing",
         "statement": "Guarda `last3` (los 3 últimos mids) y `first2` (los 2 primeros) con slicing.",
         "hint": "`mids[-3:]` y `mids[:2]`.",
         "given": "mids = [99975, 99980, 99970, 99990, 100005, 99995, 100010]\n",
         "starter": "last3 = None\nfirst2 = None\n",
         "validator": "assert last3 == [100005, 99995, 100010]\nassert first2 == [99975, 99980]\nprint('ok')",
         "solution": "last3 = mids[-3:]\nfirst2 = mids[:2]"},
        {"title": "A14. Llega un tick", "practice": "append",
         "statement": "Añade el tick `100020` al final de `mids` y guarda en `n` cuántos hay ahora.",
         "given": "mids = [99975, 99980, 99970, 99990]\n",
         "starter": "# anade el tick y cuenta\nn = None\n",
         "validator": "assert mids[-1] == 100020, 'append anade al final'\nassert n == 5\nprint('ok')",
         "solution": "mids.append(100020)\nn = len(mids)"},
        {"title": "A15. Deshaz el último", "practice": "pop",
         "statement": "El último precio de `queue` fue un error: sácalo con `pop()` y guárdalo en `removed`.",
         "given": "queue = [99950, 99960, 99970]\n",
         "starter": "removed = None\n",
         "validator": "assert removed == 99970\nassert queue == [99950, 99960], 'pop saca el elemento de la lista'\nprint('ok')",
         "solution": "removed = queue.pop()"},
        {"title": "A16. ¿Está el nivel?", "practice": "operador in",
         "statement": "Guarda `has_950` (¿está 99950 en `levels`?) y `has_million` (¿está 1000000?).",
         "given": "levels = [99950, 99940, 99930]\n",
         "starter": "has_950 = None\nhas_million = None\n",
         "validator": "assert has_950 is True and has_million is False\nprint('ok')",
         "solution": "has_950 = 99950 in levels\nhas_million = 1000000 in levels"},
        {"title": "A17. Ordena el lado bid", "practice": "sorted(reverse=True)",
         "statement": "Los bids se leen de mayor a menor. Guarda `bids_sorted` (descendente, sin tocar `bids`) y `best` (el primero).",
         "hint": "`sorted(..., reverse=True)` devuelve una lista nueva.",
         "given": "bids = [99930, 99950, 99940]\n",
         "starter": "bids_sorted = None\nbest = None\n",
         "validator": "assert bids_sorted == [99950, 99940, 99930]\nassert best == 99950\nassert bids == [99930, 99950, 99940], 'sorted no debe modificar la original'\nprint('ok')",
         "solution": "bids_sorted = sorted(bids, reverse=True)\nbest = bids_sorted[0]"},

        {"section": "Gimnasio · Bloque 5 — Diccionarios a fondo",
         "blurb": "Posiciones, comisiones, órdenes: en trading casi todo es un dict."},
        {"title": "A18. Lee con red", "practice": "get con default",
         "statement": "Guarda `btc_pos` y `eth_pos` usando `.get(clave, 0)` — ETH no existe todavía y no debe explotar.",
         "given": "positions = {'BTCUSDT': 0.5}\n",
         "starter": "btc_pos = None\neth_pos = None\n",
         "validator": "assert btc_pos == 0.5\nassert eth_pos == 0, 'get con default evita el KeyError'\nprint('ok')",
         "solution": "btc_pos = positions.get('BTCUSDT', 0)\neth_pos = positions.get('ETHUSDT', 0)"},
        {"title": "A19. Actualiza la posición", "practice": "escribir en un dict",
         "statement": "Compras 0.2 BTC más y abres 1.0 ETH. Actualiza `positions` (BTC pasa a 0.7, ETH aparece con 1.0).",
         "given": "positions = {'BTCUSDT': 0.5}\n",
         "starter": "# actualiza BTC y crea ETH\n",
         "validator": "assert abs(positions['BTCUSDT'] - 0.7) < 1e-9\nassert positions['ETHUSDT'] == 1.0\nprint('ok')",
         "solution": "positions['BTCUSDT'] = positions['BTCUSDT'] + 0.2\npositions['ETHUSDT'] = 1.0"},
        {"title": "A20. ¿Tiene el campo?", "practice": "in sobre dicts",
         "statement": "Guarda `has_price` y `has_venue` comprobando con `in` si esas claves existen en `order`.",
         "given": "order = {'symbol': 'BTCUSDT', 'side': 'buy', 'price': 99950}\n",
         "starter": "has_price = None\nhas_venue = None\n",
         "validator": "assert has_price is True and has_venue is False\nprint('ok')",
         "solution": "has_price = 'price' in order\nhas_venue = 'venue' in order"},
        {"title": "A21. Radiografía de comisiones", "practice": "values / len / sum",
         "statement": "Guarda `n_venues` (cuántos exchanges hay) y `total_fees` (la suma de todas las comisiones).",
         "given": "fees = {'binance': 10, 'kraken': 26, 'coinbase': 60}\n",
         "starter": "n_venues = None\ntotal_fees = None\n",
         "validator": "assert n_venues == 3\nassert total_fees == 96, 'sum(fees.values()) suma los valores'\nprint('ok')",
         "solution": "n_venues = len(fees)\ntotal_fees = sum(fees.values())"},

        {"section": "Gimnasio · Bloque 6 — Bucles con oficio",
         "blurb": "El for + un if dentro: el patrón que resuelve el 80% de los problemas de datos."},
        {"title": "A22. Ticks alcistas", "practice": "range(1, n) e índices",
         "statement": "Cuenta en `ups` cuántos ticks subieron respecto al anterior. Compara `mids[i]` con `mids[i-1]` usando `range(1, len(mids))`.",
         "given": "mids = [99975, 99980, 99970, 99990, 100005, 99995, 100010]\n",
         "starter": "ups = 0\n# recorre con range y compara con el anterior\n",
         "validator": "assert ups == 4, 'suben 4 de los 6 saltos'\nprint('ok ->', ups, 'ticks alcistas')",
         "solution": "ups = 0\nfor i in range(1, len(mids)):\n    if mids[i] > mids[i-1]:\n        ups = ups + 1"},
        {"title": "A23. Censo del libro", "practice": "contador con condición",
         "statement": "Cuenta `n_buys` y `n_sells` recorriendo `book` una sola vez.",
         "given": "book = [\n    {'side':'buy','price':99980,'size':0.1}, {'side':'buy','price':99990,'size':0.2},\n    {'side':'sell','price':100010,'size':0.15}, {'side':'sell','price':100005,'size':0.1},\n    {'side':'buy','price':99970,'size':0.3},\n]\n",
         "starter": "n_buys = 0\nn_sells = 0\n",
         "validator": "assert n_buys == 3 and n_sells == 2\nprint('ok')",
         "solution": "n_buys = 0\nn_sells = 0\nfor o in book:\n    if o['side'] == 'buy':\n        n_buys = n_buys + 1\n    else:\n        n_sells = n_sells + 1"},
        {"title": "A24. max() a mano", "practice": "el patrón del campeón",
         "statement": "Encuentra `highest` recorriendo `mids` **sin usar `max()`**: arranca con el primero y ve quedándote con el mayor.",
         "given": "mids = [99975, 99980, 99970, 99990, 100005, 99995]\n",
         "starter": "highest = mids[0]\n# recorre y compara\n",
         "validator": "assert highest == 100005\nprint('ok -> acabas de reinventar max()')",
         "solution": "highest = mids[0]\nfor m in mids:\n    if m > highest:\n        highest = m"},

        {"section": "Gimnasio · Bloque 7 — Decisiones con más ramas",
         "blurb": "if/elif/else con la complejidad de verdad: umbrales escalonados y decisiones que alimentan un cálculo."},
        {"title": "A25. Semáforo de presión", "practice": "if / elif / else",
         "statement": "Clasifica `pressure`: `'buy_pressure'` si imbalance > 0.65, `'sell_pressure'` si < 0.35, `'balanced'` en medio.",
         "given": "imbalance = 0.72\n",
         "starter": "# escribe el if / elif / else\n",
         "validator": "assert pressure == 'buy_pressure'\nprint('ok ->', pressure)",
         "solution": "if imbalance > 0.65:\n    pressure = 'buy_pressure'\nelif imbalance < 0.35:\n    pressure = 'sell_pressure'\nelse:\n    pressure = 'balanced'"},
        {"title": "A26. Tarifa por tramos", "practice": "umbrales escalonados + cálculo",
         "statement": "Comisión por tramos: <10k → 10 bps; <100k → 8; <1M → 5; si no → 3. Guarda `fee_bps` y calcula `fee = notional * fee_bps / 10000`.",
         "given": "notional = 250000\n",
         "starter": "fee_bps = None\n# ... y calcula fee\n",
         "validator": "assert fee_bps == 5, 'con 250k caes en el tramo <1M'\nassert abs(fee - 125.0) < 1e-9\nprint('ok -> pagas', fee)",
         "solution": "if notional < 10000:\n    fee_bps = 10\nelif notional < 100000:\n    fee_bps = 8\nelif notional < 1000000:\n    fee_bps = 5\nelse:\n    fee_bps = 3\nfee = notional * fee_bps / 10000"},

        {"section": "Para curiosos — internals y el puente a la clase 2",
         "blurb": "Un vistazo a lo que viene (funciones) y a lo que hay debajo (1s, 0s y bytecode)."},
        {"title": "A27. Función nocional", "practice": "funciones",
         "statement": "Escribe `compute_notional(price, size)` que devuelva `price * size`.",
         "starter": "def compute_notional(price, size):\n    pass\n",
         "validator": "assert abs(compute_notional(100, 0.5) - 50) < 1e-9\nprint('ok')",
         "solution": "def compute_notional(price, size):\n    return price * size"},
        {"title": "A28. Mejor bid y mejor ask", "practice": "max / min con filtro",
         "statement": "De `book` (lista de órdenes), saca `best_bid` (precio de compra más alto) y `best_ask` (precio de venta más bajo).",
         "hint": "Recorre el libro con un for y quédate con el mejor de cada lado.",
         "given": "book = [\n    {'side':'buy','price':99980,'size':0.1}, {'side':'buy','price':99990,'size':0.2},\n    {'side':'sell','price':100010,'size':0.15}, {'side':'sell','price':100005,'size':0.1},\n]\n",
         "starter": "best_bid = None\nbest_ask = None\n",
         "validator": "assert best_bid == 99990, 'best_bid debe ser 99990'\nassert best_ask == 100005, 'best_ask debe ser 100005'\nprint('ok')",
         "solution": "best_bid = None\nbest_ask = None\nfor o in book:\n    if o['side'] == 'buy' and (best_bid is None or o['price'] > best_bid):\n        best_bid = o['price']\n    if o['side'] == 'sell' and (best_ask is None or o['price'] < best_ask):\n        best_ask = o['price']\n# spoiler L2: max(o['price'] for o in book if o['side']=='buy')"},
        {"title": "A29. El problema que viene: dos activos", "practice": "reflexión → POO",
         "statement": "Imagina que sigues `buy_volume` y `sell_volume` para CADA activo por separado. Con `activos = ['BTCUSDT', 'ETHUSDT']`, ¿cuántas variables de volumen necesitas? Guárdalo en `n_vars`.",
         "hint": "2 variables (buy y sell) por cada activo.",
         "given": "activos = ['BTCUSDT', 'ETHUSDT']\n",
         "starter": "n_vars = None\n",
         "validator": "assert n_vars == 4, '2 por activo x 2 activos = 4 (y con 10 activos, 20...)'\nprint('ok -> anadir activos duplica variables. En la clase 2-3 esto lo resuelven las CLASES.')",
         "solution": "n_vars = len(activos) * 2"},
        {"title": "A30. El alfabeto de la máquina", "practice": "ord y bin (texto → 1s y 0s)",
         "statement": "Como viste en la presentación, cada carácter es un número y ese número son bits. Guarda `code_A = ord('A')` y `bits_A = bin(ord('A'))`.",
         "hint": "`ord` da el código del carácter; `bin` lo pasa a binario.",
         "starter": "code_A = None\nbits_A = None\n",
         "validator": "assert code_A == 65, \"ord('A') es 65\"\nassert bits_A == '0b1000001', 'bin(65) es 0b1000001'\nprint('ok  A ->', code_A, '->', bits_A)",
         "solution": "code_A = ord('A')\nbits_A = bin(ord('A'))"},
        {"title": "A31. Ver el bytecode con dis", "practice": "compilar texto a bytecode",
         "statement": "Python compila tu texto a bytecode. Compila `'mid = (bid + ask) / 2'` y captura su desensamblado en `bytecode` (string). Comprueba que contiene instrucciones de la VM.",
         "hint": "`dis.dis(compile(src, '<x>', 'exec'), file=buf)` escribe el bytecode en un buffer.",
         "given": "import dis, io\nsrc = 'mid = (bid + ask) / 2'\n",
         "starter": "bytecode = None\n",
         "validator": "assert isinstance(bytecode, str) and 'LOAD_NAME' in bytecode, 'debe contener instrucciones como LOAD_NAME'\nprint('ok — esto es lo que ejecuta la máquina virtual de Python')",
         "solution": "buf = io.StringIO()\ndis.dis(compile(src, '<x>', 'exec'), file=buf)\nbytecode = buf.getvalue()\nprint(bytecode)"},
    ],
    "script_name": "trading_snapshot.py",
    "script": '''# Clase 1 - Tu primer programa en un archivo .py
# Lo mismo que construiste en el notebook (ej. 1 a 7), ordenado en funciones.
# Ejecuta desde la terminal:  python trading_snapshot.py


def compute_spread(bid, ask):          # ej. 2
    return ask - bid


def compute_mid(bid, ask):             # ej. 2
    return (bid + ask) / 2


def average(values):                   # ej. 3 y 4: lista + for
    total = 0
    for v in values:
        total = total + v
    return total / len(values)


def order_notional(order):             # ej. 5: acceder a un dict
    return order["price"] * order["size"]


def classify_market(spread):           # ej. 6: if / elif / else
    if spread <= 20:
        return "tight"
    elif spread <= 60:
        return "normal"
    return "wide"


def decide(mid):                       # ej. 7: la decisión sobre el mid
    if mid <= 100000:
        return "buy"
    return "hold"


def main():                            # ej. 7: dato -> calculo -> decision
    symbol = "BTCUSDT"
    bid, ask = 99950, 100000

    spread = compute_spread(bid, ask)
    mid = compute_mid(bid, ask)

    mids = [99975, 99980, 99970, 99990, 100005]
    order = {"symbol": symbol, "side": "buy", "price": 99950, "size": 0.10}

    print("symbol:", symbol)
    print("spread:", spread)
    print("mid:", mid)
    print("media de mids:", average(mids))
    print("nocional de la orden:", order_notional(order))
    print("estado:", classify_market(spread))
    print("decision:", decide(mid))


if __name__ == "__main__":
    main()
''',
})

# ---------------------------------------------------------------------------
# L2 — Python II — El libro funcional
# ---------------------------------------------------------------------------
LESSONS.append({
    "n": 2, "slug": "02-python-ii-functional-book",
    "title": "Python II — El libro funcional",
    "piece": "funciones add_order / cancel / imbalance",
    "objective": "Pasar de scripts sueltos a funciones que construyen y modifican un libro de órdenes. Al final verás por qué tantas funciones compartiendo el mismo libro piden ser un objeto.",
    "frase": "Funciones sueltas que comparten el mismo estado están pidiendo a gritos ser un objeto.",
    "concepts": [
        ("Funciones que construyen datos",
         "Una función no solo calcula números: puede construir y devolver estructuras. `make_order(...)` te da un dict listo, sin repetir las llaves cada vez.",
         "def make_order(symbol, side, price, size):\n    return {'symbol': symbol, 'side': side,\n            'price': price, 'size': size}"),
        ("Un libro es una lista de órdenes",
         "Añadir y cancelar son funciones que reciben el libro y lo devuelven cambiado. Recorrer niveles te da spread, mid e imbalance.",
         "def add_order(book, order):\n    book.append(order)\n    return book"),
        ("El dolor que viene: estado compartido",
         "add_order, cancel, imbalance... todas reciben `book` como primer argumento y lo manosean. Eso es la señal de que `book` quiere ser un objeto con métodos. Eso es la clase 3.",
         "# book + book + book en cada función...\n# -> next class: book.add(order)"),
    ],
    "build": [
        {"title": "1. Tu fábrica de órdenes", "practice": "funciones que devuelven datos",
         "statement": "Escribe `make_order(symbol, side, price, size)` que **devuelva** el dict de la orden. Una función-fábrica: la llamas con distintos datos y te construye la orden.",
         "hint": "El cuerpo es un solo `return` con el dict.",
         "starter": "def make_order(symbol, side, price, size):\n    pass\n",
         "validator": "o = make_order('BTCUSDT','buy',99950,0.10)\nassert o == {'symbol':'BTCUSDT','side':'buy','price':99950,'size':0.10}\nprint('ok')",
         "solution": "def make_order(symbol, side, price, size):\n    return {'symbol': symbol, 'side': side, 'price': price, 'size': size}"},
        {"title": "2. Añade al libro", "practice": "listas: append",
         "statement": "Escribe `add_order(book, order)` que añada la orden al libro y lo **devuelva**.",
         "hint": "`book.append(order)` y luego `return book`.",
         "starter": "def add_order(book, order):\n    pass\n",
         "validator": "b = add_order([], {'side':'buy'})\nassert b == [{'side':'buy'}]\nprint('ok')",
         "solution": "def add_order(book, order):\n    book.append(order)\n    return book"},
        {"title": "3. Cancela una orden", "practice": "filtrar (comprensión de lista)",
         "statement": "Escribe `cancel_order(book, order_id)` que devuelva un libro **nuevo** sin la orden cuyo `id` coincide.",
         "hint": "Quédate solo con las órdenes cuyo `id` es distinto.",
         "given": "book = [{'id':1,'side':'buy'},{'id':2,'side':'sell'}]\n",
         "starter": "def cancel_order(book, order_id):\n    pass\n",
         "validator": "out = cancel_order(book, 1)\nassert out == [{'id':2,'side':'sell'}]\nprint('ok')",
         "solution": "def cancel_order(book, order_id):\n    return [o for o in book if o['id'] != order_id]"},
        {"title": "4. Mejor bid y mejor ask", "practice": "max / min con filtro",
         "statement": "Escribe `best_bid(book)` (precio de compra más **alto**) y `best_ask(book)` (precio de venta más **bajo**).",
         "given": "book = [{'side':'buy','price':99980},{'side':'sell','price':100010},{'side':'buy','price':99990}]\n",
         "starter": "def best_bid(book):\n    pass\n\ndef best_ask(book):\n    pass\n",
         "validator": "assert best_bid(book) == 99990\nassert best_ask(book) == 100010\nprint('ok')",
         "solution": "def best_bid(book):\n    return max(o['price'] for o in book if o['side']=='buy')\n\ndef best_ask(book):\n    return min(o['price'] for o in book if o['side']=='sell')"},
        {"title": "5. Imbalance del libro", "practice": "presión compra/venta",
         "statement": "Escribe `imbalance(book)` = (vol_compra − vol_venta) / (vol_compra + vol_venta), en [−1, 1]. Cerca de +1 = empuja a comprar.",
         "given": "book = [{'side':'buy','size':3},{'side':'sell','size':1}]\n",
         "starter": "def imbalance(book):\n    pass\n",
         "validator": "assert abs(imbalance(book) - 0.5) < 1e-9, 'imbalance debe ser 0.5'\nprint('ok')",
         "solution": "def imbalance(book):\n    b = sum(o['size'] for o in book if o['side']=='buy')\n    s = sum(o['size'] for o in book if o['side']=='sell')\n    return (b - s) / (b + s)"},
        {"title": "6. Spread y mid, componiendo funciones", "practice": "componer funciones",
         "statement": "Usando `best_bid` y `best_ask` ya escritas, define `spread(book)` y `mid(book)`. Una función puede llamar a otras.",
         "given": "def best_bid(book):\n    return max(o['price'] for o in book if o['side']=='buy')\ndef best_ask(book):\n    return min(o['price'] for o in book if o['side']=='sell')\nbook = [{'side':'buy','price':100},{'side':'sell','price':102}]\n",
         "starter": "def spread(book):\n    pass\n\ndef mid(book):\n    pass\n",
         "validator": "assert spread(book) == 2\nassert mid(book) == 101\nprint('ok')",
         "solution": "def spread(book):\n    return best_ask(book) - best_bid(book)\n\ndef mid(book):\n    return (best_bid(book) + best_ask(book)) / 2"},
        {"title": "7. Construye y lee tu libro", "practice": "juntar todas las funciones",
         "statement": "Júntalo todo. Con `make_order` y `add_order`, monta un libro con: compra 99980 (0.10), compra 99990 (0.20), venta 100010 (0.15). Luego léelo: guarda `bb = best_bid`, `sp = spread (best_ask − best_bid)` e `imb = imbalance`.",
         "hint": "Empieza `book = []` y añade tres órdenes.",
         "given": "def make_order(symbol, side, price, size):\n    return {'symbol': symbol, 'side': side, 'price': price, 'size': size}\ndef add_order(book, order):\n    book.append(order); return book\ndef best_bid(book):\n    return max(o['price'] for o in book if o['side']=='buy')\ndef best_ask(book):\n    return min(o['price'] for o in book if o['side']=='sell')\ndef imbalance(book):\n    b=sum(o['size'] for o in book if o['side']=='buy'); s=sum(o['size'] for o in book if o['side']=='sell'); return (b-s)/(b+s)\n",
         "starter": "book = []\n# anade 3 ordenes y calcula bb, sp, imb\n",
         "validator": "assert bb == 99990, 'best_bid debe ser 99990'\nassert abs(sp - 20) < 1e-9, 'spread debe ser 20'\nassert abs(imb - 1/3) < 1e-9, 'imbalance debe ser 0.333...'\nprint('ok  libro leido ->', bb, sp, round(imb,3))",
         "solution": "book = []\nbook = add_order(book, make_order('BTCUSDT','buy',99980,0.10))\nbook = add_order(book, make_order('BTCUSDT','buy',99990,0.20))\nbook = add_order(book, make_order('BTCUSDT','sell',100010,0.15))\nbb = best_bid(book)\nsp = best_ask(book) - best_bid(book)\nimb = imbalance(book)"},
    ],
    "aux": [
        {"section": "Gimnasio · Calentamiento — repaso exprés de L1",
         "blurb": "Tres reps de la clase anterior antes de entrenar lo nuevo. Si alguna se te resiste, vuelve al gimnasio de L1."},
        {"title": "C1. Spread, mid y ticket", "practice": "repaso: operaciones + f-string",
         "statement": "Calcula `mid` y construye `linea = f\"mid {mid:.1f}\"`.",
         "given": "bid = 99950\nask = 100000\n",
         "starter": "mid = None\nlinea = None\n",
         "validator": "assert mid == 99975.0\nassert linea == 'mid 99975.0'\nprint('ok')",
         "solution": "mid = (bid + ask) / 2\nlinea = f\"mid {mid:.1f}\""},
        {"title": "C2. Ventana y media", "practice": "repaso: slicing + sum/len",
         "statement": "Guarda `last3` (los 3 últimos mids) y su media `avg3`.",
         "given": "mids = [99975, 99980, 99970, 99990, 100005]\n",
         "starter": "last3 = None\navg3 = None\n",
         "validator": "assert last3 == [99970, 99990, 100005]\nassert abs(avg3 - 99988.33333333333) < 1e-6\nprint('ok')",
         "solution": "last3 = mids[-3:]\navg3 = sum(last3) / len(last3)"},
        {"title": "C3. Posición con red", "practice": "repaso: dict.get + actualizar",
         "statement": "Lee la posición de ETH con `.get` (default 0) y súmale 1.0 guardándola en el dict.",
         "given": "positions = {'BTCUSDT': 0.5}\n",
         "starter": "eth = None\n# ...y actualiza positions['ETHUSDT']\n",
         "validator": "assert eth == 0\nassert positions['ETHUSDT'] == 1.0\nassert positions['BTCUSDT'] == 0.5\nprint('ok')",
         "solution": "eth = positions.get('ETHUSDT', 0)\npositions['ETHUSDT'] = eth + 1.0"},

        {"section": "Gimnasio · Bloque 1 — Funciones con oficio",
         "blurb": "Defaults, devolver varias cosas y componer: las funciones dejan de ser cajas de una línea."},
        {"title": "A1. Tu primera quote", "practice": "función que devuelve tupla",
         "statement": "Escribe `make_quote(mid, spread)` que devuelva `(bid, ask)`: el mid menos/más medio spread.",
         "starter": "def make_quote(mid, spread):\n    pass\n",
         "validator": "q = make_quote(99975, 50)\nassert q == (99950.0, 100000.0), 'bid = mid - spread/2, ask = mid + spread/2'\nprint('ok ->', q)",
         "solution": "def make_quote(mid, spread):\n    return (mid - spread / 2, mid + spread / 2)"},
        {"title": "A2. Comisión con default", "practice": "parámetros por defecto",
         "statement": "Escribe `fee(notional, bps=1)`: la comisión en unidades de cuenta. Si no te pasan `bps`, vale 1.",
         "starter": "def fee(notional, bps=1):\n    pass\n",
         "validator": "assert abs(fee(100000) - 10.0) < 1e-9, 'sin bps usa el default de 1'\nassert abs(fee(100000, 5) - 50.0) < 1e-9\nprint('ok')",
         "solution": "def fee(notional, bps=1):\n    return notional * bps / 10000"},
        {"title": "A3. Al tick más cercano", "practice": "round dentro de una función",
         "statement": "Escribe `round_to_tick(price, tick=10)`: redondea el precio al múltiplo de `tick` más cercano.",
         "hint": "Divide por el tick, redondea, multiplica de vuelta.",
         "starter": "def round_to_tick(price, tick=10):\n    pass\n",
         "validator": "assert round_to_tick(99973) == 99970\nassert round_to_tick(99976) == 99980\nassert round_to_tick(99973, 25) == 99975\nprint('ok')",
         "solution": "def round_to_tick(price, tick=10):\n    return round(price / tick) * tick"},
        {"title": "A4. Spread en puntos básicos", "practice": "componer un cálculo",
         "statement": "Escribe `spread_bps(bid, ask)`: el spread relativo al mid, en bps (`(ask - bid) / mid * 10000`).",
         "starter": "def spread_bps(bid, ask):\n    pass\n",
         "validator": "assert abs(spread_bps(99950, 100000) - 5.0012503) < 1e-4\nprint('ok -> ~5 bps')",
         "solution": "def spread_bps(bid, ask):\n    mid = (bid + ask) / 2\n    return (ask - bid) / mid * 10000"},
        {"title": "A5. La función que decide", "practice": "lógica dentro de funciones",
         "statement": "Escribe `classify_spread(spread)`: `'tight'` si ≤ 20, `'normal'` si ≤ 60, `'wide'` si no.",
         "starter": "def classify_spread(spread):\n    pass\n",
         "validator": "assert classify_spread(10) == 'tight'\nassert classify_spread(50) == 'normal'\nassert classify_spread(100) == 'wide'\nprint('ok')",
         "solution": "def classify_spread(spread):\n    if spread <= 20:\n        return 'tight'\n    elif spread <= 60:\n        return 'normal'\n    return 'wide'"},

        {"section": "Gimnasio · Bloque 2 — Tuplas y unpacking",
         "blurb": "Devolver y desmontar pares de valores sin ceremonias."},
        {"title": "A6. Desempaqueta la quote", "practice": "unpacking",
         "statement": "`quote` es una tupla `(bid, ask)`. Desempaquétala en `bid` y `ask` y calcula `mid`.",
         "given": "quote = (99950, 100000)\n",
         "starter": "bid = None\nask = None\nmid = None\n",
         "validator": "assert bid == 99950 and ask == 100000\nassert mid == 99975.0\nprint('ok')",
         "solution": "bid, ask = quote\nmid = (bid + ask) / 2"},
        {"title": "A7. El feed venía cruzado", "practice": "swap con tuplas",
         "statement": "Este feed llegó invertido (bid > ask es imposible). Intercámbialos en **una sola línea** con unpacking.",
         "given": "bid = 100000\nask = 99950\n",
         "starter": "# una linea\n",
         "validator": "assert bid == 99950 and ask == 100000\nprint('ok -> libro descruzado')",
         "solution": "bid, ask = ask, bid"},
        {"title": "A8. Estadísticas del libro", "practice": "return múltiple",
         "statement": "Escribe `book_stats(bids, asks)` que devuelva `(best_bid, best_ask, spread)`, y desempaqueta el resultado en tres variables.",
         "given": "bids = [99930, 99950, 99940]\nasks = [100010, 100005, 100020]\n",
         "starter": "def book_stats(bids, asks):\n    pass\n\nbest_bid, best_ask, spread = None, None, None\n",
         "validator": "assert (best_bid, best_ask, spread) == (99950, 100005, 55)\nprint('ok')",
         "solution": "def book_stats(bids, asks):\n    bb = max(bids)\n    ba = min(asks)\n    return bb, ba, ba - bb\n\nbest_bid, best_ask, spread = book_stats(bids, asks)"},

        {"section": "Gimnasio · Bloque 3 — Dicts anidados: tu primer portfolio",
         "blurb": "Un dict de dicts lleva la cuenta de N símbolos sin duplicar variables — el embrión del PositionTracker de la clase 5."},
        {"title": "A9. Léelo", "practice": "acceso anidado",
         "statement": "Guarda `btc_position` y `eth_cash` leyendo el dict anidado (dos corchetes seguidos).",
         "given": "portfolio = {\n    'BTCUSDT': {'position': 0.5, 'cash': -49975.0},\n    'ETHUSDT': {'position': 2.0, 'cash': -7000.0},\n}\n",
         "starter": "btc_position = None\neth_cash = None\n",
         "validator": "assert btc_position == 0.5\nassert eth_cash == -7000.0\nprint('ok')",
         "solution": "btc_position = portfolio['BTCUSDT']['position']\neth_cash = portfolio['ETHUSDT']['cash']"},
        {"title": "A10. Un fill lo mueve", "practice": "escribir en anidado",
         "statement": "Ejecutas una compra de 0.1 BTC a 100000. Actualiza en `portfolio` la `position` (+0.1) y la `cash` (−0.1 × 100000) de BTCUSDT.",
         "given": "portfolio = {\n    'BTCUSDT': {'position': 0.5, 'cash': -49975.0},\n    'ETHUSDT': {'position': 2.0, 'cash': -7000.0},\n}\n",
         "starter": "# actualiza el dict anidado\n",
         "validator": "assert abs(portfolio['BTCUSDT']['position'] - 0.6) < 1e-9\nassert abs(portfolio['BTCUSDT']['cash'] - (-59975.0)) < 1e-9\nprint('ok')",
         "solution": "portfolio['BTCUSDT']['position'] = portfolio['BTCUSDT']['position'] + 0.1\nportfolio['BTCUSDT']['cash'] = portfolio['BTCUSDT']['cash'] - 0.1 * 100000"},
        {"title": "A11. Símbolo nuevo, con cuidado", "practice": "in + inicialización",
         "statement": "Vas a operar SOLUSDT. Si no está en `portfolio`, créalo con `{'position': 0.0, 'cash': 0.0}` — sin tocar los que ya existen.",
         "given": "portfolio = {\n    'BTCUSDT': {'position': 0.5, 'cash': -49975.0},\n    'ETHUSDT': {'position': 2.0, 'cash': -7000.0},\n}\n",
         "starter": "# comprueba y crea\n",
         "validator": "assert portfolio['SOLUSDT'] == {'position': 0.0, 'cash': 0.0}\nassert portfolio['BTCUSDT']['position'] == 0.5, 'no toques lo existente'\nprint('ok')",
         "solution": "if 'SOLUSDT' not in portfolio:\n    portfolio['SOLUSDT'] = {'position': 0.0, 'cash': 0.0}"},
        {"title": "A12. Recorre el portfolio", "practice": "items()",
         "statement": "Cuenta en `n_active` cuántos símbolos tienen posición distinta de 0, recorriendo con `.items()`.",
         "given": "portfolio = {\n    'BTCUSDT': {'position': 0.5, 'cash': -49975.0},\n    'ETHUSDT': {'position': 2.0, 'cash': -7000.0},\n    'SOLUSDT': {'position': 0.0, 'cash': 0.0},\n}\n",
         "starter": "n_active = 0\n",
         "validator": "assert n_active == 2\nprint('ok')",
         "solution": "n_active = 0\nfor sym, acct in portfolio.items():\n    if acct['position'] != 0:\n        n_active = n_active + 1"},

        {"section": "Gimnasio · Bloque 4 — Bucles avanzados",
         "blurb": "while, break, continue, enumerate y zip: el control fino del flujo."},
        {"title": "A13. Caída hasta el stop", "practice": "while",
         "statement": "El precio cae 120 en cada tick. Simula con `while`: mientras `price > stop`, réstale 120 y cuenta los ticks en `n_ticks`.",
         "given": "price = 100000\nstop = 99500\n",
         "starter": "n_ticks = 0\n# while ...\n",
         "validator": "assert price == 99400 and n_ticks == 5\nprint('ok -> el stop salta tras', n_ticks, 'ticks')",
         "solution": "n_ticks = 0\nwhile price > stop:\n    price = price - 120\n    n_ticks = n_ticks + 1"},
        {"title": "A14. Primer nivel con tamaño", "practice": "break",
         "statement": "Busca el precio del **primer** nivel con `size >= 0.2` y guárdalo en `first_ok`. Corta el bucle con `break` en cuanto lo encuentres.",
         "given": "levels = [\n    {'price': 99950, 'size': 0.05},\n    {'price': 99940, 'size': 0.30},\n    {'price': 99930, 'size': 0.50},\n]\n",
         "starter": "first_ok = None\n",
         "validator": "assert first_ok == 99940, 'el primero que cumple, no el mas grande'\nprint('ok')",
         "solution": "first_ok = None\nfor lv in levels:\n    if lv['size'] >= 0.2:\n        first_ok = lv['price']\n        break"},
        {"title": "A15. Ignora los ticks corruptos", "practice": "continue",
         "statement": "El feed mete precios imposibles (≤ 0). Calcula `clean_avg`, la media de los ticks válidos, saltando los corruptos con `continue`.",
         "given": "ticks = [99975, -1, 99990, 0, 100005]\n",
         "starter": "total = 0\ncount = 0\n# for ... continue\nclean_avg = None\n",
         "validator": "assert abs(clean_avg - 99990.0) < 1e-9, 'la media de los 3 validos'\nprint('ok')",
         "solution": "total = 0\ncount = 0\nfor t in ticks:\n    if t <= 0:\n        continue\n    total = total + t\n    count = count + 1\nclean_avg = total / count"},
        {"title": "A16. ¿En qué posición está el mejor?", "practice": "enumerate",
         "statement": "Encuentra `best_i`, el índice del bid más alto, recorriendo con `enumerate` (sin usar `.index()`).",
         "given": "bids = [99930, 99950, 99940]\n",
         "starter": "best_i = 0\n",
         "validator": "assert best_i == 1\nprint('ok -> el mejor bid vive en la posicion', best_i)",
         "solution": "best_i = 0\nfor i, p in enumerate(bids):\n    if p > bids[best_i]:\n        best_i = i"},
        {"title": "A17. Dos listas de la mano", "practice": "zip",
         "statement": "`prices` y `sizes` van en paralelo. Con `zip`, construye `notionals` (lista de `p*s`) y su `total`.",
         "given": "prices = [99950, 99960, 99970, 99980]\nsizes = [0.1, 0.2, 0.3, 0.4]\n",
         "starter": "notionals = []\ntotal = None\n",
         "validator": "assert len(notionals) == 4\nassert all(abs(n - e) < 1e-6 for n, e in zip(notionals, [9995.0, 19992.0, 29991.0, 39992.0]))\nassert abs(total - 99970.0) < 1e-6\nprint('ok')",
         "solution": "notionals = []\nfor p, s in zip(prices, sizes):\n    notionals.append(p * s)\ntotal = sum(notionals)"},

        {"section": "Gimnasio · Bloque 5 — Mini-retos del libro",
         "blurb": "Comprensiones + todo lo anterior, aplicado al libro con el que cerraste el cuaderno principal."},
        {"title": "A18. Nocionales en una línea", "practice": "comprensión de lista",
         "statement": "Construye `notionals` (precio × tamaño de cada orden) con una comprensión de lista.",
         "given": "book = [\n    {'side':'buy','price':99980,'size':0.1}, {'side':'buy','price':99990,'size':0.2},\n    {'side':'sell','price':100010,'size':0.15}, {'side':'sell','price':100005,'size':0.1},\n]\n",
         "starter": "notionals = None\n",
         "validator": "assert len(notionals) == 4\nassert abs(notionals[0] - 9998.0) < 1e-6\nassert abs(sum(notionals) - 54998.0) < 1e-6\nprint('ok')",
         "solution": "notionals = [o['price'] * o['size'] for o in book]"},
        {"title": "A19. Filtra los grandes", "practice": "comprensión con if",
         "statement": "Quédate en `big_orders` solo con las órdenes de `size >= 0.15`, con una comprensión con `if`.",
         "given": "book = [\n    {'side':'buy','price':99980,'size':0.1}, {'side':'buy','price':99990,'size':0.2},\n    {'side':'sell','price':100010,'size':0.15}, {'side':'sell','price':100005,'size':0.1},\n]\n",
         "starter": "big_orders = None\n",
         "validator": "assert len(big_orders) == 2\nassert all(o['size'] >= 0.15 for o in big_orders)\nprint('ok')",
         "solution": "big_orders = [o for o in book if o['size'] >= 0.15]"},
        {"title": "A20. El VWAP de tus fills", "practice": "sum con generador",
         "statement": "El precio medio ponderado por volumen: `vwap = Σ(p·s) / Σ(s)`. Calcúlalo — es el benchmark que perseguirás en la clase 12.",
         "given": "fills = [\n    {'price': 100000, 'size': 0.5},\n    {'price': 99900, 'size': 1.0},\n    {'price': 99950, 'size': 0.5},\n]\n",
         "starter": "vwap = None\n",
         "validator": "assert abs(vwap - 99937.5) < 1e-9\nprint('ok ->', vwap)",
         "solution": "vwap = sum(f['price'] * f['size'] for f in fills) / sum(f['size'] for f in fills)"},
        {"title": "A21. El gran reto: resumen del libro", "practice": "todo junto en una función",
         "statement": "Escribe `book_summary(book)` que devuelva un dict con `best_bid`, `best_ask`, `spread` y `n_orders`.",
         "given": "book = [\n    {'side':'buy','price':99980,'size':0.1}, {'side':'buy','price':99990,'size':0.2},\n    {'side':'sell','price':100010,'size':0.15}, {'side':'sell','price':100005,'size':0.1},\n]\n",
         "starter": "def book_summary(book):\n    pass\n",
         "validator": "s = book_summary(book)\nassert s['best_bid'] == 99990 and s['best_ask'] == 100005\nassert s['spread'] == 15 and s['n_orders'] == 4\nprint('ok ->', s)",
         "solution": "def book_summary(book):\n    bb = max(o['price'] for o in book if o['side'] == 'buy')\n    ba = min(o['price'] for o in book if o['side'] == 'sell')\n    return {'best_bid': bb, 'best_ask': ba, 'spread': ba - bb, 'n_orders': len(book)}"},

        {"section": "Para terminar — el puente a la clase 3",
         "blurb": "Los auxiliares clásicos: acumular sobre el libro, proteger tus datos y contar el dolor que resuelve la POO."},
        {"title": "A22. Nocional total del libro", "practice": "acumular sobre el libro",
         "statement": "Escribe `total_notional(book)` = suma de `price * size` de todas las órdenes.",
         "given": "book = [{'price':100,'size':0.5},{'price':200,'size':0.25}]\n",
         "starter": "def total_notional(book):\n    pass\n",
         "validator": "assert abs(total_notional(book) - 100) < 1e-9\nprint('ok')",
         "solution": "def total_notional(book):\n    return sum(o['price'] * o['size'] for o in book)"},
        {"title": "A23. Órdenes con seguridad", "practice": "validar en una función",
         "statement": "Haz que `make_order` lance `ValueError` si `side` no es `'buy'` ni `'sell'`. Las funciones también protegen tus datos.",
         "starter": "def make_order(symbol, side, price, size):\n    pass\n",
         "validator": "try:\n    make_order('X','byu',1,1)\n    raise SystemExit('deberia haber fallado')\nexcept ValueError:\n    pass\nassert make_order('X','buy',1,1)['side'] == 'buy'\nprint('ok')",
         "solution": "def make_order(symbol, side, price, size):\n    if side not in ('buy','sell'):\n        raise ValueError('side debe ser buy o sell')\n    return {'symbol': symbol, 'side': side, 'price': price, 'size': size}"},
        {"title": "A24. Cuenta el problema", "practice": "reflexión → POO",
         "statement": "¿Cuántas de tus funciones reciben `book` como primer argumento (add, cancel, best_bid, best_ask, imbalance, spread, mid)? Guárdalo en `funcs_con_book`. En la clase 4 nacen los objetos, y en la 5 todas estas funciones se vuelven **métodos** de un `OrderBook`.",
         "starter": "funcs_con_book = None\n",
         "validator": "assert funcs_con_book == 7\nprint('ok -> un dato + las funciones que lo manosean = un OBJETO (clases 4-5)')",
         "solution": "funcs_con_book = 7"},
    ],
    "script_name": "order_book.py",
    "script": '''# Clase 2 - El libro funcional, en un archivo .py
# Las funciones que construiste en el notebook, mas un main que arma y lee un libro.
# Ejecuta desde la terminal:  python order_book.py


def make_order(symbol, side, price, size):   # ej. 1
    return {"symbol": symbol, "side": side, "price": price, "size": size}


def add_order(book, order):                  # ej. 2
    book.append(order)
    return book


def cancel_order(book, order_id):            # ej. 3
    return [o for o in book if o.get("id") != order_id]


def best_bid(book):                          # ej. 4
    return max(o["price"] for o in book if o["side"] == "buy")


def best_ask(book):                          # ej. 4
    return min(o["price"] for o in book if o["side"] == "sell")


def spread(book):                            # ej. 6
    return best_ask(book) - best_bid(book)


def mid(book):                               # ej. 6
    return (best_bid(book) + best_ask(book)) / 2


def imbalance(book):                         # ej. 5
    buy = sum(o["size"] for o in book if o["side"] == "buy")
    sell = sum(o["size"] for o in book if o["side"] == "sell")
    return (buy - sell) / (buy + sell)


def main():                                  # ej. 7: construir y leer el libro
    book = []
    book = add_order(book, make_order("BTCUSDT", "buy", 99980, 0.10))
    book = add_order(book, make_order("BTCUSDT", "buy", 99990, 0.20))
    book = add_order(book, make_order("BTCUSDT", "sell", 100010, 0.15))

    print("ordenes:", len(book))
    print("best_bid:", best_bid(book))
    print("best_ask:", best_ask(book))
    print("spread:", spread(book))
    print("mid:", mid(book))
    print("imbalance:", round(imbalance(book), 4))
    # Fijate: TODAS estas funciones reciben book. En la clase 3, book sera un objeto.


if __name__ == "__main__":
    main()
''',
})

# ---------------------------------------------------------------------------
# L3 — Python III — Módulos y errores
# ---------------------------------------------------------------------------
LESSONS.append({
    "n": 3, "slug": "03-python-iii-modules",
    "title": "Python III — Módulos y errores",
    "piece": "tu order_book.py se vuelve un módulo importable y robusto",
    "objective": "Sacar las funciones del libro del notebook y meterlas en un módulo .py reutilizable que puedes importar desde otro archivo. Y blindarlo: que un libro vacío no lo reviente.",
    "frase": "Tu código deja de vivir en celdas: se vuelve una librería que importas. Y una librería de verdad no se cae con un dato raro.",
    "concepts": [
        ("Un módulo es un .py con funciones",
         "Cuando tus funciones crecen, las guardas en un archivo .py: eso es un módulo. Desde otro sitio lo importas y usas sus funciones, sin copiar nada.",
         "import order_book\norder_book.spread(book)"),
        ("import vs from ... import",
         "`import order_book` trae el módulo entero (usas `order_book.fn`). `from order_book import spread` trae solo lo que pides (usas `spread`).",
         "from order_book import imbalance\nimbalance(book)"),
        ("Errores como red de seguridad",
         "best_bid sobre un libro vacío revienta. `try/except` lo atrapa; `raise` lanza un error claro cuando el dato no tiene sentido.",
         "try:\n    best_bid(book)\nexcept ValueError:\n    return None"),
    ],
    "build": [
        {"title": "1. Importa una función del módulo", "practice": "from ... import",
         "statement": "Importa `imbalance` desde el módulo `order_book` y úsala sobre `book`. Guarda el resultado en `imb`.",
         "hint": "`from order_book import imbalance`.",
         "given": "book = [{'side':'buy','size':3},{'side':'sell','size':1}]\n",
         "starter": "imb = None\n",
         "validator": "assert abs(imb - 0.5) < 1e-9, 'imbalance de ese libro es 0.5'\nprint('ok  imb=%.2f' % imb)",
         "solution": "from order_book import imbalance\nimb = imbalance(book)"},
        {"title": "2. Importa el módulo entero", "practice": "import módulo",
         "statement": "Importa el módulo `order_book` completo y calcula el spread del libro con `order_book.spread(book)`. Guarda `sp`.",
         "hint": "`import order_book` y luego `order_book.spread(book)`.",
         "given": "book = [{'side':'buy','price':100},{'side':'sell','price':102}]\n",
         "starter": "sp = None\n",
         "validator": "assert sp == 2, 'spread debe ser 2'\nprint('ok  sp=%d' % sp)",
         "solution": "import order_book\nsp = order_book.spread(book)"},
        {"title": "3. Blinda con try/except", "practice": "manejo de errores",
         "statement": "Escribe `safe_best_bid(book)` que devuelva el mejor bid, o `None` si el libro no tiene compras (best_bid revienta con `ValueError`).",
         "hint": "Llama a `order_book.best_bid` dentro de un `try`.",
         "starter": "import order_book\n\ndef safe_best_bid(book):\n    pass\n",
         "validator": "assert safe_best_bid([]) is None, 'libro vacío -> None'\nassert safe_best_bid([{'side':'buy','price':100}]) == 100\nprint('ok')",
         "solution": "import order_book\n\ndef safe_best_bid(book):\n    try:\n        return order_book.best_bid(book)\n    except ValueError:\n        return None"},
        {"title": "4. Lanza un error claro", "practice": "raise",
         "statement": "Escribe `check_size(size)` que devuelva `size` si es positivo, y lance `ValueError` si es <= 0.",
         "starter": "def check_size(size):\n    pass\n",
         "validator": "assert check_size(0.1) == 0.1\ntry:\n    check_size(-1); raise SystemExit('deberia fallar')\nexcept ValueError:\n    pass\nprint('ok')",
         "solution": "def check_size(size):\n    if size <= 0:\n        raise ValueError('size debe ser positivo')\n    return size"},
        {"title": "5. Combina funciones del módulo", "practice": "usar varias del módulo",
         "statement": "Usando `best_bid` y `best_ask` del módulo, calcula el `mid` del libro a mano. Guarda `mid`.",
         "hint": "`from order_book import best_bid, best_ask`.",
         "given": "book = [{'side':'buy','price':100},{'side':'sell','price':102}]\n",
         "starter": "mid = None\n",
         "validator": "assert mid == 101\nprint('ok  mid=%d' % mid)",
         "solution": "from order_book import best_bid, best_ask\nmid = (best_bid(book) + best_ask(book)) / 2"},
        {"title": "6. Construye y lee un libro con el módulo", "practice": "juntar el módulo",
         "statement": "Con `order_book`, monta un libro (compra 99980/0.10, compra 99990/0.20, venta 100010/0.15) y léelo: guarda `bb = best_bid`, `sp = spread`, `imb = imbalance`.",
         "given": "import order_book\n",
         "starter": "book = []\n# usa order_book.make_order / add_order y luego lee bb, sp, imb\n",
         "validator": "assert bb == 99990 and sp == 20\nassert abs(imb - 1/3) < 1e-9\nprint('ok  ->', bb, sp, round(imb,3))",
         "solution": "import order_book\nbook = []\norder_book.add_order(book, order_book.make_order('BTCUSDT','buy',99980,0.10))\norder_book.add_order(book, order_book.make_order('BTCUSDT','buy',99990,0.20))\norder_book.add_order(book, order_book.make_order('BTCUSDT','sell',100010,0.15))\nbb = order_book.best_bid(book)\nsp = order_book.spread(book)\nimb = order_book.imbalance(book)"},
    ],
    "aux": [
        {"section": "Gimnasio · Calentamiento — repaso exprés de L2",
         "blurb": "Tres reps de funciones y libro antes de entrenar los módulos."},
        {"title": "C1. Medio spread", "practice": "repaso: funciones",
         "statement": "Escribe `half_spread(bid, ask)` que devuelva la mitad del spread.",
         "starter": "def half_spread(bid, ask):\n    pass\n",
         "validator": "assert half_spread(99950, 100000) == 25.0\nprint('ok')",
         "solution": "def half_spread(bid, ask):\n    return (ask - bid) / 2"},
        {"title": "C2. Tamaños compradores", "practice": "repaso: comprensión con if",
         "statement": "Con una comprensión, guarda en `buy_sizes` los tamaños de las órdenes buy.",
         "given": "book = [\n    {'side':'buy','price':99980,'size':0.5}, {'side':'sell','price':100005,'size':0.1},\n    {'side':'buy','price':99970,'size':0.2},\n]\n",
         "starter": "buy_sizes = None\n",
         "validator": "assert buy_sizes == [0.5, 0.2]\nprint('ok')",
         "solution": "buy_sizes = [o['size'] for o in book if o['side'] == 'buy']"},
        {"title": "C3. Desempaqueta", "practice": "repaso: tuplas",
         "statement": "Desempaqueta `quote` en `bid` y `ask` y calcula `spread`.",
         "given": "quote = (99950, 100000)\n",
         "starter": "bid = None\nask = None\nspread = None\n",
         "validator": "assert (bid, ask, spread) == (99950, 100000, 50)\nprint('ok')",
         "solution": "bid, ask = quote\nspread = ask - bid"},

        {"section": "Gimnasio · Bloque 1 — Import fino",
         "blurb": "Las tres formas de traerte tu módulo, y cuándo usar cada una."},
        {"title": "A1. El módulo entero", "practice": "import módulo",
         "statement": "Importa `order_book` (módulo entero) y guarda `bb = order_book.best_bid(book)`.",
         "given": "book = [\n    {'side':'buy','price':99980,'size':0.3}, {'side':'sell','price':100005,'size':0.1},\n]\n",
         "starter": "bb = None\n",
         "validator": "assert bb == 99980\nprint('ok')",
         "solution": "import order_book\nbb = order_book.best_bid(book)"},
        {"title": "A2. Dos funciones de golpe", "practice": "from ... import a, b",
         "statement": "Trae `best_ask` e `imbalance` en una sola línea `from ... import` y calcula `ba` e `imb`.",
         "given": "book = [\n    {'side':'buy','price':99980,'size':0.3}, {'side':'sell','price':100005,'size':0.1},\n]\n",
         "starter": "ba = None\nimb = None\n",
         "validator": "assert ba == 100005\nassert abs(imb - 0.5) < 1e-9, 'imbalance con signo: (0.3-0.1)/0.4'\nprint('ok')",
         "solution": "from order_book import best_ask, imbalance\nba = best_ask(book)\nimb = imbalance(book)"},
        {"title": "A3. Construye con el módulo", "practice": "usar varias funciones del módulo",
         "statement": "Usando SOLO funciones de `order_book`, crea un libro con una orden buy 99950 × 0.5. Guarda `book2` y `n = len(book2)`.",
         "starter": "book2 = None\nn = None\n",
         "validator": "assert n == 1\nassert book2[0]['price'] == 99950\nprint('ok')",
         "solution": "import order_book\nbook2 = order_book.add_order([], order_book.make_order('BTCUSDT', 'buy', 99950, 0.5))\nn = len(book2)"},

        {"section": "Gimnasio · Bloque 2 — Errores bajo control",
         "blurb": "try/except con puntería: cazar el error concreto, leer su mensaje y distinguir tipos."},
        {"title": "A4. Caza el ValueError", "practice": "try/except",
         "statement": "El feed manda `'99,950'` (con coma). Intenta convertirlo con `int()`; si falla, guarda `price = -1`.",
         "given": "price_str = '99,950'\n",
         "starter": "price = None\n",
         "validator": "assert price == -1, 'int(\"99,950\") lanza ValueError: hay que cazarlo'\nprint('ok')",
         "solution": "try:\n    price = int(price_str)\nexcept ValueError:\n    price = -1"},
        {"title": "A5. Lee el mensaje", "practice": "except ... as e",
         "statement": "Captura la excepción como `e` y guarda su mensaje en `msg` (con `str(e)`).",
         "given": "price_str = 'abc'\n",
         "starter": "msg = None\n",
         "validator": "assert 'invalid literal' in msg, 'el mensaje del ValueError explica que paso'\nprint('ok ->', msg)",
         "solution": "try:\n    price = int(price_str)\nexcept ValueError as e:\n    msg = str(e)"},
        {"title": "A6. Dos redes distintas", "practice": "varios except por tipo",
         "statement": "A `order` le falta `'size'`. Calcula el nocional dentro de un `try` con dos redes: `except KeyError` → `tipo = 'falta un campo'`; `except TypeError` → `tipo = 'tipo raro'`.",
         "given": "order = {'price': 100}\n",
         "starter": "tipo = None\n",
         "validator": "assert tipo == 'falta un campo'\nprint('ok')",
         "solution": "try:\n    n = order['price'] * order['size']\n    tipo = 'ok'\nexcept KeyError:\n    tipo = 'falta un campo'\nexcept TypeError:\n    tipo = 'tipo raro'"},

        {"section": "Gimnasio · Bloque 3 — Diseña el error",
         "blurb": "raise: fallar pronto, con mensajes que hablan de trading y no de max()."},
        {"title": "A7. Falla pronto", "practice": "raise en una función",
         "statement": "Escribe `make_safe_order(symbol, side, price, size)`: si `price <= 0`, lanza `ValueError`; si no, devuelve el dict de siempre.",
         "starter": "def make_safe_order(symbol, side, price, size):\n    pass\n",
         "validator": "try:\n    make_safe_order('X', 'buy', -5, 1); raise SystemExit('deberia fallar')\nexcept ValueError:\n    pass\nassert make_safe_order('X', 'buy', 100, 1)['price'] == 100\nprint('ok')",
         "solution": "def make_safe_order(symbol, side, price, size):\n    if price <= 0:\n        raise ValueError(f'price inválido: {price}')\n    return {'symbol': symbol, 'side': side, 'price': price, 'size': size}"},
        {"title": "A8. El mensaje útil", "practice": "raise con contexto",
         "statement": "Escribe `check_size(size)`: si `size <= 0`, lanza `ValueError` cuyo mensaje **incluya el valor** recibido (usa una f-string).",
         "starter": "def check_size(size):\n    pass\n",
         "validator": "try:\n    check_size(-0.5); raise SystemExit('deberia fallar')\nexcept ValueError as e:\n    assert '-0.5' in str(e), 'el mensaje debe incluir el valor'\nprint('ok')",
         "solution": "def check_size(size):\n    if size <= 0:\n        raise ValueError(f'size inválido: {size}')"},
        {"title": "A9. safe_mid", "practice": "validar y calcular",
         "statement": "Escribe `safe_mid(bids, asks)`: si alguna lista está vacía, `raise ValueError('libro vacío')`; si no, devuelve `(max(bids) + min(asks)) / 2`.",
         "starter": "def safe_mid(bids, asks):\n    pass\n",
         "validator": "assert safe_mid([99950, 99940], [100000]) == 99975.0\ntry:\n    safe_mid([], [100000]); raise SystemExit('deberia fallar')\nexcept ValueError:\n    pass\nprint('ok')",
         "solution": "def safe_mid(bids, asks):\n    if not bids or not asks:\n        raise ValueError('libro vacío')\n    return (max(bids) + min(asks)) / 2"},

        {"section": "Para terminar — profundización",
         "blurb": "Alias, tu propio tipo de excepción y defaults: el acabado profesional del módulo."},
        {"title": "A10. Importa con alias", "practice": "import ... as",
         "statement": "Importa `order_book` con el alias `ob` y calcula `imbalance` del libro. Guarda `imb`.",
         "given": "book = [{'side':'buy','size':2},{'side':'sell','size':2}]\n",
         "starter": "imb = None\n",
         "validator": "assert abs(imb - 0.0) < 1e-9\nprint('ok')",
         "solution": "import order_book as ob\nimb = ob.imbalance(book)"},
        {"title": "A11. Tu propio tipo de error", "practice": "excepción propia",
         "statement": "Define `class EmptyBookError(Exception)` y una función `top(book)` que la lance si el libro está vacío, o devuelva la primera orden.",
         "starter": "class EmptyBookError(Exception):\n    pass\n\ndef top(book):\n    pass\n",
         "validator": "try:\n    top([]); raise SystemExit('deberia fallar')\nexcept EmptyBookError:\n    pass\nassert top([{'id':1}]) == {'id':1}\nprint('ok')",
         "solution": "class EmptyBookError(Exception):\n    pass\n\ndef top(book):\n    if not book:\n        raise EmptyBookError('el libro está vacío')\n    return book[0]"},
        {"title": "A12. Argumentos por defecto", "practice": "parámetros con valor por defecto",
         "statement": "Escribe `make_order(symbol, side, price, size=0.01)` con `size` por defecto. Comprueba que sin pasar `size` vale 0.01.",
         "starter": "def make_order(symbol, side, price, size=0.01):\n    pass\n",
         "validator": "assert make_order('X','buy',100)['size'] == 0.01\nassert make_order('X','buy',100, 0.5)['size'] == 0.5\nprint('ok')",
         "solution": "def make_order(symbol, side, price, size=0.01):\n    return {'symbol': symbol, 'side': side, 'price': price, 'size': size}"},
    ],
    "script_name": "main.py",
    "extra_files": {"order_book.py": '''# order_book.py - el libro funcional de la clase 2, como modulo reutilizable.


def make_order(symbol, side, price, size):
    if side not in ("buy", "sell"):
        raise ValueError("side debe ser buy o sell")
    return {"symbol": symbol, "side": side, "price": price, "size": size}


def add_order(book, order):
    book.append(order)
    return book


def cancel_order(book, order_id):
    return [o for o in book if o.get("id") != order_id]


def best_bid(book):
    return max(o["price"] for o in book if o["side"] == "buy")


def best_ask(book):
    return min(o["price"] for o in book if o["side"] == "sell")


def spread(book):
    return best_ask(book) - best_bid(book)


def imbalance(book):
    buy = sum(o["size"] for o in book if o["side"] == "buy")
    sell = sum(o["size"] for o in book if o["side"] == "sell")
    return (buy - sell) / (buy + sell)
'''},
    "script": '''# main.py - importa el modulo order_book y arma + lee un libro.
# Ejecuta desde la terminal:  python main.py
import order_book


def main():
    book = []
    order_book.add_order(book, order_book.make_order("BTCUSDT", "buy", 99980, 0.10))
    order_book.add_order(book, order_book.make_order("BTCUSDT", "buy", 99990, 0.20))
    order_book.add_order(book, order_book.make_order("BTCUSDT", "sell", 100010, 0.15))

    print("best_bid:", order_book.best_bid(book))
    print("spread:", order_book.spread(book))
    print("imbalance:", round(order_book.imbalance(book), 4))


if __name__ == "__main__":
    main()
''',
})

# ---------------------------------------------------------------------------
# L4 — OOP I — Order y Trade
# ---------------------------------------------------------------------------
LESSONS.append({
    "n": 4, "slug": "04-oop-i-order-trade",
    "title": "OOP I — Order y Fill",
    "piece": "clases Order y Fill (exchange/orders.py, trades.py)",
    "objective": "Convertir el dict de orden en una clase Order con métodos, y modelar el resultado de un cruce con Fill. Primer módulo de verdad del paquete exchange.",
    "frase": "Un objeto empaqueta datos y comportamiento: la orden ya sabe calcular su nocional.",
    "concepts": [
        ("De dict a clase",
         "Una clase es una plantilla. `__init__` guarda los datos (lo que antes eran claves del dict) como atributos. Crear un objeto es rellenar la plantilla.",
         "class Order:\n    def __init__(self, symbol, side, price, size):\n        self.symbol = symbol\n        self.side = side\n        self.price = price\n        self.size = size"),
        ("Métodos: el dato sabe operar consigo mismo",
         "Antes tenías compute_notional(order). Ahora la orden lo sabe hacer sola: order.notional(). El comportamiento vive junto al dato.",
         "    def notional(self):\n        return self.price * self.size"),
        ("Fill: el resultado de un cruce",
         "Cuando una orden se ejecuta, genera un Fill. Su cash_flow es negativo si compras (sale caja) y positivo si vendes.",
         "    def cash_flow(self):\n        sign = -1 if self.side=='buy' else 1\n        return sign * self.price * self.size"),
    ],
    "build": [
        {"title": "1. La clase Order", "practice": "class, __init__ y self",
         "statement": "Convierte el dict de orden en una clase. Define `Order` con `__init__(self, symbol, side, price, size)` que guarde los 4 como atributos (`self.symbol = symbol`, etc.).",
         "hint": "`self` es el objeto que estás rellenando.",
         "starter": "class Order:\n    def __init__(self, symbol, side, price, size):\n        pass\n",
         "validator": "o = Order('BTCUSDT','buy',100,0.5)\nassert o.symbol=='BTCUSDT' and o.side=='buy' and o.price==100 and o.size==0.5\nprint('ok')",
         "solution": "class Order:\n    def __init__(self, symbol, side, price, size):\n        self.symbol = symbol\n        self.side = side\n        self.price = price\n        self.size = size"},
        {"title": "2. Un método: notional", "practice": "el dato opera consigo mismo",
         "statement": "Antes tenías `compute_notional(order)`. Ahora la orden lo hace sola: añade el método `notional(self)` que devuelva `price * size`.",
         "starter": "class Order:\n    def __init__(self, symbol, side, price, size):\n        self.symbol = symbol; self.side = side\n        self.price = price; self.size = size\n    def notional(self):\n        pass\n",
         "validator": "o = Order('X','buy',100,0.5)\nassert abs(o.notional() - 50) < 1e-9\nprint('ok')",
         "solution": "class Order:\n    def __init__(self, symbol, side, price, size):\n        self.symbol = symbol; self.side = side\n        self.price = price; self.size = size\n    def notional(self):\n        return self.price * self.size"},
        {"title": "3. __repr__: que sepa describirse", "practice": "dunder methods",
         "statement": "Añade `__repr__(self)` que devuelva, p.ej., `'Order(buy 0.5 X @ 100)'`. Así el objeto se imprime legible.",
         "starter": "class Order:\n    def __init__(self, symbol, side, price, size):\n        self.symbol=symbol; self.side=side; self.price=price; self.size=size\n    def __repr__(self):\n        pass\n",
         "validator": "o = Order('X','buy',100,0.5)\nassert repr(o) == 'Order(buy 0.5 X @ 100)', repr(o)\nprint('ok')",
         "solution": "class Order:\n    def __init__(self, symbol, side, price, size):\n        self.symbol=symbol; self.side=side; self.price=price; self.size=size\n    def __repr__(self):\n        return f'Order({self.side} {self.size} {self.symbol} @ {self.price})'"},
        {"title": "4. La clase Fill y su cash_flow", "practice": "segunda clase + signo",
         "statement": "Cuando una orden se ejecuta, genera un `Fill`. Define `Fill(symbol, side, price, size)` con `cash_flow()`: **negativo** si compras (sale caja), **positivo** si vendes.",
         "starter": "class Fill:\n    def __init__(self, symbol, side, price, size):\n        pass\n    def cash_flow(self):\n        pass\n",
         "validator": "assert abs(Fill('X','buy',100,0.5).cash_flow() + 50) < 1e-9, 'compra -> -50'\nassert abs(Fill('X','sell',100,0.5).cash_flow() - 50) < 1e-9, 'venta -> +50'\nprint('ok')",
         "solution": "class Fill:\n    def __init__(self, symbol, side, price, size):\n        self.symbol=symbol; self.side=side; self.price=price; self.size=size\n    def cash_flow(self):\n        sign = -1 if self.side=='buy' else 1\n        return sign * self.price * self.size"},
        {"title": "5. Instánciala y opérala", "practice": "crear objetos y llamar métodos",
         "statement": "Crea una `Order` de compra (BTCUSDT, 100, 0.5). Guarda su `nocional` (`order.notional()`) y su `texto` (`repr(order)`).",
         "given": "class Order:\n    def __init__(self, symbol, side, price, size):\n        self.symbol=symbol; self.side=side; self.price=price; self.size=size\n    def notional(self):\n        return self.price*self.size\n    def __repr__(self):\n        return f'Order({self.side} {self.size} {self.symbol} @ {self.price})'\n",
         "starter": "order = None\nnocional = None\ntexto = None\n",
         "validator": "assert isinstance(order, Order)\nassert abs(nocional - 50) < 1e-9\nassert texto == 'Order(buy 0.5 BTCUSDT @ 100)', texto\nprint('ok ', texto)",
         "solution": "order = Order('BTCUSDT','buy',100,0.5)\nnocional = order.notional()\ntexto = repr(order)"},
        {"title": "6. De la orden al dinero", "practice": "juntar Order, Fill y cash_flow",
         "statement": "Modela una vuelta completa: compras 0.5 @ 100 y luego vendes 0.5 @ 110. Crea los dos `Fill` y guarda `total_cash` = suma de sus `cash_flow()`.",
         "hint": "Compra resta (-50), venta suma (+55) -> total +5.",
         "given": "class Fill:\n    def __init__(self, symbol, side, price, size):\n        self.symbol=symbol; self.side=side; self.price=price; self.size=size\n    def cash_flow(self):\n        return (-1 if self.side=='buy' else 1)*self.price*self.size\n",
         "starter": "buy = None\nsell = None\ntotal_cash = None\n",
         "validator": "assert abs(total_cash - 5.0) < 1e-9, 'compra -50, venta +55 -> +5'\nprint('ok  total_cash=%.1f' % total_cash)",
         "solution": "buy = Fill('BTCUSDT','buy',100,0.5)\nsell = Fill('BTCUSDT','sell',110,0.5)\ntotal_cash = buy.cash_flow() + sell.cash_flow()"},
    ],
    "aux": [
        {"section": "Gimnasio · Calentamiento — repaso exprés de L3",
         "blurb": "Import, red y defaults en tres reps."},
        {"title": "C1. Importa y lee", "practice": "repaso: import módulo",
         "statement": "Importa `order_book` y guarda `sp = order_book.spread(book)`.",
         "given": "book = [\n    {'side':'buy','price':99980,'size':0.3}, {'side':'sell','price':100005,'size':0.1},\n]\n",
         "starter": "sp = None\n",
         "validator": "assert sp == 25\nprint('ok')",
         "solution": "import order_book\nsp = order_book.spread(book)"},
        {"title": "C2. La red puesta", "practice": "repaso: try/except",
         "statement": "Convierte `raw` con `int()`; si falla, `parsed = 0`.",
         "given": "raw = '99x50'\n",
         "starter": "parsed = None\n",
         "validator": "assert parsed == 0\nprint('ok')",
         "solution": "try:\n    parsed = int(raw)\nexcept ValueError:\n    parsed = 0"},
        {"title": "C3. Quote con default", "practice": "repaso: parámetros por defecto",
         "statement": "Escribe `make_quote(mid, spread=50)` que devuelva `(bid, ask)`.",
         "starter": "def make_quote(mid, spread=50):\n    pass\n",
         "validator": "assert make_quote(99975) == (99950.0, 100000.0)\nassert make_quote(99975, 10) == (99970.0, 99980.0)\nprint('ok')",
         "solution": "def make_quote(mid, spread=50):\n    return (mid - spread / 2, mid + spread / 2)"},

        {"section": "Gimnasio · Bloque 1 — El molde",
         "blurb": "class, __init__, self, métodos y __repr__ — la anatomía completa, drill a drill."},
        {"title": "A1. Tu primera clase", "practice": "class + __init__",
         "statement": "Escribe la clase `Quote` que guarde `bid` y `ask` en `__init__`. Crea `q = Quote(99950, 100000)`.",
         "starter": "class Quote:\n    pass\n\nq = None\n",
         "validator": "assert q.bid == 99950 and q.ask == 100000\nprint('ok')",
         "solution": "class Quote:\n    def __init__(self, bid, ask):\n        self.bid = bid\n        self.ask = ask\n\nq = Quote(99950, 100000)"},
        {"title": "A2. Un método que calcula", "practice": "métodos y self",
         "statement": "Añade a `Quote` el método `mid()` y comprueba `q.mid()`.",
         "starter": "class Quote:\n    def __init__(self, bid, ask):\n        self.bid = bid\n        self.ask = ask\n    def mid(self):\n        pass\n\nq = Quote(99950, 100000)\n",
         "validator": "assert q.mid() == 99975.0\nprint('ok')",
         "solution": "class Quote:\n    def __init__(self, bid, ask):\n        self.bid = bid\n        self.ask = ask\n    def mid(self):\n        return (self.bid + self.ask) / 2\n\nq = Quote(99950, 100000)"},
        {"title": "A3. Piezas independientes", "practice": "cada objeto, su dato",
         "statement": "Crea `q1 = Quote(99950, 100000)` y `q2 = Quote(3400, 3402)`. Sube `q1.bid` a 99960 y comprueba que `q2` ni se entera.",
         "given": "class Quote:\n    def __init__(self, bid, ask):\n        self.bid = bid\n        self.ask = ask\n",
         "starter": "q1 = None\nq2 = None\n# sube q1.bid a 99960\n",
         "validator": "assert q1.bid == 99960, 'q1 debe cambiar'\nassert q2.bid == 3400, 'q2 no debe cambiar: son objetos independientes'\nprint('ok')",
         "solution": "q1 = Quote(99950, 100000)\nq2 = Quote(3400, 3402)\nq1.bid = 99960"},
        {"title": "A4. Que sepa presentarse", "practice": "__repr__",
         "statement": "Añade `__repr__` para que `repr(q)` sea exactamente `'Quote(99950/100000)'`.",
         "starter": "class Quote:\n    def __init__(self, bid, ask):\n        self.bid = bid\n        self.ask = ask\n    def __repr__(self):\n        pass\n\nq = Quote(99950, 100000)\n",
         "validator": "assert repr(q) == 'Quote(99950/100000)'\nprint('ok ->', q)",
         "solution": "class Quote:\n    def __init__(self, bid, ask):\n        self.bid = bid\n        self.ask = ask\n    def __repr__(self):\n        return f\"Quote({self.bid}/{self.ask})\"\n\nq = Quote(99950, 100000)"},

        {"section": "Gimnasio · Bloque 2 — Order, Fill y el dinero",
         "blurb": "Las dos clases de hoy, y el signo que separa apostar de cobrar."},
        {"title": "A5. Order.notional", "practice": "la clase de la lección",
         "statement": "Escribe `Order` (side, price, size) con su método `notional()`.",
         "starter": "class Order:\n    pass\n",
         "validator": "o = Order('buy', 99950, 0.5)\nassert abs(o.notional() - 49975.0) < 1e-9\nprint('ok')",
         "solution": "class Order:\n    def __init__(self, side, price, size):\n        self.side = side\n        self.price = price\n        self.size = size\n    def notional(self):\n        return self.price * self.size"},
        {"title": "A6. Fill.cash_flow con signo", "practice": "el signo del dinero",
         "statement": "Escribe `Fill` (side, price, size) con `cash_flow()`: negativo si compras, positivo si vendes.",
         "starter": "class Fill:\n    pass\n",
         "validator": "assert abs(Fill('buy', 99950, 0.5).cash_flow() - (-49975.0)) < 1e-9\nassert abs(Fill('sell', 99950, 0.5).cash_flow() - 49975.0) < 1e-9\nprint('ok')",
         "solution": "class Fill:\n    def __init__(self, side, price, size):\n        self.side = side\n        self.price = price\n        self.size = size\n    def cash_flow(self):\n        if self.side == 'buy':\n            return -self.price * self.size\n        return self.price * self.size"},
        {"title": "A7. La caja tras la sesión", "practice": "objetos en una lista",
         "statement": "Con la lista `fills`, suma todos los `cash_flow()` en `total_cash`.",
         "given": "class Fill:\n    def __init__(self, side, price, size):\n        self.side = side; self.price = price; self.size = size\n    def cash_flow(self):\n        return -self.price * self.size if self.side == 'buy' else self.price * self.size\n\nfills = [Fill('buy', 99950, 0.5), Fill('sell', 100050, 0.5)]\n",
         "starter": "total_cash = None\n",
         "validator": "assert abs(total_cash - 50.0) < 1e-9, 'compraste a 99950 y vendiste a 100050'\nprint('ok ->', total_cash)",
         "solution": "total_cash = 0\nfor f in fills:\n    total_cash = total_cash + f.cash_flow()"},

        {"section": "Gimnasio · Bloque 3 — Objetos que se protegen",
         "blurb": "Validar al construir, describirse bien y decidir qué es dato y qué es cálculo."},
        {"title": "A8. Precio con guardia", "practice": "validar en __init__",
         "statement": "Haz que `Order.__init__` lance `ValueError` si `price <= 0`.",
         "starter": "class Order:\n    def __init__(self, side, price, size):\n        pass\n",
         "validator": "try:\n    Order('buy', -5, 1); raise SystemExit('deberia fallar')\nexcept ValueError:\n    pass\nassert Order('buy', 100, 1).price == 100\nprint('ok')",
         "solution": "class Order:\n    def __init__(self, side, price, size):\n        if price <= 0:\n            raise ValueError(f'price inválido: {price}')\n        self.side = side\n        self.price = price\n        self.size = size"},
        {"title": "A9. describe()", "practice": "método + f-string",
         "statement": "Añade `describe()` que devuelva `'BUY 0.5 @ 99950'` (lado en mayúsculas).",
         "starter": "class Order:\n    def __init__(self, side, price, size):\n        self.side = side; self.price = price; self.size = size\n    def describe(self):\n        pass\n\no = Order('buy', 99950, 0.5)\n",
         "validator": "assert o.describe() == 'BUY 0.5 @ 99950'\nprint('ok')",
         "solution": "class Order:\n    def __init__(self, side, price, size):\n        self.side = side; self.price = price; self.size = size\n    def describe(self):\n        return f\"{self.side.upper()} {self.size} @ {self.price}\"\n\no = Order('buy', 99950, 0.5)"},
        {"title": "A10. ¿Dato o cálculo?", "practice": "atributo derivado",
         "statement": "Haz que `__init__` calcule y guarde `self.notional` como **atributo** (se lee sin paréntesis).",
         "starter": "class Order:\n    def __init__(self, side, price, size):\n        pass\n\no = Order('buy', 99950, 0.5)\n",
         "validator": "assert abs(o.notional - 49975.0) < 1e-9, 'sin parentesis: es un atributo'\nassert not callable(o.notional)\nprint('ok')",
         "solution": "class Order:\n    def __init__(self, side, price, size):\n        self.side = side\n        self.price = price\n        self.size = size\n        self.notional = price * size\n\no = Order('buy', 99950, 0.5)"},

        {"section": "Para terminar — el paquete real",
         "blurb": "El Order pulido que arrastrarás todo el curso, y los enums que evitan un 'byu'."},
        {"title": "A11. Lados con seguridad", "practice": "validar en __init__",
         "statement": "Haz que `Order.__init__` lance `ValueError` si `side` no es 'buy' ni 'sell'. Un objeto puede proteger sus propios datos.",
         "starter": "class Order:\n    def __init__(self, symbol, side, price, size):\n        pass\n",
         "validator": "try:\n    Order('X','byu',1,1); raise SystemExit('deberia fallar')\nexcept ValueError:\n    pass\nassert Order('X','buy',1,1).side == 'buy'\nprint('ok')",
         "solution": "class Order:\n    def __init__(self, symbol, side, price, size):\n        if side not in ('buy','sell'):\n            raise ValueError('side debe ser buy o sell')\n        self.symbol=symbol; self.side=side; self.price=price; self.size=size"},
        {"title": "A12. El Order real del paquete", "practice": "usar exchange.orders",
         "statement": "Importa `Order` y `Side` de `exchange.orders` (la versión pulida que arrastrarás todo el curso) y crea una orden de compra. Comprueba `order.notional()`.",
         "starter": "from exchange.orders import Order, Side\norder = None\n",
         "validator": "from exchange.orders import Order\nassert isinstance(order, Order)\nassert abs(order.notional() - order.price*order.size) < 1e-9\nprint('ok')",
         "solution": "from exchange.orders import Order, Side\norder = Order('BTCUSDT', Side.BUY, 0.5, price=100)"},
        {"title": "A13. Side como Enum", "practice": "enums seguros",
         "statement": "Importa `Side` de `exchange.orders`. Comprueba que `Side.BUY` se compara con el texto `'buy'` (hereda de str) pero evita errores como `'byu'`. Guarda `es_buy = (Side.BUY == 'buy')`.",
         "starter": "from exchange.orders import Side\nes_buy = None\n",
         "validator": "from exchange.orders import Side\nassert es_buy is True\nprint('ok  Side.BUY ==', Side.BUY.value)",
         "solution": "from exchange.orders import Side\nes_buy = (Side.BUY == 'buy')"},
    ],
    "script_name": "orders_demo.py",
    "script": '''# orders_demo.py - clase 4: el dict de orden se vuelve un OBJETO.
# Datos + comportamiento juntos. Ejecuta:  python orders_demo.py


class Order:
    def __init__(self, symbol, side, price, size):   # ej. 1
        self.symbol = symbol
        self.side = side
        self.price = price
        self.size = size

    def notional(self):                              # ej. 2
        return self.price * self.size

    def __repr__(self):                              # ej. 3
        return f"Order({self.side} {self.size} {self.symbol} @ {self.price})"


class Fill:
    def __init__(self, symbol, side, price, size):   # ej. 4
        self.symbol = symbol
        self.side = side
        self.price = price
        self.size = size

    def cash_flow(self):
        sign = -1 if self.side == "buy" else 1
        return sign * self.price * self.size


def main():                                          # ej. 5 y 6
    order = Order("BTCUSDT", "buy", 99950, 0.10)
    print(order)
    print("notional:", order.notional())

    buy = Fill("BTCUSDT", "buy", 99950, 0.10)
    sell = Fill("BTCUSDT", "sell", 100050, 0.10)
    print("cash compra:", buy.cash_flow())
    print("cash venta:", sell.cash_flow())
    print("total:", round(buy.cash_flow() + sell.cash_flow(), 2))
    # Quien suma todos los cash_flows en el tiempo? El PositionTracker (clase 5).


if __name__ == "__main__":
    main()
''',
})

# ---------------------------------------------------------------------------
# L5 — OOP II — OrderBook y PositionTracker
# ---------------------------------------------------------------------------
LESSONS.append({
    "n": 5, "slug": "05-oop-ii-book-portfolio",
    "title": "OOP II — OrderBook y PositionTracker",
    "piece": "clases OrderBook y PositionTracker (composición)",
    "objective": "Construir el libro como objeto que contiene niveles, con métricas como métodos. Y un PositionTracker que consume objetos Fill. Aquí ves cómo los objetos se entrelazan.",
    "frase": "Composición: un OrderBook contiene niveles; un PositionTracker consume Fills. Los objetos se hablan entre sí.",
    "concepts": [
        ("Un objeto que contiene objetos",
         "El OrderBook guarda dos listas (bids y asks). Esas cinco funciones de la clase 2 que recibían book ahora son métodos: book.spread(), book.mid().",
         "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = bids   # [(price, size), ...]\n        self.asks = asks"),
        ("Estado privado y encapsulación",
         "El PositionTracker guarda _cash y _position con guión bajo: 'no me toques desde fuera, usa mis métodos'. apply_fill recibe un objeto Fill y actualiza el estado.",
         "class PositionTracker:\n    def __init__(self):\n        self._cash = 0.0\n        self._position = 0.0"),
        ("Los objetos colaboran",
         "tracker.apply_fill(fill): el tracker no sabe de precios sueltos, sabe de Fills. equity(mark) marca el inventario a mercado. Cada pieza tiene una responsabilidad.",
         "    def equity(self, mark_price):\n        return self._cash + self._position * mark_price"),
    ],
    "build": [
        {"title": "1. OrderBook: un objeto que contiene niveles", "practice": "composición",
         "statement": "Define `OrderBook(bids, asks)` donde cada lado es una lista de tuplas `(price, size)`. El libro **contiene** sus niveles como atributos.",
         "starter": "class OrderBook:\n    def __init__(self, bids, asks):\n        pass\n",
         "validator": "b = OrderBook([(100,1)], [(101,2)])\nassert b.bids == [(100,1)] and b.asks == [(101,2)]\nprint('ok')",
         "solution": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = bids\n        self.asks = asks"},
        {"title": "2. best_bid / best_ask / spread / mid", "practice": "métodos sobre el estado",
         "statement": "Reescribe `OrderBook` con métodos `best_bid()`, `best_ask()`, `spread()` y `mid()`. (Ordena bids desc y asks asc en `__init__`; el mejor es el primero.) Las funciones de la clase 2 ahora son **métodos**.",
         "hint": "`self.bids = sorted(bids, key=lambda x: -x[0])`.",
         "starter": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = sorted(bids, key=lambda x: -x[0])\n        self.asks = sorted(asks, key=lambda x: x[0])\n    def best_bid(self):\n        pass\n    def best_ask(self):\n        pass\n    def spread(self):\n        pass\n    def mid(self):\n        pass\n",
         "validator": "b = OrderBook([(100,1),(99,1)], [(101,1),(102,1)])\nassert b.best_bid()==100 and b.best_ask()==101\nassert b.spread()==1 and b.mid()==100.5\nprint('ok')",
         "solution": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = sorted(bids, key=lambda x: -x[0])\n        self.asks = sorted(asks, key=lambda x: x[0])\n    def best_bid(self):\n        return self.bids[0][0]\n    def best_ask(self):\n        return self.asks[0][0]\n    def spread(self):\n        return self.best_ask() - self.best_bid()\n    def mid(self):\n        return (self.best_bid() + self.best_ask()) / 2"},
        {"title": "3. imbalance() del nivel 1", "practice": "otro método",
         "statement": "Añade a `OrderBook` el método `imbalance()` = (bid_size − ask_size)/(bid_size + ask_size) en el mejor nivel.",
         "starter": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = sorted(bids, key=lambda x: -x[0])\n        self.asks = sorted(asks, key=lambda x: x[0])\n    def imbalance(self):\n        pass\n",
         "validator": "b = OrderBook([(100,3)], [(101,1)])\nassert abs(b.imbalance() - 0.5) < 1e-9\nprint('ok')",
         "solution": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = sorted(bids, key=lambda x: -x[0])\n        self.asks = sorted(asks, key=lambda x: x[0])\n    def imbalance(self):\n        bs = self.bids[0][1]; as_ = self.asks[0][1]\n        return (bs - as_) / (bs + as_)"},
        {"title": "4. PositionTracker: estado privado", "practice": "encapsulación + apply_fill",
         "statement": "Define `PositionTracker` con `_cash=0` y `_position=0` (privados) y `apply_fill(fill)` que sume `fill.cash_flow()` a la caja y `fill.size` (con signo) a la posición.",
         "hint": "El guión bajo dice 'tócalo con métodos, no a mano'.",
         "given": "class Fill:\n    def __init__(self, side, price, size):\n        self.side=side; self.price=price; self.size=size\n    def cash_flow(self):\n        return (-1 if self.side=='buy' else 1)*self.price*self.size\n",
         "starter": "class PositionTracker:\n    def __init__(self):\n        pass\n    def apply_fill(self, fill):\n        pass\n",
         "validator": "t = PositionTracker()\nt.apply_fill(Fill('buy',100,0.5))\nassert abs(t._cash + 50) < 1e-9 and abs(t._position - 0.5) < 1e-9\nprint('ok')",
         "solution": "class PositionTracker:\n    def __init__(self):\n        self._cash = 0.0\n        self._position = 0.0\n    def apply_fill(self, fill):\n        self._cash += fill.cash_flow()\n        self._position += fill.size if fill.side=='buy' else -fill.size"},
        {"title": "5. equity a mercado", "practice": "componer el estado",
         "statement": "Reescribe `PositionTracker` añadiendo `equity(mark_price)` = `_cash + _position * mark_price`.",
         "given": "class Fill:\n    def __init__(self, side, price, size):\n        self.side=side; self.price=price; self.size=size\n    def cash_flow(self):\n        return (-1 if self.side=='buy' else 1)*self.price*self.size\n",
         "starter": "class PositionTracker:\n    def __init__(self):\n        self._cash = 0.0\n        self._position = 0.0\n    def apply_fill(self, fill):\n        self._cash += fill.cash_flow()\n        self._position += fill.size if fill.side=='buy' else -fill.size\n    def equity(self, mark_price):\n        pass\n",
         "validator": "t = PositionTracker()\nt.apply_fill(Fill('buy',100,1))\nassert abs(t.equity(110) - 10) < 1e-9, 'compra a 100, marca a 110 -> equity 10'\nprint('ok')",
         "solution": "class PositionTracker:\n    def __init__(self):\n        self._cash = 0.0\n        self._position = 0.0\n    def apply_fill(self, fill):\n        self._cash += fill.cash_flow()\n        self._position += fill.size if fill.side=='buy' else -fill.size\n    def equity(self, mark_price):\n        return self._cash + self._position * mark_price"},
        {"title": "6. Los dos objetos, juntos", "practice": "composición end-to-end",
         "statement": "Junta las piezas: monta un `OrderBook`, lee su `mid`; crea un `PositionTracker`, aplícale una compra (0.5 @ 100000) y una venta (0.2 @ 100050), y guarda `eq = equity` marcado al `mid` del libro.",
         "hint": "El equity se marca al `book.mid()`.",
         "given": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = sorted(bids, key=lambda x: -x[0]); self.asks = sorted(asks, key=lambda x: x[0])\n    def best_bid(self): return self.bids[0][0]\n    def best_ask(self): return self.asks[0][0]\n    def mid(self): return (self.best_bid()+self.best_ask())/2\nclass Fill:\n    def __init__(self, side, price, size):\n        self.side=side; self.price=price; self.size=size\n    def cash_flow(self):\n        return (-1 if self.side=='buy' else 1)*self.price*self.size\nclass PositionTracker:\n    def __init__(self):\n        self._cash=0.0; self._position=0.0\n    def apply_fill(self, fill):\n        self._cash += fill.cash_flow(); self._position += fill.size if fill.side=='buy' else -fill.size\n    def equity(self, mark):\n        return self._cash + self._position*mark\n",
         "starter": "book = OrderBook([(99990,2.0),(99980,1.0)], [(100010,1.5)])\ntracker = PositionTracker()\n# aplica los dos fills y guarda eq = equity al mid del libro\neq = None\n",
         "validator": "assert abs(book.mid() - 100000) < 1e-9\nassert abs(eq - 10.0) < 1e-9, 'equity al mid debe ser 10'\nprint('ok  eq=%.1f' % eq)",
         "solution": "book = OrderBook([(99990,2.0),(99980,1.0)], [(100010,1.5)])\ntracker = PositionTracker()\ntracker.apply_fill(Fill('buy', 100000, 0.5))\ntracker.apply_fill(Fill('sell', 100050, 0.2))\neq = tracker.equity(book.mid())"},
    ],
    "aux": [
        {"section": "Gimnasio · Calentamiento — repaso exprés de L4",
         "blurb": "Clases, __repr__ y el signo del dinero: tres reps con ETH."},
        {"title": "C1. Order exprés", "practice": "repaso: clase + método",
         "statement": "Escribe `Order` (side, price, size) con `notional()`. Pruébala con ETH.",
         "starter": "class Order:\n    pass\n",
         "validator": "assert abs(Order('buy', 3400, 2.0).notional() - 6800.0) < 1e-9\nprint('ok')",
         "solution": "class Order:\n    def __init__(self, side, price, size):\n        self.side = side; self.price = price; self.size = size\n    def notional(self):\n        return self.price * self.size"},
        {"title": "C2. __repr__ exprés", "practice": "repaso: __repr__",
         "statement": "Dale a `Fill` un `__repr__` exacto: `'Fill(buy 2.0 @ 3400)'`.",
         "starter": "class Fill:\n    def __init__(self, side, price, size):\n        self.side = side; self.price = price; self.size = size\n    def __repr__(self):\n        pass\n\nf = Fill('buy', 3400, 2.0)\n",
         "validator": "assert repr(f) == 'Fill(buy 2.0 @ 3400)'\nprint('ok')",
         "solution": "class Fill:\n    def __init__(self, side, price, size):\n        self.side = side; self.price = price; self.size = size\n    def __repr__(self):\n        return f\"Fill({self.side} {self.size} @ {self.price})\"\n\nf = Fill('buy', 3400, 2.0)"},
        {"title": "C3. Caja exprés", "practice": "repaso: cash_flow",
         "statement": "Con los dos fills dados, calcula `total_cash` sumando sus `cash_flow()`.",
         "given": "class Fill:\n    def __init__(self, side, price, size):\n        self.side = side; self.price = price; self.size = size\n    def cash_flow(self):\n        return -self.price * self.size if self.side == 'buy' else self.price * self.size\n\nfills = [Fill('buy', 3400, 2.0), Fill('sell', 3410, 2.0)]\n",
         "starter": "total_cash = None\n",
         "validator": "assert abs(total_cash - 20.0) < 1e-9\nprint('ok')",
         "solution": "total_cash = sum(f.cash_flow() for f in fills)"},

        {"section": "Gimnasio · Bloque 1 — Composición",
         "blurb": "Objetos que contienen objetos, y métodos que se apoyan en otros métodos."},
        {"title": "A1. La caja que contiene", "practice": "composición mínima",
         "statement": "Escribe `Blotter`: empieza con `self.fills = []`, tiene `add(fill)` que añade y `count()` que dice cuántos lleva.",
         "starter": "class Blotter:\n    pass\n",
         "validator": "b = Blotter()\nb.add('f1'); b.add('f2')\nassert b.count() == 2\nprint('ok')",
         "solution": "class Blotter:\n    def __init__(self):\n        self.fills = []\n    def add(self, fill):\n        self.fills.append(fill)\n    def count(self):\n        return len(self.fills)"},
        {"title": "A2. best_bid y best_ask como métodos", "practice": "métodos sobre el estado",
         "statement": "Escribe `OrderBook` (bids y asks: listas de tuplas `(price, size)`) con `best_bid()` y `best_ask()`.",
         "starter": "class OrderBook:\n    pass\n",
         "validator": "ob = OrderBook([(99950, 0.5), (99940, 0.2)], [(100000, 0.3), (100010, 0.1)])\nassert ob.best_bid() == 99950 and ob.best_ask() == 100000\nprint('ok')",
         "solution": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = bids\n        self.asks = asks\n    def best_bid(self):\n        return max(p for p, s in self.bids)\n    def best_ask(self):\n        return min(p for p, s in self.asks)"},
        {"title": "A3. Métodos que se componen", "practice": "spread() y mid()",
         "statement": "Añade `spread()` y `mid()` que se apoyen en `best_bid()` / `best_ask()` (no repitas los max/min).",
         "starter": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = bids; self.asks = asks\n    def best_bid(self):\n        return max(p for p, s in self.bids)\n    def best_ask(self):\n        return min(p for p, s in self.asks)\n    def spread(self):\n        pass\n    def mid(self):\n        pass\n\nob = OrderBook([(99950, 0.5)], [(100000, 0.3)])\n",
         "validator": "assert ob.spread() == 50\nassert ob.mid() == 99975.0\nprint('ok')",
         "solution": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = bids; self.asks = asks\n    def best_bid(self):\n        return max(p for p, s in self.bids)\n    def best_ask(self):\n        return min(p for p, s in self.asks)\n    def spread(self):\n        return self.best_ask() - self.best_bid()\n    def mid(self):\n        return (self.best_bid() + self.best_ask()) / 2\n\nob = OrderBook([(99950, 0.5)], [(100000, 0.3)])"},
        {"title": "A4. El nivel más gordo", "practice": "recorrer el estado propio",
         "statement": "Añade `biggest_bid()`: el **precio** del bid con más tamaño (recorre `self.bids` con un for).",
         "given": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = bids; self.asks = asks\n",
         "starter": "class OrderBook(OrderBook):\n    def biggest_bid(self):\n        pass\n\nob = OrderBook([(99950, 0.5), (99940, 1.2), (99930, 0.8)], [])\n",
         "validator": "assert ob.biggest_bid() == 99940, 'el de mas size, no el de mejor precio'\nprint('ok')",
         "solution": "class OrderBook(OrderBook):\n    def biggest_bid(self):\n        best_price, best_size = self.bids[0]\n        for price, size in self.bids:\n            if size > best_size:\n                best_price, best_size = price, size\n        return best_price\n\nob = OrderBook([(99950, 0.5), (99940, 1.2), (99930, 0.8)], [])"},

        {"section": "Gimnasio · Bloque 2 — Encapsulación",
         "blurb": "Estado privado y la puerta única: la contabilidad que no se puede desincronizar."},
        {"title": "A5. La cartera cerrada", "practice": "estado privado + puerta",
         "statement": "Escribe `Wallet`: `_cash` empieza en 0 (privado), `deposit(x)` lo aumenta y `balance()` lo devuelve.",
         "starter": "class Wallet:\n    pass\n",
         "validator": "w = Wallet()\nw.deposit(100); w.deposit(50)\nassert w.balance() == 150\nprint('ok')",
         "solution": "class Wallet:\n    def __init__(self):\n        self._cash = 0\n    def deposit(self, x):\n        self._cash = self._cash + x\n    def balance(self):\n        return self._cash"},
        {"title": "A6. La puerta única", "practice": "apply_fill sobre privados",
         "statement": "Escribe `TrackerMini` con `_cash` y `_position` privados, `apply_fill(side, price, size)` (compra: caja baja y posición sube), y `cash()` / `position()` para leer.",
         "starter": "class TrackerMini:\n    pass\n",
         "validator": "t = TrackerMini()\nt.apply_fill('buy', 99950, 0.5)\nt.apply_fill('sell', 100050, 0.2)\nassert abs(t.cash() - (-29965.0)) < 1e-9\nassert abs(t.position() - 0.3) < 1e-9\nprint('ok')",
         "solution": "class TrackerMini:\n    def __init__(self):\n        self._cash = 0.0\n        self._position = 0.0\n    def apply_fill(self, side, price, size):\n        if side == 'buy':\n            self._cash -= price * size\n            self._position += size\n        else:\n            self._cash += price * size\n            self._position -= size\n    def cash(self):\n        return self._cash\n    def position(self):\n        return self._position"},
        {"title": "A7. equity a mercado", "practice": "componer el estado",
         "statement": "Añade `equity(mark)` = caja + posición × mark. Con los fills dados debe salir 35.0.",
         "starter": "class TrackerMini:\n    def __init__(self):\n        self._cash = 0.0; self._position = 0.0\n    def apply_fill(self, side, price, size):\n        if side == 'buy':\n            self._cash -= price * size; self._position += size\n        else:\n            self._cash += price * size; self._position -= size\n    def equity(self, mark):\n        pass\n\nt = TrackerMini()\nt.apply_fill('buy', 99950, 0.5)\nt.apply_fill('sell', 100050, 0.2)\n",
         "validator": "assert abs(t.equity(100000) - 35.0) < 1e-9\nprint('ok ->', t.equity(100000))",
         "solution": "class TrackerMini:\n    def __init__(self):\n        self._cash = 0.0; self._position = 0.0\n    def apply_fill(self, side, price, size):\n        if side == 'buy':\n            self._cash -= price * size; self._position += size\n        else:\n            self._cash += price * size; self._position -= size\n    def equity(self, mark):\n        return self._cash + self._position * mark\n\nt = TrackerMini()\nt.apply_fill('buy', 99950, 0.5)\nt.apply_fill('sell', 100050, 0.2)"},

        {"section": "Gimnasio · Bloque 3 — El toque fino",
         "blurb": "Atributos calculados y el reto que junta las dos piezas de hoy."},
        {"title": "A8. notional como property", "practice": "@property",
         "statement": "Dale a `Position` (qty, price) una **property** `notional` que se lea sin paréntesis.",
         "starter": "class Position:\n    def __init__(self, qty, price):\n        self.qty = qty\n        self.price = price\n    @property\n    def notional(self):\n        pass\n\np = Position(0.5, 99950)\n",
         "validator": "assert abs(p.notional - 49975.0) < 1e-9, 'sin parentesis: property'\nprint('ok')",
         "solution": "class Position:\n    def __init__(self, qty, price):\n        self.qty = qty\n        self.price = price\n    @property\n    def notional(self):\n        return self.qty * self.price\n\np = Position(0.5, 99950)"},
        {"title": "A9. El gran reto: libro + contable", "practice": "los dos objetos juntos",
         "statement": "Compra 0.5 al `best_ask()` del libro (vía `apply_fill`) y guarda `eq = t.equity(ob.mid())`. ¿Por qué sale negativo? Acabas de pagar el medio spread.",
         "given": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = bids; self.asks = asks\n    def best_bid(self):\n        return max(p for p, s in self.bids)\n    def best_ask(self):\n        return min(p for p, s in self.asks)\n    def mid(self):\n        return (self.best_bid() + self.best_ask()) / 2\n\nclass TrackerMini:\n    def __init__(self):\n        self._cash = 0.0; self._position = 0.0\n    def apply_fill(self, side, price, size):\n        if side == 'buy':\n            self._cash -= price * size; self._position += size\n        else:\n            self._cash += price * size; self._position -= size\n    def equity(self, mark):\n        return self._cash + self._position * mark\n\nob = OrderBook([(99950, 0.5)], [(100000, 0.3)])\nt = TrackerMini()\n",
         "starter": "# compra 0.5 al best_ask y calcula eq\neq = None\n",
         "validator": "assert abs(eq - (-12.5)) < 1e-9, 'pagaste el ask y te valoran al mid: medio spread x 0.5'\nprint('ok ->', eq)",
         "solution": "t.apply_fill('buy', ob.best_ask(), 0.5)\neq = t.equity(ob.mid())"},

        {"section": "Para terminar — profundización y el paquete real",
         "blurb": "Profundidad, @property sobre el libro y los objetos pulidos de exchange/."},
        {"title": "A10. Profundidad del libro", "practice": "sumar sobre niveles",
         "statement": "Añade a `OrderBook` el método `depth_buy()` que sume los tamaños de TODOS los bids.",
         "starter": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = bids; self.asks = asks\n    def depth_buy(self):\n        pass\n",
         "validator": "b = OrderBook([(100,1),(99,2)], [(101,1)])\nassert abs(b.depth_buy() - 3) < 1e-9\nprint('ok')",
         "solution": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = bids; self.asks = asks\n    def depth_buy(self):\n        return sum(size for price, size in self.bids)"},
        {"title": "A11. mid como propiedad (@property)", "practice": "@property",
         "statement": "Convierte `mid` en una **propiedad** con `@property`, para llamarlo como `book.mid` (sin paréntesis), como un atributo calculado.",
         "starter": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = sorted(bids, key=lambda x:-x[0]); self.asks = sorted(asks, key=lambda x:x[0])\n    @property\n    def mid(self):\n        pass\n",
         "validator": "b = OrderBook([(100,1)], [(102,1)])\nassert b.mid == 101, 'se llama sin parentesis'\nprint('ok')",
         "solution": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = sorted(bids, key=lambda x:-x[0]); self.asks = sorted(asks, key=lambda x:x[0])\n    @property\n    def mid(self):\n        return (self.bids[0][0] + self.asks[0][0]) / 2"},
        {"title": "A12. Los objetos reales del paquete", "practice": "usar exchange",
         "statement": "Usa los reales de `exchange`: crea un `OrderBook` (con `Level`), mira su `microprice`; crea un `PositionTracker`, aplícale un `Fill` de compra y comprueba que la posición sube.",
         "starter": "from exchange import OrderBook, Level, PositionTracker\nfrom exchange.trades import Fill\nbook = None\ntracker = None\n",
         "validator": "from exchange import OrderBook, PositionTracker\nassert isinstance(book, OrderBook) and book.microprice is not None\nassert isinstance(tracker, PositionTracker) and tracker.position > 0\nprint('ok')",
         "solution": "from exchange import OrderBook, Level, PositionTracker\nfrom exchange.trades import Fill\nbook = OrderBook('BTCUSDT', [Level(100,2)], [Level(101,1)])\ntracker = PositionTracker()\ntracker.apply_fill(Fill(1, 'BTCUSDT', 'buy', 100, 0.5))"},
    ],
    "script_name": "book_demo.py",
    "script": '''# book_demo.py - clase 5: composicion y encapsulacion.
# OrderBook CONTIENE niveles; PositionTracker LLEVA LA CUENTA. Ejecuta: python book_demo.py


class OrderBook:
    def __init__(self, bids, asks):                  # ej. 1: contiene niveles
        self.bids = sorted(bids, key=lambda x: -x[0])
        self.asks = sorted(asks, key=lambda x: x[0])

    def best_bid(self):                              # ej. 2
        return self.bids[0][0]

    def best_ask(self):
        return self.asks[0][0]

    def mid(self):
        return (self.best_bid() + self.best_ask()) / 2


class Fill:
    def __init__(self, side, price, size):
        self.side = side; self.price = price; self.size = size

    def cash_flow(self):
        return (-1 if self.side == "buy" else 1) * self.price * self.size


class PositionTracker:
    def __init__(self):                              # ej. 4: estado privado
        self._cash = 0.0
        self._position = 0.0

    def apply_fill(self, fill):
        self._cash += fill.cash_flow()
        self._position += fill.size if fill.side == "buy" else -fill.size

    def equity(self, mark_price):                    # ej. 5
        return self._cash + self._position * mark_price


def main():                                          # ej. 6: los dos juntos
    book = OrderBook([(99990, 2.0), (99980, 1.0)], [(100010, 1.5)])
    print("mid:", book.mid())

    tracker = PositionTracker()
    tracker.apply_fill(Fill("buy", 100000, 0.5))
    tracker.apply_fill(Fill("sell", 100050, 0.2))
    print("cash:", round(tracker._cash, 2), "| position:", tracker._position)
    print("equity @ mid:", round(tracker.equity(book.mid()), 2))
    # OrderBook contiene; PositionTracker lleva la cuenta: los dos objetos del motor.


if __name__ == "__main__":
    main()
''',
})

# ---------------------------------------------------------------------------
# L6 — OOP III — Herencia, polimorfismo y ABC
# ---------------------------------------------------------------------------
LESSONS.append({
    "n": 6, "slug": "06-oop-iii-inheritance",
    "title": "OOP III — Herencia y polimorfismo",
    "piece": "una familia Strategy de juguete: base + subclases (semilla del framework de L10)",
    "objective": "La pieza que sostendrá todo el framework: muchas estrategias que comparten un esqueleto. Aprendes herencia, sobrescritura, clases abstractas y polimorfismo construyendo tus primeras estrategias de juguete.",
    "frase": "Una clase base define el contrato; cada subclase decide a su manera. Llamar al mismo método sobre objetos distintos y que cada uno responda lo suyo: eso es polimorfismo.",
    "concepts": [
        ("Herencia: heredar y sobrescribir",
         "Una subclase hereda los métodos de su base y puede sobrescribir los que quiera. Compartes el esqueleto y cambias solo lo que difiere.",
         "class Momentum(Strategy):\n    def decide(self, imbalance):\n        return 'buy' if imbalance > 0 else 'sell'"),
        ("Clase abstracta (ABC): el contrato",
         "Una base abstracta con @abstractmethod no se puede instanciar: obliga a las subclases a implementar el método. Es la forma de fijar un contrato.",
         "class Strategy(ABC):\n    @abstractmethod\n    def decide(self, imbalance): ..."),
        ("Polimorfismo: mismo método, respuestas distintas",
         "Recorres una lista de estrategias distintas y llamas a .decide() en todas; cada una responde lo suyo. El código que las usa no necesita saber cuál es cuál.",
         "for s in strategies:\n    print(s.decide(imb))"),
    ],
    "build": [
        {"title": "1. Una clase base con un método", "practice": "clase base",
         "statement": "Define `Strategy` con un método `decide(self, imbalance)` que por defecto devuelva `'hold'`.",
         "starter": "class Strategy:\n    def decide(self, imbalance):\n        pass\n",
         "validator": "assert Strategy().decide(0.5) == 'hold'\nprint('ok')",
         "solution": "class Strategy:\n    def decide(self, imbalance):\n        return 'hold'"},
        {"title": "2. Hereda y sobrescribe", "practice": "herencia + override",
         "statement": "Define `AlwaysBuy(Strategy)` que sobrescriba `decide` para devolver siempre `'buy'`. Debe seguir siendo una `Strategy`.",
         "given": "class Strategy:\n    def decide(self, imbalance):\n        return 'hold'\n",
         "starter": "class AlwaysBuy(Strategy):\n    pass\n",
         "validator": "a = AlwaysBuy()\nassert a.decide(0) == 'buy'\nassert isinstance(a, Strategy), 'AlwaysBuy hereda de Strategy'\nprint('ok')",
         "solution": "class AlwaysBuy(Strategy):\n    def decide(self, imbalance):\n        return 'buy'"},
        {"title": "3. El contrato: clase abstracta", "practice": "ABC + @abstractmethod",
         "statement": "Haz `Strategy` **abstracta** con `@abstractmethod` en `decide`. Ya no se podrá instanciar `Strategy()` directamente; solo subclases que implementen `decide`.",
         "hint": "`from abc import ABC, abstractmethod` y `class Strategy(ABC)`.",
         "starter": "from abc import ABC, abstractmethod\n\nclass Strategy(ABC):\n    pass\n\nclass Buyer(Strategy):\n    def decide(self, imbalance):\n        return 'buy'\n",
         "validator": "try:\n    Strategy(); raise SystemExit('no deberia poder instanciarse')\nexcept TypeError:\n    pass\nassert Buyer().decide(0) == 'buy'\nprint('ok')",
         "solution": "from abc import ABC, abstractmethod\n\nclass Strategy(ABC):\n    @abstractmethod\n    def decide(self, imbalance):\n        ...\n\nclass Buyer(Strategy):\n    def decide(self, imbalance):\n        return 'buy'"},
        {"title": "4. Polimorfismo", "practice": "mismo método, objetos distintos",
         "statement": "Dadas `Momentum` (compra si imbalance>0) y `Contrarian` (vende si imbalance>0), recorre `[Momentum(), Contrarian()]` y guarda en `decisions` lo que decide cada una con `imbalance=0.5`.",
         "given": "class Momentum:\n    def decide(self, imbalance):\n        return 'buy' if imbalance > 0 else 'sell'\nclass Contrarian:\n    def decide(self, imbalance):\n        return 'sell' if imbalance > 0 else 'buy'\n",
         "starter": "strategies = [Momentum(), Contrarian()]\ndecisions = None\n",
         "validator": "assert decisions == ['buy', 'sell'], 'momentum compra, contrarian vende'\nprint('ok ', decisions)",
         "solution": "strategies = [Momentum(), Contrarian()]\ndecisions = [s.decide(0.5) for s in strategies]"},
        {"title": "5. super() en el __init__", "practice": "reutilizar la base",
         "statement": "`Strategy.__init__` guarda un `name`. Haz que `Momentum.__init__` llame a `super().__init__('momentum')`.",
         "given": "class Strategy:\n    def __init__(self, name):\n        self.name = name\n",
         "starter": "class Momentum(Strategy):\n    def __init__(self):\n        pass\n",
         "validator": "assert Momentum().name == 'momentum'\nprint('ok')",
         "solution": "class Momentum(Strategy):\n    def __init__(self):\n        super().__init__('momentum')"},
        {"title": "6. Tu familia de estrategias", "practice": "juntar herencia + polimorfismo",
         "statement": "Define `Strategy` abstracta y dos subclases (`Momentum`, `Contrarian`). Recórrelas con `imbalance=0.5` y guarda `decisions`. Esto es justo el patrón que en L10 conectarás al motor.",
         "starter": "from abc import ABC, abstractmethod\n# define Strategy (ABC), Momentum, Contrarian y decisions\n",
         "validator": "assert decisions == ['buy', 'sell']\nfor s in strategies:\n    assert isinstance(s, Strategy)\nprint('ok — tienes una jerarquía de estrategias polimórfica')",
         "solution": "from abc import ABC, abstractmethod\n\nclass Strategy(ABC):\n    @abstractmethod\n    def decide(self, imbalance):\n        ...\n\nclass Momentum(Strategy):\n    def decide(self, imbalance):\n        return 'buy' if imbalance > 0 else 'sell'\n\nclass Contrarian(Strategy):\n    def decide(self, imbalance):\n        return 'sell' if imbalance > 0 else 'buy'\n\nstrategies = [Momentum(), Contrarian()]\ndecisions = [s.decide(0.5) for s in strategies]"},
    ],
    "aux": [
        {"section": "Gimnasio · Calentamiento — repaso exprés de L5",
         "blurb": "Privados, métodos compuestos y equity: tres reps antes de heredar."},
        {"title": "C1. Wallet exprés", "practice": "repaso: estado privado",
         "statement": "Escribe `Wallet` con `_cash = 0`, `deposit(x)` y `balance()`.",
         "starter": "class Wallet:\n    pass\n",
         "validator": "w = Wallet()\nw.deposit(75)\nassert w.balance() == 75\nprint('ok')",
         "solution": "class Wallet:\n    def __init__(self):\n        self._cash = 0\n    def deposit(self, x):\n        self._cash += x\n    def balance(self):\n        return self._cash"},
        {"title": "C2. mid() exprés", "practice": "repaso: métodos compuestos",
         "statement": "Completa `mid()` apoyándote en los otros dos métodos.",
         "starter": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = bids; self.asks = asks\n    def best_bid(self):\n        return max(p for p, s in self.bids)\n    def best_ask(self):\n        return min(p for p, s in self.asks)\n    def mid(self):\n        pass\n\nob = OrderBook([(99950, 0.5)], [(100000, 0.3)])\n",
         "validator": "assert ob.mid() == 99975.0\nprint('ok')",
         "solution": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = bids; self.asks = asks\n    def best_bid(self):\n        return max(p for p, s in self.bids)\n    def best_ask(self):\n        return min(p for p, s in self.asks)\n    def mid(self):\n        return (self.best_bid() + self.best_ask()) / 2\n\nob = OrderBook([(99950, 0.5)], [(100000, 0.3)])"},
        {"title": "C3. equity exprés", "practice": "repaso: la fórmula",
         "statement": "Con `cash = -49975.0` y `position = 0.5`, calcula `eq` al mark 100000.",
         "given": "cash = -49975.0\nposition = 0.5\nmark = 100000\n",
         "starter": "eq = None\n",
         "validator": "assert abs(eq - 25.0) < 1e-9\nprint('ok')",
         "solution": "eq = cash + position * mark"},

        {"section": "Gimnasio · Bloque 1 — Herencia",
         "blurb": "Heredar gratis, sobrescribir lo justo y no copiar el __init__ jamás."},
        {"title": "A1. Hereda gratis", "practice": "subclase mínima",
         "statement": "Con la base dada, escribe `Pasiva(Strategy)` **vacía** (`pass`) y crea `p = Pasiva('p1')`. Todo lo demás llega heredado.",
         "given": "class Strategy:\n    def __init__(self, name):\n        self.name = name\n    def decide(self, imbalance):\n        return 'hold'\n",
         "starter": "# tu subclase y la instancia\np = None\n",
         "validator": "assert p.name == 'p1', 'el __init__ llega heredado'\nassert p.decide(0.9) == 'hold', 'decide tambien'\nprint('ok')",
         "solution": "class Pasiva(Strategy):\n    pass\n\np = Pasiva('p1')"},
        {"title": "A2. Override", "practice": "sobrescribir un método",
         "statement": "Escribe `Agresiva(Strategy)` cuyo `decide` devuelva siempre `'buy'`. El `__init__` sigue siendo el heredado.",
         "given": "class Strategy:\n    def __init__(self, name):\n        self.name = name\n    def decide(self, imbalance):\n        return 'hold'\n",
         "starter": "a = None\n",
         "validator": "assert a.decide(0.0) == 'buy'\nassert a.name == 'a1'\nprint('ok')",
         "solution": "class Agresiva(Strategy):\n    def decide(self, imbalance):\n        return 'buy'\n\na = Agresiva('a1')"},
        {"title": "A3. super().__init__", "practice": "extender el constructor",
         "statement": "Escribe `Umbral(Strategy)` con `__init__(self, name, thr)`: la madre guarda `name` (vía `super()`), la hija añade `self.thr`.",
         "given": "class Strategy:\n    def __init__(self, name):\n        self.name = name\n    def decide(self, imbalance):\n        return 'hold'\n",
         "starter": "class Umbral(Strategy):\n    def __init__(self, name, thr):\n        pass\n\nu = Umbral('u1', 0.6)\n",
         "validator": "assert u.name == 'u1', 'name lo guarda la madre via super()'\nassert u.thr == 0.6\nassert u.decide(0) == 'hold', 'decide sigue heredado'\nprint('ok')",
         "solution": "class Umbral(Strategy):\n    def __init__(self, name, thr):\n        super().__init__(name)\n        self.thr = thr\n\nu = Umbral('u1', 0.6)"},
        {"title": "A4. La cadena de búsqueda", "practice": "de la hija a la madre",
         "statement": "Con las clases dadas, guarda `r1 = H1('x').describe()` y `r2 = H2('x').describe()`. ¿Quién responde en cada caso?",
         "given": "class Base:\n    def __init__(self, name):\n        self.name = name\n    def describe(self):\n        return 'base'\n\nclass H1(Base):\n    pass\n\nclass H2(Base):\n    def describe(self):\n        return 'hija'\n",
         "starter": "r1 = None\nr2 = None\n",
         "validator": "assert r1 == 'base', 'H1 no tiene describe: sube a la madre'\nassert r2 == 'hija', 'H2 lo sobrescribio: gana su version'\nprint('ok')",
         "solution": "r1 = H1('x').describe()\nr2 = H2('x').describe()"},

        {"section": "Gimnasio · Bloque 2 — Polimorfismo",
         "blurb": "Una llamada, muchas respuestas — y la letra pequeña honesta."},
        {"title": "A5. El bucle polimórfico", "practice": "misma llamada, respuestas distintas",
         "statement": "Monta `familia = [Strategy('b'), Momentum('m'), Contraria('c')]` y construye `decisions` llamando `s.decide(0.5)` a cada una en un bucle.",
         "given": "class Strategy:\n    def __init__(self, name):\n        self.name = name\n    def decide(self, imbalance):\n        return 'hold'\n\nclass Momentum(Strategy):\n    def decide(self, imbalance):\n        if imbalance > 0.3:\n            return 'buy'\n        if imbalance < -0.3:\n            return 'sell'\n        return 'hold'\n\nclass Contraria(Strategy):\n    def decide(self, imbalance):\n        if imbalance > 0.3:\n            return 'sell'\n        if imbalance < -0.3:\n            return 'buy'\n        return 'hold'\n",
         "starter": "familia = None\ndecisions = None\n",
         "validator": "assert decisions == ['hold', 'buy', 'sell'], 'tres clases, tres respuestas a la MISMA llamada'\nprint('ok ->', decisions)",
         "solution": "familia = [Strategy('b'), Momentum('m'), Contraria('c')]\ndecisions = []\nfor s in familia:\n    decisions.append(s.decide(0.5))"},
        {"title": "A6. Censo de la familia", "practice": "isinstance en el bucle",
         "statement": "En `mezcla` hay estrategias y un intruso. Cuenta en `n_strats` cuántos elementos son `Strategy` (usa `isinstance`).",
         "given": "class Strategy:\n    def __init__(self, name):\n        self.name = name\n    def decide(self, imbalance):\n        return 'hold'\n\nclass Momentum(Strategy):\n    pass\n\nmezcla = [Strategy('b'), Momentum('m'), 'no soy estrategia', Momentum('m2')]\n",
         "starter": "n_strats = 0\n",
         "validator": "assert n_strats == 3, 'las Momentum tambien son Strategy'\nprint('ok')",
         "solution": "n_strats = 0\nfor x in mezcla:\n    if isinstance(x, Strategy):\n        n_strats = n_strats + 1"},
        {"title": "A7. La impostora (duck typing)", "practice": "la letra pequeña honesta",
         "statement": "`Impostora` NO hereda de `Strategy` pero tiene `decide`. Guarda `llama = Impostora().decide(0.9)` y `es_strategy = isinstance(Impostora(), Strategy)`. Python permite lo primero aunque lo segundo sea False — el bucle funciona por el **método**, no por la familia.",
         "given": "class Strategy:\n    def __init__(self, name):\n        self.name = name\n    def decide(self, imbalance):\n        return 'hold'\n\nclass Impostora:\n    def decide(self, imbalance):\n        return 'buy'\n",
         "starter": "llama = None\nes_strategy = None\n",
         "validator": "assert llama == 'buy'\nassert es_strategy is False\nprint('ok — duck typing: si anda como pato y decide como pato...')",
         "solution": "llama = Impostora().decide(0.9)\nes_strategy = isinstance(Impostora(), Strategy)"},

        {"section": "Gimnasio · Bloque 3 — El contrato ABC",
         "blurb": "Del 'deberías implementar decide' al 'no existes sin decide'."},
        {"title": "A8. Firma el contrato", "practice": "implementar el abstracto",
         "statement": "Con la ABC dada, escribe `Completa(Strategy)` que implemente `decide` devolviendo `'hold'`. Instánciala — ahora sí se puede.",
         "given": "from abc import ABC, abstractmethod\n\nclass Strategy(ABC):\n    @abstractmethod\n    def decide(self, imbalance): ...\n",
         "starter": "c = None\n",
         "validator": "assert c.decide(0.5) == 'hold'\nprint('ok — con decide implementado, la ABC te deja pasar')",
         "solution": "class Completa(Strategy):\n    def decide(self, imbalance):\n        return 'hold'\n\nc = Completa()"},
        {"title": "A9. Contrato + super", "practice": "ABC con __init__ común",
         "statement": "La ABC dada guarda `name` en su `__init__`. Escribe `Mini(Strategy)` que use `super().__init__(name)` y decida `'buy'` si `imbalance > 0`, si no `'sell'`.",
         "given": "from abc import ABC, abstractmethod\n\nclass Strategy(ABC):\n    def __init__(self, name):\n        self.name = name\n    @abstractmethod\n    def decide(self, imbalance): ...\n",
         "starter": "class Mini(Strategy):\n    pass\n\nm = None\n",
         "validator": "assert m.name == 'm1'\nassert m.decide(0.2) == 'buy' and m.decide(-0.2) == 'sell'\nprint('ok')",
         "solution": "class Mini(Strategy):\n    def __init__(self, name):\n        super().__init__(name)\n    def decide(self, imbalance):\n        return 'buy' if imbalance > 0 else 'sell'\n\nm = Mini('m1')"},

        {"section": "Para terminar — profundización",
         "blurb": "isinstance con la familia completa, por qué la ABC protege, y la estrategia que anticipa L10."},
        {"title": "A10. isinstance y la familia", "practice": "comprobar el tipo",
         "statement": "Con `Momentum(Strategy)`, comprueba que una instancia es a la vez `Momentum` y `Strategy`. Guarda `es_momentum` y `es_strategy`.",
         "given": "class Strategy:\n    pass\nclass Momentum(Strategy):\n    pass\nm = Momentum()\n",
         "starter": "es_momentum = None\nes_strategy = None\n",
         "validator": "assert es_momentum is True and es_strategy is True\nprint('ok')",
         "solution": "es_momentum = isinstance(m, Momentum)\nes_strategy = isinstance(m, Strategy)"},
        {"title": "A11. La ABC obliga a implementar", "practice": "por qué sirve @abstractmethod",
         "statement": "Una subclase que NO implementa el método abstracto tampoco se puede instanciar. Comprueba que instanciar `Incompleta()` lanza `TypeError`.",
         "given": "from abc import ABC, abstractmethod\nclass Strategy(ABC):\n    @abstractmethod\n    def decide(self, imbalance): ...\nclass Incompleta(Strategy):\n    pass\n",
         "starter": "fallo = None  # ponlo a True si Incompleta() lanza TypeError\n",
         "validator": "assert fallo is True\nprint('ok — la ABC te protege de subclases a medio hacer')",
         "solution": "try:\n    Incompleta()\n    fallo = False\nexcept TypeError:\n    fallo = True"},
        {"title": "A12. Una estrategia con umbral", "practice": "subclase con parámetro (anticipa L10)",
         "statement": "Define `ImbalanceStrategy(Strategy)` con un umbral `thr` en `__init__`: `decide(imbalance)` devuelve `'buy'` si `imbalance > thr`, `'sell'` si `< -thr`, si no `'hold'`. Es justo la idea que en la clase 11 se enchufa al motor.",
         "given": "from abc import ABC, abstractmethod\nclass Strategy(ABC):\n    @abstractmethod\n    def decide(self, imbalance): ...\n",
         "starter": "class ImbalanceStrategy(Strategy):\n    def __init__(self, thr=0.3):\n        pass\n    def decide(self, imbalance):\n        pass\n",
         "validator": "s = ImbalanceStrategy(0.3)\nassert s.decide(0.5) == 'buy'\nassert s.decide(-0.5) == 'sell'\nassert s.decide(0.0) == 'hold'\nprint('ok')",
         "solution": "class ImbalanceStrategy(Strategy):\n    def __init__(self, thr=0.3):\n        self.thr = thr\n    def decide(self, imbalance):\n        if imbalance > self.thr:\n            return 'buy'\n        if imbalance < -self.thr:\n            return 'sell'\n        return 'hold'"},
    ],
    "script_name": "strategies_toy.py",
    "script": '''# strategies_toy.py - tu primera familia de estrategias (clase 6).
# Herencia + polimorfismo: la semilla del framework Strategy de la clase 10.
# Ejecuta:  python strategies_toy.py
from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def decide(self, imbalance):
        ...


class Momentum(Strategy):          # sigue al mercado
    def decide(self, imbalance):
        return "buy" if imbalance > 0 else "sell"


class Contrarian(Strategy):        # apuesta contra el mercado
    def decide(self, imbalance):
        return "sell" if imbalance > 0 else "buy"


def main():
    strategies = [Momentum(), Contrarian()]
    for imbalance in (0.5, -0.5):
        decisions = [s.decide(imbalance) for s in strategies]
        print("imbalance", imbalance, "->", decisions)
    # mismo bucle, estrategias distintas: eso es polimorfismo.


if __name__ == "__main__":
    main()
''',
})
