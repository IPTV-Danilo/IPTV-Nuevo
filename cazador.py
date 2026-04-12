def capturar_m3u8(p, url, proxy=None):
    try:
        browser = p.chromium.launch(
            headless=True,
            proxy={"server": proxy} if proxy else None,
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

        # 🔥 capturar TODAS las requests
        def handle_response(response):
            if ".m3u8" in response.url:
                print(f"🎯 Detectado m3u8: {response.url}")
                m3u8_links.append(response.url)

        context.on("response", handle_response)

        print(f"🌐 Cargando con proxy: {proxy}")

        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # 🔥 intentar iniciar video
        for _ in range(3):
            try:
                page.click("video", timeout=3000)
            except:
                pass

            try:
                page.click("button", timeout=3000)
            except:
                pass

            page.mouse.move(300, 300)
            time.sleep(2)

        # 🔥 ESPERA INTELIGENTE (hasta 60 segundos)
        for i in range(60):
            if m3u8_links:
                break
            time.sleep(1)

        browser.close()

        if m3u8_links:
            return m3u8_links[-1]

        return None

    except Exception as e:
        print(f"Error con proxy {proxy}: {e}")
        return None

if __name__ == "__main__":
    main()
