**Metodología de Puntuación del MODULO_FUNDAMENTALES**
El objetivo central de este módulo es sintetizar múltiples dimensiones de la salud financiera de una empresa en un único número manejable (Final Score, de 0 a 100). No confiamos en una sola métrica, sino que triangulamos la realidad desde 5 ángulos distintos.

El puntaje final es una suma ponderada de 5 sub-modelos. Cada uno examina una faceta diferente de la empresa.

1. Piotroski F-Score (Fortaleza Financiera) | Peso: 15%
Este modelo busca empresas financieramente sólidas y que estén mejorando año tras año. Se basa en 9 criterios binarios (pasa/no pasa).

¿Qué evalúa?
Rentabilidad: ¿Es rentable hoy? (ROA > 0), ¿Genera caja real? (CFO > 0), ¿Es la caja mejor que la utilidad contable? (Calidad).
Apalancamiento/Liquidez: ¿Se endeudó menos este año? ¿Tiene más liquidez corriente? ¿Emitió nuevas acciones? (Dilución es malo).
Eficiencia Operativa: ¿Mejoró su margen bruto? ¿Rota sus activos más rápido (vende más con lo mismo)?
Cálculo: Se suman los puntos (0 a 9) y se normalizan a base 10.
9/9 es una fortaleza perfecta. 0/9 es una empresa en deterioro grave.
2. Altman Z-Score (Riesgo de Quiebra) | Peso: 10%
Este es un modelo de "supervivencia". Predice la probabilidad de que la empresa quiebre en los próximos 2 años.

¿Qué evalúa?
Liquidez: Capital de trabajo sobre activos.
Reservas: Utilidades retenidas sobre activos (¿Es una empresa madura con ahorros o quema dinero?).
Rentabilidad Operativa: EBIT sobre activos (El motor del negocio).
Valor de Mercado: ¿Cree el mercado que vale más que sus deudas? (Market Cap / Pasivos).
Escala de Puntuación (Normalizada):
Zona Segura (Z > 2.6): 10 Puntos. (Bajo riesgo).
Zona Gris (1.1 < Z < 2.6): 5 Puntos. (Alerta amarilla).
Zona de Peligro (Z < 1.1): 0 Puntos. (Alto riesgo de insolvencia).
3. Beneish M-Score (Manipulación Contable) | Peso: 5%
El "detector de mentiras". Busca anomalías estadísticas en la contabilidad que sugieran que la gerencia está inflando los números artificialmente (tipo Enron).

¿Qué evalúa? Compara el año actual contra el anterior en 8 variables. Si las ventas suben "demasiado raro" en comparación con el cobro de efectivo, o si la depreciación cambia drásticamente para "maquillar" gastos, el modelo se activa.
Cálculo:
No Manipulación (Probable): 10 Puntos.
Posible Manipulación: 0 Puntos (y levanta una bandera roja ACCOUNTING_RISK).
Nota: Tiene poco peso en la suma porque es un evento raro, pero su función principal es activar la bandera roja.
4. Magic Formula (Calidad + Precio) | Peso: 20%
Inspirado en Joel Greenblatt. Busca comprar "empresas buenas (rentables) a precios baratos".

¿Qué evalúa?
Earnings Yield (EY): ¿Cuánto beneficio operativo (EBIT) me da la empresa por el precio total que pago (Enterprise Value)? Es como el "interés" que recibirías si compraras toda la empresa.
Return on Capital (ROC): ¿Qué tan buena es la empresa reinvirtiendo su propio dinero? (EBIT / Capital Tangible).
Cálculo:
Si el ROC es alto (>20%) -> 5 Puntos.
Si el EY es alto (>10%) -> 5 Puntos.
Suma máxima: 10.0 (Empresa muy rentable y muy barata).
5. Growth & Momentum (Crecimiento y Tendencia) | Peso: 30%
Aquí miramos hacia el futuro y la validación del mercado. No basta con que sea barata y sólida; queremos que esté creciendo y que el mercado ya se haya dado cuenta.

¿Qué evalúa?
Crecimiento (Growth): ¿Han crecido las Ventas y las Utilidades (EPS) en los últimos 3 años? (CAGR).
20% anual: Excelente.

10% anual: Bueno.

Momentum de Precio: ¿La acción está subiendo?
Compara precio actual vs hace 3, 6 y 12 meses. Si la tendencia es alcista en todos los plazos, suma puntos.
Peso: Es el componente más pesado (30%) porque buscamos activos en movimiento, no "trampas de valor" (empresas baratas que se quedan baratas por años).
6. Analyst Upside (Consenso de Analistas) | Peso: 20%
La opinión del mercado institucional.

¿Qué evalúa? Toma el Precio Objetivo Medio de los analistas de Wall Street (según Yahoo Finance) y lo compara con el precio actual.
Calcula el Upside potencial en %.
Cálculo:
Upside > 20%: 10 Puntos (Se espera gran subida).
Upside negativo: 0 Puntos.
La Fórmula Final (The Calculation Engine)
El motor toma todos estos puntajes parciales (ya normalizados a 0-10) y aplica la receta maestra definida en tu 
config.py
:

$$ \text{Score} = (Piotroski \times 0.15) + (Altman \times 0.10) + (Beneish \times 0.05) + (Magic \times 0.20) + (Growth \times 0.30) + (Upside \times 0.20) $$

El resultado se multiplica por 10 para darte el Score Final (0-100).

Interpretación del Semáforo:

🟢 STRONG_BUY (80 - 100): La empresa es una fortaleza, está barata, crece agresivamente y los analistas la aman.
🟢 BUY (65 - 80): Muy sólida, falla en algún punto menor pero es una gran candidata.
🟡 HOLD (30 - 65): Empresa promedio o con señales mixtas (ej: muy rentable pero cara, o barata pero sin crecimiento).
🔴 SELL (< 30): Empresa peligrosa, en deterioro o extremadamente cara sin justificación.
Banderas Rojas (Risk Flags): Independientemente del puntaje, el sistema te avisa si hay peligros mortales:

BANKRUPTCY_RISK: Altman dice que puede quebrar.
ACCOUNTING_RISK: Beneish dice que los números susurran mentiras.