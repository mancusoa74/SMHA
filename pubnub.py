import log
from Pubnub import Pubnub
import uuid
import json

global pubnub
global pubnub_freeboard
global log
global message_cb

 SUB_KEY = "YOUR SUB KEY"
 PUB_KEY = "YOUR PUB KEY"
 CHIPER_KEY = "YOUR CHIPER KEY" # generate it with openssl enc -aes-256-cbc -k secret -P -md sha1
 CHANNEL = 'YOUR CHANNEL'
 CHANNEL_FB = 'YOUR FB CHANNEL'

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

    try:
        message_cb(message, channel)
    except:
        log.error("Error in executing pubnub.pubnub_message_cb")

def unsubscribe():
    global pubnub

    try:
        pubnub.unsubscribe(channel=CHANNEL)
        log.info("pubnub UNSUBSCRIBED")
    except:
        log.error("Error in executing pubnub.unsubscribe")

def send(src_id, replyto, cmd, result):
    #{"_id":"32434", src_id":"uuid1", "reply_to": "2432", "dst_pin":"1", "cmd":"unsubscribe", "result":"1"}
    _id = uuid.uuid1()

    log.debug("_id: %s" %_id)
    log.debug("src_id: %s" %src_id)
    log.debug("replyto: %s" %replyto)
    log.debug("cmd: %s" %cmd)
    log.debug("result: %s" %result)

    pubnub_mex = '{"_id": "%s", "src_id": "%s", "reply_to": "%s", "dst_pin": "none", "cmd": "%s", "result": "%s"}' %(_id, src_id, replyto, cmd, result)
    log.info("sending pubnub message: %s" %pubnub_mex)

    pubnub.publish(CHANNEL, json.loads(pubnub_mex))
        #json.loads(str)


def fb_status():
    pubnub_mex = '{"status":"ON"}'
    log.info("sending pubnub FB message: %s" %pubnub_mex)
    pubnub_freeboard.publish(CHANNEL_FB, json.loads(pubnub_mex))

def fb_update_status_caldaia(status):
    if (status == 1):
        pubnub_mex = '{"status":"ON"}'
    else:
        pubnub_mex = '{"status":"OFF"}'

    log.info("sending pubnub FB message: %s" %pubnub_mex)
    pubnub_freeboard.publish(CHANNEL_FB, json.loads(pubnub_mex))

def fb_update_status_temp(temp):
    pubnub_mex = '{"temperature":"%s"}' %temp
    log.info("sending pubnub FB message: %s" %pubnub_mex)
    pubnub_freeboard.publish(CHANNEL_FB, json.loads(pubnub_mex))


def init(func):
    global pubnub
    global pubnub_freeboard
    global message_cb

    try:
        message_cb = func
        log.info("pubnub SUBSCRIBE")
        pubnub = Pubnub(publish_key=PUB_KEY, subscribe_key=SUB_KEY, cipher_key=CHIPER_KEY, ssl_on=True)
        pubnub.subscribe(CHANNEL, callback=pubnub_message_cb, error=pubnub_error_cb, connect=pubnub_connect_cb, reconnect=pubnub_reconnect_cb, disconnect=pubnub_disconnect_cb)
        pubnub_freeboard = Pubnub(publish_key=PUB_KEY, subscribe_key=SUB_KEY, ssl_on=False)

        log.info("pubnub SUBSCRIBED")
    except:
        log.error("Error initializing pubnub...Cannot continue")
        raise SystemExit

