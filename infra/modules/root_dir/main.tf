# Módulo: root_dir
# Propósito: Crea el directorio raíz donde se alojará toda la infraestructura local.
# asegurando su existencia mediante un archivo oculto llamado .keep dentro de ese directorio.

resource "local_file" "keep_root" {
  filename = "${var.root_path}/.keep"
  content  = "Directorio raíz de la infraestructura local: ${var.root_name}"
}