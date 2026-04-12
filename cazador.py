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
# VERIFICAR IP REAL DESDE NAVEGADOR
# =========================
def verificar_ip_argentina(p, proxy):
    try:
        browser = p.chromium.launch(
            headless=True,
            proxy={"server": proxy},
            args=["--no-sandbox"]
        )

        page = browser.new_page()
        page.goto("http://ip-api.com/json", timeout=20000)

        data = page.evaluate("() => document.body.innerText")

        browser.close()

        if "Argentina" in data:
            print(f"🇦🇷 IP Argentina confirmada: {proxy}")
            return True
        else:
            print(f"🌎 Proxy no es AR: {proxy}")
            return False

    except:
        print(f"❌ Proxy muerto: {proxy}")
        return False


# =========================
# CAPTURAR M3U8
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
                print(f"🎯 Detectado: {response.url}")
                m3u8_link = response.url

        context.on("response", handle_response)

        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # intentar activar player
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
        print(f"Error capturando con proxy {proxy}: {e}")
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

                    # 🔥 verificar que sea Argentina REAL
                    if not verificar_ip_argentina(p, proxy):
                        continue

                    link = capturar_m3u8(p, url, proxy)

                    if link:
                        print(f"✅ FUNCIONA con proxy AR: {proxy}")
                        link_final = link
                        break
                    else:
                        print("❌ Proxy no sirve para stream")

                if link_final:
                    f.write(f"#EXTINF:-1,{nombre}\n{link_final}\n")
                    print(f"✅ {nombre} OK")
                else:
                    print(f"❌ {nombre} no encontrado con IP Argentina")

    print("\n✅ FINALIZADO")


if __name__ == "__main__":
    main()
