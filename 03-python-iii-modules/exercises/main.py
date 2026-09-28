"""Lesson 3 — conecta módulos y construye el programa; consulta enunciado.md."""
# TODO · Ejercicio 2.a: importa make_order de functional y describe de analytics.
# Así main conecta las piezas sin copiar sus implementaciones.


def main():
    # TODO · Ejercicio 2.b: crea orders con compra (99, 2) y venta (101, 3)
    # usando make_order; imprime describe(orders) con la etiqueta 'mercado:'.
    # TODO · Ejercicio 2.c: crea only_buys con una compra (99, 2) y muestra
    # describe(only_buys) como 'solo compras:' para probar el lado ausente.
    # TODO · Ejercicio 3.a: dentro de try, intenta make_order('buy', -10, 1).
    # Es una entrada inválida deliberada para observar el contrato de L2.
    # TODO · Ejercicio 3.b: captura solo ValueError como error e imprime
    # 'orden rechazada:' y error; otros fallos deben seguir siendo visibles.
    pass


# Entrada proporcionada: permite probar desde el ejercicio 2.
# TODO · Ejercicio 4.a: compara esta guarda con una llamada sin condición
# y restáurala después del experimento del enunciado.
if __name__ == '__main__':
    main()
# TODO · Ejercicio 4.b: comprueba en terminal la ejecución y el import silencioso
# con los dos comandos del enunciado; no pegues comandos de terminal aquí.

# TODO · Ejercicio 5.a (OPTIONAL): cambia a import analytics y adapta las DOS
# llamadas de main a analytics.describe(...), para identificar su procedencia.
# TODO · Ejercicio 5.b (OPTIONAL): repite las comprobaciones del ejercicio 4.b;
# cambia la forma de acceder a la función, no el resultado del programa.
