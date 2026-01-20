# Render.com Deployment Guide

## ✅ Archivos creados para Render:

- `Procfile` - Le dice a Render cómo ejecutar la app
- `requirements.txt` - Actualizado con `gunicorn`
- `runtime.txt` - Python 3.12

## 🚀 Pasos para Deploy en Render:

### 1. Sube los cambios a GitHub
```bash
git add .
git commit -m "Configurado para Render.com"
git push origin main
```

### 2. Crea cuenta en Render
1. Ve a https://render.com
2. Click "Get Started" o "Sign Up"
3. Conecta tu cuenta de GitHub

### 3. Crea nuevo Web Service
1. En el dashboard de Render, click "New +" → "Web Service"
2. Conecta tu repositorio `Avanzadas-UDG`
3. Render detectará automáticamente que es una app Flask

### 4. Configuración (Render auto-detecta pero verifica):
- **Name**: `oferta-siiau` (o el que quieras)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app` (ya está en Procfile)
- **Plan**: **Free** (selecciona el plan gratuito)

### 5. Variables de Entorno (Opcional pero recomendado):
En "Environment" agrega:
- `PYTHON_VERSION`: `3.12.0`
- `SECRET_KEY`: `siiau-extractor-secret-key-2025` (o genera uno nuevo)

### 6. Deploy!
1. Click "Create Web Service"
2. Render empezará a construir tu app
3. Esto tarda 2-5 minutos la primera vez
4. Te dará una URL como `https://oferta-siiau.onrender.com`

### 7. Dominio Custom (Opcional)
1. En la configuración del servicio, ve a "Settings"
2. En "Custom Domain", agrega `oferta.diferente.page`
3. Sigue las instrucciones de DNS

## ⚠️ Importante sobre Plan Gratuito:

**El plan gratuito de Render:**
- ✅ Sin límites de tiempo de ejecución (perfecto para tu scraping)
- ⚠️ Se "duerme" después de 15 minutos de inactividad
- ⚠️ La primera petición después de dormir tarda ~30 segundos en despertar
- ⏱️ 750 horas gratis al mes (suficiente para uso normal)

**Solución para el "sleep":**
- Puedes hacer ping cada 14 minutos para mantenerlo despierto
- O simplemente aceptar que la primera carga sea lenta

## 📝 Checklist:

- [ ] Sube código a GitHub
- [ ] Crea cuenta en Render.com
- [ ] Conecta GitHub con Render
- [ ] Crea nuevo Web Service
- [ ] Espera el deploy (2-5 min)
- [ ] Prueba la URL que te da Render
- [ ] (Opcional) Configura dominio custom

¿Problemas? Avísame y te ayudo a resolverlos.
