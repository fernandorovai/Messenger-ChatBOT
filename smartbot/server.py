"""
 This script is responsible for creating a flask web-server application
 to communicate to a Facebook Messenger chat bot
 Author: Fernando Rodrigues Jr
 Date  : 16/01/2018

"""
# coding=utf-8
# Developed and tested with:
#
# os:             Ubuntu Xenial (16.04)
# python version: Python 3.5

# Notes:
# The code was created using a virtualenv, please run pip install -r pip.txt
# To run the code: python server.py

from flask import Flask             # Web-server
from flask_restful import request   # Restful features
from data import Data               # Data to populate bot
from keywords import Keywords       # Set of keywords according to the question / answer
import requests                     # Lib to send post/get requests
import time                         # Adding a delay
import random                       # pick random phases from a list
import nltk                         # NLP lib to tokenize phrases
nltk.download('punkt')
from nltk import tokenize


app = Flask(__name__)
app.debug = True                   # set debug to true to auto-reload

# Consider adding ssl credentials here
context = ('/etc/letsencrypt/live/www.frodriguesjr.science/fullchain.pem',
           '/etc/letsencrypt/live/www.frodriguesjr.science/privkey.pem')
VERIFY_TOKEN = "pe:/4H>}]245kph"
PAGE_ACCESS_TOKEN = "EAAOTV8ZBzN5EBAEGGkXKbgl7uCzrgPlZCo2fGSHZBbTnVdixE8oxl3ROtVfZB5wT0nOZCxVz2APPpnxZAMDy48vnPFDKd0gsu41pPSuVtlLvYZASZBDZAMnCfNo5YvCpaZC6RPVDmZCTHIYm3gKCDP8vPmQwfukTJD3QVSQQDLoGQKeMwZDZD"

# Instantiate data object
# In real situations, load data from API / database
dataObj = Data()
luminaria_embutir = dataObj.luminaria_embutir
controladores     = dataObj.controladores
eletrofita        = dataObj.eletrofita
fita_led          = dataObj.fita_led
lampada_led       = dataObj.lampada_led
luminaria_led     = dataObj.luminaria_led
lustres           = dataObj.lustres

# Instantiate keywords
keywords = Keywords()

@app.route('/webhook', methods=['GET', 'POST'])
def index():

    # Verify webhook
    if request.method == 'GET':
        mode      = request.values['hub.mode']
        token     = request.values['hub.verify_token']
        challenge = request.values['hub.challenge']

        if mode is not None and token is not None:
            if mode == 'subscribe' and token == VERIFY_TOKEN:
                print("WEBHOOK_VERIFIED")
                return challenge, 200
        return "Forbidden, 403"

    # handle post data
    elif request.method == 'POST':
        jsonData = request.get_json()

        # check if the information came from a page
        if jsonData['object'] == 'page':
            for entry in jsonData['entry']:
                if 'messaging' in entry:
                    messaging     = entry['messaging'][0]
                    senderPSID    = messaging['sender']['id']
                    recipientPSID = messaging['recipient']['id']

                    #Checking whether the data is a message or postback
                    if 'message' in messaging:
                        handleMessage(senderPSID, recipientPSID, messaging['message'])
                    elif 'postback' in messaging:
                        handlePostback(senderPSID, recipientPSID, messaging['postback'])
                return "Ok", 200
        else:
            return "Access Forbidden, 403"


