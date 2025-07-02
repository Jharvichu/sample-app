# Módulo service_dir

Crea un subdirectorio llamado `secondary_service/`  y un archivo `service_data.txt`  dentro de él; representa un módulo dservicio adicional, como si se tratara de un microservicio o componente del sistema; también demuestra cómo un módulo puede depender de múltiples recursos anteriores ( `root_dir` y `config_files`).

### Variables

| Nombre | Tipo | Descripción | Default |
|--------|------|-------------|---------|
| service_name | string
  default     =  | Nombre lógico del servicio secundario que se crea en este módulo. | secondary_service |
| service_path | string
 | Ruta absoluta donde se creará el subdirectorio del servicio secundario. | <null> |
| config_files | list(string)
  default     = []
 | Lista de archivos de configuración principales del sistema, generados por el módulo config_files. | [] |
| depends_on_resource | any
 | Recurso del que depende la creación del servicio (por ejemplo, archivos de configuración principales). | <null> |

### Outputs

| Nombre | Descripción | Valor |
|--------|-------------|-------|
| service_path | Ruta absoluta del subdirectorio del servicio secundario creado. | var.service_path |
| service_file | Ruta del archivo de datos del servicio secundario. | local_file.service_data.filename |
| service_name | Nombre lógico del servicio secundario creado. | var.service_name |
| service_data_id | ID del recurso del archivo de datos del servicio secundario. | local_file.service_data.id |

### Recursos

- local_file keep_service
- local_file service_data
