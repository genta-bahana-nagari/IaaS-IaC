import streamlit as st
import paramiko
from streamlit_option_menu import option_menu


#Navigasi side bar menu
with st.sidebar :
        selected = option_menu ('Konfigurasi Mikrotik',
        ['Setting Koneksi', 'Konfigurasi Gateway', 
         'Konfigurasi Wireless', 'Setting IP Ethernet dan DHCP Server'],
        default_index=0)


#Halaman Koneksi ke Mikrotik
if (selected=='Setting Koneksi') :
        st.subheader('Masukkan IP, Username, Password dan Port')
        IP = st.text_input("Masukkan IP Address Mikrotik","192.168.88.1")
        user = st.text_input("Masukkan Username","admin")
        passwd = st.text_input("Masukkan Password", type="password")
        port = st.text_input("Masukkan Port", 22)
        connect = st.button("Connect")
        if connect :
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try :
                    client.connect(IP, username= user, password= passwd, port= port)
                    st.success(f'SSH Berhasil Terkoneksi ke = {IP}', icon="✅")
                    #st.success(f'SSH Berhasil Terkoneksi ke = {IP}', icon=":material/thumb_up:")
                    st.session_state.connect = True
                  
                    
                    if 'IP' not in st.session_state:
                        st.session_state.IP = IP
                        #st.write(st.session_state.IP)
                        
                    if 'passwd' not in st.session_state:
                        st.session_state.passwd = passwd
                        #st.write(st.session_state.passwd)

                    if 'port' not in st.session_state:
                        st.session_state.port = port
                        #st.write(st.session_state.port)

                    if 'user' not in st.session_state:
                        st.session_state.user = user
                        #st.write(st.session_state.user)

                    if 'terkoneksi' in st.session_state:
                        st.session_state.terkoneksi = False
                        #st.write(st.session_state.user)
                   
                except Exception:
                       st.warning('GAGAL TERKONEKSI', icon="⚠️")
                       st.session_state.connect = False
       
                       

if (selected=='Konfigurasi Wireless') :
        if 'connect' not in st.session_state:
                st.session_state.connect = False
        st.subheader('Konfigurasi Gateway dan Wireless')
        #gateway = st.text_input("Masukkan IP Address Gateway")
        ssid = st.text_input("Masukkan SSID Wireless", disabled=not st.session_state.connect)
        auth = st.text_input("Masukkan Password Wireless", disabled=not st.session_state.connect)
        #st.write(st.session_state.connect)
        connect = st.button("Proses", disabled=not st.session_state.connect)
        #st.write(is_konek)
        if connect :
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                port = st.session_state.port
                client.connect(st.session_state.IP, username= st.session_state.user, password= st.session_state.passwd, port= port)
                #stdin, stdout, stderr = client.exec_command('system identity set name=HOME2')
                #stdin, stdout, stderr = client.exec_command('interface wireless security-profiles add name=passwd_wifi  wpa2-pre-shared-key=12345678 wpa-pre-shared-key=12345678 mode=dynamic-keys group-ciphers=aes-ccm unicast-ciphers=aes-ccm authentication-types=wpa2-psk,wpa-psk')
                stdin, stdout, stderr = client.exec_command('/interface wireless security-profiles remove passwd_wifi')
                client.exec_command(f'/interface wireless security-profiles add name=passwd_wifi  wpa2-pre-shared-key={auth} wpa-pre-shared-key={auth} mode=dynamic-keys group-ciphers=aes-ccm unicast-ciphers=aes-ccm authentication-types=wpa2-psk,wpa-psk')
                client.exec_command(f'/interface wireless set wlan2 ssid={ssid} mode=ap-bridge security-profile=passwd_wifi channel-width=20mhz')
                

if (selected=='Setting IP Ethernet dan DHCP Server') :
        if 'connect' not in st.session_state:
                st.session_state.connect = False

        st.subheader('Konfigurasi IP Address dan DHCP Server')
        option = st.selectbox("Interface manakah yang akan dikonfigurasi IP Address dan DHCP Server ?",("Ether2", "ether3", "ether4", "ether5"),disabled= not st.session_state.connect)
        #interface = st.text_input("Masukkan Nama Intreface")
        ipLAN = st.text_input("Masukkan IP Address", disabled=not st.session_state.connect)
        
        connect = st.button("Proses", disabled= not st.session_state.connect)
        if connect :
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                IP = st.session_state.IP
                user = st.session_state.user
                passwd = st.session_state.passwd
                port = st.session_state.port
                client.connect(IP, username= user, password= passwd, port= port)
                #st.write(st.session_state.passwd)
                #st.write(st.session_state.IP)
                #st.write(port)

if (selected=='Konfigurasi Gateway') :
        if 'connect' not in st.session_state:
                st.session_state.connect = False        
        
        st.subheader('Konfigurasi IP Address Gateway')

        genre = st.radio(
        "Konfigurasi Gateway yang Anda Pilih :",
        ["Konfigurasi Otomatis", "Konfigurasi Manual"],
        captions=[
        "Akan dikonfigurasi otomatis, tidak perlu memasukkan IP Address.",
        "Konfigurasi Manual dengan memasukkan IP Address dan IP Address gateway",
        ], disabled= not st.session_state.connect )

        if genre == "Konfigurasi Otomatis":
                st.write("You selected OTOMATIS")
        else:
                st.write("MANUAL")
        
       