output "service_path" {
  description = "Ruta absoluta del subdirectorio del servicio secundario creado."
  value       = var.service_path
}
output "service_file" {
  description = "Ruta del archivo de datos del servicio secundario."
  value       = local_file.service_data.filename
}
output "service_name" {
  description = "Nombre lógico del servicio secundario creado."
  value       = var.service_name
}
output "service_data_id" {
  description = "ID del recurso del archivo de datos del servicio secundario."
  value       = local_file.service_data.id
}