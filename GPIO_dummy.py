BCM = 1
OUT = 1
def setmode(mode):
	print("fake GPIO.setmode")


def setwarnings(mode):
	print("fake GPIO.setwarnings")

def setup(pin, mode):
	print("fake GPIO.setup")

def output(pin, mode):
	print("fake GPIO.output")

def input(pin):
	print("fake GPIO.input")
	return 99



	