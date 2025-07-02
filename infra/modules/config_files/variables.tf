variable "root_path" {
  description = "Ruta absoluta del directorio raíz donde se crearán los archivos de configuración."
  type        = string
}
variable "project_name" {
  description = "Nombre del proyecto para contextualizar los archivos de configuración."
  type        = string
  default     = "infra_local"
}
variable "depends_on_resource" {
  description = "Recurso del que depende la creación de los archivos de configuración (generalmente el directorio raíz)."
  type        = any
}