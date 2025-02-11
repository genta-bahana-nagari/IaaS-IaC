import streamlit as st
import paramiko

# Fungsi untuk menghubungkan SSH dan menjalankan perintah
def ssh_connect(hostname, port, username, password):
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password)
        return client
    except Exception as e:
        return str(e)

# Streamlit UI
st.title('SSH Command Executor')
st.write("Masukkan kredensial SSH untuk terhubung ke server remote")

hostname = st.text_input("Hostname", "192.168.1.1")
port = st.number_input("Port", 1, 65535, 22)
username = st.text_input("Username")
password = st.text_input("Password", type="password")
command = st.text_input("Command", "ls")  # Menambahkan input untuk command

# Koneksi dan perintah SSH
if st.button("Jalankan"):
    if hostname and username and password and command:
        st.write("Menghubungkan...")
        client = ssh_connect(hostname, port, username, password)

        if isinstance(client, str):  # Jika ada error di koneksi
            st.error(client)
        else:
            st.success("Koneksi berhasil! Menjalankan perintah...")

            # Kontainer untuk streaming output secara real-time
            output_container = st.empty()

            # Jalankan perintah SSH
            stdin, stdout, stderr = client.exec_command(command, get_pty=True)
            while True:
                # Baca output baris demi baris secara real-time
                output_line = stdout.readline()
                if output_line == '' and stdout.channel.exit_status_ready():
                    break
                if output_line:
                    output_container.write(output_line.strip())  # Stream output real-time

            # Ambil error terakhir jika ada
            error = stderr.read().decode()
            if error:
                output_container.error(f"### Error:\n{error}")

            client.close()
    else:
        st.error("Semua kolom harus diisi!")
