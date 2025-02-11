import paramiko

def ssh_connect(hostname, port, username, password):
    try:
        # Membuat objek SSHClient
        client = paramiko.SSHClient()

        # Memuat kunci-kunci yang ada
        client.load_system_host_keys()

        # Menambahkan kunci jika server belum terdaftar
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Membuka koneksi ke server
        client.connect(hostname, port=port, username=username, password=password)
        print("Koneksi SSH berhasil!")
        return client
    except Exception as e:
        print(f"Gagal terhubung: {e}")
        return None
