variable "root_path" {
  description = "Ruta absoluta del directorio raíz de la infraestructura."
  type        = string
}

variable "config_files" {
  description = "Lista de rutas de archivos de configuración generados."
  type        = list(string)
}

variable "service_name" {
  description = "Nombre lógico del servicio secundario."
  type        = string
}

variable "service_path" {
  description = "Ruta absoluta del subdirectorio del servicio secundario."
  type        = string
}

variable "service_file" {
  description = "Ruta del archivo de datos del servicio secundario."
  type        = string
}

variable "service_data_id" {
  description = "ID del archivo de datos del servicio secundario (para dependencias explícitas)."
  type        = string
}

variable "depends_on_resources" {
  description = "Lista de recursos de los que depende este módulo para generar el resumen."
  type        = list(any)
  default     = []
}