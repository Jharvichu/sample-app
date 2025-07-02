# PC4_Grupo8_Proyecto10

## Archivo `setup.sh`

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


## Extractor y generación automatica de documentación

El script `doc_extractor` automatiza la generación de documentación Markdown para módulos de Terraform. Extrae información de los archivos `main.tf`, `variables.tf`, `outputs.tf` y `README.md`, y genera un archivo .md por cada módulo ubicado en la carpeta `infra/modules`. Los resultados se guardan en el directorio `docs/`.

Para generar automaticamente la documentación de los modulos de la infraestructura debemos ejecutar los siguientes comando


## `diagram_generator.py`

### Responsabilidad de `generate_diagram_dot`:

Crea un archivo .dot (formato de Graphviz) con las dependencias detectadas, entre los 4 módulos creados anteriormente, después lo convierte en una imagen PNG.

### Ejecucion:

Dentro de scripts/

```
python3 diagram_generator.py
```


### Resultados:
Un archivo con un grafo en lenguaje DOT que describe las dependencias entre nodos; representa como los módulos y variables estan relacionados y tienen dependencias entre si. Se puede usar para generar diagramas .png con `Graphivz`.También se espera una imagen PNG que contiene los módulos y su relacion de dependencias.


```bash
# Desde la raiz del proyecto
cd scripts/
python3 doc_generator.py
```
### script generate_docs.py
Va a recorrer todos los módulos Terraform en infra/modules/, extraer metadatos importantes de cada módulo(nombre, variables, outputs), genera documentación Markdown en cada módulo,
analiza dependencias entre los módulos y recursos, genera un grafo de dependencias en un formato .dot y una imagen .png usando Graphviz.

## Resultados:
Archivos markdown creados en la carpeta docs con información resumida de cada módulo.
Una  `dependencies.dot` y un `dependencies.png`con las dependencias de módulos visualizadas en un grafo.

## Herramientas

Graphviz y Python3.8+


## Ejecución
Dentro de scripts:

```
python3 generator_docs.py
```
