import time
import random
from playwright.sync_api import sync_playwright

PROXIES_AR = [
    "181.209.79.130:4145",
    "190.105.215.154:999",
    "181.118.151.106:8080"
]

def capturar_link(context, url):
    page = context.new_page()
    m3u8_url = None

    def handle_response(response):
        nonlocal m3u8_url
        try:
            if ".m3u8" in response.url:
                print(f"🎯 Detectado: {response.url}")
                m3u8_url = response.url
        except:
            pass

    page.on("response", handle_response)

    try:
        print(f"🔗 Entrando a: {url}")
        page.goto(url, timeout=90000)

        # 🔥 CLAVE: esperar a que cargue todo el JS
        page.wait_for_timeout(20000)

        # 🔥 CLAVE: intentar interacción (muchos players requieren click)
        try:
            page.mouse.click(300, 300)
            print("🖱️ Click forzado en el player")
        except:
            pass

        # Espera extra para que dispare requests del video
        page.wait_for_timeout(15000)

    except Exception as e:
        print(f"⚠️ Error: {e}")

    finally:
        page.close()

    return m3u8_url


def probar_con_proxy(proxy, canales):
    print(f"\n🌐 Probando proxy: {proxy}")

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=True,
                proxy={"server": f"http://{proxy}"}
            )

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
            )

            resultados = {}

            for nombre, url in canales.items():
                print(f"\n🔍 Buscando {nombre}")
                link = capturar_link(context, url)
                resultados[nombre] = link

            browser.close()
            return resultados

        except Exception as e:
            print(f"🚫 Proxy muerto: {e}")
            return None


def main():
    canales = {
        "Fox Sports 2": "https://streamtpnew.com/global1.php?stream=fox2ar",
        "TNT Sports": "https://streamtpnew.com/global1.php?stream=tntsports",
        "ESPN Premium": "https://streamtpnew.com/global1.php?stream=espnpremium"
    }

    random.shuffle(PROXIES_AR)

    resultados_finales = None

    for proxy in PROXIES_AR:
        resultados = probar_con_proxy(proxy, canales)

        if resultados and any(resultados.values()):
            print("✅ Proxy funcional encontrado")
            resultados_finales = resultados
            break

    # Guardar archivo
    with open("lista_fresca.m3u", "w") as f:
        f.write("#EXTM3U\n")

        if resultados_finales:
            for nombre, link in resultados_finales.items():
                if link:
                    f.write(f"#EXTINF:-1,{nombre}\n{link}\n")
                    print(f"✅ {nombre} agregado")
                else:
                    print(f"❌ {nombre} sin link")
        else:
            print("🚫 Ningún proxy funcionó")

if __name__ == "__main__":
    main()
