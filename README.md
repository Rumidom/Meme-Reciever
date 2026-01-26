# Meme receiver
Receive memes from the internet like its 1979.
![meme receiver](https://github.com/Rumidom/Meme-Reciever/blob/main/images/2026-01-24%2023-43-15.png)

## How it works
This script will receive messages and gifs from a telegram bot and display them on a 1.3" tft SPI screen.
you'll need to change the variables on the config file to include your telegram bot token and wifi credentials.
Once powered it will load the last message sent to the Telegram bot, only static 240x240 GIFs will be displayed.

## Wiring 
This script was written for the ESP32 C3 Super Mini board but should really work best on the ESP32 S3 Zero as it is faster
and has more ram (I havent tested it yet) 
![Wiring](https://github.com/Rumidom/Meme-Reciever/blob/main/images/2026-01-24%2023-43-15.png)

## Install the script
using [thonny](https://thonny.org/) or other micropython IDE upload the contents of the lib folder main.py and your
config.txt

## 3D printing files
[ESP32 Mini Computer](Cults 3d Link)

