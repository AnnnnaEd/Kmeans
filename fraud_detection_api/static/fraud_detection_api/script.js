// fraud_detection_api/static/fraud_detection_api/script.js

document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const form = event.target;
    const statusDiv = document.getElementById('status');
    const resultsSection = document.getElementById('results-section');
    const submitBtn = document.getElementById('submit-btn');
    
    // Si estás usando Ngrok (Solución de tunelización):
    const ngrokDomain = "https://willard-forgeable-lea.ngrok-free.dev"; // Reemplaza con tu dominio ngrok real
    const apiEndpoint = ngrokDomain + '/api/analyze/'; 
    

    // 1. Mostrar estado de carga y deshabilitar botón
    statusDiv.textContent = 'Procesando... Esto puede tomar unos segundos.';
    statusDiv.className = 'status-message success';
    statusDiv.style.display = 'block';
    submitBtn.disabled = true;
    resultsSection.style.display = 'none';

    const formData = new FormData(form);

    try {
        // 2. Enviar la solicitud POST al API
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            body: formData,
            mode: 'cors', 
        });

        const data = await response.json();

        if (!response.ok) {
            const errorMessage = data.error ? data.error : 'Ocurrió un error inesperado al ejecutar el análisis. (Revisa logs del servidor).';
            throw new Error(errorMessage);
        }

        // 3. Procesar y mostrar resultados
        displayResults(data);

        statusDiv.textContent = '✅ Análisis K-Means completado exitosamente.';
        statusDiv.className = 'status-message success';
        resultsSection.style.display = 'block'; 

    } catch (error) {
        // 4. Manejo de errores
        statusDiv.textContent = `❌ Error: ${error.message}`;
        statusDiv.className = 'status-message error';
        resultsSection.style.display = 'none';
    } finally {
        // 5. Restaurar el estado del formulario
        submitBtn.disabled = false;
    }
});

function formatValue(key, value) {
    if (typeof value === 'number') {
        if (key === 'purity_score') {
            return (value * 100).toFixed(2) + '%';
        }
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
        badge.innerHTML = `<span>${metricNames[key] || key.toUpperCase()}</span><strong>${formatted}</strong>`;
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
            
            if (cluster.malicious_samples > 0) {
                fraudCell.style.fontWeight = 'bold';
                const fraudRatio = cluster.malicious_samples / cluster.total_samples;
                fraudCell.style.color = (fraudRatio > 0.05) ? 'var(--warning)' : 'var(--success)';
            }
        });
    } else {
        summarySection.style.display = 'none';
        noLabelsWarning.style.display = 'block';
    }
}