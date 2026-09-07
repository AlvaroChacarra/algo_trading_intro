"""Small public notebook helpers. Validators are supplied by the lesson emitter."""
from __future__ import annotations

from contextlib import redirect_stdout
import inspect
import io
from pathlib import Path
import subprocess
import sys


class PracticeFeedback(AssertionError):
    """A real failure with a short Jupyter rendering instead of framework frames."""

    def _render_traceback_(self):
        return [str(self)]


def comprobar(exercise_id, namespace=None):
    """Check the current answer; keep technical checks outside the notebook."""
    if namespace is None:
        namespace = inspect.currentframe().f_back.f_globals
    try:
        with redirect_stdout(io.StringIO()):
            exec(compile(CHECKS[exercise_id], f'comprobación {exercise_id}', 'exec'), namespace)
    except Exception as exc:
        message = str(exc) or 'Revisa el resultado esperado de este paso.'
        feedback = message if message.startswith('⏸') else f'↻ {message}'
        raise PracticeFeedback(feedback) from None
    print('✓ Comprobado.')


def comprobar_proyecto(lesson):
    """Read saved learner files in a fresh process, never the reference package."""
    root = Path(__file__).resolve().parents[2]
    runner = root / 'check_project.py'
    if not runner.is_file():
        raise PracticeFeedback('Abre el cuaderno desde tu carpeta de estudio. Consulta GUIA_LOCAL.md.')
    result = subprocess.run([sys.executable, '-B', str(runner), str(lesson)],
                            cwd=root, capture_output=True, text=True, timeout=30)
    if result.returncode:
        problems = [line for line in result.stdout.splitlines()
                    if line.startswith('L') and 'integración OK' not in line]
        detail = '\n'.join(problems) or result.stderr.strip() or result.stdout.strip()
        raise PracticeFeedback('↻ Guarda tus archivos y revisa:\n' + detail)
    print(f'✓ Tu proyecto funciona hasta la clase {lesson}.')


# The emitter appends only public validation code, never private answers.
CHECKS = {}

CHECKS = {'L01-B03': "assert first_mid is not None, '⏸ first_mid sigue en None: completa el ejercicio antes de validar'\nassert last_mid is not None, '⏸ last_mid sigue en None: completa el ejercicio antes de validar'\nassert n_mids is not None, '⏸ n_mids sigue en None: completa el ejercicio antes de validar'\nassert first2 is not None, '⏸ first2 sigue en None: completa el ejercicio antes de validar'\nassert last3 is not None, '⏸ last3 sigue en None: completa el ejercicio antes de validar'\nassert mids == [99, 100, 98, 101, 102], 'añade una observación al final'\nassert first_mid == 99 and last_mid == 102 and n_mids == 5\nassert first2 == [99, 100] and last3 == [98, 101, 102]\nprint('ok')\n", 'L01-B04': "assert average is not None, '⏸ average sigue en None: completa el ejercicio antes de validar'\nassert total_sum is not None, '⏸ total_sum sigue en None: completa el ejercicio antes de validar'\nassert lowest is not None, '⏸ lowest sigue en None: completa el ejercicio antes de validar'\nassert highest is not None, '⏸ highest sigue en None: completa el ejercicio antes de validar'\nassert total == total_sum == 404, 'el acumulador y sum deben coincidir'\nassert average == 101\nassert lowest == 99 and highest == 104\nassert mids == [99, 101, 100, 104]\nprint('ok')\n", 'L01-B05': "assert order_side is not None, '⏸ order_side sigue en None: completa el ejercicio antes de validar'\nassert order_notional is not None, '⏸ order_notional sigue en None: completa el ejercicio antes de validar'\nassert order == {'symbol': 'BTCUSDT', 'side': 'buy', 'price': 100, 'size': 0.5}\nassert order_side == 'buy'\nassert order_notional == 50\nprint('ok')\n", 'L01-A09': "assert ticket is not None, '⏸ ticket sigue en None: completa el ejercicio antes de validar'\nassert ticket == 'BUY 0.5 BTCUSDT @ 99950.00'\nassert price == 99950, 'formatear el ticket conserva el dato numérico'\nprint('ok')\n", 'L01-A07': "assert clean is not None, '⏸ clean sigue en None: completa el ejercicio antes de validar'\nassert is_usdt is not None, '⏸ is_usdt sigue en None: completa el ejercicio antes de validar'\nassert clean == 'BTCUSDT'\nassert is_usdt is True\nassert raw == '  btcusdt ', 'el texto original permanece igual'\nprint('ok')\n", 'L01-A08': "assert bid is not None, '⏸ bid sigue en None: completa el ejercicio antes de validar'\nassert ask is not None, '⏸ ask sigue en None: completa el ejercicio antes de validar'\nassert type(bid) is int and type(ask) is int, 'convierte ambos campos'\nassert (bid, ask) == (99, 101)\nprint('ok')\n", 'L01-A18': "assert btc_pos is not None, '⏸ btc_pos sigue en None: completa el ejercicio antes de validar'\nassert eth_pos is not None, '⏸ eth_pos sigue en None: completa el ejercicio antes de validar'\nassert had_eth is not None, '⏸ had_eth sigue en None: completa el ejercicio antes de validar'\nassert btc_pos == 0.5 and eth_pos == 0 and had_eth is False\nassert abs(positions['BTCUSDT'] - 0.7) < 1e-9\nassert positions['ETHUSDT'] == 1.0 and len(positions) == 2\nprint('ok')\n", 'L01-B06': "assert market_states == ['tight', 'normal', 'normal', 'wide'], 'comprueba ambos límites'\nassert spreads == [20, 21, 60, 61]\nprint('ok')\n", 'L01-A11': "assert can_trade is not None, '⏸ can_trade sigue en None: completa el ejercicio antes de validar'\nassert needs_review is not None, '⏸ needs_review sigue en None: completa el ejercicio antes de validar'\nassert can_trade is False, 'and exige todas las condiciones'\nassert needs_review is True, 'or necesita al menos una condición'\nprint('ok')\n", 'L01-A02': "assert price_2dec is not None, '⏸ price_2dec sigue en None: completa el ejercicio antes de validar'\nassert size_whole is not None, '⏸ size_whole sigue en None: completa el ejercicio antes de validar'\nassert price_2dec == 125.46 and size_whole == 4\nassert raw_price == 125.4567\nprint('ok')\n"}
