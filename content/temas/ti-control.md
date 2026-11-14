---
ids: sistemas-de-control-y-robotica-educativa
refs: oc-ti, g30
---
## Sistemas de control
- **Sistema**: entradas → proceso → salidas. Las OC 2022 mencionan sistemas de control **eléctrico, electrónico, hidráulico y neumático**, entre otros.
- **Lazo abierto**: la salida no influye en el control (tostadora con temporizador, semáforo por tiempo).
- **Lazo cerrado (realimentado)**: un **sensor** mide la salida y el controlador corrige (nevera con termostato, tanque de inodoro con flotador, aire acondicionado).
- Elementos: **sensor** (entrada: luz, temperatura, distancia, humedad), **controlador** (microcontrolador, programa), **actuador** (salida: motor, servomotor, LED, relé, bomba).
- **Automatización**: sistemas que operan sin intervención humana constante.

## Robótica educativa
- **Robot**: máquina programable con sensores, controlador y actuadores que interactúa con el entorno.
- Plataformas: **Arduino** (microcontrolador de hardware libre; entradas/salidas digitales y analógicas; programación en C/C++ o por bloques), **micro:bit**, kits de construcción.
- Conceptos: entrada **digital** (0/1: pulsador) vs **analógica** (rango de valores: potenciómetro, LDR); **PWM** para regular intensidad o velocidad; servomotor (posición) vs motor DC (giro continuo).
- Valor pedagógico: integra mecánica, electrónica y programación (STEM), favorece el trabajo por proyectos, el ensayo-error y el pensamiento computacional.

## Ejemplo
Riego automático escolar: sensor de humedad del suelo → Arduino compara con un umbral → si está seco, activa una bomba (relé) → lazo cerrado.
```
si humedad < umbral: encender bomba
si no: apagar bomba
```

## Trampas frecuentes
- Un temporizador sin sensor es lazo abierto aunque sea "automático".
- El sensor es entrada y el actuador es salida.

## Puntos clave
- Lazo abierto vs cerrado; sensor–controlador–actuador; Arduino/micro:bit; digital vs analógico; robótica como estrategia STEM.
