# Módulo: service_dir
# Propósito: Crea un subdirectorio para un servicio secundario y un archivo de datos dentro de él.
# Referencia archivos de configuración principales y depende de recursos externos.

resource "local_file" "keep_service" {
  filename   = "${var.service_path}/.keep"
  content    = "Directorio del servicio secundario: ${var.service_name}"
  depends_on = [var.depends_on_resource]
}

resource "local_file" "service_data" {
  filename   = "${var.service_path}/service_data.txt"
  content    = "Datos simulados del servicio ${var.service_name}. Archivos de configuración: ${join(", ", var.config_files)}"
  depends_on = [var.depends_on_resource]
}