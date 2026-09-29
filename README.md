# Extensiones Johan

Repositorio propio de extensiones de manga en español para Aniyomi / Mihon, compilado desde
[keiyoushi/extensions-source](https://github.com/keiyoushi/extensions-source) y firmado con una
única llave propia.

## Agregarlo en la app

**Más → Ajustes → Navegar → Repositorios de extensiones → Agregar**

```
https://raw.githubusercontent.com/Jodaurro161997/keiyoushi-src/repo/index.pb
```

Huella SHA-256 de la firma:
`28b116d978a783bdf76a59674cf71b7e1a235057b270fc2a82759baf2c51bddd`

> Android no deja actualizar una app firmada con otra llave. Para pasar una extensión ya instalada
> (de Keiyoushi, Zosetsu, etc.) a este repositorio hay que **desinstalarla primero** y luego
> instalarla desde aquí. La biblioteca no se pierde: los mangas quedan ligados al ID de la fuente,
> que es el mismo; solo se reinician los ajustes propios de la extensión.

## Cómo funciona

- [`extensiones.txt`](extensiones.txt): qué extensiones se compilan.
- [`parches.txt`](parches.txt): PRs de keiyoushi aún no fusionados que se aplican antes de compilar
  (por ejemplo, arreglos que upstream no ha publicado). Si el PR se fusiona o cierra, se omite solo.
- El workflow [`compilar.yml`](.github/workflows/compilar.yml) corre los días **1 y 16 de cada mes**
  (o a mano desde *Actions → Compilar y publicar → Run workflow*), compila con la última versión de
  keiyoushi y publica APKs + `index.pb` en la rama [`repo`](../../tree/repo).
- El resumen de cada ejecución lista los parches aplicados y las versiones publicadas.

## Secretos del repositorio

`SIGNING_KEY` (keystore en base64), `ALIAS`, `KEY_STORE_PASSWORD`, `KEY_PASSWORD`.
La llave original está fuera del repositorio; si se pierde, todas las extensiones tendrían que
reinstalarse con una llave nueva.
