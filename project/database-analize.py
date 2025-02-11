import paramiko
import pandas as pd
import streamlit as st
import io
import seaborn as sns
import matplotlib.pyplot as plt

# =======================#
# KONFIGURASI SERVER SSH #
# =======================#
SSH_HOST = "10.20.12.123"  # IP Server Linux
SSH_USER = "root"  # User SSH (misalnya "ubuntu" atau "root")
SSH_PASSWORD = "20410*26"  # Password SSH (gunakan key jika perlu)

# =======================#
# KONFIGURASI DATABASE   #
# =======================#
DB_USER = "genta"  # User MySQL (bukan user Linux)
DB_PASSWORD = "111"  # Password MySQL
DB_NAME = "sinvent_penilaian"  # Nama database
TABLE_NAME = "kategori"  # Nama tabel yang ingin diakses

# =======================#
# STREAMLIT APP #
# =======================#

st.title("🔎 Analisis Data dari Server")
st.sidebar.header("🔧 Konfigurasi Query")

# Pilih query dari dropdown
query_option = st.sidebar.selectbox(
    "Pilih Query",
    [
        f"SELECT * FROM {TABLE_NAME};",
        f"SELECT COUNT(*) AS Total FROM {TABLE_NAME};",
        f"SELECT column1, column2 FROM {TABLE_NAME} LIMIT 10;",
    ]
)

st.sidebar.write("Klik tombol di bawah untuk mengeksekusi query:")
execute_query = st.sidebar.button("Jalankan Query")


def get_data_from_server(query):
    try:
        # Koneksi ke server Linux menggunakan SSH
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD)

        # Eksekusi Query di Server
        command = f'mysql -u {DB_USER} -p{DB_PASSWORD} -D {DB_NAME} -e "{query}" --batch --raw'
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode()
        error_output = stderr.read().decode()

        client.close()

        if error_output:
            st.error(f"Error dari server: {error_output}")
            return None

        if not output.strip():
            st.warning("Query berhasil dieksekusi, tetapi tidak ada data yang dikembalikan.")
            return None

        # Parsing hasil output MySQL ke Pandas DataFrame
        df = pd.read_csv(io.StringIO(output), sep="\t", error_bad_lines=False)
        return df

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        return None


if execute_query:
    st.subheader("📊 Hasil Query")
    data = get_data_from_server(query_option)

    if data is not None:
        st.write(data)

        # Jika dataset memiliki lebih dari 2 kolom, buat scatter plot
        if len(data.columns) >= 2:
            st.subheader("📈 Visualisasi Data")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.scatterplot(data=data, x=data.columns[0], y=data.columns[1])
            st.pyplot(fig)
