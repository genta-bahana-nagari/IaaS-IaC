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
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD)

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

        df = pd.read_csv(io.StringIO(output), sep="\t", on_bad_lines='skip')
        return df
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        return None

# =======================#
# LANDING PAGE SEBELUM LOGIN #
# =======================#

def landing_page():
    st.title("📊 Dashboard Database Analyzer")
    st.markdown(
        """
        Selamat datang di aplikasi analisis database berbasis Streamlit!
        
        **Fitur utama:**
        - Menghubungkan ke server MySQL melalui SSH
        - Mengeksekusi query SQL secara real-time
        - Menampilkan hasil dalam bentuk tabel dan grafik
        
        Klik tombol di bawah untuk mulai konfigurasi server.
        """
    )
    
    if st.button("🔧 Mulai Konfigurasi Server"):
        st.session_state.show_login = True
        st.rerun()

# =======================#
# FORM KONFIGURASI SERVER #
# =======================#

def server_config_page():
    st.sidebar.header("🔧 Konfigurasi Server & Database")
    
    if 'config_submitted' not in st.session_state:
        st.session_state.config_submitted = False

    if not st.session_state.config_submitted:
        with st.sidebar.form(key='server_form'):
            SSH_HOST = st.text_input("IP Server Linux")
            SSH_USER = st.text_input("User SSH")
            SSH_PASSWORD = st.text_input("Password SSH", type="password")

            DB_USER = st.text_input("User MySQL")
            DB_PASSWORD = st.text_input("Password MySQL", type="password")
            DB_NAME = st.text_input("Nama Database")

            submit_button = st.form_submit_button(label='Konfigurasi Server & Database')

        if submit_button:
            st.session_state.SSH_HOST = SSH_HOST
            st.session_state.SSH_USER = SSH_USER
            st.session_state.SSH_PASSWORD = SSH_PASSWORD
            st.session_state.DB_USER = DB_USER
            st.session_state.DB_PASSWORD = DB_PASSWORD
            st.session_state.DB_NAME = DB_NAME
            st.session_state.config_submitted = True
            st.sidebar.write("Pengaturan Server dan Database berhasil diupdate.")
            st.rerun()
    else:
        data_analysis_page()

# =================#
# HALAMAN ANALISIS DATA #
# =================#\

def data_analysis_page():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(st.session_state.SSH_HOST, username=st.session_state.SSH_USER, password=st.session_state.SSH_PASSWORD)

        command = f'mysql -u {st.session_state.DB_USER} -p{st.session_state.DB_PASSWORD} -D {st.session_state.DB_NAME} -e "SHOW TABLES;" --batch --raw'
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode()
        error_output = stderr.read().decode()

        client.close()

        if error_output:
            st.error(f"Error dari server: {error_output}")
        else:
            tables = output.splitlines()
            selected_table = st.sidebar.selectbox("Pilih Tabel untuk dianalisis", tables)
            query_option = f"SELECT * FROM {selected_table};"

            if st.sidebar.button("Jalankan Query"):
                st.subheader("📊 Hasil Query")
                data = get_data_from_server(query_option, st.session_state.SSH_HOST, st.session_state.SSH_USER,
                                            st.session_state.SSH_PASSWORD, st.session_state.DB_USER,
                                            st.session_state.DB_PASSWORD, st.session_state.DB_NAME)
                if data is not None:
                    st.write(data)
                    
                    # Pastikan ada kolom 'stok' dan 'title' dalam tabel
                    if "stok" in data.columns and "title" in data.columns:
                        st.subheader("📊 Analisis Stok (Bar Chart)")

                        # Plot diagram batang berdasarkan 'title' sebagai kategori
                        fig, ax = plt.subplots(figsize=(10, 6))
                        sns.barplot(x="title", y="stok", data=data, ax=ax)
                        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")  # Rotasi agar tidak tumpang tindih
                        st.pyplot(fig)
                    else:
                        st.info("Kolom 'stok' atau 'title' tidak ditemukan dalam tabel ini. Tidak ada diagram batang yang ditampilkan.")

            if st.sidebar.button("Selesai & Keluar"):
                st.session_state.config_submitted = False
                st.session_state.clear()
                st.rerun()
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

# ================#
# NAVIGASI APLIKASI #
# ================#

if 'show_login' not in st.session_state:
    st.session_state.show_login = False

if not st.session_state.show_login:
    landing_page()
else:
    server_config_page()
