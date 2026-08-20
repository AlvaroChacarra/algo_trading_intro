# Guion — Clase 6: OOP III — Herencia y polimorfismo

**Idea central:** una familia `Strategy` — base con el esqueleto, hijas con la personalidad, ABC como contrato — y el momento estrella: **una llamada, muchas respuestas**. Cierra el bloque de fundamentos; es la semilla del framework de L10.

**Formato:** documento interactivo (`oop-iii-inheritance-doc.html`), autocontenido. "Lo cian se toca."

---

## §0 · Hero — el reto (2 min)
- **Decir:** "El curso acaba con vosotros escribiendo VUESTRA estrategia y enchufándola a un motor. Ese enchufe se fabrica hoy. Mirad estas dos clases: solo cambia la decisión; el esqueleto se repite. Con clases o sin ellas, copiarlo es el mismo pecado de L2."
- **Salida:** "Herencia = el esqueleto una vez."

## §1 · Scrollytelling — el árbol genealógico (8 min)
- **0/5 gemelas:** el __init__ duplicado en rojo. "Con 10 estrategias, 10 copias."
- **1/5 la base:** Strategy con decide → 'hold'. "El default más prudente."
- **2/5 heredar:** "ese paréntesis en class Momentum(Strategy) ES la herencia. Una subclase vacía ya funciona — aburrida, pero funciona."
- **3/5 override:** "la hija redefine decide y SU versión gana. Esqueleto en un sitio, personalidad en cada hija."
- **4/5 polimorfismo:** EL momento de la clase. "El bucle no sabe ni le importa qué clase es cada una. Ese desacople es lo que hará enchufable el motor." Léelo despacio: m1 → buy, r1 → sell, base → hold.
- **5/5 ABC:** "de 'deberías implementar decide' a 'NO EXISTES sin decide'. El error se adelanta al mejor momento posible: ya."

## §2 · Base, hija y super() (4 min)
- Recorre los tres estados del simulador: hija sin `__init__` (hereda `name`); hija con `__init__` propio (`threshold` existe pero `name` falta); hija con `super()` (el mismo objeto recibe `name` en la base y `threshold` en la hija).
- Solo después cierra con: **«Madre, haz tu parte»**. La frase resume el mecanismo que ya vieron; no lo sustituye.

## §3 · Polimorfismo vivo (4 min)
- **Cede el teclado:** slider de imbalance en `[-1,+1]`, tres tarjetas respondiendo distinto a la MISMA llamada. Barre de negativo a positivo y comenta los cruces (Momentum y Contraria se espejan; la base, imperturbable).
- La nota final es el contrato con el futuro: "en L10, Backtest hará exactamente este bucle contra el mercado real. El polimorfismo es el enchufe."

## §4 · El contrato ABC (3 min)
- Alterna «comportamiento por defecto» y «contrato obligatorio» con la misma hija incompleta: en el primer modo se crea y devuelve `hold`; en el segundo ni siquiera se crea.
- Activa la tercera prueba: un método decorado con `@abstractmethod` puede contener `return 'hold'` y sigue siendo abstracto. Cierre: **`return` es comportamiento; `@abstractmethod` es contrato**.

## §5 · Quiz (3 min)
- 5 A/B/C: herencia por defecto, override, ABC, polimorfismo, super().

## §6 · Puente + mapa — cierre del bloque (3 min)
- Mapa: L1-L5 ✓, L6 iluminada. **Momento solemne:** "el bloque de fundamentos está completo. Sabéis programar."
- **Puente:** "ahora, el mercado de verdad: 500 snapshots reales de BTCUSDT en L7. Y en L10 esta familia vuelve, enchufada al motor."
- Notebook + gimnasio (15 drills: herencia, super, isinstance, la impostora y la ABC).

## Checklist
- [ ] Heredar gratis; override = su versión gana.
- [ ] super().__init__ = "madre, haz tu parte".
- [ ] Antes de esa frase se ve qué atributo falta cuando la hija reemplaza `__init__`.
- [ ] Polimorfismo: misma llamada, respuestas distintas; el bucle no pregunta clases.
- [ ] ABC: TypeError al instanciar incompleto.
- [ ] Comportamiento por defecto y contrato obligatorio quedan separados.
- [ ] Cierre del bloque de fundamentos + semilla del framework (L10).
