import time
#from kuttyPy import *
initServos()

for a in range(10):
    setServoD4(0)
    time.sleep(0.2)
    setServoD4(120)
    time.sleep(0.2)
