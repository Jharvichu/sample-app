import os
import pytest
import tempfile
from unittest.mock import patch, mock_open
from scripts.doc_extractor import (
    parse_main_tf, parse_variables_tf, parse_outputs_tf,
    parse_readme_md, build_content, write_md
)


@pytest.fixture
def directorio_temporal():
    """Fixture que da un directorio temporal"""
    with tempfile.TemporaryDirectory() as dt:
        yield dt


def crear_archivo_tf(directorio_temporal, nombre_archivo, contenido):
    """Función para crear archivos terraform de prueba"""
    ruta_archivo = os.path.join(directorio_temporal, nombre_archivo)
    with open(ruta_archivo, 'w') as f:
        f.write(contenido)
    return ruta_archivo


def crear_modulo_prueba(directorio_temporal):
    """Funcion para crear un módulo completo de prueba"""
    archivos = {
        "README.md": '''# Módulo test_module\n### Descripción\nDescripción de prueba.''',
        "variables.tf": '''variable "test_var" {\n  description = "Variable de prueba"\n  type = string\n  default = "default_value"\n}''',
        "outputs.tf": '''output "test_output" {\n  description = "Output de prueba"\n  value = var.test_var\n}''',
        "main.tf": '''resource "local_file" "test_file" {\n  filename = "/tmp/test.txt"\n  content = "Contenido de prueba"\n}'''
    }
    for nombre_archivo, contenido in archivos.items():
        crear_archivo_tf(directorio_temporal, nombre_archivo, contenido)


class TestParseMainTf:
    """Tests para función parse_main_tf"""

    def test_parse_local_file_resources(self, directorio_temporal):
        """Probar la extracción de recursos local_file"""
        contenido = '''
resource "local_file" "config1" {
  filename = "${var.root_path}/main.conf"
  content  = "Archivo de configuración principal para ${var.project_name}."
}
resource "local_file" "config2" {
  filename = "${var.root_path}/app.conf"
  content  = "Archivo de configuración secundaria para ${var.project_name}."
}
'''
        crear_archivo_tf(directorio_temporal, "main.tf", contenido)
        resultado = parse_main_tf(directorio_temporal)
        assert len(resultado) == 2
        assert resultado[0]["type"] == "local_file"
        assert resultado[0]["name"] == "config1"
        assert resultado[1]["name"] == "config2"

    def test_parse_null_resource(self, directorio_temporal):
        """Probar la extracción de recursos null_resource"""
        contenido = '''
resource "null_resource" "create_summary" {
  provisioner "local-exec" {
    command = "echo 'Summary content' > ${var.root_path}/summary.txt"
  }
}
'''
        crear_archivo_tf(directorio_temporal, "main.tf", contenido)
        resultado = parse_main_tf(directorio_temporal)
        assert len(resultado) == 1
        assert resultado[0]["type"] == "null_resource"
        assert resultado[0]["name"] == "create_summary"

    @pytest.mark.parametrize("escenario,contenido,longitud_esperada", [
        ("sin_archivo", None, 0),
        ("archivo_vacio", "", 0),
        ("sin_recursos", "# Solo comentarios\nvariable \"test\" {\n  type = string\n}", 0),
    ])
    def test_edge_cases(self, directorio_temporal, escenario, contenido, longitud_esperada):
        """Porbar casos edge con parametrize"""
        if contenido is not None:
            crear_archivo_tf(directorio_temporal, "main.tf", contenido)
        resultado = parse_main_tf(directorio_temporal)
        assert len(resultado) == longitud_esperada

    def test_missing_attributes(self, directorio_temporal):
        """Probar recursos con algunos atributos faltantes"""
        contenido = '''
resource "local_file" "incomplete" {
  filename = "/tmp/test.txt"
}
'''
        crear_archivo_tf(directorio_temporal, "main.tf", contenido)
        resultado = parse_main_tf(directorio_temporal)
        assert len(resultado) == 1
        assert resultado[0]["filename"] == "/tmp/test.txt"
        assert resultado[0]["content"] == "<null>"


class TestParseVariablesTf:
    """Tests para la función parse_variables_tf"""

    def test_parse_complete_variables(self, directorio_temporal):
        """Probar extraccion de variables completas"""
        contenido = '''
variable "root_path" {
  description = "Ruta del directorio raíz donde se crearan los archivos."
  type        = string
}
variable "project_name" {
  description = "Nombre del proyecto para los archivos."
  type        = string
  default     = "infra_local"
}
'''
        crear_archivo_tf(directorio_temporal, "variables.tf", contenido)
        resultado = parse_variables_tf(directorio_temporal)
        assert len(resultado) == 2
        assert resultado[0]["name"] == "root_path"
        assert resultado[1]["name"] == "project_name"

    def test_variables_no_file(self, directorio_temporal):
        """Probar cuando no existe variables.tf"""
        resultado = parse_variables_tf(directorio_temporal)
        assert resultado == []

    def test_variables_minimal(self, directorio_temporal):
        """Probar variables cuando tengan información mínima"""
        contenido = 'variable "simple_var" { type = string }'
        crear_archivo_tf(directorio_temporal, "variables.tf", contenido)
        resultado = parse_variables_tf(directorio_temporal)
        assert len(resultado) == 1
        assert resultado[0]["name"] == "simple_var"


