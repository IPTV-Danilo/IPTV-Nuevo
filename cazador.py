import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# =========================
# PROXIES ARGENTINOS
# =========================
def obtener_proxies():
    url = "https://www.proxynova.com/proxy-server-list/country-ar/"
    headers = {"User-Agent": "Mozilla/5.0"}

    proxies = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

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
# CAPTURA REAL (TEST + M3U8)
# =========================
def capturar_con_proxy(p, url, proxy):
    try:
        print(f"🌐 Probando proxy: {proxy}")

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

        m3u8_links = []

        context.on("response", lambda response: (
            m3u8_links.append(response.url)
            if ".m3u8" in response.url else None
        ))

        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # activar player
        try:
            page.click("video")
        except:
            pass

        try:
            page.click("button")
        except:
            pass

        page.mouse.move(200, 200)

        time.sleep(20)

        browser.close()

        # devolver último válido
        for link in reversed(m3u8_links):
            if ".m3u8" in link and "token" in link:
                print(f"✅ Proxy FUNCIONA: {proxy}")
                return link

        print(f"❌ Proxy no sirve para stream: {proxy}")
        return None

    except Exception as e:
        print(f"❌ Error proxy {proxy}: {e}")
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

                print(f"\n🎯 Buscando stream para {nombre}")

                link_final = None

                # 🔥 probar varios proxies (clave)
                for proxy in proxies[:30]:
                    link = capturar_con_proxy(p, url, proxy)

                    if link:
                        link_final = link
                        break

                if link_final:
                    f.write(f"#EXTINF:-1,{nombre}\n{link_final}\n")
                    print(f"✅ {nombre} OK")
                else:
                    print(f"❌ {nombre} no encontrado con proxies")

    print("\n✅ PROCESO TERMINADO")


if __name__ == "__main__":
    main()