# Handle messages events
def handleMessage(sender_psid, recipientPSID, received_message):
    print("--------------------------------------------------")
    print("Received a message from PSID %s" % str(sender_psid))

    # skip echo messages
    if 'is_echo' in received_message:
        if received_message['is_echo']:
            print("This message is an echo!")
            return

    # check if msg contains text
    if 'text' in received_message:
        tokenizedWords = tokenize.word_tokenize(received_message['text'].lower(), language='portuguese')

        time.sleep(2)
        sendTypingBubble(sender_psid)

        if any(x in keywords.categorias for x in tokenizedWords):
            sendCategoriesQuickReply(sender_psid, "Selecione uma categoria abaixo:")
            return

        # Greetings
        elif any(x in keywords.greetings for x in tokenizedWords):
            userInfo = getPersonInfo(sender_psid)
            greetings = random.choice(keywords.helloPhrases) % userInfo['first_name']
            callSendAPI(sender_psid, {"text": greetings})
            sendCategoriesQuickReply(sender_psid, "Selecione uma categoria abaixo:")
            return

        elif ('tudo' in tokenizedWords and any (x in keywords.howAreYou for x in tokenizedWords)) or \
                        any(x in keywords.howAreYou for x in tokenizedWords) and '?' in tokenizedWords:
            userInfo = getPersonInfo(sender_psid)
            msg = random.choice(keywords.feelingGreatPhrases) % userInfo['first_name']
            callSendAPI(sender_psid, {"text": msg})
            sendCategoriesQuickReply(sender_psid, "Veja nossas categorias:")
            return

        # Products
        # materiais elétricos
        elif any(x in keywords.materiais for x in tokenizedWords) and any(y in keywords.eletricos for y in tokenizedWords):
            sendElectricMaterialsQuickReply(sender_psid)
            return

        elif any(x in keywords.controladores for x in tokenizedWords):
            callSendAPI(sender_psid, {"text": "Encontrei controladores, veja"})
            sendCarouselMsg(sender_psid, controladores)
            sendCategoriesQuickReply(sender_psid, "Deseja ver outra categoria?")
            return

        elif any(x in keywords.eletrofita for x in tokenizedWords):
            callSendAPI(sender_psid, {"text": "Aqui estão algumas eletrofitas"})
            sendCarouselMsg(sender_psid, eletrofita)
            sendCategoriesQuickReply(sender_psid, "Deseja ver outra categoria?")
            return

        # iluminacao
        elif any(x in keywords.iluminacao for x in tokenizedWords):
            sendIluminationQuickReply(sender_psid)
            return

        elif any(x in keywords.fita for x in tokenizedWords) and any(y in keywords.led for y in tokenizedWords):
            callSendAPI(sender_psid, {"text": "Aqui estão algumas fitas LED para você"})
            sendCarouselMsg(sender_psid, fita_led)
            sendCategoriesQuickReply(sender_psid, "Deseja ver outra categoria?")
            return

        elif any(x in keywords.lampada for x in tokenizedWords):
            callSendAPI(sender_psid, {"text": "Encontrei algumas lâmpadas LED"})
            sendCarouselMsg(sender_psid, lampada_led)
            sendCategoriesQuickReply(sender_psid, "Deseja ver outra categoria?")
            return

        # luminárias
        elif any(x in keywords.luminaria for x in tokenizedWords):
            sendLightFixtureQuickReply(sender_psid)
            return

        elif any(x in keywords.lustre for x in tokenizedWords):
            callSendAPI(sender_psid, {"text": "Separei os lustres mais bonitos da loja para você!"})
            sendCarouselMsg(sender_psid, lustres)
            sendCategoriesQuickReply(sender_psid, "Deseja ver outra categoria?")
            return

        elif any(x in keywords.embutidos for x in tokenizedWords):
            callSendAPI(sender_psid, {"text": "Aqui estão alguns embutidos"})
            sendCarouselMsg(sender_psid, luminaria_embutir)
            sendCategoriesQuickReply(sender_psid, "Deseja ver outra categoria?")
            return

        elif any(x in keywords.byePhrases for x in tokenizedWords):
            callSendAPI(sender_psid, {"text": "Obrigado! Não quer aproveitar para olhar mais algumas coisas?"})
            sendCategoriesQuickReply(sender_psid, "Temos as seguintes categorias:")
            return

        elif any(x in keywords.backPhrases for x in tokenizedWords):
            callSendAPI(sender_psid, {"text": "Voltaremos para o início então"})
            sendCategoriesQuickReply(sender_psid, "Aqui estão as categorias:")
            return

        # Bot does not know the answer
        apologizePhrase = random.choice(keywords.apologizePhrases)
        callSendAPI(sender_psid, {"text": apologizePhrase})
        return

# Handle message_postbacks events
def handlePostback(sender_psid, recipientPSID, received_postback):
    print("--------------------------------------------------")
    print("Received a postback from PSID %s" % str(sender_psid))
    time.sleep(2)

    if received_postback['title'] == 'Começar' or received_postback['title'] == 'Get Started':
        userInfo = getPersonInfo(sender_psid)
        greetings = random.choice(keywords.helloPhrases) % userInfo['first_name']
        callSendAPI(sender_psid, {"text": greetings})
        sendCategoriesQuickReply(sender_psid, "Escolha uma de nossas categorias:")
        return
    return

