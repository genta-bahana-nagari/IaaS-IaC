import socket

# Membuat socket TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind ke IP dan port tertentu
server_socket.bind(('localhost', 12345))

# Mendengarkan koneksi masuk
server_socket.listen(5)
print("Server menunggu koneksi...")

# Menerima koneksi
client_socket, client_address = server_socket.accept()
print(f"Koneksi diterima dari {client_address}")

# Menerima data dari client
data = client_socket.recv(1024)
print(f"Pesan dari client: {data.decode()}")

# Mengirim respons ke client
client_socket.send("Terima kasih telah terhubung!".encode())

# Menutup koneksi
client_socket.close()
server_socket.close()