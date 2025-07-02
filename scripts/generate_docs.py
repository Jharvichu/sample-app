import os          # Para manejo de rutas y archivos
import re          # Para expresiones regulares(regex)
import subprocess  # Para que llame a 'dot' de Graphviz y generar PNG de grafo
import argparse

ROOT_DIR = os.path.join(os.path.dirname(__file__), "../infra/modules") #ruta de modulos de Terraform
DOCS_DIR = os.path.join(os.path.dirname(__file__), "../docs")  # ruta donde se generaran los markdown y diagramas 

# Extraccion de metadatos #

def parse_readme_md(module_path):
    """
    Extrae el nombre del módulo y su descripción desde README.md si existe.
    Devuelve un diccionario con:
        - modulo: nombre del módulo (extraído de encabezado)
        - descripcion: texto bajo ### Descripción
    Si README.md no existe, retorna valores "<null>".
    """
    readme_path = os.path.join(module_path, "README.md")
    if not os.path.exists(readme_path):
        return {"modulo": "<null>", "descripcion": "<null>"}

    with open(readme_path, encoding="utf-8") as f:
        content = f.read()

    # Buscara linea en el encabezado "# Módulo <nombre>"
    module_match = re.search(r'^[ \t]*#[ \t]*M[óo]dulo[ \t]+(.+)$',
                            content, re.MULTILINE | re.IGNORECASE)
    # Buscar sección bajo ### Descripción hasta el siguiente ###
    descripcion_match = re.search(r'### Descripción\s+(.*?)(?=\n###|\Z)',
                                content, re.DOTALL)

    return {
        "modulo": module_match.group(1).strip() if module_match else "<null>",
        "descripcion": descripcion_match.group(1).strip() if descripcion_match else "<null>"
    }

def parse_variables_tf(module_path):
    """
    Extrae variables de entrada de variables.tf: nombre, tipo, descripción, valor por defecto.
    Devuelve una lista de diccionarios por cada variable.
    """
    path = os.path.join(module_path, "variables.tf")
    if not os.path.exists(path):
        return []

    with open(path, encoding='utf-8') as f:
        content = f.read()

    # Regex para encontrar bloques de variable "nombre"
    pattern = r'variable\s+"(?P<name>[^"]+)"\s*\{(?P<body>.*?)\}'
    matches = re.finditer(pattern, content, re.DOTALL)
    variables = []

    for match in matches:
        name = match.group("name")
        body = match.group("body")

        # Buscar campos opcionales dentro del cuerpo de la variable
        desc = re.search(r'description\s*=\s*"([^"]+)"', body)
        type_ = re.search(r'type\s*=\s*"?([^"]+)"?', body)
        default = re.search(r'default\s*=\s*"?([^\n\"]+)"?', body)

        variables.append({
            "name": name,
            "descripcion": desc.group(1) if desc else "<null>",
            "type": type_.group(1) if type_ else "<null>",
            "default": default.group(1) if default else "<null>"
        })

    return variables

def parse_outputs_tf(module_path):
    """
    Extrae outputs de outputs.tf: nombre, descripción, valor; devuelve una lista de diccionarios por output.
    """
    path = os.path.join(module_path, "outputs.tf")
    if not os.path.exists(path):
        return []

    with open(path, encoding='utf-8') as f:
        content = f.read()

    pattern = r'output\s+"(?P<name>[^"]+)"\s*\{(?P<body>.*?)\}'
    matches = re.finditer(pattern, content, re.DOTALL)
    outputs = []

    for match in matches:
        name = match.group("name")
        body = match.group("body")

        desc = re.search(r'description\s*=\s*"([^"]+)"', body)
        value = re.search(r'value\s*=\s*"?([^\n\"\}]+)"?', body)

        outputs.append({
            "name": name,
            "descripcion": desc.group(1) if desc else "<null>",
            "value": value.group(1) if value else "<null>"
        })

    return outputs

def parse_main_tf(module_path):
    """
    Extrae los recursos creados en main.tf tipo de recurso (aws_s3_bucket, etc.) y  nombre del recurso
    Devuelve una lista de diccionarios por recurso.
    """
    path = os.path.join(module_path, "main.tf")
    if not os.path.exists(path):
        return []

    with open(path, encoding='utf-8') as f:
        content = f.read()

    # Buscara bloquesde resource "<tipo>" "<nombre>" { ... }
    pattern = r'resource\s+"(?P<type>[^"]+)"\s+"(?P<name>[^"]+)"\s*\{'
    matches = re.finditer(pattern, content)
    resources = []

    for match in matches:
        resources.append({
            "type": match.group("type"),
            "name": match.group("name")
        })

    return resources

# Generación de archivo markdown

