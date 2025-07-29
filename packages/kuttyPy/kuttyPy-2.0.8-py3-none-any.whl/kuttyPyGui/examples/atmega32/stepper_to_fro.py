import time
from kuttyPy import *
setReg('DDRC',255)

for a in range(10):
	for x in range(5):
		for a in [3,6,12,9]:    
			setReg('PORTC', a<<4)
			time.sleep(0.1)

	for x in range(10):
		for a in [12,6,3,9]:    
			setReg('PORTC', a<<4)
			time.sleep(0.1)

	for x in range(5):
		for a in [3,6,12,9]:
			setReg('PORTC', a<<4)
			time.sleep(0.1)

setReg('PORTC', 0)
