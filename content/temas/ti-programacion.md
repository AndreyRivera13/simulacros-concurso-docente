---
ids: programacion-variables-condicionales-y-ciclos
refs: oc-ti
---
## Conceptos clave
- **Programa**: algoritmo escrito en un **lenguaje de programación** que el computador puede ejecutar (compilado o interpretado). Lenguajes por bloques (**Scratch**, MakeCode, Code.org) y textuales (**Python**, JavaScript).
- **Variable**: espacio con nombre que guarda un valor que puede cambiar. **Constante**: no cambia.
- **Tipos de datos**: entero, real (decimal), texto (cadena/string), booleano (verdadero/falso), listas/arreglos.
- **Operadores**: aritméticos (+ − × / , módulo %), relacionales (=, ≠, <, >, ≤, ≥), lógicos (**Y**, **O**, **NO**).
- **Asignación**: `x = x + 1` significa "toma el valor de x, súmale 1 y guárdalo en x".
- **Condicionales**: si / si no / si no si (`if / else / elif`); condiciones anidadas.
- **Ciclos**: **para** (`for`, número conocido de repeticiones), **mientras** (`while`, se repite mientras la condición sea verdadera; riesgo de **ciclo infinito**), repetir hasta.
- **Contador** (aumenta de 1 en 1) y **acumulador** (suma valores).
- **Funciones / procedimientos**: bloques reutilizables con parámetros (modularidad).
- **Depuración (debugging)**: encontrar y corregir errores de **sintaxis** (mal escrito) y de **lógica** (corre pero da resultados incorrectos).

## Ejemplo (Python)
```
suma = 0
for i in range(1, 6):
    suma = suma + i
print(suma)   # 15
```
```
nota = 3.4
if nota >= 3.0:
    print("Aprueba")
else:
    print("No aprueba")
```

## Trampas frecuentes
- `range(1, 6)` produce 1 a 5 (el límite superior no se incluye).
- Un `while` cuya condición nunca cambia no termina.
- `=` asigna; `==` compara (en Python).

## Puntos clave
- Variables y tipos; operadores; condicionales; ciclos for/while; contador y acumulador; funciones; depuración.
