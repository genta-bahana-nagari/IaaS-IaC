import paramiko
import pandas as pd
import streamlit as st
import io
import seaborn as sns
import matplotlib.pyplot as plt

# ==============================#
# KONFIGURASI SERVER & DATABASE #
# ==============================#

def get_data_from_server(query, SSH_HOST, SSH_USER, SSH_PASSWORD, DB_USER, DB_PASSWORD, DB_NAME):
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
        df = pd.read_csv(io.StringIO(output), sep="\t", on_bad_lines='skip')
        return df

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        return None

# ==============#
# STREAMLIT APP #
# ==============#

st.title("🔎 Analisis Data dari Server")
st.sidebar.header("🔧 Konfigurasi Server & Database")

# Form untuk memasukkan detail server dan database
if 'config_submitted' not in st.session_state:
    st.session_state.config_submitted = False

if not st.session_state.config_submitted:
    with st.sidebar.form(key='server_form'):
        # Input detail server Linux
        SSH_HOST = st.text_input("IP Server Linux")
        SSH_USER = st.text_input("User SSH")
        SSH_PASSWORD = st.text_input("Password SSH", type="password")

        # Input detail database
        DB_USER = st.text_input("User MySQL")
        DB_PASSWORD = st.text_input("Password MySQL", type="password")
        DB_NAME = st.text_input("Nama Database")

        # Submit button
        submit_button = st.form_submit_button(label='Konfigurasi Server & Database')

    if submit_button:
        # Menyimpan informasi yang dimasukkan ke dalam session state
        st.session_state.SSH_HOST = SSH_HOST
        st.session_state.SSH_USER = SSH_USER
        st.session_state.SSH_PASSWORD = SSH_PASSWORD
        st.session_state.DB_USER = DB_USER
        st.session_state.DB_PASSWORD = DB_PASSWORD
        st.session_state.DB_NAME = DB_NAME
        st.session_state.config_submitted = True
        st.sidebar.write("Pengaturan Server dan Database berhasil diupdate.")
else:
    # Koneksi ke server Linux untuk mendapatkan daftar tabel
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(st.session_state.SSH_HOST, username=st.session_state.SSH_USER, password=st.session_state.SSH_PASSWORD)

        # Menjalankan query untuk mendapatkan daftar tabel dari database yang dipilih
        command = f'mysql -u {st.session_state.DB_USER} -p{st.session_state.DB_PASSWORD} -D {st.session_state.DB_NAME} -e "SHOW TABLES;" --batch --raw'
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode()
        error_output = stderr.read().decode()

        client.close()

        if error_output:
            st.error(f"Error dari server: {error_output}")
        else:
            tables = output.splitlines()

            # Dropdown untuk memilih tabel
            selected_table = st.sidebar.selectbox("Pilih Tabel untuk dianalisis", tables)

            # Menyusun query dan menampilkan hasil
            query_option = f"SELECT * FROM {selected_table};"

            st.sidebar.write("Klik tombol di bawah untuk mengeksekusi query:")
            execute_query = st.sidebar.button("Jalankan Query")

            if execute_query:
                st.subheader("📊 Hasil Query")
                data = get_data_from_server(query_option, st.session_state.SSH_HOST, st.session_state.SSH_USER,
                                            st.session_state.SSH_PASSWORD, st.session_state.DB_USER,
                                            st.session_state.DB_PASSWORD, st.session_state.DB_NAME)

                if data is not None:
                    st.write(data)

                    # Jika dataset memiliki lebih dari 2 kolom, buat bar plot
                    if len(data.columns) >= 2:
                        st.subheader("📊 Diagram Batang (Bar Chart)")
                        
                        # Memastikan kolom pertama sebagai kategori dan kolom kedua sebagai nilai
                        category_column = data.columns[1]
                        value_column = data.columns[4]

                        # Menyusun diagram batang
                        fig, ax = plt.subplots(figsize=(10, 6))
                        sns.barplot(x=category_column, y=value_column, data=data, ax=ax)
                        
                        # Menampilkan diagram batang
                        st.pyplot(fig)

            # Button untuk mengakhiri session dan ganti database/tabel
            st.sidebar.write("Klik tombol di bawah untuk kembali ke konfigurasi:")
            reset_session = st.sidebar.button("Selesai & Ganti Konfigurasi")

            if reset_session:
                # Menghapus data session untuk berpindah konfigurasi
                st.session_state.config_submitted = False
                st.session_state.clear()
                st.rerun()


    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
