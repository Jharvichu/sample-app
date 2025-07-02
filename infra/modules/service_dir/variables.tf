variable "service_name" {
  description = "Nombre lógico del servicio secundario que se crea en este módulo."
  type        = string
  default     = "secondary_service"
}

variable "service_path" {
  description = "Ruta absoluta donde se creará el subdirectorio del servicio secundario."
  type        = string
}

variable "config_files" {
  description = "Lista de archivos de configuración principales del sistema, generados por el módulo config_files."
  type        = list(string)
  default     = []
}

variable "depends_on_resource" {
  description = "Recurso del que depende la creación del servicio (por ejemplo, archivos de configuración principales)."
  type        = any
}