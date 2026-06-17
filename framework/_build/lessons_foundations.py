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
        {"title": "A1. Función nocional", "practice": "funciones",
         "statement": "Escribe `compute_notional(price, size)` que devuelva `price * size`.",
         "starter": "def compute_notional(price, size):\n    pass\n",
         "validator": "assert abs(compute_notional(100, 0.5) - 50) < 1e-9\nprint('ok')",
         "solution": "def compute_notional(price, size):\n    return price * size"},
        {"title": "A2. Mejor bid y mejor ask", "practice": "max / min con filtro",
         "statement": "De `book` (lista de órdenes), saca `best_bid` (precio de compra más alto) y `best_ask` (precio de venta más bajo).",
         "hint": "Filtra por `side` dentro de un `max`/`min` con generador.",
         "given": "book = [\n    {'side':'buy','price':99980,'size':0.1}, {'side':'buy','price':99990,'size':0.2},\n    {'side':'sell','price':100010,'size':0.15}, {'side':'sell','price':100005,'size':0.1},\n]\n",
         "starter": "best_bid = None\nbest_ask = None\n",
         "validator": "assert best_bid == 99990, 'best_bid debe ser 99990'\nassert best_ask == 100005, 'best_ask debe ser 100005'\nprint('ok')",
         "solution": "best_bid = max(o['price'] for o in book if o['side']=='buy')\nbest_ask = min(o['price'] for o in book if o['side']=='sell')"},
        {"title": "A3. El problema que viene: dos activos", "practice": "reflexión → POO",
         "statement": "Imagina que sigues `buy_volume` y `sell_volume` para CADA activo por separado. Con `activos = ['BTCUSDT', 'ETHUSDT']`, ¿cuántas variables de volumen necesitas? Guárdalo en `n_vars`.",
         "hint": "2 variables (buy y sell) por cada activo.",
         "given": "activos = ['BTCUSDT', 'ETHUSDT']\n",
         "starter": "n_vars = None\n",
         "validator": "assert n_vars == 4, '2 por activo x 2 activos = 4 (y con 10 activos, 20...)'\nprint('ok -> anadir activos duplica variables. En la clase 2-3 esto lo resuelven las CLASES.')",
         "solution": "n_vars = len(activos) * 2"},
        {"title": "A4. El alfabeto de la máquina", "practice": "ord y bin (texto → 1s y 0s)",
         "statement": "Como viste en la presentación, cada carácter es un número y ese número son bits. Guarda `code_A = ord('A')` y `bits_A = bin(ord('A'))`.",
         "hint": "`ord` da el código del carácter; `bin` lo pasa a binario.",
         "starter": "code_A = None\nbits_A = None\n",
         "validator": "assert code_A == 65, \"ord('A') es 65\"\nassert bits_A == '0b1000001', 'bin(65) es 0b1000001'\nprint('ok  A ->', code_A, '->', bits_A)",
         "solution": "code_A = ord('A')\nbits_A = bin(ord('A'))"},
        {"title": "A5. Ver el bytecode con dis", "practice": "compilar texto a bytecode",
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
        {"title": "A1. Nocional total del libro", "practice": "acumular sobre el libro",
         "statement": "Escribe `total_notional(book)` = suma de `price * size` de todas las órdenes.",
         "given": "book = [{'price':100,'size':0.5},{'price':200,'size':0.25}]\n",
         "starter": "def total_notional(book):\n    pass\n",
         "validator": "assert abs(total_notional(book) - 100) < 1e-9\nprint('ok')",
         "solution": "def total_notional(book):\n    return sum(o['price'] * o['size'] for o in book)"},
        {"title": "A2. Órdenes con seguridad", "practice": "validar en una función",
         "statement": "Haz que `make_order` lance `ValueError` si `side` no es `'buy'` ni `'sell'`. Las funciones también protegen tus datos.",
         "starter": "def make_order(symbol, side, price, size):\n    pass\n",
         "validator": "try:\n    make_order('X','byu',1,1)\n    raise SystemExit('deberia haber fallado')\nexcept ValueError:\n    pass\nassert make_order('X','buy',1,1)['side'] == 'buy'\nprint('ok')",
         "solution": "def make_order(symbol, side, price, size):\n    if side not in ('buy','sell'):\n        raise ValueError('side debe ser buy o sell')\n    return {'symbol': symbol, 'side': side, 'price': price, 'size': size}"},
        {"title": "A3. Cuenta el problema", "practice": "reflexión → POO",
         "statement": "¿Cuántas de tus funciones reciben `book` como primer argumento (add, cancel, best_bid, best_ask, imbalance, spread, mid)? Guárdalo en `funcs_con_book`. En la clase 3 todas serán **métodos** de un objeto `OrderBook`.",
         "starter": "funcs_con_book = None\n",
         "validator": "assert funcs_con_book == 7\nprint('ok -> un dato + las funciones que lo manosean = un OBJETO (clase 3)')",
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
        {"title": "A1. Importa con alias", "practice": "import ... as",
         "statement": "Importa `order_book` con el alias `ob` y calcula `imbalance` del libro. Guarda `imb`.",
         "given": "book = [{'side':'buy','size':2},{'side':'sell','size':2}]\n",
         "starter": "imb = None\n",
         "validator": "assert abs(imb - 0.0) < 1e-9\nprint('ok')",
         "solution": "import order_book as ob\nimb = ob.imbalance(book)"},
        {"title": "A2. Tu propio tipo de error", "practice": "excepción propia",
         "statement": "Define `class EmptyBookError(Exception)` y una función `top(book)` que la lance si el libro está vacío, o devuelva la primera orden.",
         "starter": "class EmptyBookError(Exception):\n    pass\n\ndef top(book):\n    pass\n",
         "validator": "try:\n    top([]); raise SystemExit('deberia fallar')\nexcept EmptyBookError:\n    pass\nassert top([{'id':1}]) == {'id':1}\nprint('ok')",
         "solution": "class EmptyBookError(Exception):\n    pass\n\ndef top(book):\n    if not book:\n        raise EmptyBookError('el libro está vacío')\n    return book[0]"},
        {"title": "A3. Argumentos por defecto", "practice": "parámetros con valor por defecto",
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
        {"title": "A1. Lados con seguridad", "practice": "validar en __init__",
         "statement": "Haz que `Order.__init__` lance `ValueError` si `side` no es 'buy' ni 'sell'. Un objeto puede proteger sus propios datos.",
         "starter": "class Order:\n    def __init__(self, symbol, side, price, size):\n        pass\n",
         "validator": "try:\n    Order('X','byu',1,1); raise SystemExit('deberia fallar')\nexcept ValueError:\n    pass\nassert Order('X','buy',1,1).side == 'buy'\nprint('ok')",
         "solution": "class Order:\n    def __init__(self, symbol, side, price, size):\n        if side not in ('buy','sell'):\n            raise ValueError('side debe ser buy o sell')\n        self.symbol=symbol; self.side=side; self.price=price; self.size=size"},
        {"title": "A2. El Order real del paquete", "practice": "usar exchange.orders",
         "statement": "Importa `Order` y `Side` de `exchange.orders` (la versión pulida que arrastrarás todo el curso) y crea una orden de compra. Comprueba `order.notional()`.",
         "starter": "from exchange.orders import Order, Side\norder = None\n",
         "validator": "from exchange.orders import Order\nassert isinstance(order, Order)\nassert abs(order.notional() - order.price*order.size) < 1e-9\nprint('ok')",
         "solution": "from exchange.orders import Order, Side\norder = Order('BTCUSDT', Side.BUY, 0.5, price=100)"},
        {"title": "A3. Side como Enum", "practice": "enums seguros",
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
        {"title": "A1. Profundidad del libro", "practice": "sumar sobre niveles",
         "statement": "Añade a `OrderBook` el método `depth_buy()` que sume los tamaños de TODOS los bids.",
         "starter": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = bids; self.asks = asks\n    def depth_buy(self):\n        pass\n",
         "validator": "b = OrderBook([(100,1),(99,2)], [(101,1)])\nassert abs(b.depth_buy() - 3) < 1e-9\nprint('ok')",
         "solution": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = bids; self.asks = asks\n    def depth_buy(self):\n        return sum(size for price, size in self.bids)"},
        {"title": "A2. mid como propiedad (@property)", "practice": "@property",
         "statement": "Convierte `mid` en una **propiedad** con `@property`, para llamarlo como `book.mid` (sin paréntesis), como un atributo calculado.",
         "starter": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = sorted(bids, key=lambda x:-x[0]); self.asks = sorted(asks, key=lambda x:x[0])\n    @property\n    def mid(self):\n        pass\n",
         "validator": "b = OrderBook([(100,1)], [(102,1)])\nassert b.mid == 101, 'se llama sin parentesis'\nprint('ok')",
         "solution": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = sorted(bids, key=lambda x:-x[0]); self.asks = sorted(asks, key=lambda x:x[0])\n    @property\n    def mid(self):\n        return (self.bids[0][0] + self.asks[0][0]) / 2"},
        {"title": "A3. Los objetos reales del paquete", "practice": "usar exchange",
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
        {"title": "A1. isinstance y la familia", "practice": "comprobar el tipo",
         "statement": "Con `Momentum(Strategy)`, comprueba que una instancia es a la vez `Momentum` y `Strategy`. Guarda `es_momentum` y `es_strategy`.",
         "given": "class Strategy:\n    pass\nclass Momentum(Strategy):\n    pass\nm = Momentum()\n",
         "starter": "es_momentum = None\nes_strategy = None\n",
         "validator": "assert es_momentum is True and es_strategy is True\nprint('ok')",
         "solution": "es_momentum = isinstance(m, Momentum)\nes_strategy = isinstance(m, Strategy)"},
        {"title": "A2. La ABC obliga a implementar", "practice": "por qué sirve @abstractmethod",
         "statement": "Una subclase que NO implementa el método abstracto tampoco se puede instanciar. Comprueba que instanciar `Incompleta()` lanza `TypeError`.",
         "given": "from abc import ABC, abstractmethod\nclass Strategy(ABC):\n    @abstractmethod\n    def decide(self, imbalance): ...\nclass Incompleta(Strategy):\n    pass\n",
         "starter": "fallo = None  # ponlo a True si Incompleta() lanza TypeError\n",
         "validator": "assert fallo is True\nprint('ok — la ABC te protege de subclases a medio hacer')",
         "solution": "try:\n    Incompleta()\n    fallo = False\nexcept TypeError:\n    fallo = True"},
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
