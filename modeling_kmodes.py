import numpy as np
import pandas as pd
import ast
from kmodes.kmodes import KModes

# Membaca file CSV
df = pd.read_csv('./data/sample_data_random.csv')

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

# Konversi kolom menjadi tipe string agar sesuai dengan k-modes
for col in selected_columns.columns:
    selected_columns.loc[:, col] = selected_columns[col].astype(str)

# Inisialisasi model K-Modes
km = KModes(n_clusters=3, init='Huang', n_init=10, verbose=1, random_state=42)

# Melakukan fitting dan prediksi
clusters = km.fit_predict(selected_columns)

# Menambahkan hasil clustering ke DataFrame
selected_columns['cluster'] = clusters

# Menyimpan hasil clustering ke file Excel baru dengan masing-masing cluster di sheet yang berbeda
with pd.ExcelWriter('./data/clustered_data_kmodes.xlsx') as writer:
    for cluster in sorted(selected_columns['cluster'].unique()):
        cluster_data = selected_columns[selected_columns['cluster'] == cluster]
        cluster_data.to_excel(writer, sheet_name=f'Cluster {cluster}', index=False)

# Menampilkan beberapa baris pertama dari DataFrame hasil
print(selected_columns.head())
