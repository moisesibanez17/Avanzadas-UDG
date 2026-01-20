# Netlify Deployment Guide

## Archivos creados para Netlify:

- ✅ `netlify.toml` - Configuración de Netlify
- ✅ `runtime.txt` - Versión de Python (3.12)
- ✅ `netlify/functions/api.py` - Función serverless para Flask
- ✅ `static/index.html` - Página principal
- ✅ `static/results.html` - Página de resultados

## ⚠️ Limitaciones Importantes

**Netlify Functions tiene un límite de 10 segundos (plan gratuito)**. Tu scraping puede tardar más, especialmente con búsquedas grandes.

Si encuentras timeouts:
1. Reduce el tamaño de las búsquedas
2. O considera migrar a Render.com (sin límites de tiempo)

## Pasos para deploy:

### 1. Sube tu código a GitHub
```bash
git add .
git commit -m "Preparado para Netlify"
git push origin main
```

### 2. En Netlify:
1. Ve a https://app.netlify.com
2. Click "Add new site" → "Import an existing project"
3. Conecta tu repositorio de GitHub
4. Netlify detectará automáticamente `netlify.toml`
5. Click "Deploy site"

### 3. Configura el dominio
- En Netlify, ve a "Domain settings"
- Agrega `oferta.diferente.page` como dominio custom
- Sigue las instrucciones de DNS

## Si hay problemas de timeout:

Render.com es mejor opción (gratis, sin límites):
1. Más simple para Flask
2. Sin límites de tiempo de ejecución
3. Deploy automático desde GitHub

¿Necesitas ayuda con la migración a Render?
