#!/usr/bin/python

import log
import pubnub
import gpio
import sys

VERSION = "1.0"
# messages have the following format
# _id: UUID of the message
# src_id: UUID of the sender
# dst_pin: pin to control )Rapsberry BCM mode)
# cmd: command to execute (unsubscribe, switch_on, switch_off)
#
# example: {"_id":"32434", "src_id":"uuid1", "dst_pin":"1", "cmd":"unsubscribe"}

# list of authorize clients
authorized_client_ids = ["YOUR CLIENT ID"]

# command handlers
def cmd_unsubscribe_handler(message):
	log.debug("handling cmd_unsubscribe")
	pubnub.unsubscribe()

def cmd_switch_on_handler(message):
	log.debug("handling cmd_switch_on")
	dst_pin = int(message['dst_pin'])
	gpio.on(dst_pin)
	

def cmd_switch_off_handler(message):
	log.debug("handling cmd_switch_off")
	dst_pin = int(message['dst_pin'])
	gpio.off(dst_pin)

def cmd_status_handler(message):
	log.debug("handling cmd_status")
	dst_pin = int(message['dst_pin'])
	status = gpio.status(dst_pin)
	log.info("GPIO %s status: %s" %(dst_pin, status))

def cmd_test_handler(message):
	log.debug("handling cmd_test")

# mapping between commands and handler
message_cbs = {"unsubscribe" : cmd_unsubscribe_handler,
			   "switch_on"   : cmd_switch_on_handler,
			   "switch_off"  : cmd_switch_off_handler,
			   "status"      : cmd_status_handler,
			   "test"        : cmd_test_handler
			  }

# authorization of each individual message
def authorize_message(_id, src_id):
	# this is a very simple. can be more sophisticated.
	# however we have SSL and AES encryption so should be enough

	auth = src_id in authorized_client_ids
	log.info("pubnub message %s is authorization: %s" %(_id, auth))
	return auth

# handle incming message
def message_handler(message):
	log.debug("pubnub message received: %s" %message)

	_id = message['_id']
	src_id = message['src_id']
	dst_pin = message['dst_pin']
	cmd = message['cmd']

	log.debug("pubnub message _id: %s" %_id)
	log.debug("pubnub src_id: %s" %src_id)
	log.debug("pubnub dst_pin: %s" %dst_pin)
	log.debug("pubnub cmd: %s" %cmd)

	auth = authorize_message(_id, src_id)

	if auth:
		# if authorized then execute specific command functions
		# if not discard message
		if cmd in message_cbs:
			message_cbs[cmd](message)
		else:
			log.error("pubnub message command not recognized")
	else:
		log.error("pubsub message NOT authorized and discarded")

# call back fron pubnub library on reception of a message
def pubnub_message_handler(message, channel):
	# check for a valid message otherwise discard it
	if message == "":
		log.error("pubnub message not valid")
	else:
		message_handler(message)

		
def main():
	log.init() #init logging 
	log.info("Staring SMHAutomation v %s" %VERSION)
	gpio.init() #init GPIO communication
	pubnub.init(pubnub_message_handler) #init and subscribe to pubnub channel
	
if __name__ == "__main__":
	main()


