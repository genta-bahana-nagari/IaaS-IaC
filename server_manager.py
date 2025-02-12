import paramiko
import streamlit as st
import os

# Fungsi untuk melakukan koneksi SSH
def ssh_connect(host, username, private_key_path):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, key_filename=private_key_path)
        return ssh
    except Exception as e:
        st.error(f"Error connecting to server: {e}")
        return None

# Fungsi untuk menjalankan perintah di server
def run_command(ssh, command):
    try:
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read().decode()
        error = stderr.read().decode()
        return error if error else result
    except Exception as e:
        return f"Error running command: {e}"

# Fungsi untuk upload file ke server
def upload_file(ssh, local_file_path, remote_file_path):
    try:
        sftp = ssh.open_sftp()
        sftp.put(local_file_path, remote_file_path)
        sftp.close()
        return f"File uploaded successfully to {remote_file_path}"
    except Exception as e:
        return f"Error uploading file: {e}"

# Fungsi untuk download file dari server
def download_file(ssh, remote_file_path, local_file_path):
    try:
        # Pastikan direktori tujuan ada
        local_dir = os.path.dirname(local_file_path)
        if local_dir and not os.path.exists(local_dir):
            os.makedirs(local_dir)  # Buat direktori jika belum ada
        
        sftp = ssh.open_sftp()
        sftp.get(remote_file_path, local_file_path)
        sftp.close()
        return f"File downloaded successfully to {local_file_path}"
    except Exception as e:
        return f"Error downloading file: {e}"

# Streamlit UI
st.title("Manajer Server Jarak Jauh")

# Input untuk koneksi SSH
host = st.text_input("Server Host (IP Address)", "")
username = st.text_input("Username", "")
private_key_path = st.text_input("Private Key Path", "~/.ssh/my_ssh_key")

# Gunakan session state agar koneksi tetap aktif
if "ssh" not in st.session_state:
    st.session_state.ssh = None

if st.button("Connect to Server"):
    st.session_state.ssh = ssh_connect(host, username, private_key_path)
    if st.session_state.ssh:
        st.success(f"Connected to {host}")

# Jika sudah terkoneksi, tampilkan fitur tambahan
if st.session_state.ssh:
    st.subheader("Command Execution")
    command = st.text_area("Enter command to run on server", "")
    if st.button("Run Command"):
        result = run_command(st.session_state.ssh, command)
        st.text_area("Command Output", result, height=300)

    st.subheader("Upload File to Server")
    uploaded_file = st.file_uploader("Choose a file to upload")
    remote_upload_path = st.text_input("Enter target upload directory", "/home/genta/")
    if uploaded_file and remote_upload_path:
        local_path = os.path.join("temp", uploaded_file.name)
        os.makedirs("temp", exist_ok=True)  # Pastikan folder 'temp' ada
        with open(local_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        if st.button("Upload File"):
            result = upload_file(st.session_state.ssh, local_path, os.path.join(remote_upload_path, uploaded_file.name))
            st.success(result)

    st.subheader("Download File from Server")
    remote_file_path = st.text_input("Enter remote file path", "/home/genta/sample.txt")
    local_download_path = st.text_input("Enter local save path", "Downloads\example.txt")
    if st.button("Download File"):
        result = download_file(st.session_state.ssh, remote_file_path, local_download_path)
        st.success(result)

    if st.button("Disconnect"):
        st.session_state.ssh.close()
        st.session_state.ssh = None
        st.success("Disconnected from server")
