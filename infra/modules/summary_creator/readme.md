# Módulo summary_creator

### Descripción
Ejecuta un script local que genera el archivo summary.txt con un resumen de lo creado y simula una automatización de documentación o auditoría, además es el único que no crea archivos directamente con Terraform, sino mediante un script (`local-exec` con `null_resource`); depende explícitamente de todos los demás módulos, para asegurarse de que el resumen refleje correctamente la infraestructura final.