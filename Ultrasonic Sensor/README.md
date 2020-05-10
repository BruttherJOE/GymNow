# Ultrasonic Sensor


## Features

### Median filter
```
samplesize = 7
def medfilter(samplesize):
    ls = [] #init empty list
    dist2 = distance() #calls distance function
    for i in range(samplesize):
        ls.append(dist2)
    sorted_dist2_list = sorted(ls)
    ls = []
    return sorted_dist2_list[samplesize//2]
```
  The code makes use of a simple median filter written by us to discard noise, as the ultrasonic sensor is not foolproof and sometimes it's values are a little bit off.  
  
  To prevent significant lag, we chose to only take 7 samples. This means getting 7 sets of data, then sorting them from smallest to largest, then taking the median value as one data value to be read. The other 6 data sets are then discarded.  
  
  Because it is a median filter, sample sizes have to be in odd numbers (e.g. 3,5,7,9...)
  
  ### Firebase server
  The code makes use of the firebase server to store and manage data.
  ```python
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
```
  ## libdw
  The code makes use of libdw, a library made by one of our professors in SUTD (cr : Oka Kurniawan)  
  
  `from libdw import pyrebase`  
  
  We used pyrebase in libdw library to connect to firebase for the simplification of code.  
