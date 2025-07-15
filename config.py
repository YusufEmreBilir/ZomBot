
#ZomBot.py

server_on_output_count = 8420 #TBD, Zomboid server proccess'inin kaç satır inputtan sonra serveri açacağı (Yüzde hesabı yapmak için)

config_path = 'C:\\Users\\Yusuf Emre Bilir\\Zomboid\\Server\\servertest.ini' # Zomboid server config path'i
channel_ID = 1201982960333770822 #Discord botunun iletişim odası id'si





#server.py

start_server_path = 'C:\\steamcmd\\steamapps\\common\\Project Zomboid Dedicated Server\\StartServer64.bat' #Zomboid serveri executable yolu
start_server_name = 'StartServer64.bat' #Zomboid serveri executable ismi
server_load_start_log = 'LoggerManager.init                  > Initializing...' #TBD, Programın zomboid serverinin açılmaya başladığını anlamak için kullandığı log satırı
server_on_log = '*** SERVER STARTED ****' #Programın zomboid serverinin açıldığını anlamak için kullandığı log satırı
server_off_log = 'Shutting down Steam Game Server' #Programın zomboid serverinin kapandığını anlamak için kullandığı log satırı
loading_asset_log = 'LOADING ASSETS: START' #Programın zomboid serverinin Assetleri yüklemeye başladığını anlamak için kullandığı log satırı