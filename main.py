import time
import st7789 as st7789
import fontlib
from machine import Pin, SPI
import framebuf
from random import random, seed, randint
from ugif import gif
import network
import fontlib
import urequests
import os
import sys

# set landscape screen
screen_width = 240
screen_height = 240
screen_rotation = 3
textH = 8
textW = 240

spi = SPI(1,
          baudrate=31250000,
          polarity=1,
          phase=1,
          bits=8,
          firstbit=SPI.MSB,
          sck=Pin(4),
          mosi=Pin(5))

display = st7789.ST7789(
    spi,
    screen_width,
    screen_height,
    reset=Pin(9, Pin.OUT),
    #cs=Pin(9, Pin.OUT),
    dc=Pin(8, Pin.OUT),
    backlight=Pin(7, Pin.OUT),
    rotation=screen_rotation)

wlan = network.WLAN(network.STA_IF)
white = st7789.color565(255, 255, 255)

def PrintToScreen(text,x,y):
    textW = screen_width
    textH = 8
    IBM_font = fontlib.font("IBM BIOS (8,8).bmp") # Loads font to ram
    textBuffer = bytearray(screen_width * textH * 2)
    textfbuf = framebuf.FrameBuffer(textBuffer, textW, textH, framebuf.RGB565)
    fontlib.prt(text,0,0,1,textfbuf,IBM_font,color=white)
    display.blit_buffer(textBuffer, x, y, textW, textH)
    textBuffer = bytearray()
    gc.collect()
    
def ConnectToSSID(SSID,password=''):
    wlan.active(True)
    wlan.disconnect()
    wlan.connect(SSID, password)
    # Wait for connection.
    timeout = 0
    display.fill(0)
    while not wlan.isconnected():
        PrintToScreen(wifi_ssid,0,0)
        PrintToScreen('Connecting'+'.'*timeout,0,10)
        timeout += 1
        if timeout == 10:
            break
        time.sleep(1)
    if wlan.isconnected():
        display.fill(0)
        PrintToScreen('Connected!',0,0)
        PrintToScreen(str(wlan.ifconfig()[0]),0,10)
        time.sleep(4)
        return(True)
    else:
        display.fill(0)
        PrintToScreen("Connection Failed.",0,0)
        time.sleep(4)
        return(False)

#Load config file
wifi_ssid = ''
wifi_password = ''
telegram_token = ''

def getConfig():
    with open("config.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            splt = line.split('=')
            if splt[0] == 'SSID':
                wifi_ssid = splt[1].strip()
            elif splt[0] == 'PASS':
                wifi_password = splt[1].strip()
            elif splt[0] == 'TOKEN':
                telegram_token = splt[1].strip()
    return (wifi_ssid,wifi_password,telegram_token)    
    
def drawToScreen(x,y,color):
    #global gif_buffer
    #buffer_width = 240
    #buffer_height = 1
    #gif_buffer = bytearray()
    #gif_buffer.extend(color.to_bytes(2,'big'))
    #print(x,y,color)
    #if x == buffer_width-1 and y%buffer_height == 0 and y!=0:
        #display.blit_buffer(gif_buffer, 0, y, buffer_width, buffer_height)
        #gif_buffer = bytearray()
    display.pixel(x,y,color)

def sendTelegram(token,chat_id,Message):
    data = {"chat_id": chat_id,"text": Message}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    url = 'https://api.telegram.org/bot'+token+'/sendMessage'
    
    try:
        resp = urequests.post(url, json=data,headers=headers)
        resp.close()
        return True
    except Exception as e:
        sys.print_exception(e, sys.stdout)
        return None

def readTelegram(token):
    query_updates = {
    'offset': -1,
    'limit': 1,
    'timeout': 30,
    'allowed_updates': ['message']}
    
    url = 'https://api.telegram.org/bot'+token
    result = []
    try:
        update_messages = urequests.post(url + '/getUpdates', json=query_updates).json() 
        if 'result' in update_messages:
            for item in update_messages['result']:
                result.append(item)
        return result
    except (ValueError):
        return None
    except (OSError):
        print("OSError: request timed out")
        return None

def downloadFromID(token,FileId):
    url = 'https://api.telegram.org/bot'+token
    url = url+'/getFile?file_id='+FileId

    # Fetch data from a URL
    PrintToScreen('Fetching filepath',0,10)
    resp = urequests.get(url)
    if resp.status_code == 200:
        if resp.json()['ok']:
            result = resp.json()['result']
            file_path = result['file_path']
            filename = file_path.split('/')[-1]
            resp.close()
            url = 'https://api.telegram.org/file/bot'+token
            url = url+'/'+file_path
            PrintToScreen('Downloading Meme',0,20)
            #print('Downloading Meme')
            resp = urequests.get(url)
            #print(url)
            #print(resp.json())
            f = open(filename, "wb")
            f.write(resp.content)
            f.close()
            resp.close()
            gc.collect()
            return filename
        
def checkForNewMessages(token,checking_Delay = 5):
    lastMSG_id = 0
    #micropython.mem_info()
    display.fill(0)
    while True:
        if lastMSG_id == 0:
            PrintToScreen('Waiting For Messages',0,0)
        try:
            lastMSG = readTelegram(token)
            if lastMSG != None:
                MSG_id = lastMSG[0]['message']['message_id']
                chat_id = lastMSG[0]['message']['from']['id']
                if MSG_id != lastMSG_id:
                    if lastMSG_id != 0:
                        if 'text' in lastMSG[0]['message']:
                            display.fill(0)
                            PrintToScreen('New Message!',0,0)
                            firstName = lastMSG[0]['message']['chat']['first_name']
                            message = lastMSG[0]['message']['text']
                            line = 0
                            message_piece = firstName+': '
                            for char in message:
                                message_piece += char
                                if len(message_piece)%25 == 0:
                                    PrintToScreen(message_piece,0,20+line*10)
                                    line = line+1
                                    message_piece = ''
                            PrintToScreen(message_piece,0,20+line*10)
                            sendTelegram(token,chat_id,'Message Recieved')

                        if 'document' in lastMSG[0]['message']:
                            display.fill(0)
                            PrintToScreen('New Meme Arrived!',0,10)
                            deletePreviusMemes()
                            gc.collect()
                            fileid = lastMSG[0]['message']['document']['file_id']
                            file_name = downloadFromID(token,fileid)
                            gif_obj = None
                            gif_obj = gif(file_name)
                            display.fill(0)
                            sendTelegram(token,chat_id,'Meme Recieved')
                            gif_obj.BlitToScreen(0,drawToScreen)
                            
                    lastMSG_id = MSG_id
        except Exception as e:
            print("Error Downloading Message")
            sys.print_exception(e, sys.stdout)
        time.sleep(checking_Delay)
        
def deletePreviusMemes():
    files = os.listdir()
    for file in files:
        if file.split('.')[-1] == 'gif':
            print('deleting ',file)
            os.remove(file)

wifi_ssid,wifi_password,telegram_token = getConfig()
ConnectToSSID(wifi_ssid,password=wifi_password)
checkForNewMessages(telegram_token)