# Sends response messages via the Send API
def callSendAPI(sender_psid, response):
    print("--------------------------------------------------")
    print("Sending a message to %s" % sender_psid)
    # construct message body
    requestBody = {"recipient": {"id": sender_psid},
                   "message"  : response
                   }
    r  = requests.post('https://graph.facebook.com/v2.6/me/messages', params={"access_token": PAGE_ACCESS_TOKEN}, json=requestBody)

# Person profile information
def getPersonInfo(psid):
    url = "https://graph.facebook.com/v2.6/%s" % psid
    payload = {"fields": "first_name", "access_token": PAGE_ACCESS_TOKEN}
    r = requests.get(url, params=payload)
    return r.json()

# Three dots while typing
def sendTypingBubble(psid):
    url = "https://graph.facebook.com/v2.6/me/messages"
    requestBody = {"recipient": {"id": psid},
                   "sender_action": "typing_on"
                   }
    r  = requests.post(url, params={"access_token": PAGE_ACCESS_TOKEN}, json=requestBody)
    time.sleep(4.0)

# Generic quick reply message
def sendQuickReply(psid, msgText, quickReplies):
    url = "https://graph.facebook.com/v2.6/me/messages"
    requestBody = {"recipient": {"id":psid },
                   "message"  : {"text": msgText,
                                "quick_replies":quickReplies
                                }
                  }
    r  = requests.post(url, params={"access_token": PAGE_ACCESS_TOKEN}, json=requestBody)
    # print(r.url)

# Generic Carousel message
def sendCarouselMsg(psid, elements):
    url = "https://graph.facebook.com/v2.6/me/messages"
    requestBody = {"recipient": {"id":psid },
                   "message"  : {"attachment":{"type": "template",
                                               "payload": {"template_type": "generic",
                                                           "elements": elements}
                                              }
                                }

                  }

    r  = requests.post(url, params={"access_token": PAGE_ACCESS_TOKEN}, json=requestBody)

# Quick replies according to the product
def sendCategoriesQuickReply(psid, text):
    text         =  text
    quickReplies = [{"content_type": "text", "title": "Iluminação", "payload": "iluminacao"},
                    {"content_type": "text", "title": "Luminárias", "payload": "luminarias"},
                    {"content_type": "text", "title": "Materiais Elétricos", "payload": "materiais-eletricos"}]
    sendQuickReply(psid, text, quickReplies)


def sendLightFixtureQuickReply(psid):
    text         = "Qual tipo de luminária você está procurando?"
    quickReplies = [{"content_type": "text","title": "Lustres","payload": "lustres"},
                    {"content_type": "text","title": "Embutidos","payload": "embutidos"},
                    {"content_type": "text","title": "Ir para Categorias","payload": "categorias"}]
    sendQuickReply(psid, text, quickReplies)

def sendElectricMaterialsQuickReply(psid):
    text         = "Qual material elétrico você está procurando?"
    quickReplies = [{"content_type": "text","title": "Controladores","payload": "controladores"},
                    {"content_type": "text","title": "Eletrofita"   ,"payload": "eletrofita"},
                    {"content_type": "text", "title": "Ir para Categorias", "payload": "categorias"}]
    sendQuickReply(psid, text, quickReplies)

def sendIluminationQuickReply(psid):
    text         = "Em qual tipo de iluminação você está interessado(a)?"
    quickReplies = [{"content_type": "text","title": "Fita LED","payload": "fita_led"},
                    {"content_type": "text","title": "Lâmpada LED"   ,"payload": "lampada_led"},
                    {"content_type": "text", "title": "Ir para Categorias", "payload": "categorias"}]
    sendQuickReply(psid, text, quickReplies)

# Add "get_started" button
@app.route('/setupMessenger')
def setMessengerProfile():
    url = "https://graph.facebook.com/v2.6/me/messenger_profile"
    qs = {"access_token": PAGE_ACCESS_TOKEN}
    properties = {"get_started": {"payload": "getStarted"}}

    requests.post(url, params=qs, json=properties)
    return "OK", 200


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, threaded=True, ssl_context=context)