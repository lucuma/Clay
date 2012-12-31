
## Macros

Muchas veces quieres repetir un bloque de código solo cambiando algunos detalles, por ejemplo, si en un listado de noticias quieres que sus títulos no sean iguales, aunque el resto del  HTML no cambie. Podrías crear varios archivos ligéramente diferentes e insertarlos con `{% include … %}`, pero hay una mejor forma: **macros**!

El concepto de un macro es sencillo: unas bloque de código, igual que un *include*, pero con uno o varios textos que puedes reemplazar por otros, al momento de insertarlo.

Por ejemplo, en vez de tener cinco archivos, casi idénticos, y hacer:

````jinja
{% include "noticia-1.html" %}
{% include "noticia-2.html" %}
{% include "noticia-3.html" %}
{% include "noticia-4.html" %}
{% include "noticia-5.html" %}
````

tienes un solo macro llamado `noticia` y, en cambio, escribes:

````jinja
{{ noticia('Lorem ipsum') }}
{{ noticia('Noticia muy interesante') }}
{{ noticia('Título que tiene cinco palabras') }}
{{ noticia('Lalala') }}
{{ noticia('abc defghi') }}
````

la ventaja es que, cuando quieras cambiar algo del código de la noticia, solo es un solo archivo que actualizar en vez de cinco.

### Escribiendo un macro

````jinja
{% macro noticia(titulo) %}
<article>
	<h1>{{ titulo }}</h1>
	<p>Lorem ipsum ad his scripta blandit partiendo, eum fastidii accumsan euripidis in, eum liber hendrerit an.</p>
</article>
{% endmacro %}
````

Puedes definir un macro donde quieras pues, hasta que lo llames, no se mostrará en el HTML, pero para poder llamarlo desde distintas páginas, escribámoslo en un archivo separado, llamado, por ejemplo "_macros.html_".

Para usarlo en una página, como el macro no está escrito en el mismo archivo, lo primero es "importar" _macros.html_ y darle un nombre.

````jinja
{% extend "base.html" %}
{% import "macros.html" as m %}

{% block content %}
  <h1>Noticias</h1>
  {{ m.noticia('Lorem ipsum') }}
  {{ m.noticia('Noticia muy interesante') }}
  {{ m.noticia('Título que tiene cinco palabras') }}
{% endblock %}
````

Nota que ahora llamamos al macro usando `m.noticia(…)`.

Nuestro macro puede tener más de un texto reemplazables (llamémoslos "parámetros"), por ejemplo, una fecha o un autor:

````jinja
{% macro noticia(titulo='Lorem ipsum', fecha='05/05/2013', autor='Admin') %}
<article>
	<h1>{{ titulo }}</h1>
	<h4>Publicado el {{ fecha }}</h4>
	<p>Lorem ipsum ad his scripta blandit partiendo, eum fastidii accumsan euripidis in, eum liber hendrerit an.</p>
</article>
{% endmacro %}
````

Aquí además hemos usado un **valor por defecto**, que son los que se usarán a menos que los sobreescribas, así que no es necesario llamar al macro pasándole todos los valores. De hecho,  usando los nombres de los parámetros, ni siquiera hay por que pasárselos en orden.

````jinja
{% extend "base.html" %}
{% import "macros.html" as m %}

{% block content %}
  <h1>Noticias</h1>
	{{ m.noticia('lalala', '24/12/2009') }}
  {{ m.noticia(autor='Anon', titulo='Lorem ipsum ad') }}
  {{ m.noticia(fecha='2/2/1989') }}
  {{ m.noticia() }}
{% endblock %}
````

### Por último
Otra diferencia con los include, es que un archivo puede contener más de un macro. Basta importar ese archivo una vez por página y llamar al macro que necesites.
