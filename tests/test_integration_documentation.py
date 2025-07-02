import os
import subprocess
import tempfile
import shutil


def crear_modulo_ejemplo(ruta):
    os.mkdir(ruta)
    with open(os.path.join(ruta, "main.tf"), "w") as f:
        f.write("""
module "mod2" {
  source = "../mod2"
}
variable "var1" {
  description = "Una variable"
  type = string
  default = "valor1"
}
""")
    with open(os.path.join(ruta, "variables.tf"), "w") as f:
        f.write("""
variable "var1" {
  description = "Una variable"
  type = string
  default = "valor1"
}
""")
    with open(os.path.join(ruta, "outputs.tf"), "w") as f:
        f.write("""
output "salida1" {
  description = "Un output"
  value = var.var1
}
""")
    with open(os.path.join(ruta, "README.md"), "w") as f:
        f.write("# Módulo mod1\n### Descripción\nMódulo de prueba.")


def crear_estructura_infra(base_path):
    modules_path = os.path.join(base_path, "infra", "modules")
    os.makedirs(modules_path)
    crear_modulo_ejemplo(os.path.join(modules_path, "mod1"))
    crear_modulo_ejemplo(os.path.join(modules_path, "mod2"))


def test_integracion_documentacion_y_diagrama():
    with tempfile.TemporaryDirectory() as tmpdir:
        crear_estructura_infra(tmpdir)

        # Copiar scripts a tmpdir/scripts
        os.makedirs(os.path.join(tmpdir, "scripts"))
        shutil.copy("scripts/doc_extractor.py", os.path.join(tmpdir, "scripts", "doc_extractor.py"))
        shutil.copy("scripts/diagram_generator.py", os.path.join(tmpdir, "scripts", "diagram_generator.py"))

        # Ejecutar doc_extractor
        ret1 = subprocess.run(
            ["python", "doc_extractor.py"],
            cwd=os.path.join(tmpdir, "scripts"),
            capture_output=True,
            text=True
        )
        assert ret1.returncode == 0

        # Verificar que se genera la documentación de los módulos
        docs_path = os.path.join(tmpdir, "docs")
        assert os.path.isdir(docs_path)
        assert os.path.isfile(os.path.join(docs_path, "mod1.md"))
        assert os.path.isfile(os.path.join(docs_path, "mod2.md"))

        # Ejecutar diagram_generator
        ret2 = subprocess.run(
            ["python", "diagram_generator.py"],
            cwd=os.path.join(tmpdir, "scripts"),
            capture_output=True,
            text=True
        )
        assert ret2.returncode == 0
        assert os.path.isfile(os.path.join(docs_path, "dependencies.dot"))


if __name__ == "__main__":
    test_integracion_documentacion_y_diagrama()
