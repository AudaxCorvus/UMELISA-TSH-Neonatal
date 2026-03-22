import os
import ast
import subprocess

def extraer_imports(directorio="."):
    paquetes = set()
    for root, _, files in os.walk(directorio):
        for file in files:
            if file.endswith(".py"):
                ruta = os.path.join(root, file)
                with open(ruta, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read(), filename=ruta)
                        for nodo in ast.walk(tree):
                            if isinstance(nodo, ast.Import):
                                for alias in nodo.names:
                                    paquetes.add(alias.name.split('.')[0])
                            elif isinstance(nodo, ast.ImportFrom):
                                if nodo.module:
                                    paquetes.add(nodo.module.split('.')[0])
                    except Exception:
                        pass
    return paquetes

def crear_requirements(directorio=".", archivo="requirements.txt"):
    paquetes = extraer_imports(directorio)
    dependencias = []
    for paquete in paquetes:
        try:
            resultado = subprocess.run(
                ["pip", "show", paquete],
                capture_output=True,
                text=True
            )
            for linea in resultado.stdout.splitlines():
                if linea.startswith("Version:"):
                    version = linea.split(":", 1)[1].strip()
                    dependencias.append(f"{paquete}=={version}")
        except Exception:
            dependencias.append(paquete)

    with open(archivo, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(dependencias)))

    print(f"Archivo '{archivo}' creado con {len(dependencias)} dependencias.")

# Uso
crear_requirements(".")