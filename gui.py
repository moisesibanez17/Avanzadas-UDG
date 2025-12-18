import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import re

# Constantes del script original
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

class SIIAUExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Extractor de Oferta Académica SIIAU")

        # Variables para almacenar selecciones
        self.ciclo_var = tk.StringVar(value="202520")  # Valor por defecto
        self.centro_var = tk.StringVar()
        self.carrera_var = tk.StringVar()
        self.materia_var = tk.StringVar()
        self.hora_inicio_var = tk.StringVar()
        self.hora_fin_var = tk.StringVar()
        self.dias_vars = {dia: tk.BooleanVar() for dia in ['LU', 'MA', 'MI', 'JU', 'VI', 'SA']}
        self.edificio_var = tk.StringVar()
        self.aula_var = tk.StringVar()
        self.solo_disponibles_var = tk.BooleanVar()
        self.orden_var = tk.StringVar(value="0")  # 0=Materia, 1=Clave, 2=NRC
        self.mostrar_var = tk.StringVar(value="100")

        # Status bar
        self.status_var = tk.StringVar()

        # Frame principal con scrollbar
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Canvas y scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Organizar los widgets
        self._create_ciclo_section()
        self._create_centro_section()
        self._create_carrera_section()
        self._create_materia_section()
        self._create_horario_section()
        self._create_lugar_section()
        self._create_opciones_section()
        self._create_buttons_section()
        self._create_status_bar()

        # Empaquetar todo
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

    def _create_ciclo_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Ciclo", padding="5")
        frame.pack(fill="x", padx=5, pady=5)

        ciclos = ["202520 - Calendario 25 B"]  # Aquí podrías cargar los ciclos disponibles
        combo = ttk.Combobox(frame, textvariable=self.ciclo_var, values=ciclos)
        combo.pack(fill="x")
        if ciclos:
            combo.set(ciclos[0])

    def _create_centro_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Centro", padding="5")
        frame.pack(fill="x", padx=5, pady=5)

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
        combo = ttk.Combobox(frame, textvariable=self.centro_var, values=list(centros.values()))
        combo.pack(fill="x")

    def _create_carrera_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Carrera", padding="5")
        frame.pack(fill="x", padx=5, pady=5)

        # Aquí agregarías un listbox o combobox para las carreras
        ttk.Label(frame, text="Se cargarán las carreras según el centro seleccionado").pack()
        combo = ttk.Combobox(frame, textvariable=self.carrera_var)
        combo.pack(fill="x")

    def _create_materia_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Materia", padding="5")
        frame.pack(fill="x", padx=5, pady=5)

        entry = ttk.Entry(frame, textvariable=self.materia_var)
        entry.pack(fill="x")

    def _create_horario_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Horario", padding="5")
        frame.pack(fill="x", padx=5, pady=5)

        # Horas
        hora_frame = ttk.Frame(frame)
        hora_frame.pack(fill="x", pady=5)

        ttk.Label(hora_frame, text="Hora Inicio:").pack(side="left", padx=5)
        ttk.Entry(hora_frame, textvariable=self.hora_inicio_var, width=10).pack(side="left", padx=5)

        ttk.Label(hora_frame, text="Hora Fin:").pack(side="left", padx=5)
        ttk.Entry(hora_frame, textvariable=self.hora_fin_var, width=10).pack(side="left", padx=5)

        # Días
        dias_frame = ttk.Frame(frame)
        dias_frame.pack(fill="x", pady=5)

        for dia in self.dias_vars:
            ttk.Checkbutton(dias_frame, text=dia, variable=self.dias_vars[dia]).pack(side="left", padx=5)

    def _create_lugar_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Lugar", padding="5")
        frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(frame, text="Edificio:").pack(side="left", padx=5)
        ttk.Entry(frame, textvariable=self.edificio_var).pack(side="left", padx=5)

        ttk.Label(frame, text="Aula:").pack(side="left", padx=5)
        ttk.Entry(frame, textvariable=self.aula_var).pack(side="left", padx=5)

    def _create_opciones_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Opciones", padding="5")
        frame.pack(fill="x", padx=5, pady=5)

        # Sólo disponibles
        ttk.Checkbutton(frame, text="Incluir sólo secciones con lugares disponibles",
                       variable=self.solo_disponibles_var).pack(pady=5)

        # Ordenado por
        orden_frame = ttk.Frame(frame)
        orden_frame.pack(fill="x", pady=5)
        ttk.Label(orden_frame, text="Ordenado por:").pack(side="left", padx=5)
        ttk.Radiobutton(orden_frame, text="Materia", variable=self.orden_var,
                       value="0").pack(side="left", padx=5)
        ttk.Radiobutton(orden_frame, text="Clave", variable=self.orden_var,
                       value="1").pack(side="left", padx=5)
        ttk.Radiobutton(orden_frame, text="NRC", variable=self.orden_var,
                       value="2").pack(side="left", padx=5)

        # Mostrar de
        mostrar_frame = ttk.Frame(frame)
        mostrar_frame.pack(fill="x", pady=5)
        ttk.Label(mostrar_frame, text="Mostrar de:").pack(side="left", padx=5)
        ttk.Radiobutton(mostrar_frame, text="100 en 100", variable=self.mostrar_var,
                       value="100").pack(side="left", padx=5)
        ttk.Radiobutton(mostrar_frame, text="200 en 200", variable=self.mostrar_var,
                       value="200").pack(side="left", padx=5)
        ttk.Radiobutton(mostrar_frame, text="500 en 500", variable=self.mostrar_var,
                       value="500").pack(side="left", padx=5)

    def _create_buttons_section(self):
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill="x", padx=5, pady=10)

        ttk.Button(frame, text="Buscar", command=self._buscar).pack(side="left", padx=5)
        ttk.Button(frame, text="Limpiar", command=self._limpiar).pack(side="left", padx=5)

    def _create_status_bar(self):
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _buscar(self):
        # Diccionario de centros universitarios
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
        centro_seleccionado = self.centro_var.get()
        codigo_centro = ''
        for k, v in centros.items():
            if v == centro_seleccionado:
                codigo_centro = k
                break

        # Extraer solo el número del ciclo
        ciclo_seleccionado = self.ciclo_var.get()
        codigo_ciclo = ciclo_seleccionado.split('-')[0].strip() if ciclo_seleccionado else '202520'

        # Construir string de días seleccionados ('. L . . . . .')
        dias_orden = ['LU', 'MA', 'MI', 'JU', 'VI', 'SA']
        dias_str = ''
        for dia in dias_orden:
            dias_str += dia[0] if self.dias_vars[dia].get() else '.'
            dias_str += ' '
        dias_str = dias_str.strip()

        # Construir el payload con los valores corregidos (sin diasp)
        payload = {
            "ciclop": codigo_ciclo,
            "cup": codigo_centro,
            "majrp": self.carrera_var.get().strip(),
            "crsep": "",
            "materiap": self.materia_var.get().strip(),
            "horaip": self.hora_inicio_var.get().strip(),
            "horafp": self.hora_fin_var.get().strip(),
            "edifp": self.edificio_var.get().strip(),
            "aulap": self.aula_var.get().strip(),
            "ordenp": self.orden_var.get(),
            "mostrarp": self.mostrar_var.get(),
            "dispp": "1" if self.solo_disponibles_var.get() else "",
        }

        # Validar que al menos tengamos centro universitario
        if not codigo_centro:
            messagebox.showwarning("Datos incompletos", "Por favor selecciona un Centro Universitario")
            return

        # Actualizar la barra de estado
        self.status_var.set("Iniciando extracción...")
        self.root.update()

        try:
            with requests.Session() as s:
                s.headers.update(HEADERS)
                s.cookies.update(COOKIES)

                # Usar las funciones existentes para la extracción
                all_data = fetch_all_pages(s, POST_URL, payload, debug_mode=False)

                if all_data:
                    df = pd.DataFrame(all_data)
                    # Filtrar por días seleccionados si hay alguno marcado
                    dias_seleccionados = [dia for dia in dias_orden if self.dias_vars[dia].get()]
                    if dias_seleccionados:
                        # El campo 'Dias' en el DataFrame puede tener algo como '. M . J . .'
                        def cumple_dias(fila):
                            dias_fila = fila.get('Dias', '')
                            for dia in dias_seleccionados:
                                if dia[0] not in dias_fila:
                                    return False
                            return True
                        df = df[df.apply(cumple_dias, axis=1)]

                    # Filtrar por horarios si se especificó alguno
                    hora_inicio = self.hora_inicio_var.get().strip()
                    hora_fin = self.hora_fin_var.get().strip()
                    if hora_inicio or hora_fin:
                        def parse_h(h):
                            if not h:
                                return None
                            h_clean = ''.join(ch for ch in h if ch.isdigit())
                            if len(h_clean) == 3:  # ej 700 -> 0700
                                h_clean = '0' + h_clean
                            if len(h_clean) != 4 or not h_clean.isdigit():
                                return None
                            return int(h_clean)

                        f_start = parse_h(hora_inicio) if hora_inicio else 0
                        f_end = parse_h(hora_fin) if hora_fin else 2400
                        if f_start and f_end and f_start > f_end:
                            # Intercambiar si el usuario los invirtió
                            f_start, f_end = f_end, f_start

                        def cumple_horario(fila):
                            horas = fila.get('Horas', '')
                            if not horas:
                                return False
                            partes = horas.replace(' ', '').split('-')
                            if len(partes) != 2:
                                return False
                            if not (partes[0].isdigit() and partes[1].isdigit()):
                                return False
                            h_inicio_clase = int(partes[0])
                            h_fin_clase = int(partes[1])
                            # Validar rango básico
                            if h_inicio_clase <= 0 or h_fin_clase <= 0 or h_inicio_clase >= h_fin_clase:
                                return False
                            # Lógica de solapamiento: (start < filtro_fin) y (end > filtro_inicio)
                            return (h_inicio_clase < f_end) and (h_fin_clase > f_start)

                        df = df[df.apply(cumple_horario, axis=1)]

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"oferta_{codigo_centro}_{payload['majrp'] if payload['majrp'] else 'TODAS'}_{timestamp}.csv"
                    df.to_csv(filename, index=False, encoding="utf-8")
                    self.status_var.set(f"Extracción completada. {len(df)} registros guardados en {filename}")
                    messagebox.showinfo("Éxito", f"Se han extraído {len(df)} registros.\nGuardados en: {filename}")
                else:
                    self.status_var.set("No se encontraron registros.")
                    messagebox.showwarning("Sin resultados", "No se encontraron registros con los filtros especificados.")

        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error durante la extracción: {str(e)}")

    def _limpiar(self):
        # Resetear todas las variables
        self.ciclo_var.set("")
        self.centro_var.set("")
        self.carrera_var.set("")
        self.materia_var.set("")
        self.hora_inicio_var.set("")
        self.hora_fin_var.set("")
        for dia in self.dias_vars:
            self.dias_vars[dia].set(False)
        self.edificio_var.set("")
        self.aula_var.set("")
        self.solo_disponibles_var.set(False)
        self.orden_var.set("0")
        self.mostrar_var.set("100")

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
    debug_files = []  # Lista para registrar archivos de depuración generados

    while True:
        page += 1
        payload = dict(payload_base)
        payload['p_start'] = str(p_start)

        print(f"\n[Página {page}] solicitando p_start={p_start} ...")
        print(f"Payload: {payload}")

        try:
            resp = session.post(post_url, data=payload, timeout=30)
            print(f"Status Code: {resp.status_code}")

            if resp.status_code != 200:
                print(f"Error HTTP en página {page}: {resp.status_code}")
                print("Contenido de respuesta:", resp.text[:500])  # Primeros 500 caracteres
                break

            # Guardar la respuesta HTML para diagnóstico solo si debug_mode está activado
            if debug_mode:
                debug_file = f'debug_page_{page}.html'
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(resp.text)
                debug_files.append(debug_file)
                print(f"Respuesta guardada en {debug_file}")

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
                # El valor de p_start debe incrementarse por el número mostrado (100, 200, etc.)
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
            time.sleep(1.5)  # Aumentado a 1.5 segundos

        except Exception as e:
            print(f"Error en página {page}: {str(e)}")
            break

    # Eliminar los archivos de depuración si se generaron
    if not debug_mode:
        for file in debug_files:
            try:
                import os
                if os.path.exists(file):
                    os.remove(file)
                    print(f"Archivo de depuración eliminado: {file}")
            except Exception as e:
                print(f"No se pudo eliminar {file}: {str(e)}")

    print(f"\nExtracción completada: {total_extraido} registros en {page} páginas")
    return results

if __name__ == "__main__":
    root = tk.Tk()
    app = SIIAUExtractorGUI(root)
    root.mainloop()
