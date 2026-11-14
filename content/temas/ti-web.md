---
ids: aplicaciones-y-paginas-web-con-lenguajes-de-prog
refs: oc-ti
---
## Cómo funciona la Web
- **Cliente** (navegador) solicita una página a un **servidor** mediante **HTTP/HTTPS**; el servidor responde con archivos (HTML, CSS, JavaScript, imágenes).
- **Front-end** (lo que ve el usuario) vs **back-end** (servidor, lógica, bases de datos). **Dominio** + **hosting** (alojamiento).
- **Página estática** (contenido fijo) vs **dinámica** (se genera según datos o usuario).

## Lenguajes del front-end
- **HTML**: estructura y contenido mediante **etiquetas**: `<h1>` títulos, `<p>` párrafos, `<a href="...">` enlaces, `<img src="..." alt="...">` imágenes (el `alt` es clave para la **accesibilidad**), `<ul>/<li>` listas, `<table>`, `<form>`.
- **CSS**: presentación (colores, tipografía, márgenes, distribución); selectores (`p`, `.clase`, `#id`); diseño **responsive** para celulares (media queries).
- **JavaScript**: comportamiento e interactividad (responder a clics, validar formularios, modificar la página).

## Ejemplo mínimo
```
<!DOCTYPE html>
<html>
  <head><title>Mi huerta</title>
    <style>h1 { color: green; }</style></head>
  <body>
    <h1>Huerta escolar</h1>
    <p>Registro de siembra.</p>
    <button onclick="alert('¡Gracias!')">Participar</button>
  </body>
</html>
```

## Aplicaciones
- **Apps móviles**: nativas (Android/iOS) o web; herramientas por bloques como **App Inventor** permiten a estudiantes crear apps con eventos y componentes.
- **Ciclo de desarrollo**: requisitos → diseño (bocetos/wireframes, experiencia de usuario) → programación → pruebas → publicación → mantenimiento.
- **Usabilidad y accesibilidad**: contraste, tamaño de letra, texto alternativo, navegación por teclado.

## Trampas frecuentes
- HTML no es un lenguaje de programación en sentido estricto (es de marcado); la lógica la aporta JavaScript.
- CSS presenta; HTML estructura.

## Puntos clave
- Cliente-servidor y HTTP; HTML (estructura), CSS (estilo), JavaScript (comportamiento); responsive y accesible; App Inventor; ciclo de desarrollo.
