import re
import requests

def extraer_m3u8(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://streamtpnew.com/'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # Buscamos el link m3u8 en el código fuente
        match = re.search(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', response.text)
        if match:
            return match.group(1).replace('\\', '')
    except:
        return ""
    return ""

canales = {
    "Fox Sports 2": "https://streamtpnew.com/global1.php?stream=fox2ar",
    "TNT Sports": "https://streamtpnew.com/global1.php?stream=tntsports",
    "ESPN Premium": "https://streamtpnew.com/global1.php?stream=espnpremium"
}

with open("lista_fresca.m3u", "w") as f:
    f.write("#EXTM3U\n")
    for nombre, url in canales.items():
        link = extraer_m3u8(url)
        if link:
            f.write(f"#EXTINF:-1, {nombre}\n{link}\n")
            print(f"✅ {nombre} encontrado.")
        else:
            print(f"❌ {nombre} falló.")