def generate_markdown(module_name, metadata, variables, outputs, resources, output_dir):
    """
    Genera un archivo Markdown en docs/ con la documentación del módulo:
        * nombre y descripción
        * tabla de variables
        * tabla de outputs
        * lista de recursos creados
    """
    md = []
    md.append(f"# Módulo {metadata['modulo']}\n\n")
    md.append(f"{metadata['descripcion']}\n\n")

    # Para las tablas de variables si existen
    if variables:
        md.append("### Variables\n\n| Nombre | Tipo | Descripción | Default |\n|--------|------|-------------|---------|\n")
        for var in variables:
            md.append(f"| {var['name']} | {var['type']} | {var['descripcion']} | {var['default']} |\n")
        md.append("\n")

    # Para la tabla de outputs si existen
    if outputs:
        md.append("### Outputs\n\n| Nombre | Descripción | Valor |\n|--------|-------------|-------|\n")
        for out in outputs:
            md.append(f"| {out['name']} | {out['descripcion']} | {out['value']} |\n")
        md.append("\n")

    # Lista de recursos si existen
    if resources:
        md.append("### Recursos\n\n")
        for res in resources:
            md.append(f"- {res['type']} {res['name']}\n")

    # Guardar archivo Markdown con nombre del módulo
    if not os.path.exists(f"{DOCS_DIR}/{output_dir}"):
        os.makedirs(f"{DOCS_DIR}/{output_dir}")
    with open(os.path.join(f"{DOCS_DIR}/{output_dir}", f"{module_name}.md"), 'w', encoding='utf-8') as f:
        f.writelines(md)

# Generación del diagrama DOT

def extract_dependencies(module_path):
    """
    Extrae dependencias de main.tf como módulos utilizados, depends_on, referencias a variables y data
    source a módulos locales. Devuelve una lista de dependencias encontradas en el módulo.
    """
    dependencies = []
    path = os.path.join(module_path, "main.tf")
    if not os.path.exists(path):
        return dependencies

    with open(path, encoding='utf-8') as f:
        content = f.read()

    patterns = [
        r'module\s+"([^"]+)"',                 # módulos utilizados
        r'depends_on\s*=\s*\[([^\]]+)\]',      # depends_on
        r'var\.([a-zA-Z0-9_-]+)',              # variables referenciadas
        r'data\.([a-zA-Z0-9_-]+)',             # data referenciado
        r'source\s*=\s*"../([a-zA-Z0-9_-]+)"'  # source a módulos locales
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # match puede ser tupla si el patrón llegara a capturar múltiples grupos.
            if isinstance(match, tuple):
                dependencies.append(match[0])
            else:
                dependencies.append(match)

    return dependencies

def generate_diagram_dot(all_dependencies, output_dir):
    """
    Genera un archivo dependencies.dot y una imagen PNG (grafo de dependencias entre módulos).
    Usa Graphviz (dot) para convertir el .dot en .png automáticamente.
    """
    dot_path = os.path.join(f"{DOCS_DIR}/{output_dir}", "dependencies.dot")
    png_path = os.path.join(f"{DOCS_DIR}/{output_dir}", "dependencies.png")

    with open(dot_path, 'w', encoding='utf-8') as f:
        f.write('digraph Dependencies {\n')
        written = set()  # para evitar escribir aristas duplicadas

        for module, deps in all_dependencies.items():
            for dep in set(deps):  #  set() para evitar duplicados
                line = f'    "{module}" -> "{dep}";\n'
                if line not in written:
                    f.write(line)
                    written.add(line)

        f.write('}\n')

    try:
        subprocess.run(["dot", "-Tpng", dot_path, "-o", png_path], check=True)
        print(f" Diagrama generado en {png_path}")
    except FileNotFoundError:
        print(" Graphviz no instalado o 'dot' no está en PATH. Instálalo para generar el PNG.")

# Funcion main

def main():
    
    parser = argparse.ArgumentParser(description="Generador de documentacion de IaC")
    parser.add_argument('--output', type=str, default='../docs/lastet')
    args = parser.parse_args()
    version = args.output

    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)

    if not os.path.exists(ROOT_DIR):
        print(f" Directorio {ROOT_DIR} no existe")
        return

    modules = os.listdir(ROOT_DIR)  # Lista de carpetas de módulos Terraform
    all_dependencies = {}  # Guardará las dependencias por módulo para el grafo

    for module in modules:
        module_path = os.path.join(ROOT_DIR, module)
        if not os.path.isdir(module_path):
            continue  # saltar si no es un directorio

        # Extraer metadatos y dependencias del módulo
        metadata = parse_readme_md(module_path)
        variables = parse_variables_tf(module_path)
        outputs = parse_outputs_tf(module_path)
        resources = parse_main_tf(module_path)
        dependencies = extract_dependencies(module_path)

        # Generar archivo Markdown con documentación de cada módulo
        generate_markdown(module, metadata, variables, outputs, resources, version)

        # Guardar dependencias para grafo final
        all_dependencies[module] = dependencies

    # Generar grafo de dependencias global entre los módulos
    generate_diagram_dot(all_dependencies, version)

    print(f"\n Documentación y diagrama generados en {version}.")


if __name__ == "__main__":
    main()

