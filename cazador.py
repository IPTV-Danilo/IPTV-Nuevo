import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# =========================
# OBTENER PROXIES ARGENTINOS
# =========================
def obtener_proxies():
    url = "https://www.proxynova.com/proxy-server-list/country-ar/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        proxies = []

        filas = soup.select("table tbody tr")
        for fila in filas:
            try:
                ip = fila.select_one("td:nth-child(1)").text.strip()
                port = fila.select_one("td:nth-child(2)").text.strip()
                proxies.append(f"http://{ip}:{port}")
            except:
                continue

        return proxies

    except:
        return []


# =========================
# PROBAR PROXY
# =========================
def probar_proxy(proxy):
    try:
        requests.get(
            "https://api.ipify.org",
            proxies={"http": proxy, "https": proxy},
            timeout=5
        )
        return True
    except:
        return False


# =========================
# CAPTURAR M3U8
# =========================
def capturar_link(p, url, proxy=None):
    try:
        browser = p.chromium.launch(
            headless=True,
            proxy={"server": proxy} if proxy else None,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--autoplay-policy=no-user-gesture-required"
            ]
        )

        context = browser.new_context()
        page = context.new_page()

        m3u8_links = []

        # 🔥 capturar TODO el tráfico (iframes incluidos)
        context.on("response", lambda response: (
            m3u8_links.append(response.url)
            if ".m3u8" in response.url else None
        ))

        print(f"🌐 Entrando a {url} (proxy={proxy})")

        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # intentar activar video
        try:
            page.click("video")
        except:
            pass

        try:
            page.click("button")
        except:
            pass

        page.mouse.move(300, 300)

        time.sleep(25)

        browser.close()

        # devolver último link válido
        for link in reversed(m3u8_links):
            if ".m3u8" in link and "token" in link:
                return link

        return None

    except Exception as e:
        print(f"Error capturando: {e}")
        return None


# =========================
# MAIN
# =========================
def main():
    canales = {
        "TNT Sports": "https://streamtpnew.com/global1.php?stream=tntsports",
        "ESPN Premium": "https://streamtpnew.com/global1.php?stream=espnpremium"
    }

    print("🔍 Buscando proxies argentinos...")
    proxies = obtener_proxies()

    print(f"Total proxies: {len(proxies)}")

    with sync_playwright() as p:

        proxy_valido = None

        # probar proxies (máx 20)
        for proxy in proxies[:20]:
            print(f"Probando proxy {proxy}...")
            if probar_proxy(proxy):
                proxy_valido = proxy
                print(f"✅ Proxy válido: {proxy}")
                break

        with open("lista_fresca.m3u", "w") as f:
            f.write("#EXTM3U\n")

            for nombre, url in canales.items():

                link = None

                # 🔥 intentar con proxy
                if proxy_valido:
                    link = capturar_link(p, url, proxy_valido)

                # 🔥 fallback SIN proxy (CLAVE)
                if not link:
                    print("⚠️ Fallback sin proxy...")
                    link = capturar_link(p, url, None)

                if link:
                    f.write(f"#EXTINF:-1,{nombre}\n{link}\n")
                    print(f"✅ {nombre} OK")
                else:
                    print(f"❌ {nombre} no encontrado")

    print("✅ Proceso terminado")


if __name__ == "__main__":
    main()
  
