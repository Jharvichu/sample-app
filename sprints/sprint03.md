[Video del Sprint 03](https://unipe-my.sharepoint.com/:f:/g/personal/luis_alanya_c_uni_pe/EhtGzayR_yxImugh8lIdsyEBnHnMLsvhf50CpsYyiFJBcg?e=xpwUTF)

## Archivo `test_terraform_docs_validation.py`

Tests para validar la relación entre archivos Terraform y su documentación en formato Markdown que se genera.

### Funciones probadas:
- `obtener_modulos()`: Obtiene la lista de módulos disponibles en el directorio.
- `parsear_doc_variables()`: Extrae variables documentadas de archivos Markdown.
- `parsear_doc_outputs()`: Extrae outputs documentados de archivos Markdown.
- `verificar_variables()`: Compara variables Terraform con documentación.
- `verificar_outputs()`: Compara outputs Terraform con documentación.

### Tests implementados:

**Tests de variables por módulo:**
- **`test_variables_root_dir`**: Verifica que variables del módulo `root_dir` estén correctamente documentadas.
- **`test_variables_config_files`**: Confirma documentación completa de variables en módulo `config_files`.

**Tests de outputs por módulo:**
- **`test_outputs_root_dir`**: Valida que outputs del módulo `root_dir` coincidan con documentación.
- **`test_outputs_config_files`**: Verifica outputs del módulo `config_files` estén documentados.

**Tests globales:**
- **`test_todos_modulos_variables`**: Valida variables de todos los módulos detectados automáticamente.
- **`test_todos_modulos_outputs`**: Verifica outputs de todos los módulos del proyecto.

### Técnicas usadas:
- Fixtures pytest para configuración reutilizable del validador.
- Expresiones regulares para parsear tablas Markdown de variables y outputs.
- Operaciones de conjuntos para detectar elementos faltantes o extra.
- Validación automática de consistencia entre código Terraform y documentación.

## Archivo `test_integration.py`

Tests de integración para validar la generación automática de documentación y diagramas de dependencias a partir de módulos Terraform.

### Propósito general

Este archivo contiene pruebas de integración end-to-end que verifican la correcta ejecución de los scripts de extracción de documentación (`doc_extractor.py`) y generación de diagramas (`diagram_generator.py`). Se asegura que, a partir de una estructura de módulos Terraform simulada, ambos scripts generen los archivos de documentación y diagramas esperados.

### Funciones principales probadas

- **`test_integracion_documentacion_y_diagrama()`**: Prueba integral que:
  - Crea una estructura temporal de infraestructura con módulos Terraform de ejemplo y sus archivos correspondientes.
  - Copia los scripts de documentación y diagrama al entorno temporal.
  - Ejecuta ambos scripts y valida:
    - Que la documentación Markdown por módulo se genera correctamente.
    - Que el diagrama de dependencias (`dependencies.dot`) se crea exitosamente.

### Detalles de la implementación

- **Generación de módulos de ejemplo**:
  - `crear_modulo_ejemplo(ruta)`: Crea un módulo ficticio con archivos `main.tf`, `variables.tf`, `outputs.tf` y un `README.md` básico.
  - `crear_estructura_infra(base_path)`: Construye una estructura de carpetas tipo `infra/modules/mod1` y `infra/modules/mod2` con los módulos de ejemplo.

- **Ejecución y validación**:
  - Los scripts `doc_extractor.py` y `diagram_generator.py` son copiados a un entorno temporal y ejecutados mediante `subprocess.run`.
  - Se comprueba que la ejecución de ambos scripts termina exitosamente (`returncode == 0`).
  - Se valida la existencia de los archivos de documentación (`mod1.md`, `mod2.md`) y del diagrama (`dependencies.dot`) en la ruta esperada.

### Técnicas usadas

- Uso de `tempfile.TemporaryDirectory` para aislar el entorno de pruebas.
- Manipulación de archivos y carpetas con `os` y `shutil` para simular una estructura de módulos realista.
- Ejecución de scripts externos con `subprocess.run`.
- Asserts para validar la correcta generación de archivos resultantes.
- Pruebas automatizadas que pueden ejecutarse directamente desde el archivo.
