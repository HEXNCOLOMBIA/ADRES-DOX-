# ================== AUTO-INSTALADOR ==================
import sys
import subprocess
import time
import os

REQUIRED_PACKAGES = [
    "requests",
    "beautifulsoup4",
    "lxml",
    "2captcha-python",
    "urllib3"
]

def instalar_dependencias():
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg.split("-")[0])
        except ImportError:
            print(f"[+] Instalando dependencia: {pkg}")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", pkg
            ])

instalar_dependencias()

# ================== IMPORTS ==================
import requests
from twocaptcha import TwoCaptcha
from bs4 import BeautifulSoup
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================== ESTILO ==================
R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
C = "\033[96m"
W = "\033[97m"
RESET = "\033[0m"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

# ================== BANNER ==================
BANNER = f"""
{C}
 ██████╗ ██████╗  ██████╗
██╔═══██╗██╔══██╗██╔════╝
██║   ██║██████╔╝██║     
██║   ██║██╔══██╗██║     
╚██████╔╝██║  ██║╚██████╗
 ╚═════╝ ╚═╝  ╚═╝ ╚═════╝

   MODULO ADRES • SISTEMA DE CONSULTA
   BY HEXN — PROYECTO GRATUITO
{RESET}
"""

def boot():
    clear()
    print(BANNER)
    for i in range(1, 31):
        sys.stdout.write(f"\r{Y}[+] Iniciando sistema BY HEXN [{'█'*i}{'.'*(30-i)}]{RESET}")
        sys.stdout.flush()
        time.sleep(0.08)
    time.sleep(0.5)
    clear()

# ================== CONFIG ==================
API_KEY_2CAP = "8654da01344220293827510be7bf2d09"
SITE_KEY = "6LdjqjksAAAAAAduGUnDTl7-kSoeSDI7S-vAazXp"
URL_BASE = "https://aplicaciones.adres.gov.co/BDUA_Internet/Pages/ConsultarAfiliadoWeb_2.aspx"

solver = TwoCaptcha(API_KEY_2CAP)

# ================== LÓGICA ==================
def extraer_limpio(cedula):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Referer": URL_BASE
    })

    try:
        print(f"\n[+] Consultando CC: {cedula}")

        r_init = session.get(URL_BASE, verify=False)
        soup = BeautifulSoup(r_init.text, "html.parser")

        vs = soup.find("input", {"id": "__VIEWSTATE"})["value"]
        vsg = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"]
        ev = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]

        print("[+] Resolviendo reCAPTCHA...")
        result = solver.recaptcha(
            sitekey=SITE_KEY,
            url=URL_BASE,
            version="v3",
            enterprise=1,
            action="verify"
        )
        token = result["code"]

        payload = {
            "__EVENTTARGET": "btnConsultar",
            "__VIEWSTATE": vs,
            "__VIEWSTATEGENERATOR": vsg,
            "__EVENTVALIDATION": ev,
            "tipoDoc": "CC",
            "txtNumDoc": cedula,
            "g-recaptcha-response": token,
            "recaptchaToken": token,
            "btnConsultar": "Consultar"
        }

        r_post = session.post(URL_BASE, data=payload, verify=False)
        match = re.search(r"RespuestaConsulta\.aspx\?tokenId=([^']+)", r_post.text)

        if not match:
            print("[!] No se pudo obtener el tokenId")
            return

        url_final = f"https://aplicaciones.adres.gov.co/BDUA_Internet/Pages/RespuestaConsulta.aspx?tokenId={match.group(1)}"
        r_data = session.get(url_final, verify=False)
        soup_final = BeautifulSoup(r_data.text, "html.parser")

        print("\n" + "="*55)
        print(" RESULTADOS MODULO ADRES • BY HEXN ")
        print("="*55)

        tabla = soup_final.find("table", {"id": "GridViewBasica"})
        if tabla:
            for row in tabla.find_all("tr")[1:]:
                c = row.find_all("td")
                print(f" - {c[0].text.strip()}: {c[1].text.strip()}")

        afi = soup_final.find("table", {"id": "GridViewAfiliacion"})
        if afi:
            d = afi.find_all("tr")[1].find_all("td")
            print("\n[ AFILIACIÓN ]")
            print(f" - Estado : {d[0].text.strip()}")
            print(f" - Entidad: {d[1].text.strip()}")
            print(f" - Régimen: {d[2].text.strip()}")

        print("="*55)

    except Exception as e:
        print(f"[!] Error crítico: {e}")

# ================== MAIN ==================
if __name__ == "__main__":
    boot()
    cc = input("Ingrese la Cédula: ").strip()
    extraer_limpio(cc)
