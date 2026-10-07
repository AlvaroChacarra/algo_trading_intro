"""Datos y dibujo proporcionados para L11; no contiene estrategias ni métricas.

Cinco fotos sintéticas: precios USDT/BTC y tamaños BTC. Los timestamps 0/1
ordenan las dos primeras fotos; las restantes conservan su índice de replay.
No son operaciones históricas ni evidencia de predictividad.
"""

metric_rows = [
    {'timestamp':0,'bid_price_1':99,'bid_size_1':2,
     'ask_price_1':101,'ask_size_1':.4,'ask_price_2':102,'ask_size_2':.6},
    {'timestamp':1,'bid_price_1':101,'bid_size_1':2,
     'ask_price_1':103,'ask_size_1':1},
    {'bid_price_1':99,'bid_size_1':2,'ask_price_1':101,'ask_size_1':1},
    {'bid_price_1':102,'bid_size_1':2,'ask_price_1':104,'ask_size_1':1},
    {'bid_price_1':96,'bid_size_1':2,'ask_price_1':98,'ask_size_1':1},
]


def show_curve(values, initial):
    # Gráfica proporcionada: no es una tarea de programación.
    try:
        from IPython import get_ipython
    except ImportError:
        return
    if get_ipython() is None:
        return
    from IPython.display import SVG, display
    points = [initial] + list(values)
    lo, hi = min(points), max(points)
    span = max(hi-lo, 1)
    coords = ' '.join(f'{45+i*480/max(len(points)-1,1):.1f},{160-(v-lo)*120/span:.1f}'
                      for i,v in enumerate(points))
    display(SVG(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 580 205">'
                f'<rect width="580" height="205" fill="#111827"/>'
                f'<text x="15" y="22" fill="white">Equity · USDT · inicial {initial}</text>'
                f'<polyline points="{coords}" fill="none" stroke="#22d3ee" stroke-width="3"/>'
                f'<text x="35" y="190" fill="white">Inicio → fotos 0–4 · {lo:.1f} a {hi:.1f}</text></svg>'))
