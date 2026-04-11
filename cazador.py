import time
import requests
import re
from playwright.sync_api import sync_playwright

def obtener_proxies_ar():
    """Extrae una lista de proxies de Argentina de fuentes públicas."""
    print("🌐 Buscando proxies de Argentina actualizados...")
    url = "https://www.proxy-list.download/api/v1/get?type=http&country=AR"
    try:
        response = requests.get(url, timeout=10)
        proxies = response.text.splitlines()
        print(f"✅ Se encontraron {len(proxies)} proxies potenciales.")
        return proxies
    except Exception as e:
        print(f"❌ Error obteniendo lista de proxies: {e}")
        return []

def capturar_link(browser_context, url):
    page = browser_context.new_page()
    m3u8_url = None

    def handle_response(response):
        nonlocal m3u8_url
        # Buscamos el link maestro (que no tenga 'tracks' o 'segment')
        if ".m3u8" in response.url and "tracks" not in response.url:
            m3u8_url = response.url

    page.on("response", handle_response)

    try:
        print(f"🔗 Navegando a: {url}")
        page.goto(url, wait_until="networkidle", timeout=60000)
        time.sleep(15) # Tiempo para que el player dispare el link
    except Exception as e:
        print(f"⚠️ Error en la página: {e}")
    finally:
        page.close()
    return m3u8_url

def main():
    canales = {
        "Fox Sports 2": "https://streamtpnew.com/global1.php?stream=fox2ar",
        "TNT Sports": "https://streamtpnew.com/global1.php?stream=tntsports",
        "ESPN Premium": "https://streamtpnew.com/global1.php?stream=espnpremium"
    }

    proxies = obtener_proxies_ar()
    lista_final = []

    with sync_playwright() as p:
        exito = False
        
        # Intentamos con los primeros 5 proxies de la lista hasta que uno funcione
        for proxy_ip in proxies[:5]:
            print(f"🚀 Probando con proxy: {proxy_ip}")
            try:
                browser = p.chromium.launch(
                    headless=True,
                    proxy={"server": f"http://{proxy_ip}"}
                )
                context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0")
                
                temp_links = []
                for nombre, url in canales.items():
                    print(f"🔍 Buscando {nombre}...")
                    link = capturar_link(context, url)
                    if link:
                        temp_links.append((nombre, link))
                        print(f"✅ {nombre} capturado!")
                
                if temp_links:
                    lista_final = temp_links
                    exito = True
                    browser.close()
                    break # Si funcionó, dejamos de probar proxies
                
                browser.close()
            except Exception as e:
                print(f"❌ Proxy {proxy_ip} falló o es muy lento. Reintentando...")

        # Guardar resultados
        with open("lista_fresca.m3u", "w") as f:
            f.write("#EXTM3U\n")
            if lista_final:
                for nombre, link in lista_final:
                    f.write(f"#EXTINF:-1, {nombre}\n{link}\n")
                print("💾 Lista guardada con éxito.")
            else:
                print("EOF: No se pudo obtener ningún link con los proxies actuales.")

if __name__ == "__main__":
    main()
