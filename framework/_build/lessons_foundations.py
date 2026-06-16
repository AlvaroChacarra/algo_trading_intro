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
        {"title": "1. Fábrica de órdenes", "practice": "funciones que devuelven dicts",
         "statement": "Escribe `make_order(symbol, side, price, size)` que devuelva el dict de orden.",
         "starter": "def make_order(symbol, side, price, size):\n    pass\n",
         "validator": "o = make_order('BTCUSDT','buy',100,0.5)\nassert o == {'symbol':'BTCUSDT','side':'buy','price':100,'size':0.5}\nprint('ok')",
         "solution": "def make_order(symbol, side, price, size):\n    return {'symbol': symbol, 'side': side, 'price': price, 'size': size}"},
        {"title": "2. Añade al libro", "practice": "mutar una lista",
         "statement": "Escribe `add_order(book, order)` que añada la orden y devuelva el libro.",
         "starter": "def add_order(book, order):\n    pass\n",
         "validator": "b = add_order([], {'side':'buy'})\nassert b == [{'side':'buy'}]\nprint('ok')",
         "solution": "def add_order(book, order):\n    book.append(order)\n    return book"},
        {"title": "3. Cancela por id", "practice": "filtrar una lista",
         "statement": "Escribe `cancel_order(book, order_id)` que devuelva un libro sin la orden cuyo `id` coincide.",
         "given": "book = [{'id':1,'side':'buy'},{'id':2,'side':'sell'}]\n",
         "starter": "def cancel_order(book, order_id):\n    pass\n",
         "validator": "out = cancel_order(book, 1)\nassert out == [{'id':2,'side':'sell'}]\nprint('ok')",
         "solution": "def cancel_order(book, order_id):\n    return [o for o in book if o['id'] != order_id]"},
        {"title": "4. Mejor bid y mejor ask", "practice": "recorrer con condición",
         "statement": "Escribe `best_bid(book)` y `best_ask(book)` (precio buy más alto, sell más bajo).",
         "given": "book = [{'side':'buy','price':99980},{'side':'sell','price':100010},{'side':'buy','price':99990}]\n",
         "starter": "def best_bid(book):\n    pass\n\ndef best_ask(book):\n    pass\n",
         "validator": "assert best_bid(book) == 99990\nassert best_ask(book) == 100010\nprint('ok')",
         "solution": "def best_bid(book):\n    return max(o['price'] for o in book if o['side']=='buy')\n\ndef best_ask(book):\n    return min(o['price'] for o in book if o['side']=='sell')"},
        {"title": "5. Imbalance del libro", "practice": "ratio compra/venta",
         "statement": "Escribe `imbalance(book)` = (vol_buy - vol_sell) / (vol_buy + vol_sell), en [-1, 1].",
         "given": "book = [{'side':'buy','size':3},{'side':'sell','size':1}]\n",
         "starter": "def imbalance(book):\n    pass\n",
         "validator": "assert abs(imbalance(book) - 0.5) < 1e-9, 'imbalance debe ser 0.5'\nprint('ok')",
         "solution": "def imbalance(book):\n    b = sum(o['size'] for o in book if o['side']=='buy')\n    s = sum(o['size'] for o in book if o['side']=='sell')\n    return (b - s) / (b + s)"},
    ],
    "aux": [
        {"title": "A1. Spread y mid", "practice": "componer funciones",
         "statement": "Usando best_bid/best_ask, escribe `spread(book)` y `mid(book)`.",
         "given": "def best_bid(book):\n    return max(o['price'] for o in book if o['side']=='buy')\ndef best_ask(book):\n    return min(o['price'] for o in book if o['side']=='sell')\nbook = [{'side':'buy','price':100},{'side':'sell','price':102}]\n",
         "starter": "def spread(book):\n    pass\ndef mid(book):\n    pass\n",
         "validator": "assert spread(book) == 2\nassert mid(book) == 101\nprint('ok')",
         "solution": "def spread(book):\n    return best_ask(book) - best_bid(book)\ndef mid(book):\n    return (best_bid(book) + best_ask(book)) / 2"},
        {"title": "A2. Nocional total", "practice": "acumular sobre el libro",
         "statement": "Escribe `total_notional(book)` = suma de price*size de todas las órdenes.",
         "given": "book = [{'price':100,'size':0.5},{'price':200,'size':0.25}]\n",
         "starter": "def total_notional(book):\n    pass\n",
         "validator": "assert abs(total_notional(book) - 100) < 1e-9\nprint('ok')",
         "solution": "def total_notional(book):\n    return sum(o['price'] * o['size'] for o in book)"},
        {"title": "A3. Cuenta el problema", "practice": "reflexión + conteo",
         "statement": "Define `funcs_que_reciben_book = 5` (add, cancel, best_bid, best_ask, imbalance). En la próxima clase, todas serán métodos de un objeto `OrderBook`.",
         "starter": "funcs_que_reciben_book = None\n",
         "validator": "assert funcs_que_reciben_book == 5\nprint('ok — eso es composición pidiendo una clase')",
         "solution": "funcs_que_reciben_book = 5"},
    ],
})

