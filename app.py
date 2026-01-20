from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from flask_session import Session
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import re
import io

app = Flask(__name__)
app.secret_key = 'siiau-extractor-secret-key-2025'  # Required for sessions

# Configure server-side session storage
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_FILE_DIR'] = './flask_session'
Session(app)

CORS(app)

# Constantes del scraping
POST_URL = "https://siiauescolar.siiau.udg.mx/wal/sspseca.consulta_oferta"

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

CENTROS = {
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

def extract_rows_from_table(soup):
    """Extrae las filas de la tabla principal, expandiendo los horarios en columnas separadas."""
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

        # Extraer profesor
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

        # Procesar horario
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
            fila_vacia = base_info.copy()
            fila_vacia.update({
                'SesionNum': '', 'Horas': '', 'Dias': '', 'Edificio': '', 'Aula': '', 'Periodo': ''
            })
            datos_finales.append(fila_vacia)

    return datos_finales

def get_next_p_start(soup):
    """Busca en el HTML un input hidden llamado p_start y devuelve su valor como int, o None si no existe."""
    form = soup.find('form', attrs={'name': True})
    if not form:
        inp = soup.find('input', attrs={'name': 'p_start'})
    else:
        inp = form.find('input', attrs={'name': 'p_start'})
    if inp and inp.get('value'):
        try:
            return int(inp.get('value'))
        except ValueError:
            return None
    return None

def fetch_all_pages(session, post_url, payload_base, debug_mode=False):
    """Itera páginas enviando p_start y acumulando resultados hasta que no haya siguiente página."""
    results = []
    p_start = 0
    seen_any = False
    page = 0
    total_extraido = 0

    while True:
        page += 1
        payload = dict(payload_base)
        payload['p_start'] = str(p_start)

        print(f"\n[Página {page}] solicitando p_start={p_start} ...")

        try:
            resp = session.post(post_url, data=payload, timeout=30)
            print(f"Status Code: {resp.status_code}")

            if resp.status_code != 200:
                print(f"Error HTTP en página {page}: {resp.status_code}")
                break

            soup = BeautifulSoup(resp.text, 'html.parser')

            # Buscar mensaje de error o sin resultados
            error_msg = soup.find('div', class_='error')
            if error_msg:
                print(f"Mensaje de error encontrado: {error_msg.text}")
                break

            # Extraer filas
            page_rows = extract_rows_from_table(soup)
            print(f"  -> filas extraídas esta página: {len(page_rows)}")

            if page_rows:
                seen_any = True
                results.extend(page_rows)
                total_extraido += len(page_rows)
                print(f"  -> Total acumulado: {total_extraido} registros")
            else:
                if seen_any:
                    print("  -> no hubo filas en esta página; finalizando paginación.")
                    break
                elif page == 1:
                    print("  -> no se encontraron resultados en la primera página")
                    break

            # Buscar botón o form de siguiente página
            next_p = get_next_p_start(soup)
            print(f"  -> siguiente p_start sugerido en la página: {next_p}")

            # Buscar botón "100 Próximos" y simular avance si existe
            next_button = soup.find('input', {'value': '100 Próximos'})
            if next_button:
                print("  -> encontrado botón '100 Próximos', avanzando a la siguiente página")
                mostrar_val = int(payload_base.get('mostrarp', '100'))
                p_start += mostrar_val
                continue

            # Si no hay botón, usar next_p si es válido
            if next_p and next_p > p_start:
                p_start = next_p
                continue

            print("  -> no se encontró manera de avanzar página o p_start no avanza; finalizando.")
            break

            # Pausa entre peticiones
            time.sleep(1.5)

        except Exception as e:
            print(f"Error en página {page}: {str(e)}")
            break

    print(f"\nExtracción completada: {total_extraido} registros en {page} páginas")
    return results

@app.route('/')
def index():
    return render_template('index.html', centros=CENTROS)

@app.route('/results')
def results():
    """Show search results page"""
    from flask import session
    results_data = session.get('search_results', [])
    results_count = session.get('search_count', 0)
    return render_template('results.html', data=results_data, count=results_count)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve files from assets folder"""
    from flask import send_from_directory
    import os
    assets_dir = os.path.join(app.root_path, 'assets')
    return send_from_directory(assets_dir, filename)

@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.json
        print(f"Datos recibidos: {data}")

        # Obtener código del centro
        centro_seleccionado = data.get('centro', '')
        codigo_centro = ''
        for k, v in CENTROS.items():
            if v == centro_seleccionado:
                codigo_centro = k
                break

        if not codigo_centro:
            return jsonify({'error': 'Debe seleccionar un Centro Universitario'}), 400

        # Extraer ciclo
        ciclo_seleccionado = data.get('ciclo', '202520')
        codigo_ciclo = ciclo_seleccionado.split('-')[0].strip() if ciclo_seleccionado else '202520'

        # Construir payload - ENVIAR FILTROS DIRECTAMENTE A SIIAU
        payload = {
            "ciclop": codigo_ciclo,
            "cup": codigo_centro,
            "majrp": data.get('carrera', '').strip(),
            "crsep": "",
            "materiap": data.get('materia', '').strip(),
            "horaip": data.get('hora_inicio', '').strip(),
            "horafp": data.get('hora_fin', '').strip(),
            "edifp": data.get('edificio', '').strip(),
            "aulap": data.get('aula', '').strip(),
            "ordenp": data.get('orden', '0'),
            "mostrarp": data.get('mostrar', '100'),
            "dispp": "1" if data.get('solo_disponibles', False) else "",
        }

        print(f"Payload enviado a SIIAU: {payload}")

        # Realizar scraping
        with requests.Session() as s:
            s.headers.update(HEADERS)
            s.cookies.update(COOKIES)
            all_data = fetch_all_pages(s, POST_URL, payload, debug_mode=False)

        if all_data:
            df = pd.DataFrame(all_data)
            
            # Filtrar por días (del lado del cliente, ya que SIIAU no tiene parámetro 'diasp')
            # Formato de SIIAU: 'L . I . . .' donde:
            # L=Lunes, M=Martes, I=Miércoles (mIércoles), J=Jueves, V=Viernes, S=Sábado
            dias_seleccionados = data.get('dias', [])
            if dias_seleccionados:
                # Mapeo correcto de días: el frontend envía ['LU', 'MI', etc.]
                # SIIAU usa: L, M, I (mIércoles), J, V, S
                dia_map = {
                    'LU': 'L',
                    'MA': 'M',
                    'MI': 'I',  # ¡Importante! Miércoles = I, no M
                    'JU': 'J',
                    'VI': 'V',
                    'SA': 'S'
                }
                
                dias_buscados = [dia_map.get(dia, dia[0]) for dia in dias_seleccionados]
                print(f"Filtrando por días: {dias_seleccionados} → {dias_buscados}")
                print(f"Registros antes del filtro: {len(df)}")
                
                def cumple_dias(fila):
                    dias_fila = fila.get('Dias', '')
                    # Verificar que TODOS los días seleccionados estén presentes
                    for dia_letra in dias_buscados:
                        if dia_letra not in dias_fila:
                            return False
                    return True
                
                df = df[df.apply(cumple_dias, axis=1)]
                print(f"Registros después del filtro: {len(df)}")
            
            # Guardar en sesión y redirigir
            from flask import session
            session['search_results'] = df.to_dict('records')
            session['search_count'] = len(df)
            
            return jsonify({
                'success': True,
                'redirect': '/results'
            })
        else:
            from flask import session
            session['search_results'] = []
            session['search_count'] = 0
            return jsonify({
                'success': True,
                'redirect': '/results'
            })

    except Exception as e:
        print(f"Error en búsqueda: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-excel', methods=['POST'])
def download_excel():
    try:
        data = request.json.get('data', [])
        
        if not data:
            return jsonify({'error': 'No hay datos para descargar'}), 400
        
        df = pd.DataFrame(data)
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Oferta Académica')
        
        output.seek(0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"oferta_academica_{timestamp}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        print(f"Error en descarga: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
