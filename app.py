import paramiko
import streamlit as st

# Fungsi untuk menghubungkan SSH
def ssh_connect(hostname, port, username, password):
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password, timeout=10)
        st.success(f"Koneksi SSH berhasil ke {hostname}!")
        return client
    except paramiko.AuthenticationException:
        st.error("Autentikasi gagal! Periksa username atau password.")
    except paramiko.SSHException as e:
        st.error(f"Kesalahan SSH: {e}")
    except Exception as e:
        st.error(f"Gagal terhubung: {e}")
    return None

# Fungsi untuk menjalankan perintah
def run_ssh_command(client, command):
    try:
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        return output, error
    except Exception as e:
        st.error(f"Kesalahan saat menjalankan perintah: {e}")
        return None, None

# Streamlit UI
st.title('SSH Command Executor')
st.write("Masukkan kredensial SSH untuk terhubung ke server remote")

# Input SSH Credentials
hostname = st.text_input("Hostname", "10.201.1.23")
port = st.number_input("Port", 1, 65535, 22)
username = st.text_input("Username")
password = st.text_input("Password", type="password")

# Koneksi dan Perintah SSH
if st.button("Connect"):
    if hostname and username and password:
        with st.spinner("Menghubungkan ke server..."):
            client = ssh_connect(hostname, port, username, password)

        if client:
            st.success("Koneksi berhasil!")
            command = st.text_input("Command", "ls")
            if st.button("Run Command"):
                with st.spinner("Menjalankan perintah..."):
                    output, error = run_ssh_command(client, command)
                if output:
                    st.write("### Output")
                    st.code(output)
                if error:
                    st.write("### Error")
                    st.code(error)
            # client.close()
    else:
        st.error("Semua kolom harus diisi!")
