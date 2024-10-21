import numpy as np
import pandas as pd
import ast
from kmodes.kmodes import KModes
import matplotlib.pyplot as plt
from kneed import KneeLocator
import seaborn as sns

# Membaca file CSV
df = pd.read_csv('./data/sample_data_random.csv')

# print(df.head())

# Fungsi untuk mengekstrak field yang diperlukan
def extract_fields(fields):
    try:
        # Mengubah string menjadi dictionary
        fields_dict = ast.literal_eval(fields)
        # Mengambil field yang diperlukan
        return {
            'analyzer_id': fields_dict.get('analyzer_id'),
            'source_address': fields_dict.get('source_address'),
            'source_protocol': fields_dict.get('source_protocol'),
            'target_protocol': fields_dict.get('target_protocol')
        }
    except (ValueError, SyntaxError):
        # Jika fields tidak bisa diubah menjadi dictionary, kembalikan None
        return None

# Menerapkan fungsi extract_fields pada kolom 'fields'
extracted_fields = df['fields'].apply(extract_fields)

# Mengubah hasil menjadi DataFrame
fields_df = pd.DataFrame(extracted_fields.tolist())

# Menggabungkan dengan kolom lain jika diperlukan
result_df = pd.concat([df, fields_df], axis=1)

# Memilih kolom yang diperlukan dan membuat salinan eksplisit
selected_columns = result_df[['analyzer_id', 'source_address', 'source_protocol', 'target_protocol']].copy()

# print(selected_columns.head())

# Melakukan K-Modes Clustering
# Konversi kolom menjadi tipe string agar sesuai dengan k-modes
for col in selected_columns.columns:
    selected_columns.loc[:, col] = selected_columns[col].astype(str)

# Fungsi untuk menghitung WCSS atau total mismatches
def calculate_wcss(data, max_clusters, random_state=42):
    wcss = []
    for k in range(2, max_clusters + 1):  # Mengubah rentang iterasi dari 2 hingga max_clusters
        km = KModes(n_clusters=k, init='Huang', n_init=10, verbose=0, random_state=random_state, max_iter=100)
        km.fit(data)
        wcss.append(km.cost_)
    return wcss

# Menentukan jumlah maksimum cluster yang akan diuji
max_clusters = 7

# Menghitung WCSS untuk berbagai jumlah cluster dari 2 hingga 7
wcss = calculate_wcss(selected_columns, max_clusters)

# Plot WCSS vs jumlah cluster
plt.plot(range(2, max_clusters + 1), wcss, marker='o')
plt.title('Elbow Method for Optimal k')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')
plt.grid(True)
plt.show()

# Menggunakan KneeLocator untuk menemukan titik elbow
kneedle = KneeLocator(range(2, max_clusters + 1), wcss, curve='convex', direction='decreasing')
optimal_clusters = kneedle.elbow

print(f"Optimal number of clusters: {optimal_clusters}")

# Inisialisasi model K-Modes dengan jumlah cluster yang optimal
km_optimal = KModes(n_clusters=optimal_clusters, init='Huang', n_init=10, verbose=1, random_state=42, max_iter=100)

# Melakukan fitting dan prediksi untuk clustering optimal
clusters_optimal = km_optimal.fit_predict(selected_columns)

# Menambahkan hasil clustering optimal ke DataFrame untuk visualisasi
selected_columns['cluster_optimal'] = clusters_optimal

# Menampilkan hasil clustering
# print(selected_columns.head())

# Visualisasi hasil clustering satu per satu untuk jumlah cluster optimal
for col in selected_columns.columns[:-1]:  # Kecualikan kolom cluster
    plt.figure(figsize=(14, 8))
    sns.scatterplot(x=selected_columns.index, y=selected_columns[col], hue=selected_columns['cluster_optimal'], palette='viridis', s=100, alpha=0.6)
    plt.title(f'Cluster visualization for {col}')
    plt.xlabel('index')
    plt.ylabel(col)
    plt.tight_layout()
    plt.savefig(f'./img/cluster_visualization_{col}.png')
    plt.show()
    plt.close()

# Menyimpan hasil clustering optimal ke file Excel
output_file_optimal = './data/clustered_data_kmodes_optimal_clusters.xlsx'
with pd.ExcelWriter(output_file_optimal) as writer:
    for cluster in np.unique(clusters_optimal):
        cluster_data = selected_columns[selected_columns['cluster_optimal'] == cluster]
        cluster_data.to_excel(writer, sheet_name=f'Cluster_{cluster}', index=False)

print(f"Hasil clustering optimal telah disimpan ke dalam file {output_file_optimal}")

# Menyimpan hasil WCSS ke file Excel terpisah
output_file_wcss = './data/wcss_scores.xlsx'
wcss_df = pd.DataFrame({'Number of Clusters': range(2, max_clusters + 1), 'WCSS': wcss})
with pd.ExcelWriter(output_file_wcss) as writer:
    wcss_df.to_excel(writer, sheet_name='WCSS_Scores', index=False)
    # Menyimpan score hasil optimal dari elbow method
    score_df = pd.DataFrame({'Optimal Number of Clusters': [optimal_clusters], 'WCSS': [wcss[optimal_clusters - 2]]})
    score_df.to_excel(writer, sheet_name='Optimal_Cluster_Score', index=False)

print(f"Hasil WCSS telah disimpan ke dalam file {output_file_wcss}")

# Menyimpan hasil clustering untuk rentang jumlah cluster dari 2 hingga 7
for n_clusters in range(2, max_clusters + 1):
    km = KModes(n_clusters=n_clusters, init='Huang', n_init=10, verbose=1, random_state=42, max_iter=100)
    clusters = km.fit_predict(selected_columns.drop(columns='cluster_optimal'))  # Drop the optimal cluster column to avoid confusion
    selected_columns_temp = selected_columns.drop(columns='cluster_optimal').copy()  # Make a copy for each clustering range
    selected_columns_temp['cluster'] = clusters  # Add a new column for each cluster range

    output_file = f'./data/member_of_cluster/clustered_data_kmodes_{n_clusters}_clusters.xlsx'
    with pd.ExcelWriter(output_file) as writer:
        for cluster in np.unique(clusters):
            cluster_data = selected_columns_temp[selected_columns_temp['cluster'] == cluster]
            cluster_data.to_excel(writer, sheet_name=f'Cluster_{cluster}', index=False)

    print(f"Hasil clustering dengan {n_clusters} clusters telah disimpan ke dalam file {output_file}")
