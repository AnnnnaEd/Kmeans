# fraud_detection_api/analysis.py
import pandas as pd
from collections import Counter
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import io
import base64
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# --- Funciones auxiliares de Graficado del Notebook ---

def plot_data(X, y, ax):
    """Grafica los puntos de datos, diferenciando las clases originales."""
    # X es el array 2D de V10 y V14
    ax.plot(X[:, 0][y==0], X[:, 1][y==0], 'k.', markersize=2, label='Normal (0)')
    ax.plot(X[:, 0][y==1], X[:, 1][y==1], 'r.', markersize=2, label='Fraud (1)')
    # Agregamos la leyenda si hay etiquetas para diferenciar
    if 1 in y:
        ax.legend(loc='lower right')

def plot_centroids(centroids, ax, weights=None, circle_color='w', cross_color='k'):
    """Grafica los centroides de K-Means."""
    if weights is not None:
        centroids = centroids[weights > weights.max() / 10]
    ax.scatter(centroids[:, 0], centroids[:, 1],
                marker='o', s=100, linewidths=8,
                color=circle_color, zorder=10, alpha=0.9)
    ax.scatter(centroids[:, 0], centroids[:, 1],
                marker='x', s=150, linewidths=20,
                color=cross_color, zorder=11, alpha=1)

def plot_decision_boundaries(clusterer, X, y, ax, resolution=1000, show_centroids=True):
    """Grafica las regiones de decisión y llama a las funciones auxiliares."""
    
    # 1. Definir límites del gráfico
    X_min, X_max = X[:, 0].min() - 0.1, X[:, 0].max() + 0.1
    Y_min, Y_max = X[:, 1].min() - 0.1, X[:, 1].max() + 0.1

    xx, yy = np.meshgrid(np.linspace(X_min, X_max, resolution),
                         np.linspace(Y_min, Y_max, resolution))
    
    # 2. Predecir clusters para cada punto de la cuadrícula
    Z = clusterer.predict(np.c_[xx.ravel(), yy.ravel()]) 
    Z = Z.reshape(xx.shape)

    # 3. Dibujar las regiones de decisión
    ax.contourf(Z, extent=(X_min, X_max, Y_min, Y_max),
                cmap="Pastel2")
    ax.contour(Z, extent=(X_min, X_max, Y_min, Y_max),
                linewidths=1, colors='k')
    
    # 4. Dibujar los puntos y centroides
    plot_data(X, y, ax)
    
    if show_centroids:
        plot_centroids(clusterer.cluster_centers_, ax)

def generate_plot_base64(X_reduced_df, y_series, kmeans_model):
    """
    Genera el gráfico de Matplotlib (V10 vs V14) y lo devuelve como Base64.
    """
    # Verificamos si las características necesarias están presentes
    if 'V10' not in X_reduced_df.columns or 'V14' not in X_reduced_df.columns:
        return None 

    # 1. Prepara datos para graficar (solo V10 y V14)
    X_plot = X_reduced_df[['V10', 'V14']].values 
    y_plot = y_series.values 
    
    # 2. Re-entrenamos K-Means para 2D para obtener los límites de decisión correctos en el gráfico
    try:
        plot_kmeans = KMeans(n_clusters=kmeans_model.n_clusters, random_state=42, n_init='auto')
        plot_kmeans.fit(X_plot)
    except Exception:
        return None 
        
    
    # 3. Generar gráfico
    fig, ax = plt.subplots(figsize=(10, 6))
    
    plot_decision_boundaries(plot_kmeans, X_plot, y_plot, ax)
    
    ax.set_xlabel("V10 (Proyección)", fontsize=12)
    ax.set_ylabel("V14 (Proyección)", fontsize=12)
    ax.set_title(f"Límites de Decisión K-Means (K={kmeans_model.n_clusters})")
    
    # 4. Guardar gráfico en buffer y codificar
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig) # Cierra la figura para liberar memoria
    
    # 5. Codificar a Base64
    plot_data = base64.b64encode(buffer.getvalue()).decode()
    return plot_data