# ---------------------------------------------------------------------------
# L3 — OOP I — Order y Trade
# ---------------------------------------------------------------------------
LESSONS.append({
    "n": 3, "slug": "03-oop-i-order-trade",
    "title": "OOP I — Order y Trade",
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
        {"title": "1. La clase Order", "practice": "class e __init__",
         "statement": "Define `Order` con `__init__(self, symbol, side, price, size)` que guarde los 4 como atributos.",
         "starter": "class Order:\n    def __init__(self, symbol, side, price, size):\n        pass\n",
         "validator": "o = Order('BTCUSDT','buy',100,0.5)\nassert o.symbol=='BTCUSDT' and o.side=='buy' and o.price==100 and o.size==0.5\nprint('ok')",
         "solution": "class Order:\n    def __init__(self, symbol, side, price, size):\n        self.symbol = symbol\n        self.side = side\n        self.price = price\n        self.size = size"},
        {"title": "2. Método notional", "practice": "métodos",
         "statement": "Añade `notional(self)` que devuelva `price * size`.",
         "starter": "class Order:\n    def __init__(self, symbol, side, price, size):\n        self.symbol = symbol; self.side = side\n        self.price = price; self.size = size\n    def notional(self):\n        pass\n",
         "validator": "o = Order('X','buy',100,0.5)\nassert abs(o.notional() - 50) < 1e-9\nprint('ok')",
         "solution": "class Order:\n    def __init__(self, symbol, side, price, size):\n        self.symbol = symbol; self.side = side\n        self.price = price; self.size = size\n    def notional(self):\n        return self.price * self.size"},
        {"title": "3. __repr__ legible", "practice": "dunder methods",
         "statement": "Añade `__repr__(self)` que devuelva, p.ej., `'Order(buy 0.5 X @ 100)'`.",
         "starter": "class Order:\n    def __init__(self, symbol, side, price, size):\n        self.symbol=symbol; self.side=side; self.price=price; self.size=size\n    def __repr__(self):\n        pass\n",
         "validator": "o = Order('X','buy',100,0.5)\nassert repr(o) == 'Order(buy 0.5 X @ 100)', repr(o)\nprint('ok')",
         "solution": "class Order:\n    def __init__(self, symbol, side, price, size):\n        self.symbol=symbol; self.side=side; self.price=price; self.size=size\n    def __repr__(self):\n        return f'Order({self.side} {self.size} {self.symbol} @ {self.price})'"},
        {"title": "4. La clase Fill", "practice": "segunda clase + método",
         "statement": "Define `Fill(symbol, side, price, size)` con método `cash_flow()` (buy negativo, sell positivo).",
         "starter": "class Fill:\n    def __init__(self, symbol, side, price, size):\n        pass\n    def cash_flow(self):\n        pass\n",
         "validator": "assert abs(Fill('X','buy',100,0.5).cash_flow() + 50) < 1e-9\nassert abs(Fill('X','sell',100,0.5).cash_flow() - 50) < 1e-9\nprint('ok')",
         "solution": "class Fill:\n    def __init__(self, symbol, side, price, size):\n        self.symbol=symbol; self.side=side; self.price=price; self.size=size\n    def cash_flow(self):\n        sign = -1 if self.side=='buy' else 1\n        return sign * self.price * self.size"},
        {"title": "5. Úsalas juntas", "practice": "instanciar y operar",
         "statement": "Crea una `Order` de compra y un `Fill` de esa compra; guarda el cash_flow en `flow`.",
         "given": "class Order:\n    def __init__(self,symbol,side,price,size):\n        self.symbol=symbol;self.side=side;self.price=price;self.size=size\nclass Fill:\n    def __init__(self,symbol,side,price,size):\n        self.symbol=symbol;self.side=side;self.price=price;self.size=size\n    def cash_flow(self):\n        return (-1 if self.side=='buy' else 1)*self.price*self.size\n",
         "starter": "order = None\nfill = None\nflow = None\n",
         "validator": "assert isinstance(order, Order) and isinstance(fill, Fill)\nassert abs(flow + order.notional() if hasattr(order,'notional') else flow + 50) < 1e-9 or abs(flow + 50) < 1e-9\nprint('ok')",
         "solution": "order = Order('BTCUSDT','buy',100,0.5)\nfill = Fill('BTCUSDT','buy',100,0.5)\nflow = fill.cash_flow()  # -50.0"},
    ],
    "aux": [
        {"title": "A1. Lados con seguridad", "practice": "validar en __init__",
         "statement": "Haz que `Order.__init__` lance `ValueError` si `side` no es 'buy' ni 'sell'.",
         "starter": "class Order:\n    def __init__(self, symbol, side, price, size):\n        pass\n",
         "validator": "try:\n    Order('X','byu',1,1); raise SystemExit('deberia fallar')\nexcept ValueError:\n    print('ok')",
         "solution": "class Order:\n    def __init__(self, symbol, side, price, size):\n        if side not in ('buy','sell'):\n            raise ValueError('side debe ser buy o sell')\n        self.symbol=symbol; self.side=side; self.price=price; self.size=size"},
        {"title": "A2. El paquete real", "practice": "usar exchange.orders",
         "statement": "Importa `Order` y `Side` de `exchange.orders` y crea una orden de compra. Comprueba `order.notional()`.",
         "starter": "from exchange.orders import Order, Side\norder = None\n",
         "validator": "from exchange.orders import Order\nassert isinstance(order, Order)\nassert abs(order.notional() - order.price*order.size) < 1e-9\nprint('ok')",
         "solution": "from exchange.orders import Order, Side\norder = Order('BTCUSDT', Side.BUY, 0.5, price=100)"},
    ],
})

