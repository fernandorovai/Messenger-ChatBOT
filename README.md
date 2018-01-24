# Luizalabs-AIEngineer Task
Flask based HTTP application to consume / provide data to a real time Facebook Messenger chat bot.

![Demo](https://user-images.githubusercontent.com/3229701/35335503-f0a1c494-00fc-11e8-9759-6eff7f8ba4a2.gif)
The project is up and running for demo purposes: [ProjectDemo](https://www.facebook.com/HunterDesign-165135967439067/)

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
```
Linux system: Ubuntu 16.04 (Xenial) or later
python 3.5
pip
```

### Installing
Clone source code from git repo

```
$ git clone https://github.com/fernandorovai/Luizalabs-AIEngineer
```

Setup and activate virtual environment

```
$ virtualenv Luizalabs-AIEngineer -p python3
$ cd Luizalabs-AIEngineer
$ source ./bin/activate
```

Install python dependencies via pip
```
$ pip install -r requirements.txt
```

## Running the Server
Start the webserver
```
Facebook requires ssl certificate.
Setup ssl credentials in context variable (server.py):
context = ('/path/fullchain.pem',
           '/path/privkey.pem')

obs: if your credentials are in root dir, you may have to install the dependencies also using root

$ cd Luizalabs-AIEngineer
$ python3 server.py or sudo python3 server.py
```
Expected output
```
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

## Principal Methods

* sendCarouselMsg(sender_id, elements)
```
# elements structure
elements = [
                {'subtitle': 'Price or a subtitle', 
                 'buttons': [{'url': 'url', 'type': 'web_url', 'title': 'Ver Detalhes'}], 
                 'image_url': 'imageUrl', 
                 'title': 'Product Title'}, 
                {...}
             ]
```
* sendQuickReply(sender_id, quickReplies)
```
quickReplies = [{"content_type": "text","title": "Lustres","payload": "lustres"},
                {"content_type": "text","title": "Embutidos","payload": "embutidos"},
                {"content_type": "text","title": "Ir para Categorias","payload": "categorias"}]
```              
* sendTypingBubble(sender_id)
* getPersonInfo(sender_id)
* callSendAPI(sender_id, {"text": "yourText"})



## Keywords / Phrases
This bot uses pre-defined keywords to chat. These keywords are found in keywords.py file.
In order to advance its intelligence, consider using RNN (Recurrent Neural Networks).

## Products Data
The file data.py holds all products offered by the bot.
All products information belongs to [HunterTrade](www.huntertrade.com.br) company that authorized the usage for this demonstration.
Consider retrieving information from database / API.

## Deployment

Flask’s built-in server is not suitable for production. Consider deploying the application to a WSGI Server.

For more information, check [Flask Documentation](http://flask.pocoo.org/docs/0.12/deploying/)

## Built With

* [Flask](http://flask.pocoo.org/)           - Microframework for Python
* [Pip](https://pip.pypa.io/en/stable/)      - Dependency Management
* [Nltk](http://www.nltk.org/)               - Natural Language Toolkit

## Authors
* **Fernando Rodrigues Jr** - *Initial work* - [Fernando](https://github.com/fernandorovai)

## License
This project is restricted to LuizaLabs.