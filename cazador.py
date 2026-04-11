import time
from playwright.sync_api import sync_playwright

def capturar_link(browser, url):
    page = browser.new_page()
    m3u8_url = None

    def handle_response(response):
        nonlocal m3u8_url
        if ".m3u8" in response.url:
            print(f"🎯 Detectado: {response.url}")
            m3u8_url = response.url

    page.on("response", handle_response)

    try:
        page.goto(url, wait_until="networkidle", timeout=60000)

        # Esperamos a que cargue el reproductor
        time.sleep(20)

    except Exception as e:
        print(f"❌ Error en {url}: {e}")
    finally:
        page.close()

    return m3u8_url


def main():
    canales = {
        "Fox Sports 2": "https://streamtpnew.com/global1.php?stream=fox2ar",
        "TNT Sports": "https://streamtpnew.com/global1.php?stream=tntsports",
        "ESPN Premium": "https://streamtpnew.com/global1.php?stream=espnpremium"
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        with open("lista_fresca.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

            for nombre, url in canales.items():
                print(f"🔍 Buscando {nombre}...")

                link = capturar_link(browser, url)

                if link:
                    f.write(f"#EXTINF:-1,{nombre}\n{link}\n")
                    print(f"✅ {nombre} OK\n")
                else:
                    print(f"❌ {nombre} NO encontrado\n")

        browser.close()


if __name__ == "__main__":
    main()
