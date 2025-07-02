# Módulo root_dir

Crea el directorio raíz de toda la infraestructura local: infra_local/ y además es
practicamente la base; los demás (archivos, subdirectorios, scripts) se construyen 
dentro de este directorio.

### Variables

| Nombre | Tipo | Descripción | Default |
|--------|------|-------------|---------|
| root_name | string
  default     =  | Nombre lógico del directorio raíz de la infraestructura local. | infra_local |
| root_path | string
 | Ruta absoluta donde se creará el directorio raíz. | <null> |

### Outputs

| Nombre | Descripción | Valor |
|--------|-------------|-------|
| root_path | Ruta absoluta del directorio raíz creado por este módulo. | var.root_path |
| root_name | Nombre lógico del directorio raíz creado por este módulo. | var.root_name |

### Recursos

- local_file keep_root
