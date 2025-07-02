# Módulo: config_files
# Propósito: Crea archivos de configuración principales poniendolos
# dentro del directorio raíz creado antes.

resource "local_file" "config1" {
  filename   = "${var.root_path}/main.conf"
  content    = "Archivo de configuración principal para ${var.project_name}."
  depends_on = [var.depends_on_resource]
}

resource "local_file" "config2" {
  filename   = "${var.root_path}/app.conf"
  content    = "Archivo de configuración secundaria para ${var.project_name}."
  depends_on = [var.depends_on_resource]
}