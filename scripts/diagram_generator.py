import os  # permite interactuar con el sistema operativo donde se utiliza Python
import re  # proporciona operaciones con regex
import subprocess  # libreria que permite ejecutar comandos externos del sistema operativo


# Esta función principal recorre todos los módulos Terraform ubicados en  infra/modules
# y genera un diccionario con las dependencias encontradas en los archivos main.tf
def generate_dependencies():
    dependencies = {}  # Diccionario final con el nombre del módulo y sus dependencias
    root = os.path.join(os.path.dirname(__file__), "../infra/modules")  # Ruta base de los módulos
    modules = os.listdir(root)  # Lista de carpetas (módulos)

    for module in modules:
        content = parce_dependencies(f'{root}/{module}')  # Extrae dependencias del módulo
        dependencies[f'{module}'] = content  # Almacena en el diccionario

    return dependencies


# Esta función analiza un módulo Terraform hasta encontrar todas sus dependencias
def parce_dependencies(module) -> list:
    dependencias = []  # Lista de dependencias que han sido halladas

    # Patrones de expresiones regulares que buscan distintas referencias comunes en Terraform:
    patrones = [
        r'module\s*"([^"]+)"',             # Coincide con referencias a submódulos
        r'depends_on\s*=\s*\[([^\]]+)\]',  # Coincide con declaraciones "depends_on = [ ... ]"
        r'var\.([a-zA-Z0-9_-]+)',          # Coincide con variables (var.nombre)
        r'data\.([a-zA-Z0-9_-]+)',         # Coincide con datos externos (data.tipo)
        r'source\s*=\s*"../([a-zA-Z0-9_-]+)"',  # Coincide con módulos locales "../modulo"
    ]
    for archivo in os.listdir(module):
        if archivo.endswith("main.tf"):
            with open(os.path.join(module, archivo), 'r') as f:
                contenido = f.read()

                # Aplica todos los patrones menos el último
                for patron in patrones[:-1]:
                    coincidencias = re.findall(patron, contenido)
                    dependencias.extend(coincidencias)

                # Patrón especial para fuentes relativas a otros módulos locales
                coincidencias_remote = re.findall(patrones[-1], contenido, re.DOTALL)
                for coincidencia in coincidencias_remote:
                    # coincidencia es una cadena, no una tupla, por eso se usa directamente
                    dependencias.append(coincidencia[1])

    return dependencias


# Crea un archivo .dot (formato de Graphviz) con las dependencias detectadas
# y lo convierte en una imagen PNG
def generate_diagram_dot():
    docs_path = os.path.join(os.path.dirname(__file__), "../docs")  # Ruta del directorio docs

    # Si el directorio 'docs' no existe, se crea
    if not os.path.isdir(docs_path):
        print("Creando directorio docs")
        try:
            os.mkdir(docs_path)
        except PermissionError:
            print("Permisos denegados")

    # Llama a la función para obtener dependencias de los módulos
    dependencies = generate_dependencies()
    relaciones_escritas = set()  # Para evitar relaciones duplicadas

    # Salida para los archivos .dot y .png
    dot_path = os.path.join(docs_path, "dependencies.dot")
    png_path = os.path.join(docs_path, "dependencies.png")

    # Escribe el archivo DOT con relaciones entre módulos
    with open(dot_path, 'w') as f:
        f.write('digraph Dependencies {\n')  # Comienza el grafo

        for modulo, deps in dependencies.items():
            for dep in set(deps):  # Con esto evito se evita repetir dependencias entre módulos
                relacion = f'"{modulo}" -> "{dep}";'
                if relacion not in relaciones_escritas:
                    f.write(f'    {relacion}\n')  # Escribe la relación en el archivo
                    relaciones_escritas.add(relacion)  # Marca como ya escrita

        f.write('}\n')  # Acaba el grafo

    # Intenta convertir el archivo .dot en una imagen PNG utilizando Graphviz
    try:
        subprocess.run(["dot", "-Tpng", dot_path, "-o", png_path], check=True)
        print(f"Imagen generada en: {png_path}")
    except FileNotFoundError:
        print("Error: Graphviz no está instalado o 'dot' no está en el PATH.")


# Entrada principal del script
if __name__ == "__main__":
    generate_diagram_dot()  # Ejecuta esta función para que genere archivo dot y su imagen.
