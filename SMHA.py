#!/usr/bin/python

import log
import pubnub
import gpio
import sys
import schedule
import time
import subprocess

# SMHAutomation: simple framework for my home automation long term project
# Antonio "monk" Mancuso - October 2014
#
# v.1.0: initial framework version with basic functionalities
# v.1.0.1: introduced a couple of decorator to be more python compliant :)
# v.1.0.2: gpio.status seding pubnub reply message
# v.1.0.3: adding temperature measurement and monitoring on freeboard.io

VERSION = "1.0.3"
# messages have the following format
# _id: UUID of the message
# src_id: UUID of the sender
# dst_pin: pin to control )Rapsberry BCM mode)
# cmd: command to execute (unsubscribe, switch_on, switch_off)
#
# example: {"_id":"32434", src_id":"uuid1", "reply_to": "2432", "dst_pin":"1", "cmd":"unsubscribe", "result":"1"}

# list of authorize clients
authorized_client_ids = ["YOUR CLIENT ID"]
SMHA_ID = "YOUR SERVER ID"


CALDAIA_GPIO = 15

# command handlers
def cmd_unsubscribe_handler(message):
	try:
		log.debug("handling cmd_unsubscribe")
		pubnub.unsubscribe()
	except:
		log.error("Error in executing cmd_unsubscribe_handler")

def cmd_switch_on_handler(message):
	try:
		log.debug("handling cmd_switch_on")
		dst_pin = int(message['dst_pin'])
		gpio.on(dst_pin)
	except:
		log.error("Error in executing cmd_switch_on_handler")
	

def cmd_switch_off_handler(message):
	try:
		log.debug("handling cmd_switch_off")
		dst_pin = int(message['dst_pin'])
		gpio.off(dst_pin)
	except:
		log.error("Error in executing cmd_switch_off_handler")

def cmd_status_handler(message):
	try:
		log.debug("handling cmd_status")
		_id = message['_id']
		dst_pin = int(message['dst_pin'])
		status = gpio.status(dst_pin)
		log.info("GPIO %s status: %s" %(dst_pin, status))
		pubnub.send(SMHA_ID, _id, 'status', status)
	except:
		log.error("Error in executing cmd_status_handler")

def cmd_test_handler(message):
	log.debug("handling cmd_test")

def cmd_testfb_handler(message):
	log.debug("handling cmd_testfb")
	pubnub.fb_status()

# mapping between commands and handler
message_cbs = {"unsubscribe" : cmd_unsubscribe_handler,
			   "switch_on"   : cmd_switch_on_handler,
			   "switch_off"  : cmd_switch_off_handler,
			   "status"      : cmd_status_handler,
			   "test"        : cmd_test_handler,
			   "testfb"      : cmd_testfb_handler
			  }

def authorize(func):
    def authorize_and_call(*args, **kwargs):
		try:
			log.debug("authorizing message in @decorator")
			_id = args[0]['_id']
			src_id = (args[0]['src_id'])
			auth = src_id in authorized_client_ids or (src_id == SMHA_ID)
			log.info("pubnub message %s authorization: %s" %(_id, auth))
			if not auth: 
				log.error('pubnub message Authorization Failed.')
				log.debug("here5")
				return None
			log.info("pubnub message AUTHORIZED")
			return func(*args, **kwargs)
		except:
			log.error("Error in executing authorize decorator")

    return authorize_and_call

def validate(func):
	def validate_and_call(*args, **kwargs):
		try:
			log.debug("validating message in @decorator")		
			log.debug("pubnub message received: %s" %args[0])
			 #{"_id":"32434", src_id":"uuid1", "reply_to": "2432", "dst_pin":"1", "cmd":"unsubscribe", "result":"1"}
			if not (('_id' in args[0]) & ('src_id' in args[0]) & ('reply_to' in args[0]) & ('dst_pin' in args[0]) & ('cmd' in args[0]) & ('result' in args[0])):
				log.error('pubnub message Validation Failed.')
				log.error("pubsub message format INVALID and discarded")
				return None
			else:
				log.info("pubnub message VALIDATED")
				_id = args[0]['_id']
				src_id = args[0]['src_id']
				reply_to = args[0]['reply_to']
				dst_pin = args[0]['dst_pin']
				cmd = args[0]['cmd']
				result = args[0]['result']

				log.debug("pubnub message _id: %s" %_id)
				log.debug("pubnub message reply_to: %s" %reply_to)
				log.debug("pubnub src_id: %s" %src_id)
				log.debug("pubnub dst_pin: %s" %dst_pin)
				log.debug("pubnub cmd: %s" %cmd)
				log.debug("pubnub result: %s" %result)
				return func(*args, **kwargs)
		except:
			log.error("Error in executing validate decorator")

	return validate_and_call


@validate
@authorize
def message_handler(message):
	cmd = message['cmd']
	src_id = message['src_id']

	# if message is validated and authorized then execute specific command functions
	# if not discard message
	if src_id != SMHA_ID:
		if cmd in message_cbs:
			message_cbs[cmd](message)
		else:
			log.error("pubnub message command not recognized")
	else:
		log.info("not handling outbound published command")
	

# call back fron pubnub library on reception of a message
def pubnub_message_handler(message, channel):
	# check for a valid message otherwise discard it
	if message == "":
		log.error("pubnub message not valid")
	else:
		message_handler(message)


def update_fb_status_caldaia():
	log.info("updating Caldaia status on FB")
	status = gpio.status(CALDAIA_GPIO)
	log.info("GPIO %s status: %s" %(CALDAIA_GPIO, status))
	pubnub.fb_update_status_caldaia(status)


def update_fb_status_temp():
	command = "/home/pi/SMHA/DTH11/dth11_sensor"
	process = subprocess.Popen(command, stdout=subprocess.PIPE)
	temp = process.communicate()[0]
	log.info("updating Temperature: %s statuys on FB" %temp)
	pubnub.fb_update_status_temp(temp)

		
def main():
		log.init() #init logging 
		log.info("Staring SMHAutomation v %s" %VERSION)
		gpio.init() #init GPIO communication
		pubnub.init(pubnub_message_handler) #init and subscribe to pubnub channel

		schedule.every(5).seconds.do(update_fb_status_caldaia)
		schedule.every(120).seconds.do(update_fb_status_temp)

		while True:
			schedule.run_pending()
			time.sleep(1)
	

if __name__ == "__main__":
	main()
