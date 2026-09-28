"""Lesson 4 — conecta la clase de models.py; sigue los apartados de enunciado.md."""
# TODO · Ejercicio 1.b: importa Fill desde models, fuera de main().
# Reutiliza el módulo como en L3; la definición de la clase vive en models.py.


def main():
    # TODO · Ejercicio 2.a: crea buy = Fill('buy', 100, 2) y sell = Fill('sell', 110, 2).
    # Son dos ejecuciones confirmadas distintas, con sus propios atributos.
    # TODO · Ejercicio 2.b: imprime side, price y size de buy, sell y buy de nuevo.
    # Comprueba que crear la venta no cambió los datos de la compra.

    # TODO · Ejercicio 3.b: imprime buy.cash_flow(), sell.cash_flow() y otra
    # consulta a buy.cash_flow(). Predice los signos antes de ejecutar.

    # TODO · Ejercicio 4.a: calcula total_cash sumando los flujos de buy y sell,
    # y remaining_units restando sus tamaños: seguimos dinero y unidades por separado.
    # TODO · Ejercicio 4.b: imprime ambos resultados para comprobar el cierre
    # completo. El enunciado explica cuándo esa caja coincide con el beneficio.

    # TODO · Ejercicio 5.a: crea partial_sell, venta a 110 de UNA unidad.
    # Es una alternativa a sell, no una tercera ejecución que debas acumular.
    # TODO · Ejercicio 5.b: calcula partial_cash con buy y partial_sell y las
    # unidades restantes; imprime ambos para ver por qué caja no siempre es beneficio.

    # TODO · Ejercicio 6.b: imprime buy para ver su representación; después,
    # intenta Fill('buy', -10, 2) en try y captura solo ValueError como error.
    # Imprime 'Ejecución rechazada:' y error para observar la validación proporcionada.

    # TODO · Ejercicio 7.a (OPTIONAL): crea f y g iguales, cambia solo f.price
    # a 110 y compara sus flujos; comprueba que las instancias son independientes.
    # TODO · Ejercicio 7.b (OPTIONAL): vuelve a crear f, guarda f.notional como
    # precio por tamaño y cambia su precio; compara el valor guardado y el recalculado.
    pass


# Guarda proporcionada desde L3: importar este módulo no ejecuta main().
if __name__ == '__main__':
    main()

# TODO · Ejercicio 6.c: ejecuta en terminal los dos comandos del enunciado
# para comprobar resultados e import silencioso; conserva la guarda proporcionada.
