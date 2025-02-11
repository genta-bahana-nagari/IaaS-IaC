import socket

# Membuat socket TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Menghubungkan ke server
client_socket.connect(('localhost', 12345))

# Mengirim pesan ke server
client_socket.send("Halo, server!".encode())

# Menerima respons dari server
data = client_socket.recv(1024)
print(f"Pesan dari server: {data.decode()}")

# Menutup koneksi
client_socket.close()
