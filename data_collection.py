import pandas as pd
import pymongo
from datetime import datetime
import random
from dateutil import parser

# Menghubungkan ke MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["honeynet"]
collection = db["data_ihp"]

# Mendefinisikan jangka waktu
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 5, 31, 23, 59, 59)

# Mengambil data dari MongoDB berdasarkan jangka waktu (dengan time sebagai string)
query = {
    "time": {
        "$gte": start_date.isoformat(),
        "$lte": end_date.isoformat()
    }
}

# Mengambil semua dokumen yang sesuai dengan query
cursor = collection.find(query)
all_data = list(cursor)

# Memeriksa jumlah data yang ditemukan
data_count = len(all_data)
print(f"Jumlah data yang ditemukan: {data_count}")

# Memastikan ada cukup data untuk pengambilan sampel
if data_count < 1000:
    raise ValueError("Tidak ada cukup data untuk diambil sampel.")

# Mengambil 1000 sampel secara acak
sample_data = random.sample(all_data, 1000)

# Mengonversi string 'time' menjadi datetime
for item in sample_data:
    item['time'] = parser.parse(item['time'])

# Mengonversi data ke dalam DataFrame pandas
df = pd.DataFrame(sample_data)

# Menampilkan DataFrame
print(df)

# Menyimpan DataFrame ke dalam file CSV
df.to_csv("./data/sample_data_random.csv", index=False)

print("Data sampel telah disimpan ke sample_data_random.csv")
