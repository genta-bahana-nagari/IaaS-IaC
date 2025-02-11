import paramiko

# Fungsi untuk menghubungkan ke server menggunakan SSH
def ssh_connect(hostname, username, password):
    try:
        # Membuat objek SSHClient
        client = paramiko.SSHClient()

        # Memuat kunci host yang ada
        client.load_system_host_keys()

        # Menambahkan kunci host jika server belum terdaftar
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Membuka koneksi ke server
        client.connect(hostname, username=username, password=password)
        print(f"Koneksi SSH berhasil ke {hostname}!")

        return client
    except Exception as e:
        print(f"Gagal terhubung: {e}")
        return None

# Fungsi untuk menjalankan perintah di server remote
def run_ssh_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    
    # Membaca hasil dari perintah
    output = stdout.read().decode()
    error = stderr.read().decode()
    
    if output:
        print("Output:")
        print(output)
    if error:
        print("Error:")
        print(error)

# Ganti dengan username dan hostname sesuai kebutuhan
hostname = "10.201.1.23"  # Alamat IP atau nama domain server
username = "root"         # Nama pengguna SSH
password = "111"  # Kata sandi untuk autentikasi

# Melakukan koneksi SSH
client = ssh_connect(hostname, username, password)

if client:
    # Menjalankan perintah di server remote, misalnya perintah 'ls'
    command = "ls"
    run_ssh_command(client, command)

    # Menutup koneksi setelah selesai
    client.close()
