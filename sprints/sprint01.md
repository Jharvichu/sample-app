## Archivo `setup.sh`

[Video del Sprint 01](https://unipe-my.sharepoint.com/:f:/g/personal/luis_alanya_c_uni_pe/EhtGzayR_yxImugh8lIdsyEBnHnMLsvhf50CpsYyiFJBcg?e=xpwUTF)

**Archivo importante, ejecutar al inicio.**

Este archivo automatiza la creación del setup adecuado para trabajar en este proyecto. Realiza las siguientes operaciones:

- Crea el entorno virtual `venv`. (si es que aún no está creado)
- Activa dicho entorno.
- Instalar las dependencias dentro de `requirements.txt` (si es que existe).
- Mueve los hooks de `hooks/` (`pre-commit`, `commit-msg` y `pre-push`) al directorio `.git/hooks/` y les de permisos de ejecución.

Dicho script bash se puede ejecutar de la siguiente manera

```
source setup.sh
```

Cabe mencionar que algunos comandos dentro de `setup.sh` (como `source venv/bin/activate`) solamente funcionan en sistemas tipo Unix, por lo cual, si se usa otro sistema operativo simplemente dichos comandos no tendrán efecto.

## Hooks

### pre-commit

- Impide commits directamente en ramas protegidas: `main`, `develop`, `release`.
- Realiza validaciones rápidas solamente para los archivos staged para commit.
- Ejecuta linter Python (`flake8`) solo en archivos `.py` staged, reportando errores críticos.
- Ejecuta `terraform fmt -check` solo en archivos `.tf` staged, verificando que estén bien formateados.
- Ejemplo:
  ```bash
  flake8 --select=E9,F63,F7,F82 --show-source archivo.py
  terraform fmt -check archivo.tf
  ```
- Si algún archivo Python tiene un error crítico o algún archivo terraform no está bien formateado, el commit se cancela.

### commit-msg

- Valida que el mensaje de commit siga la estructura definida.
- No permite mensajes que no sigan la estructura.
- Formato requerido:
  ```
  <tipo>([alcance]): (Issue #n) descripción corta
  ```
  Ejemplo:
  ```
  feat(hook): (Issue #12) validar mensajes de commit
  ```

### pre-push

- Ejecuta validaciones automáticas antes de subir cambios al repositorio remoto.
- Corre linters python (`flake8`) sobre todo el proyecto.
- Valida formato de archivos terraform (`terraform fmt -check`).
- Ejecuta pruebas automáticas (`pytest`) y se exige un porcentaje mínimo de cobertura (≥80%).
- Permite el push si no hay tests, mostrando solo una advertencia.
- Secuencia:
  ```bash
  flake8 .
  terraform fmt -check
  pytest
  ```

## Infraestructura Basica

Instrucciones de ejecución de la infraestructura en la termina

``` bash
# Ejecución de infraestructura
terraform init
terraform apply -auto-approve
```

### **Modulos**

| Modulos | Funcion | Dependencia |
|---------|---------|-------------|
|root_dir/| Crea un directorio raíz en el sistema de archivos local. Este directorio actúa como la base de la infraestructura sobre la cual se construyen los demás componentes.||
|config_files/|Genera archivos de configuración (main.conf, app.conf) dentro del directorio raíz.| Requiere que root_dir haya creado correctamente su estructura.
|service_dir|Crea un subdirectorio (secondary_service/) dentro del directorio raíz y un archivo representativo de un servicio secundario (service_data.txt).|Depende tanto de root_dir como de los archivos generados en `config_files`.|
|summary_creator|Ejecuta un script mediante null_resource y local-exec que genera un archivo `summary.txt` dentro del directorio raíz. Este archivo resume las rutas de los archivos y directorios creados por los módulos anteriores.|Depende explícitamente de todos los módulos previos.|


### Archivos importantes en la raiz de la infraestructura

`main.tf` este archivo orquesta la integración de los módulos, pasando variables y conectando las salidas entre sí, garantizando que las dependencias estén explícitamente modeladas.


### Resultado Esperado
Al ejecutar correctamente terraform apply, se debe crear una estructura como esta:


### Estructura generada por Terraform
- `infra_local/`:Este es el directorio raíz de la infraestructura local. Fue creado por el módulo root_dir. Todo lo demás se construye dentro de él.

- `main.conf` y `app.conf`: Estos son archivos de configuración básicos.Fueron generados por el módulo config_files dentro del directorio raíz infra_local/. Simulan archivos que una aplicación o servicio podría necesitar para funcionar.

- `secondary_service/`: Ubicación en `infra_local/secondary_service/` Este es un subdirectorio que representa un servicio secundario dentro de la infraestructura. Fue creado por el módulo service_dir.

- `service_data.txt`: Este archivo está dentro del subdirectorio `secondary_service/` Contiene información ficticia o simulada, como si fuera la configuración o datos de ese servicio.

- `summary.txt` Este archivo fue generado por el módulo summary_creator, usando un script que corre localmente con `null_resource` y `local-exec`. Contiene un resumen de todos los recursos creados por los otros módulos: rutas, nombres de archivo, etc. Sirve como una forma de validar que todo fue creado y que las dependencias se resolvieron correctamente.

El archivo summary.txt contendrá información sobre los directorios y archivos creados por cada módulo, verificando que las dependencias funcionaron correctamente.

## Extractor y generación automatica de documentación

El script `doc_extractor` automatiza la generación de documentación Markdown para módulos de Terraform. Extrae información de los archivos `main.tf`, `variables.tf`, `outputs.tf` y `README.md`, y genera un archivo .md por cada módulo ubicado en la carpeta `infra/modules`. Los resultados se guardan en el directorio docs.

### Funciones principales

| Función             | Propósito                                                      |
|---------------------|----------------------------------------------------------------|
| `parse_main_tf()`   | Extrae recursos tipo `local_file` y `null_resource`            |
| `parse_variables_tf()` | Extrae variables (nombre, tipo, descripción, valor por defecto) |
| `parse_outputs_tf()`   | Extrae outputs (nombre, descripción, valor)                   |
| `parse_readme_md()`    | Extrae título del módulo y descripción                        |
| `build_content()`      | Compone el contenido Markdown de cada módulo                  |
| `write_md()`           | Genera y escribe todos los archivos `.md` en la carpeta `docs/` |

Para generar automaticamente la documentación de los modulos de la infraestructura debemos ejecutar los siguientes comando

```bash
# Desde la raiz del proyecto
cd scripts/
python3 doc_generator.py
```

Tendriamos una salida un archivo **markdown** con la documentacion del modulo de la infraestrcutura y tendria esta estructura:

```
# Módulo Generador de Archivos

Este módulo crea archivos locales a partir de contenido dinámico generado por comandos o definido directamente.

### Tabla de variables:

| Nombre     | Tipo   | Descripcion                       | Default    |
|------------|--------|-----------------------------------|------------|
| file_name  | string | Nombre del archivo a crear        | output.txt |
| file_mode  | string | Permisos del archivo              | 0644       |

### Tabla de outputs:

| Nombre     | Descripción                  | Valor     |
|------------|------------------------------|-----------|
| file_path  | Ruta al archivo generado     | path/to/file |

### Lista de recursos:

- Recurso de tipo `local_file` con nombre **archivo_local** crea el archivo `output.txt` con contenido `Generado dinámicamente`
- Recurso de tipo `null_resource` con nombre **generador_cmd** ejecuta el comando `echo hola > output.txt` en `output.txt`

```
