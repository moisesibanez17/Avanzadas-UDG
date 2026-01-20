// Global variable to store search results
let searchResults = [];

// DOM Elements
const searchForm = document.getElementById('searchForm');
const clearBtn = document.getElementById('clearBtn');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('resultsSection');
const resultsBody = document.getElementById('resultsBody');
const resultsCount = document.getElementById('resultsCount');
const downloadBtn = document.getElementById('downloadBtn');

// Event Listeners
searchForm.addEventListener('submit', handleSearch);
clearBtn.addEventListener('click', handleClear);
downloadBtn.addEventListener('click', handleDownload);

// Handle form submission
async function handleSearch(e) {
    e.preventDefault();

    const formData = new FormData(searchForm);
    const data = {
        ciclo: formData.get('ciclo'),
        centro: formData.get('centro'),
        carrera: formData.get('carrera') || '',
        materia: formData.get('materia') || '',
        hora_inicio: formData.get('hora_inicio') || '',
        hora_fin: formData.get('hora_fin') || '',
        edificio: formData.get('edificio') || '',
        aula: formData.get('aula') || '',
        orden: formData.get('orden'),
        mostrar: formData.get('mostrar'),
        solo_disponibles: formData.get('solo_disponibles') === 'on',
        dias: formData.getAll('dias')
    };

    // Validation
    if (!data.centro) {
        showNotification('Por favor selecciona un Centro Universitario', 'error');
        return;
    }

    // Show loading
    loading.style.display = 'block';

    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Error en la búsqueda');
        }

        // Redirect to results page
        if (result.redirect) {
            window.location.href = result.redirect;
        }

    } catch (error) {
        console.error('Error:', error);
        showNotification(`Error: ${error.message}`, 'error');
        loading.style.display = 'none';
    }
}

// Display results in table
function displayResults(data, count) {
    resultsCount.textContent = `${count} registro${count !== 1 ? 's' : ''} encontrado${count !== 1 ? 's' : ''}`;

    if (count === 0) {
        resultsBody.innerHTML = `
            <tr>
                <td colspan="11" style="text-align: center; padding: 2rem;">
                    <i class="fas fa-inbox" style="font-size: 3rem; color: rgba(255,255,255,0.3); margin-bottom: 1rem;"></i>
                    <p style="color: rgba(255,255,255,0.6);">No se encontraron resultados con los filtros especificados</p>
                </td>
            </tr>
        `;
        resultsSection.style.display = 'block';
        return;
    }

    resultsBody.innerHTML = data.map(row => `
        <tr>
            <td>${escapeHtml(row.NRC || '')}</td>
            <td>${escapeHtml(row.Clave || '')}</td>
            <td>${escapeHtml(row.Materia || '')}</td>
            <td>${escapeHtml(row.Sec || '')}</td>
            <td>${escapeHtml(row.CR || '')}</td>
            <td>${escapeHtml(row.DIS || '')}</td>
            <td>${escapeHtml(row.Horas || '')}</td>
            <td>${escapeHtml(row.Dias || '')}</td>
            <td>${escapeHtml(row.Edificio || '')}</td>
            <td>${escapeHtml(row.Aula || '')}</td>
            <td>${escapeHtml(row.Profesor || '')}</td>
        </tr>
    `).join('');

    resultsSection.style.display = 'block';

    // Smooth scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// Handle clear button
function handleClear() {
    searchForm.reset();
    resultsSection.style.display = 'none';
    searchResults = [];

    showNotification('Formulario limpiado', 'success');
}

// Handle download button
async function handleDownload() {
    if (searchResults.length === 0) {
        showNotification('No hay datos para descargar', 'error');
        return;
    }

    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ data: searchResults })
        });

        if (!response.ok) {
            throw new Error('Error al descargar el archivo');
        }

        // Create blob and download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `oferta_academica_${new Date().getTime()}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showNotification('Archivo descargado exitosamente', 'success');

    } catch (error) {
        console.error('Error:', error);
        showNotification(`Error al descargar: ${error.message}`, 'error');
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;

    // Add styles if not already present
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                z-index: 1000;
                animation: slideInRight 0.3s ease;
                max-width: 400px;
            }

            .notification-error {
                border-left: 4px solid #ef4444;
            }

            .notification-success {
                border-left: 4px solid #10b981;
            }

            .notification-info {
                border-left: 4px solid #3b82f6;
            }

            @keyframes slideInRight {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Add input validation for time fields
const horaInicio = document.getElementById('hora_inicio');
const horaFin = document.getElementById('hora_fin');

[horaInicio, horaFin].forEach(input => {
    input.addEventListener('input', (e) => {
        // Only allow digits
        e.target.value = e.target.value.replace(/\D/g, '');

        // Limit to 4 digits
        if (e.target.value.length > 4) {
            e.target.value = e.target.value.slice(0, 4);
        }
    });
});

// Add loading state to submit button
searchForm.addEventListener('submit', () => {
    const submitBtn = searchForm.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Buscando...';

    // Reset button after response (will be handled in finally block)
    setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-search"></i> Buscar';
    }, 100);
});

console.log('SIIAU Extractor - Frontend cargado correctamente');
