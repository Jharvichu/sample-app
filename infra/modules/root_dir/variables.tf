variable "root_name" {
  description = "Nombre lógico del directorio raíz de la infraestructura local."
  type        = string
  default     = "infra_local"
}

variable "root_path" {
  description = "Ruta absoluta donde se creará el directorio raíz."
  type        = string
}