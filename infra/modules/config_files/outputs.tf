output "config_files" {
  description = "Lista de rutas de los archivos de configuración generados por este módulo."
  value = [
    local_file.config1.filename,
    local_file.config2.filename
  ]
}
output "config_files_ids" {
  description = "IDs de los recursos de archivos de configuración generados (para dependencias)."
  value = [
    local_file.config1.id,
    local_file.config2.id
  ]
}