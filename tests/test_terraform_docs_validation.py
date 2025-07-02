import os
import pytest
import re
from scripts.doc_extractor import parse_variables_tf, parse_outputs_tf


class ValidadorTerraform:
    # Inicializar rutas para encontrar modulos y docs
    def __init__(self, ruta_modulos, ruta_docs):
        self.ruta_modulos = ruta_modulos
        self.ruta_docs = ruta_docs

    def obtener_modulos(self):
        # Buscar todos los directorios de modulos
        if not os.path.exists(self.ruta_modulos):
            return []
        return [n for n in os.listdir(self.ruta_modulos)
                if os.path.isdir(os.path.join(self.ruta_modulos, n))]

    def parsear_doc_variables(self, modulo):
        # Extraer las variables documentadas del markdown
        archivo_doc = os.path.join(self.ruta_docs, f"{modulo}.md")
        if not os.path.exists(archivo_doc):
            return []
        with open(archivo_doc, 'r') as f:
            contenido = f.read()
        # Se busca patron de tabla de variables
        patron = r'### Tabla de variables:.*?\n\|.*?\n\|.*?\n((?:\|.*?\n)*)'
        match = re.search(patron, contenido, re.DOTALL)
        if not match:
            return []
        variables = []
        # Procesando cada fila de la tabla para obtener nombres
        for fila in match.group(1).strip().split('\n'):
            if '|' in fila:
                partes = [p.strip() for p in fila.split('|')[1:-1]]
                if len(partes) >= 4:
                    variables.append(partes[0])  # solo el nombre
        return variables

    def parsear_doc_outputs(self, modulo):
        # Obtener outputs del archivo de documentacion
        archivo_doc = os.path.join(self.ruta_docs, f"{modulo}.md")
        if not os.path.exists(archivo_doc):
            return []
        with open(archivo_doc, 'r') as f:
            contenido = f.read()
        # Se usa regex para encontrar la tabla de outputs
        patron = r'### Tabla de outputs:.*?\n\|.*?\n\|.*?\n((?:\|.*?\n)*)'
        match = re.search(patron, contenido, re.DOTALL)
        if not match:
            return []
        outputs = []
        # Se recorre filas para extraer nombres
        for fila in match.group(1).strip().split('\n'):
            if '|' in fila:
                partes = [p.strip() for p in fila.split('|')[1:-1]]
                if len(partes) >= 3:
                    outputs.append(partes[0])  # solo el nombre
        return outputs

    def verificar_variables(self, modulo):
        # Comparar variables del tf con las documentadas
        ruta_modulo = os.path.join(self.ruta_modulos, modulo)
        vars_tf = [v['name'] for v in parse_variables_tf(ruta_modulo)]
        vars_doc = self.parsear_doc_variables(modulo)
        # Detectar variables que faltan o sobran
        faltantes = set(vars_tf) - set(vars_doc)
        extras = set(vars_doc) - set(vars_tf)
        return faltantes, extras

    def verificar_outputs(self, modulo):
        # Verificar si outputs coinciden con documentacion
        ruta_modulo = os.path.join(self.ruta_modulos, modulo)
        outs_tf = [o['name'] for o in parse_outputs_tf(ruta_modulo)]
        outs_doc = self.parsear_doc_outputs(modulo)
        # Identificar outputs faltantes o adicionales
        faltantes = set(outs_tf) - set(outs_doc)
        extras = set(outs_doc) - set(outs_tf)
        return faltantes, extras


@pytest.fixture
def validador():
    # Configurar rutas
    base = os.path.dirname(os.path.dirname(__file__))
    modulos = os.path.join(base, "infra", "modules")
    docs = os.path.join(base, "docs")
    return ValidadorTerraform(modulos, docs)


class TestDocsTerraform:

    def test_variables_root_dir(self, validador):
        # Verificar que variables estan bien documentadas
        faltantes, extras = validador.verificar_variables("root_dir")
        assert not faltantes, f"Variables sin documentar: {faltantes}"
        assert not extras, f"Variables extra en docs: {extras}"

    def test_variables_config_files(self, validador):
        # Comprobar documentacion de variables de config
        faltantes, extras = validador.verificar_variables("config_files")
        assert not faltantes, f"Variables sin documentar: {faltantes}"
        assert not extras, f"Variables extra en docs: {extras}"

    def test_outputs_root_dir(self, validador):
        # Verificar outputs del modulo root_dir
        faltantes, extras = validador.verificar_outputs("root_dir")
        assert not faltantes, f"Outputs sin documentar: {faltantes}"
        assert not extras, f"Outputs extra en docs: {extras}"

    def test_outputs_config_files(self, validador):
        # Verificar outputs del modulo config_files
        faltantes, extras = validador.verificar_outputs("config_files")
        assert not faltantes, f"Outputs sin documentar: {faltantes}"
        assert not extras, f"Outputs extra en docs: {extras}"

    def test_todos_modulos_variables(self, validador):
        # Procesar todos los modulos para variables
        modulos = validador.obtener_modulos()
        for modulo in modulos:
            faltantes, extras = validador.verificar_variables(modulo)
            assert not faltantes and not extras, f"Problemas en {modulo}"

    def test_todos_modulos_outputs(self, validador):
        # Validar outputs de todos los modulos
        modulos = validador.obtener_modulos()
        for modulo in modulos:
            faltantes, extras = validador.verificar_outputs(modulo)
            assert not faltantes and not extras, f"Problemas en {modulo}"
