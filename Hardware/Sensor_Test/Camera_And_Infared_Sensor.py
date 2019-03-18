import RPi.GPIO as GPIO
import picamera
import picamera.array
import time, io
import numpy, cv2

lightGPIO = [2, 3, 4]
infaredGPIO = 18
background = None

def stream2CV(stream):
	data = numpy.fromstring(stream.getvalue(), dtype=numpy.uint8)
	image = cv2.imdecode(data, 1)
	# image = image[:, :, ::-1]
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	image = cv2.GaussianBlur(image, (21, 21), 0)
	return image

def detect(camera):
	global background
	global lightGPIO, infaredGPIO
	
	try:
		camera.start_preview()
		time.sleep(0.5)
		with io.BytesIO() as stream:
			for frame in camera.capture_continuous(stream, format='jpeg', use_video_port = True):
				# Get Image From Camera
				image = stream2CV(stream)
				stream.seek(0)
				stream.truncate(0)

				# Stop Detect When Infared Sensor Stop
                                if GPIO.input(infaredGPIO) == GPIO.LOW:
                                	print("Recollect", time.time())
					background = image # Record Background
                                        # cv2.imshow("BackGround", image)
                              	  	# cv2.waitKey(5)
	 				break
				
				# Diff Image
				es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 4))
				diff = cv2.absdiff(background, image)
				diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
				diff = cv2.dilate(diff, es, iterations=2)
				cnts, hierarchy = cv2.findContours(diff.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
				cnt = 0
				for c in cnts:
					if cv2.contourArea(c) < 1500:
						continue
					cnt = cnt + 1
					(x, y, w, h) = cv2.boundingRect(c)
					cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
				
				# cv2.imshow("Contours", image)
				# cv2.waitKey(5)
				if (cnt > 0):
					GPIO.output(lightGPIO, GPIO.HIGH)
				else:
					GPIO.output(lightGPIO, GPIO.LOW)

	finally:
		camera.stop_preview()

def infared(camera):
	global lightGPIO, infaredGPIO
	global background
	
	# Init & Set GPIO
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(infaredGPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(lightGPIO, GPIO.OUT)

	GPIO.output(lightGPIO, GPIO.LOW)

	try:
		while True:
			if GPIO.input(infaredGPIO) == GPIO.LOW:
				print("Infared : Nothing", time.time())
				time.sleep(0.5)
				GPIO.output(lightGPIO, GPIO.LOW)
			else:
				print("Infared : Find", time.time())
				# Start To Detect Motion
				detect(camera)
	finally:
		GPIO.cleanup()
		camera.close()
		
def main():
	global background
	
	# Init Camera
	with picamera.PiCamera() as camera:
		# Set Camera
		camera.resolution = (640, 360)
		camera.framerate = 25
		camera.annotate_text = "Intelligent_lighting_System"
		
		# Get Background Image
		with io.BytesIO() as stream:
			camera.start_preview()
			time.sleep(2)
			camera.capture(stream, format = 'jpeg', use_video_port = True)
			background = stream2CV(stream)
			camera.stop_preview()

		# cv2.imshow("BackGround", background)
		# cv2.waitKey(50)
		
		infared(camera)

if __name__ == "__main__": main()

