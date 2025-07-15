import os
from time import sleep
import discord
from discord.ext import commands
import subprocess
import threading
import socket
import asyncio
import re
import configparser
from config import *
from token_config import token


os.system('cls')

direct_commands_allowed = True

server_is_open = 'Offline'
server_is_open_emoji = ':red_circle:'
player_count = 0
output_count = 0
server_status_sent = True
server_loading = False
loading_bar_message = ''
config = configparser.ConfigParser()

subprocess.Popen(['start', 'cmd', '/k', 'python', 'server.py'], shell=True)


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((socket.gethostname(), 12345))  # Sunucuya bağlanmak için IP ve port tanımlama
print('\033[32mSunucu ile baglanti kuruldu!\033[0m')



command = ''
discord_input = ''


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!pz ',
                   intents=intents)




@bot.event
async def on_ready():
    global server_status_sent, loading_bar_message
    channel = bot.get_channel(channel_ID)
    print(f'\033[32m*** Discord Botu Uyandi! *** \n{bot.user} adina giris yapildi\033[0m')
    await channel.send('***         Bot Uyandı!***')
    await channel.send(get_server_status())
    await bot.change_presence(activity=discord.CustomActivity(name=get_server_status_without_emoji()))

    while True:

        if server_loading:
            load_percent = output_count*100/server_on_output_count
            if not loading_bar_message:
                loading_bar_message = await channel.send(loading_bar(load_percent, 20) + ' %' + str(round(load_percent, 2)))
            else:
                await loading_bar_message.edit(content=loading_bar(load_percent, 20) + ' %' + str(round(load_percent, 2)))
        elif loading_bar_message != '':
            try:
                await loading_bar_message.delete()
            except:
                pass

        if not server_status_sent:
            await channel.send(get_server_status())
            await bot.change_presence(activity=discord.CustomActivity(name=get_server_status_without_emoji()))
            server_status_sent = True
            loading_bar_message = ''



        await asyncio.sleep(5)


def server_feedback():
    global server_is_open, player_count, server_status_sent, server_loading, output_count
    print('LOG-internal: Server ile iletisim basladi')
    while True:

        coming_code = client_socket.recv(1024).decode()


        if coming_code == '0':
            server_is_open = 'Offline'
            print('LOG-internal: Server kapanma onayi alindi!, Duyuruluyor...')
            server_status_sent = False
            server_loading = False

        elif coming_code == '1':
            server_is_open = 'Online'
            print('LOG-internal: Server acilma onayi alindi!')

            server_status_sent = False
            server_loading = False

        elif coming_code == 'loading':
            server_loading = True

        elif 'player_count_data' in coming_code:
            player_count = int(re.search(r"(\d+)", coming_code).group(1))

        elif 'output_count' in coming_code:
            search_result = re.search(r"\((\d+)\)", coming_code)
            if search_result:
                output_count = int(search_result.group(1))

        sleep(1)

def get_server_status_emoji():
    global server_is_open_emoji
    if 'Online' in server_is_open:
        server_is_open_emoji = ':green_circle:'
    else:
        server_is_open_emoji = ':red_circle:'
    return server_is_open_emoji

def get_server_status():
    return f'Server durumu: {get_server_status_emoji()}{server_is_open}'

def get_server_status_without_emoji():
    return f'Server durumu: {server_is_open}'

def update_player_count():
    client_socket.send('players'.encode())

def loading_bar(progress_percent, lenght = 20):
    completed = int(progress_percent * lenght / 100)
    bar = '[' + '/'*completed + '-'*(lenght - completed) + ']'
    return bar



@bot.event
async def on_message(message):
    global discord_input, server_is_open, direct_commands_allowed, config_path
    if message.author == bot.user:
        return

    # Komutun formatı '!komut string_deger'
    if message.content.startswith('!pz '):
        # Komuttan sonra gelen string değeri al
        user_input = message.content[len('!pz '):]  # Komuttan sonrasını yakala
        print(f'LOG-input: Kullanicidan gelen istek: {user_input}')

        discord_input = user_input.lower()

        if discord_input == 'durum' or discord_input == 'status':
            print('LOG-action: Server durumu gönderiliyor.')
            await message.channel.send(get_server_status())

        #elif 'Offline' in get_server_status():
         #   await message.channel.send(f'Server açık olmadığı için {discord_input} isteğiniz reddedildi.')
         #   print(f'LOG-action: Server acik olmadigi icin {discord_input} istegi reddedildi.')

        elif discord_input == 'oyuncular' or discord_input == 'players':
            update_player_count()
            await asyncio.sleep(1)
            await message.channel.send(f'Sunucuya bağlı oyuncu sayısı: {player_count}')
            print(f'LOG-action: Sunucuya bagli oldugu tespit edilen oyuncu sayisi: {player_count}, Gonderiliyor')

        elif discord_input == 'restart' or discord_input == 'reset' or discord_input == 'reboot':
            update_player_count()
            await asyncio.sleep(1)
            if player_count > 0:
                await message.channel.send(f'Şuan bağlı {player_count} oyuncu var.\nBağlı oyuncu olduğu sürece,'
                                           f'Admin izinleri olmadan, sunucuyu kapamak/yeniden başlatmak mümkün değil.')
                print('LOG-action: Yeniden baslatma reddedildi, bagli oyuncular var.')
            else:
                client_socket.send('restart'.encode())
                await message.channel.send('Sunucu yeniden başlatılıyor.\nBu işlem yaklaşık 2 dakika sürecek.')
                print('LOG-action: Kaydediliyor ve Yeniden baslatiliyor.')

        elif discord_input == 'quit' or discord_input == 'close' or discord_input == 'shutdown' or discord_input == 'kapat':
            update_player_count()
            await asyncio.sleep(1)
            if player_count > 0:
                await message.channel.send(f'Şuan bağlı {player_count} oyuncu var.\nBağlı oyuncu olduğu sürece,'
                                           f'Admin izinleri olmadan, sunucuyu kapamak/yeniden başlatmak mümkün değil.')
                print('LOG-action: Kapatma reddedildi, bagli oyuncular var.')
            else:
                client_socket.send('quit'.encode())
                await message.channel.send('Sunucu kaydediliyor ve kapatılıyor.')
                print('LOG-action: Sunucu kapatılıyor.')

        elif 'mod ekle' in discord_input or 'add mod' in discord_input:
            numbers = user_input.split()[1]
            wsid, modid = numbers.split(':')
            config.read(config_path)
            mods_id = config.get('Settings', 'Mods')
            workshop_id = config.get('Settings', 'WorkshopItems')
            mod_list = mods_value.split(';')
            mod_list.append(mods_id)
            workshop_list = mods_value.split(';')
            workshop_list.append(workshop_id)

            new_mods_value = ';'.join(mod_list)  # Listeyi tekrar string haline getir
            config.set('Settings', 'Mods', new_mods_value)

            new_workshop_value = ';'.join(workshop_list)  # Listeyi tekrar string haline getir
            config.set('Settings', 'WorkshopItems', new_workshop_value)

            with open(config_path, 'w') as configfile:
                config.write(configfile)



        elif direct_commands_allowed:
            client_socket.send(discord_input.encode())
            print(f'LOG-action: Direkt komutlar etkin, {discord_input} komutu direkt olarak sunucuya gonderildi.')
            await message.channel.send(f'Direkt komut girdiniz: {discord_input}')
        else:
            await message.channel.send('Geçersiz komut.')
            print('LOG-action: Gecersiz komut reddedildi.')

    discord_input = ''




threading.Thread(target = server_feedback, daemon = True).start()
bot.run(token)



