#Libraries
from libdw import pyrebase

projectid = "gymnow-520ab"
dburl = "https://" + projectid + ".firebaseio.com"
authdomain = projectid + ".firebaseapp.com"
apikey = "AIzaSyAlOktsnWFzzZ_S3wBieWYZXdEcZKWnS0c"
email = "yufan.fong@gmail.com"
password = "123456"

config = {
    "apiKey": apikey,
    "authDomain": authdomain,
    "databaseURL": dburl,
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(email, password)

while True:
    import RPi.GPIO as GPIO
    import time
 
#GPIO Mode (BOARD / BCM)
    GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
    GPIO_TRIGGER = 18
    GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)
 
    def distance():
    # set Trigger to HIGH
        GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
        time.sleep(0.2)
        GPIO.output(GPIO_TRIGGER, False)
 
        StartTime = time.time()
        StopTime = time.time()
 
    # save StartTime
        while GPIO.input(GPIO_ECHO) == 0:
            StartTime = time.time()
 
    # save time of arrival
        while GPIO.input(GPIO_ECHO) == 1:
            StopTime = time.time()
 
    # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
        distance = (TimeElapsed * 34300) / 2
 
        return distance
        
    samplesize = 7
    def medfilter(samplesize):
        ls = [] #init empty list
        dist2 = distance() #calls distance function
        for i in range(samplesize):
            ls.append(dist2)
        sorted_dist2_list = sorted(ls)
        ls = []
        return sorted_dist2_list[samplesize//2]

    if __name__ == '__main__':
        counter = 0
        try:
            while True:
                dist = medfilter(samplesize)
                
                if dist <= 10 :
                    print ("Measured Distance = %.1f cm" % dist)
                    counter += 1
                    time.sleep(3)

                if 10 < dist <= 20:
                    print ("Measured Distance = %.1f cm" % dist)
                    counter -= 1
                    time.sleep(3)
                            
                if dist > 20:
                    print ("")

                if counter <= 0:
                    counter = 0

                print(counter)

                    
                db.child("Overall").set(counter, user['idToken'])
                    
            # Reset by pressing CTRL + C
        except KeyboardInterrupt:
            print("Measurement stopped by User")
            GPIO.cleanup() 
        
        # upload total_count into db
                






        
    
    
