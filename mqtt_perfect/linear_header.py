# leftMotor_DIR_pin : 19, leftMotor_DIR_pin2 : 26, rightMotor_DIR_pin : 20, rightMotor_DIR_pin2 : 21
# leftMotor_PWM_pin : 5, rightMotor_PWM_pin : 25
# 1 -> rightMotor, 2-> leftMotor
# 모터 핀 설정 및 모터 구동을 위한 함수들 정의
# 핀 번호 설정해야 함
import RPi.GPIO as io
io.setmode(io.BCM)

PWM_MAX = 100

io.setwarnings(False)
 
leftMotor_DIR_pin = 19
leftMotor_DIR_pin2 = 26
io.setup(leftMotor_DIR_pin, io.OUT)
io.setup(leftMotor_DIR_pin2, io.OUT)
rightMotor_DIR_pin = 20
rightMotor_DIR_pin2 = 21
io.setup(rightMotor_DIR_pin, io.OUT) 
io.setup(rightMotor_DIR_pin2, io.OUT)  
io.output(leftMotor_DIR_pin, False)
io.output(leftMotor_DIR_pin2, False)
io.output(rightMotor_DIR_pin, False)  
io.output(rightMotor_DIR_pin2, False)  
  
leftMotor_PWM_pin = 5
rightMotor_PWM_pin = 25
io.setup(leftMotor_PWM_pin, io.OUT)  
io.setup(rightMotor_PWM_pin, io.OUT)  

leftMotorPWM = io.PWM(leftMotor_PWM_pin,20)  
rightMotorPWM = io.PWM(rightMotor_PWM_pin,20)  
  
leftMotorPWM.start(0)  
leftMotorPWM.ChangeDutyCycle(0)  
rightMotorPWM.start(0)  
rightMotorPWM.ChangeDutyCycle(0)  

leftMotorPower = 0  
rightMotorPower = 0  

def getMotorPowers():  # 모터 속도 반환
	return (leftMotorPower,rightMotorPower)

def setMotorLeft(power):  # 왼쪽 모터 set
	if power < 0:
		io.output(leftMotor_DIR_pin, False)
		io.output(leftMotor_DIR_pin2, True)
		pwm = -int(PWM_MAX * power)  

		if pwm > PWM_MAX:  
			pwm = PWM_MAX
	elif power > 0:  
		io.output(leftMotor_DIR_pin, True)  
		io.output(leftMotor_DIR_pin2, False)  
		pwm = int(PWM_MAX * power)  

		if pwm > PWM_MAX:  
			pwm = PWM_MAX
	else: 
		io.output(leftMotor_DIR_pin, False)  
		io.output(leftMotor_DIR_pin2, True)  
		pwm = 0

	leftMotorPower = pwm  
	leftMotorPWM.ChangeDutyCycle(pwm)
		
def setMotorRight(power):  # 오른쪽 모터 set
	if power < 0:  
		io.output(rightMotor_DIR_pin, True)  
		io.output(rightMotor_DIR_pin2, False)  
		pwm = -int(PWM_MAX * power)  

		if pwm > PWM_MAX:  
			pwm = PWM_MAX  
	elif power > 0: 
		io.output(rightMotor_DIR_pin, False) 
		io.output(rightMotor_DIR_pin2, True)  
		pwm = int(PWM_MAX * power)

		if pwm > PWM_MAX:  
			pwm = PWM_MAX  
	else:
		io.output(rightMotor_DIR_pin, False)  
		io.output(rightMotor_DIR_pin2, False) 
		pwm = 0

	rightMotorPower = pwm  
	rightMotorPWM.ChangeDutyCycle(pwm)

def exit():  # 종료
	io.output(leftMotor_DIR_pin, False)
	io.output(rightMotor_DIR_pin, False)
	io.cleanup()
