
## Archivos estáticos
¿Que hacer con las imágenes, hojas de estilo, scripts, etc.?

Una buena idea es ponerlos dentro de una carpeta `static`, que es como están en el proyecto por defecto, pero es solo una forma de organizarlos: para Clay es lo mismo si están diréctamente en `source` o dentro de cualquier subcarpeta. La carpeta `static` no tiene nada de especial.

Si el nombre de un archivo no termina en `.html` o `.algo.tmpl`, 
no será interpretado como plantilla, sino que se mostrará directamente.

## Enlazando otros archivos
Si usas subcarpetas en tu proyecto y por ejemplo, tiene un árbol  de archivos como este:

podrias estar tentada de enlazar archivos estáticos u otras páginas desde `b.html` de esta manera:

	href="../a.html"
	src="../static/main.js"

No lo hagas. Aunque funcione, te traerá problemas cuando quieras mover `b.html` a otra carpeta o, más aún, si estás usando `{% include … %}`. En vez de eso, **siempre enlaza otros archivos usando su ruta desde la raíz**. Por ejemplo:

		href="/a.html"
		src="/static/main.js"

Esto funcionará en el servidor de desarrollo y cuando generes una versión estática del sitio, Clay automáticamente los convertirá a los enlaces relativos correctos.





