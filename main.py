import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import re

# URL de destino
POST_URL = "https://siiauescolar.siiau.udg.mx/wal/sspseca.consulta_oferta"

# Headers avanzados (idénticos a los de PowerShell)
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "es-419,es;q=0.9",
    "Cache-Control": "max-age=0",
    "DNT": "1",
    "Origin": "https://siiauescolar.siiau.udg.mx",
    "Referer": "https://siiauescolar.siiau.udg.mx/wal/sspseca.forma_consulta",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "sec-ch-ua": '"Chromium";v="141", "Not?A_Brand";v="8"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded"
}

# Cookies necesarias (idénticas a las de PowerShell)
COOKIES = {
    "21082024SIIAUSESION": "1542435678",
    "21082024SIIAUUDG": "1692153",
    "07122024SIIAUSESION": "611522407",
    "07122024SIIAUUDG": "1692153",
    "utag_main": "v_id:019788e0aa58009c8f3c1a1adde80506f004206700978$_sn:1$_se:5$_ss:0$_st:1750349971926$ses_id:1750348114522%3Bexp-session$_pn:2%3Bexp-session$vapi_domain:ieeexplore-ieee-org.wdg.biblio.udg.mx",
    "06082025SIIAUSESION": "1015485614",
    "06082025SIIAUUDG": "1692153",
    "07082025SIIAUUDG": "1692153",
    "07082025SIIAUSESION": "588707643",
    "cookiesession1": "678B287E4E1A792C793C3634D5FF5F58",
    "_ga": "GA1.1.1433791055.1759320410",
    "_ga_Y8QVN46M0G": "GS2.1.s1759338546$o3$g0$t1759338546$j60$l0$h0",
    "_ga_XYBCFG4RNW": "GS2.1.s1759338546$o2$g0$t1759338546$j60$l0$h0",
    "03102025SIIAUSESION": "1280826723",
    "03102025SIIAUUDG": "1692153",
    "05102025SIIAUSESION": "1231724026",
    "05102025SIIAUUDG": "1692153"
}

# Intervalo entre peticiones para no sobrecargar el servidor
SLEEP_BETWEEN_REQUESTS = 1.0  # segundos

# Payload base (se actualizará p_start en la paginación)
PAYLOAD_BASE = {
    "ciclop": "202520",
    "cup": "D",
    "majrp": "",
    "crsep": "",
    "materiap": "",
    "horaip": "",
    "horafp": "",
    "edifp": "",
    "aulap": "",
    "ordenp": "0",
    "mostrarp": "100",  # pedir 100 por página
    # 'p_start' se añadirá dinámicamente
}


def extract_rows_from_table(soup):
    """Extrae las filas de la tabla principal, expandiendo los horarios en columnas separadas.
    """
    tabla = soup.find('table')
    if not tabla:
        return []

    filas = tabla.find_all('tr', recursive=False)
    datos_finales = []
    for tr in filas:
        tds = tr.find_all('td', recursive=False)
        if not tds or not re.match(r'^\d{4,}', tds[0].get_text(strip=True)):
            continue

        def txt(cell):
            return cell.get_text(' ', strip=True)

        # Extraer información base de la materia
        base_info = {
            'NRC': txt(tds[0]),
            'Clave': txt(tds[1]) if len(tds) > 1 else '',
            'Materia': txt(tds[2]) if len(tds) > 2 else '',
            'Sec': txt(tds[3]) if len(tds) > 3 else '',
            'CR': txt(tds[4]) if len(tds) > 4 else '',
            'CUP': txt(tds[5]) if len(tds) > 5 else '',
            'DIS': txt(tds[6]) if len(tds) > 6 else '',
        }

        # Extraer profesor (puede tener tabla anidada)
        profesor = ''
        if len(tds) > 8:
            inner_prof = tds[8].find('table')
            if inner_prof:
                prof_tr = inner_prof.find('tr')
                if prof_tr and len(prof_tr.find_all('td')) >= 2:
                    profesor = prof_tr.find_all('td')[1].get_text(' ', strip=True)
                elif prof_tr:
                    profesor = txt(prof_tr)
            else:
                profesor = txt(tds[8])
        base_info['Profesor'] = profesor

        # Procesar la celda de horario
        horario_str = ''
        if len(tds) > 7:
            inner_table = tds[7].find('table')
            if inner_table:
                parts = []
                for ir in inner_table.find_all('tr'):
                    parts.append(' | '.join([c.get_text(' ', strip=True) for c in ir.find_all('td')]))
                horario_str = ' ; '.join(p for p in parts if p.strip())
            else:
                horario_str = txt(tds[7])

        if horario_str.strip():
            sesiones = horario_str.split(';')
            for sesion in sesiones:
                partes = [p.strip() for p in sesion.split('|')]
                fila_expandida = base_info.copy()
                fila_expandida.update({
                    'SesionNum': partes[0] if len(partes) > 0 else '',
                    'Horas': partes[1] if len(partes) > 1 else '',
                    'Dias': partes[2] if len(partes) > 2 else '',
                    'Edificio': partes[3] if len(partes) > 3 else '',
                    'Aula': partes[4] if len(partes) > 4 else '',
                    'Periodo': partes[5] if len(partes) > 5 else '',
                })
                datos_finales.append(fila_expandida)
        else:
            # Si no hay horario, agregar una fila con campos de horario vacíos
            fila_vacia = base_info.copy()
            fila_vacia.update({
                'SesionNum': '', 'Horas': '', 'Dias': '', 'Edificio': '', 'Aula': '', 'Periodo': ''
            })
            datos_finales.append(fila_vacia)

    return datos_finales


