import subprocess
import sys

if __name__ == "__main__":
    print("Iniciando servidor MES Honda Celaya...")
    try:
        # Ejecuta uvicorn usando el intérprete de Python actual (del entorno virtual)
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--app-dir", "backend"
        ])
    except KeyboardInterrupt:
        print("\nServidor detenido.")
