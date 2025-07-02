# Infraestructura local compuesta por cuatro módulos, cada uno con
# sus respectivos metadatos y dependencias.

module "root_dir" {
  source    = "./modules/root_dir"
  root_name = "infra_local"
  root_path = "${path.module}/infra_local"
}

module "config_files" {
  source      = "./modules/config_files"
  root_path   = module.root_dir.root_path
  project_name = "infra_local"
  depends_on_resource = module.root_dir.root_path
}

module "service_dir" {
  source       = "./modules/service_dir"
  service_name = "secondary_service"
  service_path = "${module.root_dir.root_path}/secondary_service"
  config_files = module.config_files.config_files
  depends_on_resource = module.config_files.config_files_ids[0]
}

module "summary_creator" {
  source        = "./modules/summary_creator"
  root_path     = module.root_dir.root_path
  config_files  = module.config_files.config_files
  service_name  = module.service_dir.service_name
  service_path  = module.service_dir.service_path
  service_file  = module.service_dir.service_file
  service_data_id = module.service_dir.service_data_id
  depends_on_resources = module.config_files.config_files_ids
}