def get_next_p_start(soup):
    """Busca en el HTML un input hidden llamado p_start y devuelve su valor como int, o None si no existe.
    El formulario del sitio incluye un formulario con <INPUT NAME="p_start" VALUE="100"> para avanzar.
    """
    form = soup.find('form', attrs={'name': True})
    if not form:
        # buscar cualquier input p_start
        inp = soup.find('input', attrs={'name': 'p_start'})
    else:
        inp = form.find('input', attrs={'name': 'p_start'})
    if inp and inp.get('value'):
        try:
            return int(inp.get('value'))
        except ValueError:
            return None
    return None


def fetch_all_pages(session, post_url, payload_base):
    """Itera páginas enviando p_start y acumulando resultados hasta que no haya siguiente página.
    Devuelve la lista completa de registros.
    """
    results = []
    p_start = 0
    seen_any = False
    page = 0
    while True:
        page += 1
        payload = dict(payload_base)
        payload['p_start'] = str(p_start)
        print(f"[Página {page}] solicitando p_start={p_start} ...")
        resp = session.post(post_url, data=payload, timeout=30)
        if resp.status_code != 200:
            print(f"Error HTTP en página {page}: {resp.status_code}")
            break

        soup = BeautifulSoup(resp.text, 'html.parser')
        page_rows = extract_rows_from_table(soup)
        print(f"  -> filas extraídas esta página: {len(page_rows)}")
        if page_rows:
            seen_any = True
            results.extend(page_rows)
        else:
            # Si no se extrajeron filas y ya habíamos extraído antes, probablemente no hay más
            if seen_any:
                print("  -> no hubo filas en esta página; finalizando paginación.")
                break

        next_p = get_next_p_start(soup)
        print(f"  -> siguiente p_start sugerido en la página: {next_p}")
        if not next_p or next_p <= p_start:
            # no more pages
            print("  -> no hay siguiente página o p_start no avanza; finalizando.")
            break

        # actualizar p_start y continuar
        p_start = next_p
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    return results


if __name__ == "__main__":
    print("=====================================================")
    print("== Extractor de Oferta Académica del SIIAU (UDG) ==")
    print("=====================================================")

    # Diccionario de centros universitarios para facilitar la selección
    centros = {
        'A': 'CUAAD - Arte, Arquitectura y Diseño',
        'B': 'CUCBA - Ciencias Biológicas y Agropecuarias',
        'C': 'CUCEA - Ciencias Económico Administrativas',
        'D': 'CUCEI - Ciencias Exactas e Ingenierías',
        'E': 'CUCS - Ciencias de la Salud',
        'F': 'CUCSH - Ciencias Sociales y Humanidades',
        'G': 'CUALTOS - de los Altos',
        'H': 'CUCIENEGA - de la Ciénega',
        'I': 'CUCOSTA - de la Costa',
        'J': 'CUCSUR - de la Costa Sur',
        'K': 'CUNORTE - del Norte',
        'L': 'CUSUR - del Sur',
        'M': 'CUTONALA - de Tonalá',
        'N': 'SUV - Sistema de Universidad Virtual',
        'P': 'CUTLAJOMULCO - de Tlajomulco',
        'Q': 'CUVALLES - de los Valles',
        'R': 'CUZAPOTLANEJO - de Zapotlanejo',
    }

    print("\nCentros Universitarios disponibles:")
    for key, value in centros.items():
        print(f"  [{key}]: {value}")

    # Solicitar datos al usuario
    cup_input = input("\n> Introduce el código del Centro Universitario (ej. D): ").strip().upper()
    majrp_input = input("> Introduce el código de la Carrera (ej. INCO) o deja vacío para todas: ").strip().upper()

    # Validar que el centro universitario exista
    if cup_input not in centros:
        print(f"Error: El código de centro '{cup_input}' no es válido.")
    else:
        # Actualizar el payload con la entrada del usuario
        PAYLOAD_BASE['cup'] = cup_input
        PAYLOAD_BASE['majrp'] = majrp_input

        print(f"\nBuscando en: {centros[cup_input]}")
        if majrp_input:
            print(f"Carrera: {majrp_input}")
        else:
            print("Carrera: Todas las del centro")

        with requests.Session() as s:
            s.headers.update(HEADERS)
            s.cookies.update(COOKIES)

            print("\nIniciando extracción paginada...")
            all_data = fetch_all_pages(s, POST_URL, PAYLOAD_BASE)
            print(f"Extracción completada. Total registros: {len(all_data)}")

            if all_data:
                df = pd.DataFrame(all_data)
                # Guardar en un archivo con nombre dinámico
                filename = f"oferta_{cup_input}_{majrp_input if majrp_input else 'TODAS'}.csv"
                df.to_csv(filename, index=False)
                print(f"\nDatos guardados en '{filename}'.")
                print("\nPrimeras 5 filas:")
                print(df.head())
            else:
                print("No se extrajeron registros. Revisa los parámetros o la disponibilidad en SIIAU.")
