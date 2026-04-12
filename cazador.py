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
# VERIFICAR SI ES ARGENTINA
# =========================
def es_argentina(proxy):
    try:
        r = requests.get(
            "http://ip-api.com/json",
            proxies={"http": proxy, "https": proxy},
            timeout=5
        )
        data = r.json()
        return data.get("country") == "Argentina"
    except:
        return False


# =========================
# CAPTURAR LINK M3U8
# =========================
def capturar_m3u8(p, url, proxy):
    try:
        browser = p.chromium.launch(
            headless=True,
            proxy={"server": proxy},
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--autoplay-policy=no-user-gesture-required"
            ]
        )

        context = browser.new_context()
        page = context.new_page()

        m3u8_link = None

        def handle_response(response):
            nonlocal m3u8_link
            if ".m3u8" in response.url:
                print("🎯 M3U8 detectado")
                m3u8_link = response.url

        context.on("response", handle_response)

        print(f"🌐 Cargando con proxy: {proxy}")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # intentar activar el video
        for _ in range(3):
            try:
                page.click("video", timeout=2000)
            except:
                pass

            try:
                page.click("button", timeout=2000)
            except:
                pass

        # espera inteligente
        start = time.time()
        while time.time() - start < 40:
            if m3u8_link:
                break
            time.sleep(0.5)

        browser.close()

        return m3u8_link

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

                for proxy in proxies[:50]:
                    print(f"🌐 Probando proxy: {proxy}")

                    link = capturar_m3u8(p, url, proxy)

                    if link:
                        print("🎯 Link encontrado, verificando país...")

                        if es_argentina(proxy):
                            print("🇦🇷 Proxy válido (Argentina)")
                            link_final = link
                            break
                        else:
                            print("🌎 No es Argentina → descartado")

                if link_final:
                    f.write(f"#EXTINF:-1,{nombre}\n{link_final}\n")
                    print(f"✅ {nombre} OK")
                else:
                    print(f"❌ {nombre} no encontrado")

    print("\n✅ PROCESO TERMINADO")


if __name__ == "__main__":
    main()
