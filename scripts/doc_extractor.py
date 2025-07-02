import os
import re
import sys


def parse_main_tf(modulo_path):
    """
    Lee main.tf y extrae recursos (tipo, nombre, filename, command).
    """
    main_tf_path = os.path.join(modulo_path, "main.tf")

    if not os.path.exists(main_tf_path):
        return []

    try:
        with open(main_tf_path, 'r', encoding='utf-8') as f:
            content = f.read()

        resources = []
        pattern = r'resource\s+"(?P<type>[^"]+)"\s+"(?P<name>[^"]+)"\s*{(?P<body>.*?)\n}'
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            resource_type = match.group("type")
            resource_name = match.group("name")
            body = match.group("body")

            if (resource_type == "local_file"):
                filename_match = re.search(r'filename\s*=\s*["\'](.+?)["\']', body, re.DOTALL)
                content_match = re.search(r'content\s*=\s*["\'](.+?)["\']', body, re.DOTALL)

                filename = filename_match.group(1) if filename_match else "<null>"
                content_description = content_match.group(1) if content_match else "<null>"

                resources.append({
                    "type": resource_type,
                    "name": resource_name,
                    "filename": filename,
                    "content": content_description
                })

            elif (resource_type == "null_resource"):
                cmd_match = re.search(r'command\s*=\s*"(.*?)"\s*$', body, re.MULTILINE)
                command = cmd_match.group(1).strip() if cmd_match else "<null>"

                output_file = re.search(r'>\s*([^\s>]+)', command)
                output_file = output_file.group(1) if output_file else "<null>"

                resources.append({
                    "type": resource_type,
                    "name": resource_name,
                    "command": command,
                    "output_file": output_file
                })

        return resources

    except Exception as e:
        print(f"Error leyendo {main_tf_path}: {e}")
        return []


def parse_variables_tf(modulo_path):
    """
    Lee variables.tf y extrae recursos (nombre, tipo, descripcion, valor por defecto).
    """
    variables_tf_path = os.path.join(modulo_path, "variables.tf")

    if not os.path.exists(variables_tf_path):
        return []

    try:
        with open(variables_tf_path, 'r', encoding='utf-8') as f:
            content = f.read()

        resources = []
        pattern = r'variable\s+"(?P<name>[^"]+)"\s*{\s*(?P<body>[^}]+)}'
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            variable_name = match.group("name")
            body = match.group("body")

            description_match = re.search(r'description\s*=\s*["\'](.+?)["\']', body)
            type_match = re.search(r'type\s*=\s*(?:"|\')?([^\n"\']+)(?:"|\')?', body)
            default_match = re.search(r'default\s*=\s*(?:"|\')?([^"\']+)(?:"|\')?', body)

            description = description_match.group(1) if description_match else "<null>"
            type = type_match.group(1) if type_match else "<null>"
            default = default_match.group(1).strip() if default_match else "<null>"

            resources.append({
                "name": variable_name,
                "descripcion": description,
                "type": type,
                "default": default
            })

        return resources

    except Exception as e:
        print(f"Error leyendo {variables_tf_path}: {e}")
        return []


def parse_outputs_tf(modulo_path):
    """
    Lee outputs.tf y extrae recursos (descripcion, nombre, valor).
    """
    outputs_tf_path = os.path.join(modulo_path, "outputs.tf")

    if not os.path.exists(outputs_tf_path):
        return []

    try:
        with open(outputs_tf_path, 'r', encoding='utf-8') as f:
            content = f.read()

        resources = []
        pattern = r'output\s+"(?P<name>[^"]+)"\s*{(?P<body>.*?)\n}'
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            variable_name = match.group("name")
            body = match.group("body")

            description_match = re.search(r'description\s*=\s*["\'](.+?)["\']', body)
            value_match = re.search(r'value\s*=\s*(?:"|\')?([^"\'}\s]+)(?:"|\')?', body)

            description = description_match.group(1) if description_match else "<null>"
            value = value_match.group(1) if value_match else "<null>"

            resources.append({
                "name": variable_name,
                "descripcion": description,
                "value": value,
            })

        return resources

    except Exception as e:
        print(f"Error leyendo {outputs_tf_path}: {e}")
        return []


