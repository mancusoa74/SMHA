import log
from Pubnub import Pubnub

global pubnub
global log
global message_cb

SUB_KEY = "YOUR SUB KEY"
PUB_KEY = "YOUR PUB KEY"
CHIPER_KEY = "YOUR CHIPER KEY" # generate it with openssl enc -aes-256-cbc -k secret -P -md sha1
CHANNEL = 'YOUR CHANNEL'

def pubnub_error_cb(message):
    log.error("ERROR : " + str(message))


def pubnub_connect_cb(message):
    log.info("pubnub CONNECTED")


def pubnub_reconnect_cb(message):
    log.info("pubnub RECONNECTED")


def pubnub_disconnect_cb(message):
  log.error("pubnub DISCONNECTED")

def pubnub_message_cb(message, channel):
    global message_cb
    message_cb(message, channel)

def unsubscribe():
    global pubnub
    pubnub.unsubscribe(channel=CHANNEL)
    log.info("pubnub UNSUBSCRIBED")

def init(func):
    global pubnub
    global message_cb
    message_cb = func
    log.info("pubnub SUBSCRIBE")
    pubnub = Pubnub(publish_key=PUB_KEY, subscribe_key=SUB_KEY, cipher_key=CHIPER_KEY, ssl_on=True)
    pubnub.subscribe(CHANNEL, callback=pubnub_message_cb, error=pubnub_error_cb, connect=pubnub_connect_cb, reconnect=pubnub_reconnect_cb, disconnect=pubnub_disconnect_cb)
    log.info("pubnub SUBSCRIBED")

