---
ids: representacion-de-la-informacion-datos-sistema-b
refs: oc-ti
---
## Datos e información
- **Dato**: valor sin interpretar (37,5). **Información**: datos procesados con contexto y significado ("temperatura del paciente: 37,5 °C"). **Conocimiento**: información interpretada y aplicada.
- Las OC 2022 mencionan los **números binarios** y la **comprensión de datos** como contenidos que pueden enseñarse incluso sin computadores.

## Sistema binario
- Base 2: dígitos **0 y 1** (bit). Posiciones: 1, 2, 4, 8, 16, 32, 64, 128…
- **Binario → decimal**: 1011₂ = 8 + 0 + 2 + 1 = **11**.
- **Decimal → binario**: dividir sucesivamente entre 2 y leer los residuos de abajo hacia arriba: 13 → 1101₂.
- Con **n bits** se representan **2ⁿ** valores (8 bits = 256 valores, 0 a 255).
- **Hexadecimal** (base 16: 0–9, A–F): abrevia binario; 4 bits = 1 dígito hex (colores web: #FF0000 = rojo).

## Codificación
- **Texto**: ASCII (7 bits, 128 caracteres; 'A' = 65), **Unicode/UTF-8** (todos los idiomas, tildes y emojis).
- **Imágenes**: mapa de bits (**píxeles**), cada píxel con color **RGB** (3 bytes = 24 bits); resolución; formatos con compresión (JPG con pérdida; PNG sin pérdida) e imágenes **vectoriales** (SVG: formas matemáticas, escalan sin perder calidad).
- **Sonido**: muestreo de la onda (frecuencia de muestreo, bits por muestra).
- **Unidades**: 1 byte = 8 bits; KB, MB, GB, TB.

## Organización y análisis de datos
Tablas, hojas de cálculo, bases de datos, gráficos (barras para comparar, líneas para tendencias, circular para partes de un todo); visualización y lectura crítica de datos.

## Ejemplo
¿Cuántos bits para numerar 30 estudiantes? 2⁵ = 32 ≥ 30 → **5 bits**.
Una imagen de 100 × 100 píxeles en RGB de 24 bits ocupa 10.000 × 3 bytes = 30.000 bytes (≈ 30 KB sin compresión).

## Trampas frecuentes
- 10₂ es dos, no diez.
- JPG pierde calidad al comprimir; PNG no.

## Puntos clave
- Dato vs información; binario ↔ decimal; 2ⁿ valores; hexadecimal; ASCII/Unicode; píxeles y RGB; vector vs mapa de bits.
