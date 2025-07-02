# Módulo config_files

Genera archivos de configuración (main.conf, app.conf) dentro del directorio raíz y además
requiere que root_dir haya creado correctamente su estructura.

### Variables

| Nombre | Tipo | Descripción | Default |
|--------|------|-------------|---------|
| root_path | string
 | Ruta absoluta del directorio raíz donde se crearán los archivos de configuración. | <null> |
| project_name | string
  default     =  | Nombre del proyecto para contextualizar los archivos de configuración. | infra_local |
| depends_on_resource | any
 | Recurso del que depende la creación de los archivos de configuración (generalmente el directorio raíz). | <null> |

### Outputs

| Nombre | Descripción | Valor |
|--------|-------------|-------|
| config_files | Lista de rutas de los archivos de configuración generados por este módulo. | [ |
| config_files_ids | IDs de los recursos de archivos de configuración generados (para dependencias). | [ |

### Recursos

- local_file config1
- local_file config2