class TestParseOutputsTf:
    """Tests para parse_outputs_tf"""

    def test_parse_complete_outputs(self, directorio_temporal):
        """Probar extracción de outputs"""
        contenido = '''
output "config_files" {
  description = "Lista de rutas de los archivos de configuración que se generan."
  value = [ local_file.config1.filename, local_file.config2.filename ]
}
output "root_path" {
  description = "Ruta del directorio raíz creado."
  value = var.root_path
}
'''
        crear_archivo_tf(directorio_temporal, "outputs.tf", contenido)
        resultado = parse_outputs_tf(directorio_temporal)
        assert len(resultado) == 2
        assert resultado[0]["name"] == "config_files"
        assert resultado[1]["name"] == "root_path"

    def test_no_outputs_file(self, directorio_temporal):
        """Probar cuando no hay outputs.tf"""
        assert parse_outputs_tf(directorio_temporal) == []


class TestParseReadmeMd:
    """Tests para función parse_readme_md"""

    def test_readme_complete(self, directorio_temporal):
        """Probar parsing de README completo"""
        contenido = '''# Módulo config_files\n### Descripción\nEste módulo crea archivos de configuración principales.'''
        crear_archivo_tf(directorio_temporal, "README.md", contenido)
        resultado = parse_readme_md(directorio_temporal)
        assert resultado["modulo"] == "config_files"
        assert "Este módulo crea archivos" in resultado["descripcion"]

    def test_readme_no_file(self, directorio_temporal):
        """Probar cuando no hay README.md"""
        resultado = parse_readme_md(directorio_temporal)
        assert resultado == {}

    def test_readme_missing_sections(self, directorio_temporal):
        """Probar README con estructura faltante"""
        contenido = "# Algun contenido\nSin estructura."
        crear_archivo_tf(directorio_temporal, "README.md", contenido)
        resultado = parse_readme_md(directorio_temporal)
        assert resultado["modulo"] == "<null>"
        assert resultado["descripcion"] == "<null>"


class TestBuildContent:
    """Tests para función build_content"""

    def test_complete_module(self, directorio_temporal):
        """Probar generación de contenido para un módulo"""
        crear_modulo_prueba(directorio_temporal)
        resultado = build_content(directorio_temporal)
        assert "# Módulo test_module" in resultado
        assert "### Tabla de variables:" in resultado
        assert "### Lista de recursos:" in resultado

    def test_empty_module(self, directorio_temporal):
        """Probar generación para módulo vacío"""
        resultado = build_content(directorio_temporal)
        assert "# Módulo <sin módulo>" in resultado
        assert "<sin descripción>" in resultado


class TestWriteMd:
    """Tests para función write_md"""

    @patch('scripts.doc_extractor.os.path.dirname')
    @patch('scripts.doc_extractor.os.path.isdir')
    @patch('scripts.doc_extractor.os.listdir')
    @patch('scripts.doc_extractor.os.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_write_md_success(self, mock_file, mock_mkdir, mock_listdir, mock_isdir, mock_dirname):
        """Probar escritura exitosa"""
        mock_dirname.return_value = "/falsos/scripts"
        mock_isdir.side_effect = [True, False]  # modules en true, docs en false
        mock_listdir.return_value = ["config_files", "root_dir"]
        write_md()
        mock_mkdir.assert_called_once()
        assert mock_file.call_count >= 2

    @patch('scripts.doc_extractor.os.path.dirname')
    @patch('scripts.doc_extractor.os.path.isdir')
    @patch('scripts.doc_extractor.sys.exit')
    def test_write_md_no_modules_dir(self, mock_exit, mock_isdir, mock_dirname):
        """Probar cuando no haya directorio modules"""
        mock_dirname.return_value = "/falsos/scripts"
        mock_isdir.return_value = False
        mock_exit.side_effect = SystemExit(1)
        with pytest.raises(SystemExit):
            write_md()


class TestErrorHandling:
    """Tests de manejo de errores"""

    def test_permission_error(self, directorio_temporal):
        """Probar manejo de errores en permisos"""
        ruta_archivo = crear_archivo_tf(directorio_temporal, "main.tf", "test content")
        os.chmod(ruta_archivo, 0o000)
        try:
            resultado = parse_main_tf(directorio_temporal)
            assert resultado == []
        finally:
            os.chmod(ruta_archivo, 0o644)

    def test_malformed_content(self, directorio_temporal):
        """Probar estructura malformada"""
        contenido = '''
        variable "roto" {
          description = "Falta comillas dobles
          type = string'''
        crear_archivo_tf(directorio_temporal, "variables.tf", contenido)
        resultado = parse_variables_tf(directorio_temporal)
        assert isinstance(resultado, list)


if __name__ == "__main__":
    pytest.main([__file__])
