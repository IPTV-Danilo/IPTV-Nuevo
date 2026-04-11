import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# =========================
# OBTENER PROXIES
# =========================
def obtener_proxies():
    url = "https://www.proxynova.com/proxy-server-list/country-ar/"
    headers = {"User-Agent": "Mozilla/5.0"}

    proxies = []

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        filas = soup.select("table tbody tr")

        for fila in filas:
            try:
                ip = fila.select_one("td:nth-child(1)").text.strip()
                port = fila.select_one("td:nth-child(2)").text.strip()
                proxies.append(f"http://{ip}:{port}")
            except:
                continue

    except Exception as e:
        print("Error obteniendo proxies:", e)

    return proxies


# =========================
# CAPTURA REAL
# =========================
def capturar_m3u8(p, url, proxy=None):
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

        # 🔥 capturar TODAS las requests (clave)
        context.on("response", lambda response: (
            m3u8_links.append(response.url)
            if ".m3u8" in response.url else None
        ))

        print(f"🌐 Cargando {url} con proxy={proxy}")

        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # 🔥 activar video
        try:
            page.click("video", timeout=5000)
        except:
            pass

        try:
            page.click("button", timeout=5000)
        except:
            pass

        page.mouse.move(300, 300)

        # 🔥 esperar más tiempo (CLAVE)
        time.sleep(30)

        browser.close()

        # devolver último válido
        for link in reversed(m3u8_links):
            if ".m3u8" in link:
                return link

        return None

    except Exception as e:
        print(f"Error con proxy {proxy}: {e}")
        return None


# =========================
# MAIN
# =========================
def main():
    canales = {
        "TNT Sports": "https://streamtpnew.com/global1.php?stream=tntsports",
        "ESPN Premium": "https://streamtpnew.com/global1.php?stream=espnpremium"
    }

    proxies = obtener_proxies()

    print(f"🔍 Proxies encontrados: {len(proxies)}")

    with sync_playwright() as p:

        with open("lista_fresca.m3u", "w") as f:
            f.write("#EXTM3U\n")

            for nombre, url in canales.items():

                print(f"\n🎯 Buscando {nombre}")

                link_final = None

                # 🔥 PROBAR VARIOS PROXIES
                for proxy in proxies[:40]:
                    link = capturar_m3u8(p, url, proxy)

                    if link:
                        print(f"✅ Proxy FUNCIONA: {proxy}")
                        link_final = link
                        break
                    else:
                        print(f"❌ Proxy no sirve")

                # 🔥 FALLBACK SIN PROXY (IMPORTANTE)
                if not link_final:
                    print("⚠️ Probando sin proxy...")
                    link_final = capturar_m3u8(p, url, None)

                if link_final:
                    f.write(f"#EXTINF:-1,{nombre}\n{link_final}\n")
                    print(f"✅ {nombre} OK")
                else:
                    print(f"❌ {nombre} NO encontrado")

    print("\n✅ FIN")


if __name__ == "__main__":
    main()
