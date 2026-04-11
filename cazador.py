import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def obtener_proxies():
    url = "https://www.proxynova.com/proxy-server-list/country-ar/"
    headers = {"User-Agent": "Mozilla/5.0"}

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


def probar_proxy(proxy):
    try:
        r = requests.get(
            "https://api.ipify.org",
            proxies={"http": proxy, "https": proxy},
            timeout=5
        )
        return True
    except:
        return False


def capturar_link(p, url, proxy):
    try:
        browser = p.chromium.launch(
            headless=True,
            proxy={"server": proxy},
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        page = browser.new_page()
        m3u8_links = []

        def handle_response(response):
            if ".m3u8" in response.url and "token" in response.url:
                m3u8_links.append(response.url)

        page.on("response", handle_response)

        page.goto(url, wait_until="networkidle", timeout=60000)

        try:
            page.click("video")
        except:
            pass

        time.sleep(20)

        page.close()
        browser.close()

        return m3u8_links[-1] if m3u8_links else None

    except Exception as e:
        print(f"Error con proxy {proxy}: {e}")
        return None


def main():
    canales = {
        "TNT Sports": "https://streamtpnew.com/global1.php?stream=tntsports"
    }

    print("🔍 Buscando proxies...")
    proxies = obtener_proxies()

    print(f"Total proxies: {len(proxies)}")

    with sync_playwright() as p:
        proxy_valido = None

        for proxy in proxies[:30]:
            print(f"Probando {proxy}...")
            if probar_proxy(proxy):
                proxy_valido = proxy
                print(f"✅ Proxy válido: {proxy}")
                break

        if not proxy_valido:
            print("❌ No se encontró proxy válido")
            return

        with open("lista_fresca.m3u", "w") as f:
            f.write("#EXTM3U\n")

            for nombre, url in canales.items():
                link = capturar_link(p, url, proxy_valido)

                if link:
                    f.write(f"#EXTINF:-1,{nombre}\n{link}\n")
                    print(f"✅ {nombre}")
                else:
                    print(f"❌ {nombre}")


if __name__ == "__main__":
    main()
