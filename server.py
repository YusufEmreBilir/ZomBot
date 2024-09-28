import subprocess
import threading
import os
from time import sleep
import socket
import re


server_loading = False
output_count = 0

os.system('cls')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((socket.gethostname(), 12345))  # Localhost ve port tanımlanıyor
server_socket.listen(5)

print("Sunucu başlatıldı, istemci bekleniyor...")

connection, address = server_socket.accept()
print(f"Bağlantı kabul edildi: {address}")
sleep(3)


start_server_path = 'C:\\SteamCMD\\steamapps\\common\\Project Zomboid Dedicated Server\\StartServer64.bat'
start_server_name = 'StartServer64.bat'
server_load_start_log = 'LoggerManager.init                  > Initializing...' #TBD
server_on_log = 'Zomboid Server is VAC Secure'
server_off_log = 'Shutting down Steam Game Server'
server_process = None

def start_server():
    global server_process, connection, address
    try:
        try:
            server_process = subprocess.Popen(
                [start_server_name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except FileNotFoundError:
            server_process = subprocess.Popen(
                [start_server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
    except FileNotFoundError:
        print('\033[91mHATA: Server bulunamadi\033[0m')
        exit()



# Sunucuya komut gönder
def send_command(command_to_send):
    server_process.stdin.write(command_to_send + '\n')
    # noinspection PyUnresolvedReferences
    server_process.stdin.flush()

# Sunucu loglarını ayrı bir thread'de sürekli olarak oku
def read_output():
    global connection, address, server_loading, output_count
    while True:
        output = server_process.stdout.readline()

        if output:

            if server_loading:
                output_count += 1
                connection.send(f'output_count ({output_count})'.encode())

            print(output.strip())  # Yeni gelen log satırını yazdır

            if 'Players connected' in output.strip():
                search_result = re.search(r"\((\d+)\)", output.strip())
                if search_result:
                    player_count = int(search_result.group(1))
                else:
                    player_count = '-404'
                connection.send(f'player_count_data {player_count}'.encode())


            elif server_load_start_log in output.strip():
                connection.send('loading'.encode())
                print('YUKLEME BASLADI')
                server_loading = True

            elif server_on_log in output.strip():
                sleep(1.5)
                connection.send('1'.encode())
                print(f'SERVER BASLADI {output_count}')
                server_loading = False
                output_count = 0

            elif server_off_log in output.strip():
                connection.send('0'.encode())
                print('SERVER KAPANDI')

        else:
            pass

def restart_server():
    close_server()
    start_server()


def close_server():
    send_command('quit')
    sleep(15)
    server_process.terminate() #güzellikten anlamıyor


start_server()
# Log okuma thread'i
log_thread = threading.Thread(target=read_output, daemon=True)
log_thread.start()

while True:
    sleep(1)
    # İstemciden gelen veriyi al
    data = connection.recv(1024).decode()
    command = data #Malca ama içimden düzeltmek gelmiyor.
    print(f"Discord uzerinden gelen veri: {data}")
    if command:
        if command == 'restart':
            restart_server()

        elif command == 'close_server':
            close_server()


        else:
            send_command(command)

        command = ''