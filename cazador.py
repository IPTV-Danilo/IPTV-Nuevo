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
# VERIFICAR IP ARGENTINA (REAL)
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
            print(f"🇦🇷 Proxy AR verificado: {proxy}")
            return True
        else:
            print(f"🌎 No AR: {proxy}")
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

        # intentar activar el player
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

                # =========================
                # FASE 1: PROXIES AR VERIFICADOS
                # =========================
                print("🇦🇷 Fase 1: proxies verificados")

                for proxy in proxies[:30]:
                    if not verificar_ip_argentina(p, proxy):
                        continue

                    link = capturar_m3u8(p, url, proxy)

                    if link:
                        print(f"✅ FUNCIONA AR verificado: {proxy}")
                        link_final = link
                        break

                # =========================
                # FASE 2: PROXIES SIN VALIDAR
                # =========================
                if not link_final:
                    print("⚠️ Fase 2: proxies sin validar")

                    for proxy in proxies[:30]:
                        link = capturar_m3u8(p, url, proxy)

                        if link:
                            print(f"✅ FUNCIONA sin validar: {proxy}")
                            link_final = link
                            break

                # =========================
                # RESULTADO FINAL
                # =========================
                if link_final:
                    f.write(f"#EXTINF:-1,{nombre}\n{link_final}\n")
                    print(f"✅ {nombre} OK")
                else:
                    print(f"❌ {nombre} no encontrado")

    print("\n✅ FINALIZADO")


if __name__ == "__main__":
    main()
