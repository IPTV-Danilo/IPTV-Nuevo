import os
import re
import time
from playwright.sync_api import sync_playwright

def capturar_link(browser, url):
    page = browser.new_page()
    try:
        # Entramos a la web
        page.goto(url, wait_until="networkidle", timeout=60000)
        # Esperamos 10 segundos a que el reproductor genere el link
        time.sleep(10)
        content = page.content()
        
        # Buscamos el link .m3u8
        match = re.search(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', content)
        if match:
            return match.group(1).replace('\\', '')
    except Exception as e:
        print(f"Error en {url}: {e}")
    finally:
        page.close()
    return None

def main():
    canales = {
        "Fox Sports 2": "https://streamtpnew.com/global1.php?stream=fox2ar",
        "TNT Sports": "https://streamtpnew.com/global1.php?stream=tntsports",
        "ESPN Premium": "https://streamtpnew.com/global1.php?stream=espnpremium"
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        with open("lista_fresca.m3u", "w") as f:
            f.write("#EXTM3U\n")
            for nombre, url in canales.items():
                print(f"Buscando {nombre}...")
                link = capturar_link(browser, url)
                if link:
                    f.write(f"#EXTINF:-1, {nombre}\n{link}\n")
                    print(f"✅ {nombre} OK")
                else:
                    print(f"❌ {nombre} no encontrado")
        browser.close()

if __name__ == "__main__":
    main()
