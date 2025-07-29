import time
from kuttyPy import *
setReg('DDRC',255)
steps = [3,2,6,4,12,8,9,1]
curpos=0

def step_fwd():
	global curpos
	curpos+=1
	if curpos>=len(steps):
		curpos=0
	setReg('PORTC',steps[curpos]<<4)
	print('F',steps[curpos])

def step_back():
	global curpos
	curpos-=1
	if curpos<0:
		curpos=len(steps)-1
	setReg('PORTC',steps[curpos]<<4)
	print('B',steps[curpos])


setReg('PORTC', steps[curpos] << 4)
time.sleep(0.5)

for a in range(2):
	for x in range(10):
		step_fwd()
		time.sleep(0.1)

	for x in range(20):
		step_back()
		time.sleep(0.1)

	for x in range(10):
		step_fwd()
		time.sleep(0.1)

setReg('PORTC', 0)
