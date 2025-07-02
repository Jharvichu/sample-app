resource "null_resource" "create_summary" {
  provisioner "local-exec" {
    command = "echo 'Infraestructura creada en ${var.root_path}. Archivos de configuración: ${join(", ", var.config_files)}. Servicio: ${var.service_name} en ${var.service_path} con datos en ${var.service_file}' > ${var.root_path}/summary.txt"
  }

  triggers = {
    config_files     = join(",", var.config_files)
    service_name     = var.service_name
    service_path     = var.service_path
    service_file     = var.service_file
    service_data_id  = var.service_data_id
  }
}