# -------------------------------------------------------------
# --- FUNCIÓN PRINCIPAL DE ANÁLISIS ---
# -------------------------------------------------------------

def run_kmeans_analysis(file_path, n_clusters=5):
    """
    Carga el dataset y ejecuta todo el flujo de análisis K-Means.
    """
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return {"error": f"Error al cargar el CSV: {e}"}
    
    # === LÓGICA DE MUESTREO (SAMPLING) PARA EVITAR TIMEOUT EN RENDER ===
    # El límite de 50,000 transacciones es seguro para el plan gratuito.
    SAMPLE_LIMIT = 50000 
    if len(df) > SAMPLE_LIMIT:
        df = df.sample(n=SAMPLE_LIMIT, random_state=42)
    # ===================================================================

    # Asume que si 'Class' no existe, las métricas de pureza no se pueden calcular
    y = df.get("Class", pd.Series(np.zeros(len(df)), dtype=int)) 
    
    # 1. Preparación y selección de datos
    if 'Time' in df.columns and 'Amount' in df.columns:
        X = df.drop(["Time", "Amount", "Class"], axis=1, errors='ignore')
    else:
        X = df.drop("Class", axis=1, errors='ignore')

    # 2. Selección de características con Random Forest (si 'Class' real existe)
    if 'Class' in df.columns and df['Class'].nunique() > 1:
        try:
            clf_rnd = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
            clf_rnd.fit(X, df['Class']) # Usamos df['Class'] directamente para el ajuste
            feature_importances = {name: score for name, score in zip(X.columns, clf_rnd.feature_importances_)}
            
            top_features = list(pd.Series(feature_importances).sort_values(ascending=False).head(7).index)
            X_reduced = X[top_features].copy()
        except ValueError:
            X_reduced = X.copy()
    else:
        X_reduced = X.copy()

    # 3. K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    clusters = kmeans.fit_predict(X_reduced)
    
    # --- Generar Plot Base64 ---
    plot_base64 = generate_plot_base64(X_reduced, y, kmeans)
    # ---------------------------
    
    # 4. Evaluación de los resultados
    results = {
        "clusters_summary": [],
        "evaluation_metrics": {},
        "clustering_plot_base64": plot_base64, # AÑADIMOS LA GRÁFICA
    }

    # Resumen de Clusters y Purity Score (solo si 'Class' existía y tenía varianza)
    if 'Class' in df.columns and df['Class'].nunique() > 1:
        counter = Counter(clusters.tolist())
        bad_counter = Counter(clusters[df['Class'] == 1].tolist())
        
        for key in sorted(counter.keys()):
            malicious_count = bad_counter.get(key, 0)
            results["clusters_summary"].append({
                "label": int(key), 
                "total_samples": int(counter[key]),
                "malicious_samples": int(malicious_count)
            })
            
        # Purity Score
        purity = np.sum(np.amax(metrics.cluster.contingency_matrix(df['Class'], clusters), axis=0)) / np.sum(metrics.cluster.contingency_matrix(df['Class'], clusters))
        results["evaluation_metrics"]["purity_score"] = float(purity)
    
    # Métricas sin etiquetas (Siempre se calculan)
    sample_size = min(len(X_reduced), 10000)
    
    try:
        silhouette_score = metrics.silhouette_score(X_reduced, clusters, sample_size=sample_size)
        results["evaluation_metrics"]["silhouette_score"] = float(silhouette_score)
    except Exception:
        results["evaluation_metrics"]["silhouette_score"] = "N/A (Error al calcular)"

    try:
        calinski_harabasz_score = metrics.calinski_harabasz_score(X_reduced, clusters)
        results["evaluation_metrics"]["calinski_harabasz_score"] = float(calinski_harabasz_score)
    except Exception:
        results["evaluation_metrics"]["calinski_harabasz_score"] = "N/A (Error al calcular)"
        
    return results