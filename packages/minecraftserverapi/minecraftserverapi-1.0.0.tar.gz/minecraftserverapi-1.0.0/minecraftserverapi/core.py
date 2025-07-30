# ---------------------------------------
# Librería: minecraftserverapi v1.
# Autor: Bautista Fabris, V4FAB
# Descripción: Creador de servidores de Minecraft
# ---------------------------------------


import os
import subprocess
import threading
import time
import requests
import zipfile

try:
    import utilfab as fb
except ImportError:
    print("Utilfab no está instalado, instalalo con: !pip install utilfab --upgrade")
    fb = None  # Para que no falle

class HelpModule:
    @staticmethod
    def general():
        print("""
        mcserverapi - Ayuda general:

        Configuración básica:
          - use_drive: True para Google Drive, False local.
          - path: Ruta absoluta para el servidor.
          - ngrok_authtoken: Token ngrok.
          - server: 'paper', 'forge', etc.
          - version: Versión del servidor.
          - build: (opcional) Build específica.

        Comandos principales:
          - .start_server(), .stop_server(), .start_ngrok(), .repair(), .help

        Para ayuda específica, llama:
          - .help.ngrok("topic")
          - .help.forge()
          - .help.paper()
        """)

    @staticmethod
    def ngrok(topic=None):
        topics = {
            "link": "Para exponer tu servidor con ngrok, necesitás un token de autenticación que sacás desde https://dashboard.ngrok.com/get-started/your-authtoken . Usá .start_ngrok() para iniciar y obtener la URL pública TCP.",
            "token": "El token ngrok se copia desde el dashboard de ngrok, y debe pasarse en config bajo la clave 'ngrok_authtoken'.",
            "instalacion": "Ngrok se descarga y configura automáticamente. No necesitás instalarlo manualmente.",
            "errores": "Si ngrok no se conecta o no aparece la URL, revisá que tu red permita conexiones TCP salientes y que no haya conflictos en localhost:4040."
        }
        if topic and topic.lower() in topics:
            print(f"ngrok - {topic}:\n{topics[topic.lower()]}")
        else:
            print("Temas ngrok disponibles:", ", ".join(topics.keys()))
            print("Ejemplo: mcserverapi.MinecraftServer.help.ngrok('link')")

    @staticmethod
    def paper():
        print("""
        PaperMC:
          - Descarga automática de builds oficiales.
          - Usa builds más recientes o especifica build en config.
          - Documentación API builds: https://papermc.io/api
          - Problemas comunes: puerto ocupado, RAM insuficiente, eula.txt no aceptado.
        """)

    @staticmethod
    def forge():
        print("""
        Forge:
          - La instalación requiere descargar el instalador de Forge para la versión deseada.
          - El instalador genera el jar del servidor y archivos necesarios.
          - mcserverapi intenta automatizar esta descarga y ejecución.
          - Asegúrate de tener Java instalado y permisos adecuados.
          - Si hay problemas, ejecuta el instalador manualmente y luego usa mcserverapi con el jar generado.
          - Documentación: https://files.minecraftforge.net/
        """)


