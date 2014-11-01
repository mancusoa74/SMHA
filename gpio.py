import log
import RPi.GPIO as GPIO

out_pins = [15] #list of OUTPUT GPIO pins to manage

def init():
	log.info("initialize GPIO")
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	#set pins to output
	for pin in out_pins:
		log.info("setting GPIO %s to OUT" %pin)
		GPIO.setup(pin, GPIO.OUT)
	log.info("GPIO initialized")

def on(pin):
	if pin in out_pins:
		log.info("setting GPIO %s to ON" %pin)
		GPIO.output(pin, 1)
		return True
	else:
		log.error("cannot set GPIO %s to ON as it is not an output pin" %pin)
		return False

def off(pin):
	if pin in out_pins:
		log.info("setting GPIO %s to OFF" %pin)
		GPIO.output(pin, 0)
		return True
	else:
		log.error("cannot set GPIO %s to OFF as it is not an output pin" %pin)
		return False

def status(pin):
	if pin in out_pins:
		log.info("reading GPIO %s status" %pin)
		return GPIO.input(pin)
	else:
		log.error("cannot read GPIO %s status as it is not an output pin" %pin)
		return -1
