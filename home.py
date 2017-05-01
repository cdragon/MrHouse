#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rio de Janeiro, Brazil
February 23, 2017
author: Elias Gonçalves
email: falarcomelias@gmail.com
"""

import time
import random
import datetime
import telepot
import sqlite3
import sys
import os
import logging
from subprocess import check_output
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(7, GPIO.OUT)
GPIO.output(7, GPIO.HIGH)


class MrHouse(telepot.Bot):

    def __init__(self, access_token):
        telepot.Bot.__init__(self, access_token)
        self.helpme = {
            'ajuda': 'Mostra os comandos disponiveis.',
            'velox': 'Velocidade atual de download e upload da rede.',
            'status': 'retorna o status do bot.',
            'foto': 'tira uma foto e envia.',
            'video': 'grava 10 segundos de vídeo e envia.',
            'temp': 'Temperatura e umidade no interior da casa.',
            'venton': 'Liga o ventilador.',
            'ventoff': 'Desliga o ventilador.',
            'ledon': 'Liga o led.',
            'ledoff': 'Desliga o led.',
            'cozinhaon': 'Liga a luz da cozinha.',
            'cozinhaoff': 'Desliga a luz da cozinha.',
            'salaon': 'Liga a luz da sala.',
            'salaoff': 'Desliga a luz da sala.',
            'quartoon': 'Liga a luz do quarto.',
            'quartooff': 'Desliga a luz d o quarto.',
            'musicaon': 'Comeca a tocar musica',
            'musicaoff': 'Para de tocar musica.',
            'alarmeon': 'Ativa os alarmes programados.',
            'alarmeoff': 'Desativa os alarmes programados.',
        }
        # Set some camera options if needed
        # self.camera.vflip = True
        # self.camera.hflip = True

    def update(self, sql):
        connect = sqlite3.connect('mrhouse_auth.db')
        c = connect.cursor()
        c.execute(sql)
        connect.commit()
        c.close


    def read(self, sql):
        connect = sqlite3.connect('mrhouse_auth.db')
        c = connect.cursor()
        c.execute(sql)
        query = c.fetchall()
        c.close
        return query


    def handle(self, msg):
        row = self.read('SELECT * FROM status WHERE id=1')
        listening_since = row[0][1]
        request_count = int(row[0][2])
        invalid_users_count = int(row[0][3])
        command = msg['text']
        chat_id = msg['chat']['id']
        user_id = msg['from']['id']
        name = msg['chat']['first_name']
        username = msg['chat']['username']

        # Logging
        logging.info("Recebido o comando %s do user_id: %s, nome: %s (%s)" % (command, chat_id, name, username))

        # Update request number
        self.update('UPDATE status SET request_count = ' + str(int(request_count+1)) + ' WHERE id = 1')

        # Load permited users
        valid_ids = []
        for row in self.read('SELECT id FROM user_id_permitidos'):
            valid_ids.append(str(row[0]))

        # User not passed
        if not str(user_id) in valid_ids:
            logging.warning("Falha ao autenticar o user_id: %s" % user_id)
            self.sendMessage(chat_id, "Desculpe, sou um bot privado. Eu nao posso falar com voce.")

            # Update number of denied access
            self.update('UPDATE status SET invalid_users_count = ' + str(int(invalid_users_count+1)) + ' WHERE id = 1')

        # User is acept to send/request command
        else:
            if command == '/start':
               self.sendMessage(chat_id, 'Bem-vindo, %s\n%s' % (name, datetime.datetime.now().strftime("%d/%m/%Y - %H:%M")))
               logging.info("Boas vindas para %s (username: %s )" % (chat_id, username))

            elif command == '/ajuda':
                action = "Os seguintes comandos estao disponiveis:\n"
                for key in self.helpme:
                    action += "/" + key + ": " + self.helpme[key] + "\n"
                self.sendMessage(chat_id, action)

            elif command == '/velox':
                action = check_output("speedtest-cli --share > velox.txt && sed -n '10p' velox.txt | cut -d: -f3,2", shell=True)
                self.sendPhoto(chat_id, action.strip())
                logging.info("Enviando velocidade de download e upload para %s (username: %s )" % (chat_id, username))
                try:
                    os.remove("velox.txt")
                except OSError:
                    pass

            elif command == '/status':
                row = self.read('SELECT * FROM status WHERE id=1')
                action = 'Ligado desde: ' + datetime.datetime.fromtimestamp(int(row[0][1])).strftime('%d-%m-%Y %H:%M:%S') + '\n'
                action += 'Total de request: ' + str(row[0][2]) + '\n'
                action += 'Total acessos negados: ' + str(row[0][3])
                self.sendMessage(chat_id, action)
                logging.info("Enviando o estado atual do Mr. House para %s (username: %s )" % (chat_id, username))

            elif command == '/foto':
                action = "Em desenvolvimento."
                """
                self.camera.resolution = (1920, 1080)
                self.camera.capture('image.jpg')
                action = open('image.jpg', 'rb')
                self.sendPhoto(chat_id, action)
                """
                logging.info("Enviando foto atual da raspicam para %s (username: %s )" % (chat_id, username))
                self.sendMessage(chat_id, action)

            elif command == '/video':
                action = "Em desenvolvimento."
                """
                try:
                    os.remove('video.h264')
                except OSError:
                    pass
                try:
                    os.remove('video.mp4')
                except OSError:
                    pass
                self.camera.resolution = (1280, 720)
                self.camera.start_recording('video.h264')
                self.camera.wait_recording(10)
                self.camera.stop_recording()
                cmd = ['MP4Box', '-add', 'video.h264', 'video.mp4']
                try:
                    check_call(cmd)
                    action = open('video.mp4', 'rb')
                    self.sendVideo(chat_id, action)
                    logging.info("Enviando video atual da raspicam para %s (username: %s )" % (chat_id, username))
                except CalledProcessError:
                    logging.info("Ocorreu um problema com o encoder do video!")
                    self.sendMessage(chat_id, 'Lamento, mas ocorreu um problema!')
                """
                logging.info("Enviando video atual da raspicam para %s (username: %s )" % (chat_id, username))
                self.sendMessage(chat_id, action)

            elif command == '/quartoon':
                GPIO.output(7, GPIO.LOW)
                logging.info("Lampada do quarto acesa por %s (username: %s )" % (chat_id, username))

            elif command == '/quartooff':
                GPIO.output(7, GPIO.HIGH)
                logging.info("Lampada do quarto apagada por %s (username: %s )" % (chat_id, username))

            else:
                self.sendMessage(chat_id, "Desculpe, o comando %s ainda nao foi implementado." % msg['text'])


# Application setup
TOKEN = sys.argv[1]

# Logging format
logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', filename='logs/mrhome_bot.log', level=logging.INFO)

# Initialize the bot
bot = MrHouse(TOKEN)
bot.setWebhook()
bot.message_loop(bot.handle)
logging.info("Listening...")

# Main loop catching Keyboard Interrupts: If one is detected it shuts down the bot and cleans up the produces files except for the log file
while 1:
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        try:
            os.remove("image.jpg")
        except OSError:
            pass
        try:
            os.remove("video.h264")
        except OSError:
            pass
        try:
            os.remove("video.mp4")
        except OSError:
            pass
        logging.info("KeyboardInterrupt detectado, desligando o Mr. House!")
        sys.exit("\nDesligando o Telegram Bot!")