class MinecraftServer:
    SUPPORTED_SERVERS = {
        "paper": {
            "1.20.1": {
                "164": "https://api.papermc.io/v2/projects/paper/versions/1.20.1/builds/164/downloads/paper-1.20.1-164.jar",
                "165": "https://api.papermc.io/v2/projects/paper/versions/1.20.1/builds/165/downloads/paper-1.20.1-165.jar"
            }
            # Puedes añadir más versiones y builds aquí si quieres.
        },
        "forge": {
            "installer_base_url": "https://maven.minecraftforge.net/net/minecraftforge/forge/{version}/forge-{version}-installer.jar"
        }
    }

    COMMON_ERRORS = {
        "java.lang.OutOfMemoryError": "Falta memoria RAM asignada, considera aumentar -Xmx (ej: -Xmx2G).",
        "Port already in use": "El puerto está ocupado, cambialo o cerrá otro servidor que lo esté usando.",
        "eula.txt missing": "Acepta el EULA creando el archivo eula.txt con 'eula=true'.",
        "java not found": "Java no está instalado o no está en el PATH del sistema.",
        "Could not reserve enough space": "No hay suficiente memoria RAM libre para el servidor, liberá RAM o bajá -Xmx.",
        "Failed to bind to port": "Puerto bloqueado o usado, cambiar puerto o cerrar procesos."
    }

    help = HelpModule

    def __init__(self, config):
        self.use_drive = config.get("use_drive", False)
        self.drive_path = config.get("path")
        self.port = config.get("port", 25565)
        self.ngrok_token = config.get("ngrok_authtoken")
        self.server_type = config.get("server", "paper").lower()
        self.version = config.get("version", "1.20.1")
        self.build = config.get("build")
        self.server_process = None
        self.ngrok_process = None
        self.ngrok_url = None

        if self.use_drive:
            try:
                from google.colab import drive
                print("Montando Google Drive...")
                drive.mount('/content/drive')
            except ModuleNotFoundError:
                print("No estamos en Colab, no se montó Drive.")

        if not os.path.exists(self.drive_path):
            os.makedirs(self.drive_path)

    def _get_paper_builds(self):
        url = f"https://api.papermc.io/v2/projects/paper/versions/{self.version}"
        try:
            resp = requests.get(url).json()
            return resp.get('builds', [])
        except Exception as e:
            print(f"Error al obtener builds para PaperMC: {e}")
            return []

    def _get_download_url(self):
        if self.server_type == "paper":
            if self.version not in self.SUPPORTED_SERVERS.get("paper", {}):
                builds = self._get_paper_builds()
                if not builds:
                    raise ValueError(f"No hay builds disponibles para la versión {self.version}")
                selected_build = self.build or str(max(builds))
                print(f"Seleccionando build {selected_build} para PaperMC {self.version}")
                url = f"https://api.papermc.io/v2/projects/paper/versions/{self.version}/builds/{selected_build}/downloads/paper-{self.version}-{selected_build}.jar"
                return url
            else:
                builds = self.SUPPORTED_SERVERS["paper"][self.version]
                if self.build:
                    if self.build in builds:
                        return builds[self.build]
                    else:
                        raise ValueError(f"Build {self.build} no disponible para la versión {self.version}")
                else:
                    last_build = sorted(builds.keys(), key=int)[-1]
                    return builds[last_build]

        elif self.server_type == "forge":
            base_url = self.SUPPORTED_SERVERS["forge"]["installer_base_url"]
            url = base_url.format(version=self.version)
            return url

        else:
            raise NotImplementedError(f"Servidor '{self.server_type}' no soportado aún.")

    def download_server(self):
        jar_name = "server.jar"
        destino = os.path.join(self.drive_path, jar_name)
        if os.path.exists(destino):
            print("Servidor ya descargado.")
            return True

        url = self._get_download_url()
        print(f"Descargando servidor desde {url} ...")

        r = requests.get(url)
        if r.status_code != 200:
            print(f"Error al descargar: código {r.status_code}")
            return False

        if self.server_type == "forge":
            instalador_path = os.path.join(self.drive_path, "forge-installer.jar")
            with open(instalador_path, "wb") as f:
                f.write(r.content)
            print("Ejecutando instalador Forge para preparar servidor...")
            try:
                subprocess.run(
                    ["java", "-jar", instalador_path, "--installServer"],
                    cwd=self.drive_path,
                    check=True
                )
                for f in os.listdir(self.drive_path):
                    if f.endswith(".jar") and "forge" in f and "installer" not in f:
                        os.rename(os.path.join(self.drive_path, f), destino)
                        print(f"Jar de Forge preparado: {destino}")
                        break
                else:
                    print("No se encontró jar generado por instalador Forge.")
                    return False
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error ejecutando instalador Forge: {e}")
                return False
        else:
            with open(destino, "wb") as f:
                f.write(r.content)
            print("Servidor descargado.")
            return True

    def accept_eula(self):
        eula_path = os.path.join(self.drive_path, 'eula.txt')
        with open(eula_path, "w") as f:
            f.write("eula=true\n")
        print("EULA aceptado.")

    def start_server(self):
        if self.server_process and self.server_process.poll() is None:
            print("El servidor ya está corriendo.")
            return

        jar_path = os.path.join(self.drive_path, "server.jar")
        if not os.path.exists(jar_path):
            if not self.download_server():
                return

        self.accept_eula()
        print("Iniciando servidor...")
        self.server_process = subprocess.Popen(
            ["java", "-Xmx1G", "-Xms1G", "-jar", jar_path, "nogui"],
            cwd=self.drive_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        threading.Thread(target=self._log_reader, daemon=True).start()

    def _log_reader(self):
        for line in self.server_process.stdout:
            print("[MC]", line, end='')
            self._check_errors(line)

    def _check_errors(self, line):
        for error_text, solution in self.COMMON_ERRORS.items():
            if error_text.lower() in line.lower():
                print(f"[ERROR DETECTADO]: {error_text}\n[SOLUCIÓN]: {solution}")

    def stop_server(self):
        if self.server_process and self.server_process.poll() is None:
            print("Deteniendo servidor...")
            self.server_process.terminate()
            self.server_process.wait()
            print("Servidor detenido.")
        else:
            print("Servidor no está corriendo.")

    def start_ngrok(self):
        if not self.ngrok_token:
            print("No se proporcionó ngrok_authtoken, no se expondrá el servidor.")
            return None

        if self.ngrok_process and self.ngrok_process.poll() is None:
            print("Ngrok ya está corriendo.")
            return self.ngrok_url

        ngrok_path = os.path.join(self.drive_path, "ngrok")
        if not os.path.exists(ngrok_path):
            self._download_ngrok()

        print("Autenticando ngrok...")
        subprocess.run([ngrok_path, "authtoken", self.ngrok_token], cwd=self.drive_path)

        print(f"Iniciando ngrok en el puerto {self.port}...")
        self.ngrok_process = subprocess.Popen(
            [ngrok_path, "tcp", str(self.port)],
            cwd=self.drive_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        time.sleep(5)

        try:
            tunnels = requests.get("http://localhost:4040/api/tunnels").json()['tunnels']
            for tunnel in tunnels:
                if tunnel['proto'] == 'tcp':
                    self.ngrok_url = tunnel['public_url']
                    print(f"Ngrok URL: {self.ngrok_url}")
                    return self.ngrok_url
        except Exception as e:
            print(f"Error al obtener URL de ngrok: {e}")
            return None

    def _download_ngrok(self):
        import urllib.request
        url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-amd64.zip"
        zip_path = os.path.join(self.drive_path, "ngrok.zip")

        print("Descargando ngrok...")
        urllib.request.urlretrieve(url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.drive_path)

        os.remove(zip_path)
        ngrok_path = os.path.join(self.drive_path, "ngrok")
        os.chmod(ngrok_path, 0o755)

    def repair(self):
        repaired = False
        eula_path = os.path.join(self.drive_path, 'eula.txt')
        if not os.path.exists(eula_path):
            print("Reparando: creando eula.txt")
            with open(eula_path, "w") as f:
                f.write("eula=true\n")
            repaired = True

        ngrok_path = os.path.join(self.drive_path, "ngrok")
        if os.path.exists(ngrok_path):
            mode = os.stat(ngrok_path).st_mode
            if not mode & 0o111:
                print("Reparando: asignando permisos ejecutables a ngrok")
                os.chmod(ngrok_path, 0o755)
                repaired = True

        jar_path = os.path.join(self.drive_path, "server.jar")
        if not os.path.exists(jar_path):
            print("Servidor no encontrado, descargando de nuevo...")
            if self.download_server():
                repaired = True

        if repaired:
            print("Reparaciones aplicadas.")
        else:
            print("No se detectaron problemas a reparar.")

    @staticmethod
    def easyMake():
        if fb is None:
            print("La librería utilfab no está instalada, instalala con: !pip install utilfab --upgrade")
            return None

        print("\nBienvenido a mcserverapi.easyMake()")
        print("Este asistente te guiará paso a paso para crear un servidor Minecraft profesional.\n")
        fb.space()

        # Paso 1
        print("¿Vas a usar Google Drive para guardar tu servidor? Esto es útil si usas Google Colab o quieres persistencia en la nube.")
        print("Si no usas Colab o prefieres una carpeta local, responde 'no'.")
        use_drive_str = input("Usar Google Drive? (si/no): ").strip().lower()
        use_drive = use_drive_str.startswith("s")
        fb.space()

        # Paso 2
        if use_drive:
            print("La ruta debe ser la carpeta en tu Google Drive donde se guardará el servidor.")
            print("Ejemplo: /content/drive/MyDrive/MinecraftServer01")
        else:
            print("Elige una ruta local absoluta o relativa donde se guardará el servidor.")
            print("Ejemplo: ./minecraft_server")
        path = input("Ingresa la ruta para guardar el servidor: ").strip()
        fb.space()

        # Paso 3
        print("¿Querés exponer tu servidor públicamente usando ngrok? (Necesitarás un token ngrok válido).")
        print("Si no sabes qué es ngrok, respondé 'no'.")
        usar_ngrok_str = input("Usar ngrok? (si/no): ").strip().lower()
        usar_ngrok = usar_ngrok_str.startswith("s")
        ngrok_token = None
        if usar_ngrok:
            print("Para obtener un token ngrok, registrate en: https://dashboard.ngrok.com/get-started/your-authtoken")
            print("Después de registrarte, copia tu token y pegalo aquí.")
            ngrok_token = input("Ingresá tu token ngrok: ").strip()
        fb.space()

        # Paso 4
        print("Elige qué tipo de servidor querés crear:")
        print("1) paper (recomendado para servidores estables, plugin-friendly)")
        print("2) forge (para mods, más avanzado)")
        tipo_servidor = ""
        while tipo_servidor not in ["1", "2"]:
            tipo_servidor = input("Seleccioná (1 o 2): ").strip()
        server = "paper" if tipo_servidor == "1" else "forge"
        fb.space()

        # Paso 5
        if server == "paper":
            print("Ejemplo de versión para PaperMC: 1.20.1")
            version = input("Ingresá la versión de PaperMC que querés usar: ").strip()
        else:
            print("Para Forge la versión tiene formato especial, ejemplo: 1.20.1-47.0.84")
            print("Para obtener versiones Forge visita: https://files.minecraftforge.net/")
            version = input("Ingresá la versión Forge que querés usar: ").strip()
        fb.space()

        # Paso 6
        print("Elegí el puerto para el servidor (por defecto 25565). Si no sabés qué poner, dejalo vacío y presioná Enter.")
        puerto_str = input("Puerto: ").strip()
        port = int(puerto_str) if puerto_str.isdigit() else 25565
        fb.space()

        # Paso 7
        print("Confirmá la configuración:")
        print(f" - Usar Google Drive: {use_drive}")
        print(f" - Ruta: {path}")
        print(f" - Usar ngrok: {usar_ngrok}")
        if usar_ngrok:
            print(f" - Token ngrok: {'*' * 8} (oculto)")
        print(f" - Tipo de servidor: {server}")
        print(f" - Versión: {version}")
        print(f" - Puerto: {port}")

        confirm = input("Es correcto? (si/no): ").strip().lower()
        if not confirm.startswith("s"):
            print("Operación cancelada. Ejecuta easyMake() de nuevo para comenzar.")
            return None

        config = {
            "use_drive": use_drive,
            "path": path,
            "ngrok_authtoken": ngrok_token if usar_ngrok else None,
            "port": port,
            "server": server,
            "version": version
        }

        print("\nCreando servidor con la configuración indicada...")
        server_instance = MinecraftServer(config)
        print("Intentando reparar servidor...")
        server_instance.repair()
        print("Servidor listo para iniciar con .start_server()")
        return server_instance


def createServer(config):
    return MinecraftServer(config)
