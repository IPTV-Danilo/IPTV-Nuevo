import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# =========================
# OBTENER PROXIES DE ARGENTINA
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
# VERIFICAR QUE EL PROXY SEA ARGENTINA REAL
# =========================
def validar_proxy_argentina(proxy):
    try:
        r = requests.get(
            "http://ip-api.com/json",
            proxies={"http": proxy, "https": proxy},
            timeout=6
        )
        data = r.json()

        if data.get("country") == "Argentina":
            print(f"🇦🇷 Proxy AR válido: {proxy}")
            return True
        else:
            print(f"🌎 Proxy NO AR ({data.get('country')}): {proxy}")
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

        m3u8_links = []

        context.on("response", lambda response: (
            m3u8_links.append(response.url)
            if ".m3u8" in response.url else None
        ))

        print(f"🎬 Cargando stream con proxy AR: {proxy}")

        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        try:
            page.click("video", timeout=5000)
        except:
            pass

        try:
            page.click("button", timeout=5000)
        except:
            pass

        page.mouse.move(200, 200)

        time.sleep(25)

        browser.close()

        for link in reversed(m3u8_links):
            if ".m3u8" in link:
                return link

        return None

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

                # 🔥 SOLO PROXIES ARGENTINA REALES
                for proxy in proxies[:50]:

                    if not validar_proxy_argentina(proxy):
                        continue

                    link = capturar_m3u8(p, url, proxy)

                    if link:
                        print(f"✅ FUNCIONÓ con proxy AR: {proxy}")
                        link_final = link
                        break
                    else:
                        print("❌ No sirvió para stream")

                if link_final:
                    f.write(f"#EXTINF:-1,{nombre}\n{link_final}\n")
                    print(f"✅ {nombre} OK")
                else:
                    print(f"❌ {nombre} no encontrado con proxies AR")

    print("\n✅ FIN")


if __name__ == "__main__":
    main()
