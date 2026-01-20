# Extractor de Oferta Académica SIIAU - Web App

Aplicación web desarrollada con Flask para extraer y consultar la oferta académica del sistema SIIAU de la Universidad de Guadalajara.

## 🚀 Características

- ✨ Interfaz web moderna con diseño glassmorphism
- 🔍 Búsqueda avanzada con múltiples filtros
- 📊 Visualización de resultados en tabla
- 💾 Exportación a CSV
- 📱 Diseño responsive (mobile-friendly)
- 🎨 Animaciones suaves y efectos visuales

## 📋 Requisitos

- Python 3.8 o superior
- Dependencias listadas en `requirements.txt`

## 🛠️ Instalación Local

1. Clona este repositorio:
```bash
git clone https://github.com/tu-usuario/Avanzadas-UDG.git
cd Avanzadas-UDG
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:
```bash
python app.py
```

4. Abre tu navegador en: `http://localhost:5000`

## 🌐 Despliegue en la Nube

### Opción 1: Render.com (Recomendado - Gratis)

1. Crea una cuenta en [Render.com](https://render.com)
2. Crea un nuevo **Web Service**
3. Conecta tu repositorio de GitHub
4. Configuración:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Agrega `gunicorn` a `requirements.txt`

### Opción 2: Railway.app

1. Crea una cuenta en [Railway.app](https://railway.app)
2. Crea un nuevo proyecto desde GitHub
3. Railway detectará automáticamente Flask
4. Deploy automático

### Opción 3: PythonAnywhere

1. Crea una cuenta en [PythonAnywhere](https://www.pythonanywhere.com)
2. Sube los archivos o clona desde GitHub
3. Configura una nueva Web App con Flask
4. Configura el archivo WSGI

## 📖 Uso

1. **Selecciona el ciclo escolar** (por defecto: 202520)
2. **Elige el Centro Universitario** (requerido)
3. **Aplica filtros opcionales**:
   - Carrera
   - Materia
   - Horario
   - Días de la semana
   - Edificio/Aula
   - Solo disponibles
4. **Haz clic en "Buscar"**
5. **Descarga los resultados** en CSV si lo deseas

## 🎯 Filtros Disponibles

- **Ciclo**: Selecciona el periodo académico
- **Centro Universitario**: CUCEI, CUCEA, CUCSH, etc.
- **Carrera**: Código de carrera (ej: INCO, ICOM)
- **Materia**: Nombre de la materia
- **Horario**: Rango de horas (formato: 0700-1400)
- **Días**: Lunes a Sábado
- **Lugar**: Edificio y aula específicos
- **Ordenar por**: Materia, Clave o NRC
- **Mostrar**: 100, 200 o 500 resultados por página

## 🗂️ Estructura del Proyecto

```
Avanzadas-UDG/
├── app.py                 # Backend Flask
├── gui.py                 # Aplicación de escritorio (legacy)
├── templates/
│   └── index.html        # Frontend HTML
├── static/
│   ├── style.css         # Estilos CSS
│   └── script.js         # Lógica JavaScript
├── requirements.txt      # Dependencias Python
└── README.md            # Este archivo
```

## 🔧 Tecnologías Utilizadas

### Backend
- **Flask**: Framework web
- **BeautifulSoup4**: Web scraping
- **Pandas**: Procesamiento de datos
- **Requests**: HTTP requests

### Frontend
- **HTML5**: Estructura
- **CSS3**: Estilos (Glassmorphism, Gradientes)
- **JavaScript**: Interactividad
- **Font Awesome**: Iconos
- **Google Fonts**: Tipografía (Poppins)

## ⚠️ Notas Importantes

- Los datos se extraen directamente del sistema SIIAU oficial
- La aplicación requiere conexión a internet
- Las cookies de sesión están hardcodeadas y pueden expirar
- Actualiza las cookies en `app.py` si experimentas problemas de autenticación

## 📝 Licencia

Este proyecto es de código abierto y está disponible para uso educativo.

## 👤 Autor

Desarrollado por **Moises Ibañez**

---

Para más información sobre el sistema SIIAU, visita: [SIIAU UDG](https://siiauescolar.siiau.udg.mx)
