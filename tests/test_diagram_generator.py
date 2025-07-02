import os
import tempfile
from unittest.mock import patch, mock_open
from scripts.diagram_generator import (
    generate_dependencies, parce_dependencies, generate_diagram_dot
)


class TestDiagramGenerator:

    def test_parce_dependencies_con_contenido(self):
        """Probar que parce_dependencies encuentra dependencias en un archivo .tf"""
        with tempfile.TemporaryDirectory() as directorio_temp:
            archivo_main = os.path.join(directorio_temp, 'main.tf')
            contenido = '''
            module "ejemplo" {
                source = "../modulo"
            }
            variable "var_prueba" {
                description = "Variable prueba"
            }
            depends_on = [module.ejemplo]
            '''
            with open(archivo_main, 'w') as f:
                f.write(contenido)
            resultado = parce_dependencies(directorio_temp)
            assert isinstance(resultado, list)
            assert len(resultado) > 0

    def test_parce_dependencies_directorio_vacio(self):
        """Probar que funciona con directorios vacíos"""
        with tempfile.TemporaryDirectory() as directorio_temp:
            resultado = parce_dependencies(directorio_temp)
            assert resultado == []

    def test_parce_dependencies_sin_main_tf(self):
        """Porbar con directorios que no tienen main.tf"""
        with tempfile.TemporaryDirectory() as directorio_temp:
            archivo_otro = os.path.join(directorio_temp, 'otro.tf')
            with open(archivo_otro, 'w') as f:
                f.write('resource "test" "ejemplo" {}')
            resultado = parce_dependencies(directorio_temp)
            assert resultado == []

    @patch('os.listdir')
    @patch('os.path.join')
    def test_generate_dependencies_basico(self, mock_join, mock_listdir):
        """Test basico de funcion generate_dependencies"""
        mock_listdir.return_value = ['modulo1', 'modulo2']
        mock_join.return_value = '/ruta/falsa'
        with patch('scripts.diagram_generator.parce_dependencies') as mock_parce:
            mock_parce.return_value = ['dep1', 'dep2']
            resultado = generate_dependencies()
            assert isinstance(resultado, dict)
            assert 'modulo1' in resultado
            assert 'modulo2' in resultado

    @patch('os.path.isdir')
    @patch('os.mkdir')
    @patch('subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_diagram_dot_crea_archivos(self, mock_archivo, mock_subprocess, mock_mkdir, mock_isdir):
        """Probar que funcion generate_diagram_dot crea los archivos"""
        mock_isdir.return_value = False
        with patch('scripts.diagram_generator.generate_dependencies') as mock_deps:
            mock_deps.return_value = {'modulo1': ['dep1']}
            generate_diagram_dot()
            mock_mkdir.assert_called_once()
            mock_archivo.assert_called()
            mock_subprocess.assert_called_once()

    @patch('os.path.isdir')
    @patch('subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_diagram_dot_directorio_existe(self, mock_archivo, mock_subprocess, mock_isdir):
        """Porbar caso cuando el directorio docs ya existe"""
        mock_isdir.return_value = True
        with patch('scripts.diagram_generator.generate_dependencies') as mock_deps:
            mock_deps.return_value = {'modulo1': ['dep1']}
            generate_diagram_dot()
            mock_archivo.assert_called()
            mock_subprocess.assert_called_once()

    @patch('os.path.isdir')
    @patch('subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_diagram_dot_error_subprocess(self, mock_archivo, mock_subprocess, mock_isdir):
        """Porbar que se maneja errores cuando no está instalado Graphviz"""
        mock_isdir.return_value = True
        mock_subprocess.side_effect = FileNotFoundError("No se encontró dot")
        with patch('scripts.diagram_generator.generate_dependencies') as mock_deps:
            mock_deps.return_value = {'modulo1': ['dep1']}
            generate_diagram_dot()  # No debería fallar
            mock_archivo.assert_called()