def parse_readme_md(modulo_path):
    """
    Extrae la descripción de un README.md con estructura esperada: ## Descripción.
    """
    readme_path = os.path.join(modulo_path, "README.md")

    if not os.path.exists(readme_path):
        return {}

    with open(readme_path, encoding="utf-8") as f:
        content = f.read()

    module_match = re.search(r'^[ \t]*#[ \t]*M[óo]dulo[ \t]+(.+)$', content, re.MULTILINE | re.IGNORECASE)
    descripcion_match = re.search(r'### Descripción\s+(.*?)(?=\n###|\Z)', content, re.DOTALL)

    descripcion = descripcion_match.group(1).strip() if descripcion_match else "<null>"
    module = module_match.group(1) if module_match else "<null>"

    return {
        "modulo": module,
        "descripcion": descripcion
    }


def build_content(modulo_path):
    """
    Genera el contenido Markdown de un modulo.
    """
    readme = parse_readme_md(modulo_path)
    main_resources = parse_main_tf(modulo_path)
    variables = parse_variables_tf(modulo_path)
    outputs = parse_outputs_tf(modulo_path)

    md = []
    titulo = readme.get("modulo", "<sin módulo>").strip()
    descripcion = readme.get("descripcion", "<sin descripción>").strip()

    md.append(f"# Módulo {titulo}\n")
    md.append(f"{descripcion}\n")
    md.append("\n")

    if variables:
        md.append("### Tabla de variables:\n")
        md.append("| Nombre | Tipo | Descripcion | Default |\n")
        md.append("|--------|------|-------------|---------|\n")
        for var in variables:
            default = var.get("default", "") if var.get("default") is not None else ""
            md.append(f"| {var.get('name', '')} | {var.get('type', '')} | {var.get('descripcion', '')} | {default} |\n")
        md.append("\n")

    if outputs:
        md.append("### Tabla de outputs:\n")
        md.append("| Nombre | Descripción | Valor |\n")
        md.append("|--------|-------------|-------|\n")
        for out in outputs:
            md.append(f"| {out.get('name', '')} | {out.get('descripcion', '')} | {out.get('value', '')} |\n")
        md.append("\n")

    if main_resources:
        md.append("### Lista de recursos:\n")
        for res in main_resources:
            if res["type"] == "local_file":
                md.append(
                    f'- Recurso de tipo `{res["type"]}` con nombre **{res["name"]}** crea el archivo `{res["filename"]}` con contenido `{res["content"]}`\n'
                )
            elif res["type"] == "null_resource":
                md.append(
                    f'- Recurso de tipo `{res["type"]}` con nombre **{res["name"]}** ejecuta el comando `{res["command"]}` en `{res["output_file"]}`\n'
                )
            else:
                md.append(f'- Recurso de tipo `{res["type"]}` con nombre **{res["name"]}**\n')
        md.append("\n")

    return "".join(md)


def write_md():
    """
    Escribe el contenido dado en un archivo README.md en la ruta especificada.
    """
    root = os.path.join(os.path.dirname(__file__), "../infra/modules")
    docs_path = os.path.join(os.path.dirname(__file__), "../docs")

    if not os.path.isdir(root):
        print(f"ERROR: No se encontro el directorio '{root}' ")
        sys.exit(1)

    if not os.path.isdir(docs_path):
        print("Creando directorio docs")
        try:
            os.mkdir(docs_path)
        except PermissionError:
            print("Permisos denegados")

    modules_list = os.listdir(root)

    for module in modules_list:
        content = build_content(f'{root}/{module}')
        with open(f'{docs_path}/{module}.md', 'w') as doc:
            doc.write(content)


if __name__ == "__main__":
    write_md()
