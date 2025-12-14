// fraud_detection_api/static/fraud_detection_api/script.js

document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const form = event.target;
    const statusDiv = document.getElementById('status');
    const resultsContainer = document.getElementById('results-container');
    const submitBtn = document.getElementById('submit-btn');

    // 1. Mostrar estado de carga y deshabilitar botón
    statusDiv.textContent = 'Procesando... Esto puede tomar unos segundos.';
    statusDiv.className = 'status-message success';
    statusDiv.style.display = 'block';
    submitBtn.disabled = true;
    resultsContainer.style.display = 'none';

    const formData = new FormData(form);
    // Usamos una URL relativa para el mismo servidor
    const apiEndpoint = '/api/analyze/'; 

    try {
        // 2. Enviar la solicitud POST al API de Django
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            // Manejo de errores del servidor o del análisis
            const errorMessage = data.error ? data.error : 'Ocurrió un error inesperado al ejecutar el análisis.';
            throw new Error(errorMessage);
        }

        // 3. Procesar y mostrar resultados
        displayResults(data);

        statusDiv.textContent = 'Análisis K-Means completado exitosamente.';
        statusDiv.className = 'status-message success';
        // Usamos 'grid' porque la clase 'results-container' lo usa en el CSS
        resultsContainer.style.display = 'grid'; 

    } catch (error) {
        // 4. Manejo de errores
        statusDiv.textContent = `Error: ${error.message}`;
        statusDiv.className = 'status-message error';
        resultsContainer.style.display = 'none';
    } finally {
        // 5. Restaurar el estado del formulario
        submitBtn.disabled = false;
    }
});

function formatValue(key, value) {
    if (typeof value === 'number') {
        // Formatear la pureza como porcentaje
        if (key === 'purity_score') {
            return (value * 100).toFixed(2) + '%';
        }
        // Formatear otros scores a 4 decimales
        return value.toFixed(4);
    }
    return value;
}

function displayResults(data) {
    const metricsOutput = document.getElementById('metrics-output');
    const tableBody = document.getElementById('clusters-table-body');
    const summarySection = document.getElementById('summary-section');
    const noLabelsWarning = document.getElementById('no-labels-warning');
    
    // Elementos del Gráfico
    const clusteringGraph = document.getElementById('clustering-graph');
    const graphLoadingMessage = document.getElementById('graph-loading-message');

    metricsOutput.innerHTML = '';
    tableBody.innerHTML = '';

    // --- A. Lógica del Gráfico (Base64) ---
    if (data.clustering_plot_base64) {
        // Establece la fuente de la imagen con el prefijo data:image/png;base64,
        clusteringGraph.src = `data:image/png;base64,${data.clustering_plot_base64}`;
        clusteringGraph.style.display = 'block';
        graphLoadingMessage.style.display = 'none';
    } else {
        clusteringGraph.src = '';
        clusteringGraph.style.display = 'none';
        graphLoadingMessage.textContent = 'Gráfico no disponible (V10 o V14 faltantes).';
        graphLoadingMessage.style.display = 'block';
    }
    // ----------------------------------------


    // --- B. Mostrar Métricas de Evaluación ---
    const metricNames = {
        'purity_score': 'Purity Score',
        'silhouette_score': 'Silhouette Score',
        'calinski_harabasz_score': 'Calinski Harabasz'
    };

    for (const key in data.evaluation_metrics) {
        const value = data.evaluation_metrics[key];
        const formatted = formatValue(key, value);
        
        const badge = document.createElement('div');
        badge.className = 'metric-badge';
        badge.innerHTML = `${metricNames[key] || key.toUpperCase()}: <strong>${formatted}</strong>`;
        metricsOutput.appendChild(badge);
    }

    // --- C. Mostrar Resumen de Clusters (si hay etiquetas) ---
    if (data.clusters_summary && data.clusters_summary.length > 0) {
        summarySection.style.display = 'block';
        noLabelsWarning.style.display = 'none';
        
        data.clusters_summary.forEach(cluster => {
            const row = tableBody.insertRow();
            row.insertCell().textContent = `Cluster ${cluster.label}`;
            row.insertCell().textContent = cluster.total_samples.toLocaleString();
            
            const fraudCell = row.insertCell();
            fraudCell.textContent = cluster.malicious_samples.toLocaleString();
            
            // Colorear las celdas de fraude para llamar la atención
            if (cluster.malicious_samples > 0) {
                fraudCell.style.fontWeight = 'bold';
                // Resaltamos en amarillo/naranja si el % de fraude es significativo (ej. > 5%)
                const fraudRatio = cluster.malicious_samples / cluster.total_samples;
                fraudCell.style.color = (fraudRatio > 0.05) ? 'var(--warning)' : 'var(--success)';
            }
        });
    } else {
        summarySection.style.display = 'none';
        // Advertencia se activa si el dataset subido no tenía la columna 'Class'
        noLabelsWarning.style.display = 'block';
    }
}