# ---------------------------------------------------------------------------
# L4 — OOP II — OrderBook y PositionTracker
# ---------------------------------------------------------------------------
LESSONS.append({
    "n": 4, "slug": "04-oop-ii-book-portfolio",
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
        {"title": "1. OrderBook con niveles", "practice": "atributos que son listas",
         "statement": "Define `OrderBook(bids, asks)` donde cada lado es una lista de tuplas `(price, size)`.",
         "starter": "class OrderBook:\n    def __init__(self, bids, asks):\n        pass\n",
         "validator": "b = OrderBook([(100,1)], [(101,2)])\nassert b.bids == [(100,1)] and b.asks == [(101,2)]\nprint('ok')",
         "solution": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = bids\n        self.asks = asks"},
        {"title": "2. best_bid / best_ask / spread / mid", "practice": "métodos sobre estado",
         "statement": "Añade métodos `best_bid()`, `best_ask()`, `spread()`, `mid()`. (bids ordenados desc, asks asc; el mejor es el primero.)",
         "given": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = sorted(bids, key=lambda x:-x[0])\n        self.asks = sorted(asks, key=lambda x:x[0])\n",
         "starter": "    # añade los métodos dentro de la clase de arriba\n    pass\n",
         "validator": "b = OrderBook([(100,1),(99,1)], [(101,1),(102,1)])\nassert b.best_bid()==100 and b.best_ask()==101\nassert b.spread()==1 and b.mid()==100.5\nprint('ok')",
         "solution": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = sorted(bids, key=lambda x:-x[0])\n        self.asks = sorted(asks, key=lambda x:x[0])\n    def best_bid(self):\n        return self.bids[0][0]\n    def best_ask(self):\n        return self.asks[0][0]\n    def spread(self):\n        return self.best_ask() - self.best_bid()\n    def mid(self):\n        return (self.best_bid() + self.best_ask()) / 2"},
        {"title": "3. Imbalance del nivel 1", "practice": "método con cálculo",
         "statement": "Añade `imbalance()` = (bid_size - ask_size)/(bid_size + ask_size) en el mejor nivel.",
         "given": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = sorted(bids, key=lambda x:-x[0])\n        self.asks = sorted(asks, key=lambda x:x[0])\n",
         "starter": "    def imbalance(self):\n        pass\n",
         "validator": "b = OrderBook([(100,3)], [(101,1)])\nassert abs(b.imbalance() - 0.5) < 1e-9\nprint('ok')",
         "solution": "class OrderBook:\n    def __init__(self, bids, asks):\n        self.bids = sorted(bids, key=lambda x:-x[0])\n        self.asks = sorted(asks, key=lambda x:x[0])\n    def imbalance(self):\n        bs = self.bids[0][1]; as_ = self.asks[0][1]\n        return (bs - as_) / (bs + as_)"},
        {"title": "4. PositionTracker", "practice": "estado privado",
         "statement": "Define `PositionTracker` con `_cash=0`, `_position=0` y `apply_fill(fill)` que sume `fill.cash_flow()` a cash y `fill.size` (con signo) a position.",
         "given": "class Fill:\n    def __init__(self, side, price, size):\n        self.side=side; self.price=price; self.size=size\n    def cash_flow(self):\n        return (-1 if self.side=='buy' else 1)*self.price*self.size\n",
         "starter": "class PositionTracker:\n    def __init__(self):\n        pass\n    def apply_fill(self, fill):\n        pass\n",
         "validator": "t = PositionTracker()\nt.apply_fill(Fill('buy',100,0.5))\nassert abs(t._cash + 50) < 1e-9 and abs(t._position - 0.5) < 1e-9\nprint('ok')",
         "solution": "class PositionTracker:\n    def __init__(self):\n        self._cash = 0.0\n        self._position = 0.0\n    def apply_fill(self, fill):\n        self._cash += fill.cash_flow()\n        self._position += fill.size if fill.side=='buy' else -fill.size"},
        {"title": "5. Equity a mercado", "practice": "componer estado",
         "statement": "Añade `equity(mark_price)` = cash + position * mark_price.",
         "given": "class Fill:\n    def __init__(self, side, price, size):\n        self.side=side; self.price=price; self.size=size\n    def cash_flow(self):\n        return (-1 if self.side=='buy' else 1)*self.price*self.size\nclass PositionTracker:\n    def __init__(self):\n        self._cash=0.0; self._position=0.0\n    def apply_fill(self, fill):\n        self._cash += fill.cash_flow()\n        self._position += fill.size if fill.side=='buy' else -fill.size\n",
         "starter": "    def equity(self, mark_price):\n        pass\n",
         "validator": "t = PositionTracker()\nt.apply_fill(Fill('buy',100,1))\nassert abs(t.equity(110) - 10) < 1e-9, 'compra a 100, marca a 110 -> equity 10'\nprint('ok')",
         "solution": "# dentro de PositionTracker:\n    def equity(self, mark_price):\n        return self._cash + self._position * mark_price"},
    ],
    "aux": [
        {"title": "A1. El paquete real: OrderBook", "practice": "usar exchange",
         "statement": "Importa `OrderBook` y `Level` de `exchange`, crea un libro y comprueba `mid` y `microprice`.",
         "starter": "from exchange import OrderBook, Level\nbook = None\n",
         "validator": "from exchange import OrderBook\nassert isinstance(book, OrderBook)\nassert book.mid is not None and book.microprice is not None\nprint('ok')",
         "solution": "from exchange import OrderBook, Level\nbook = OrderBook('BTCUSDT', [Level(100,2)], [Level(101,1)])"},
        {"title": "A2. PositionTracker del paquete", "practice": "usar exchange",
         "statement": "Usa `PositionTracker` y `Fill` de `exchange`: aplica un fill de compra y mira equity.",
         "starter": "from exchange import PositionTracker\nfrom exchange.trades import Fill\ntracker = PositionTracker()\n# aplica un Fill de compra de 0.5 @ 100\n",
         "validator": "assert abs(tracker.equity(100) - 0) < 1e-6, 'comprar a mid no cambia equity'\nassert tracker.position > 0\nprint('ok')",
         "solution": "from exchange import PositionTracker\nfrom exchange.trades import Fill\ntracker = PositionTracker()\ntracker.apply_fill(Fill(1, 'BTCUSDT', 'buy', 100, 0.5))"},
    ],
})
