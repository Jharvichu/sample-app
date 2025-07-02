[Video del Sprint 02](https://unipe-my.sharepoint.com/:f:/g/personal/luis_alanya_c_uni_pe/EhtGzayR_yxImugh8lIdsyEBnHnMLsvhf50CpsYyiFJBcg?e=xpwUTF)


## Archivo `test_diagram_generator.py`

Tests para el generador de diagramas de dependencias de módulos Terraform.

### Funciones probadas:
- `parce_dependencies()`: Extrae dependencias de archivos `main.tf`.
- `generate_dependencies()`: Recolecta dependencias de todos los módulos.
- `generate_diagram_dot()`: Genera archivos .dot y .png con diagramas.

### Tests implementados:

**Tests de `parce_dependencies`:**
- **Contenido con dependencias**: Verifica que encuentre dependencias en archivos `main.tf` con módulos, variables y depends_on.
- **Directorio vacío**: Confirma que retorna lista vacía cuando no hay archivos.
- **Sin archivo `main.tf`**: Verifica que solo procesa archivos main.tf, ignorando otros `.tf`.

**Tests de `generate_dependencies`:**
- **Funcionalidad básica**: Con mocks simula módulos y verifica que retorna diccionario con dependencias por módulo.

**Tests de `generate_diagram_dot`:**
- **Creación de archivos**: Verifica que crea directorio `docs/`, archivo `.dot` y ejecuta comando `dot` para generar el grafo `.png`.
- **Directorio existente**: Prueba cuando el directorio docs ya existe.
- **Error de Graphviz**: Maneja el caso cuando `dot` no está instalado sin fallar.

### Técnicas usadas:
- Directorios temporales para tests aislados.
- Mocks para evitar dependencias externas (filesystem, subprocess).
- Patches para simular comportamiento de funciones del sistema.

## Archivo `test_doc_extractor.py`

Tests para el extractor de documentación de módulos Terraform que genera archivos markdown.

### Funciones probadas:
- `parse_main_tf()`: Extrae recursos de archivos `main.tf`.
- `parse_variables_tf()`: Extrae variables con descripción, tipo y valor por defecto.
- `parse_outputs_tf()`: Extrae outputs con descripción y valor.
- `parse_readme_md()`: Extrae nombre del módulo y descripción del `README`.
- `build_content()`: Construye contenido markdown completo.
- `write_md()`: Escribe documentación en archivo markdown.

### Tests implementados:

**Tests de `parse_main_tf`:**
- **Recursos local_file**: Verifica extracción de recursos con filename y content.
- **Recursos null_resource**: Prueba extracción de recursos null con provisioners.
- **Casos límite**: Archivos vacíos, sin recursos, contenido malformado.
- **Atributos faltantes**: Maneja recursos sin algunos atributos requeridos.

**Tests de `parse_variables_tf`:**
- **Variables completas**: Extrae variables con descripción, tipo y valor por defecto.
- **Sin archivo**: Retorna lista vacía cuando no existe `variables.tf`.
- **Variables mínimas**: Maneja variables solo con nombre.

**Tests de `parse_outputs_tf`:**
- **Outputs completos**: Extrae outputs con descripción y valor.
- **Sin archivo**: Retorna lista vacía cuando no existe `outputs.tf`.

**Tests de `parse_readme_md`:**
- **README completo**: Extrae nombre del módulo y descripción.
- **Sin archivo**: Retorna valores por defecto.
- **Secciones faltantes**: Maneja READMEs incompletos.

**Tests de `build_content`:**
- **Módulo completo**: Construye markdown con todas las secciones.
- **Módulo vacío**: Genera contenido básico cuando no hay datos.

**Tests de `write_md`:**
- **Escritura exitosa**: Verifica creación de directorio docs y archivo markdown.
- **Sin directorio modules**: Maneja error cuando no existe el directorio.
- **Errores de permisos**: Prueba manejo de errores de escritura.
- **Contenido malformado**: Verifica comportamiento con datos incorrectos.

### Técnicas usadas:
- Fixtures para directorios temporales reutilizables.
- Funciones auxiliares para crear archivos de prueba.
- Tests parametrizados para múltiples escenarios.
- Mocks para operaciones de sistema de archivos.
- Manejo de excepciones y casos límite.

## Archivo `diagram_generator.py`

Script para analizar los módulos Terraform dentro de `infra/modules`, detectar dependencias entre ellos y generar un diagrama visual en formato DOT y PNG usando Graphviz.

---

### Funciones principales

- **`generate_dependencies()`**  
  Recorre los módulos, analiza sus archivos `main.tf` y construye un diccionario con sus dependencias.

- **`parce_dependencies(module)`**  
  Extrae, usando expresiones regulares, referencias a submódulos, dependencias, variables, datos y fuentes locales de los archivos `main.tf`.

- **`generate_diagram_dot()`**  
  Toma las dependencias encontradas, genera el archivo `docs/dependencies.dot` y lo convierte a imagen PNG con `dot` (Graphviz).

---

### Uso

Ejecutar el script crea (o actualiza) en el directorio `docs` el grafo `.dot` y su imagen `.png` que visualiza las relaciones entre los módulos.

**Requiere:**  
- Python  
- Graphviz instalado y accesible vía línea de comandos.

```bash
python3 scripts/diagram_generator.py
```