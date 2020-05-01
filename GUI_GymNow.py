from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.utils import get_color_from_hex
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import os
import datetime as dt
from kivy.uix.floatlayout import FloatLayout
#from libdw import pyrebase

#----------------Firebase-----------------#
'''
projectid = "gymnow-520ab"
dburl = "https://" + projectid + ".firebaseio.com"
authdomain = projectid + ".firebaseapp.com"
apikey = "AIzaSyAlOktsnWFzzZ_S3wBieWYZXdEcZKWnS0c"
email = "yufan.fong@gmail.com"
password = "123456"

config = {
    "apiKey": apikey,
    "authDomain": authdomain,
    "databaseURL": dburl}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(email, password)
'''

#----------------GymUser Class-----------------#
class GymUser:
    card_scanned = ''
    sutdid_input = ''
    machine_choice = ''
    booking_dict = {'Bench Machine':[],'Squat Machine':[],'Deadlift Machine':[]}    
    
    def create_user(self,card,sutdid,machine,duration,start_time,end_time):
        self.card = card
        self.sutdid = sutdid
        self.machine = machine
        self.duration = duration
        self.start_time = start_time
        self.end_time = end_time
        
#----------------Main Kivy Code-----------------#
class ImageButton(ButtonBehavior, Image):
    pass

class HomeScreen(Screen, GymUser):    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def next_button(self):
        # the RFID should scan the card and store number in GymUser.card_scanned
        
        # check for & remove expired bookings
        for machine in GymUser.booking_dict:
            booking_list = GymUser.booking_dict[machine]
            for i in range(len(booking_list)):
                user = booking_list[i]
                if user.end_time < dt.datetime.now():
                    print("{}'s {} booking has expired".format(user.sutdid, machine))
                    booking_list.pop(i)
                          
class IDScreen(Screen, GymUser):    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def autofill_button(self):        
        '''
        Checks existence of ti_card in prev_profiles.txt
        Set the ti_card & ti_sutdid attribute for next page
        '''
        GymUser.card_scanned = self.ids.ti_cardid.text
        if os.path.isfile("prev_profiles.txt"):
            with open("prev_profiles.txt","r") as f:
                line = f.readline()
                while line:
                    profile = line.split(',')
                    if GymUser.card_scanned == profile[0]:
                        self.ids.ti_cardid.text = profile[0]
                        self.ids.ti_sutdid.text = profile[1].rstrip()                     
                        break
                    else:
                        self.ids.ti_cardid.text = GymUser.card_scanned
                    line = f.readline()
    
    def proceed_button(self):
        '''
        Creates a new profile if card num non-existent in prev_profiles.txt
        Clears the entries for Card & SUTD ID
        '''        
        GymUser.card_scanned = self.ids["ti_cardid"].text
        GymUser.sutdid_input = self.ids["ti_sutdid"].text
        
        if GymUser.card_scanned == '' or GymUser.sutdid_input == '':
            show_popup(1)
            return
        
        # create new profile if non-existent
        f = open("prev_profiles.txt", "r+")
        line = f.readline()
        exist = False
        while line:
            profile = line.split(',')
            # profile elements are strings
            if GymUser.card_scanned == profile[0]:
                exist = True
                break
            else:
                line = f.readline()    
        if exist == False:
            f.write(f"{GymUser.card_scanned},{GymUser.sutdid_input}" + '\n')
        f.close()
                    
        # clear entries
        self.manager.current = "Machine_screen"
        self.manager.transition.direction = "left"
        self.ids["ti_cardid"].text = ""
        self.ids["ti_sutdid"].text = ""

class MachineScreen(Screen, GymUser):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def change_dlcolor(self):
        self.ids['dl_button'].background_normal = ""
        self.ids['dl_button'].background_color = get_color_from_hex("#6200EE")
        self.ids['b_button'].background_normal = ""
        self.ids['b_button'].background_color = get_color_from_hex("#585858")
        self.ids['s_button'].background_normal = ""
        self.ids['s_button'].background_color = get_color_from_hex("#585858")
        GymUser.machine_choice = 'Deadlift Machine'
        
    def change_bcolor(self):
        self.ids['b_button'].background_normal = ""
        self.ids['b_button'].background_color = get_color_from_hex("#6200EE")
        self.ids['dl_button'].background_normal = ""
        self.ids['dl_button'].background_color = get_color_from_hex("#585858")
        self.ids['s_button'].background_normal = ""
        self.ids['s_button'].background_color = get_color_from_hex("#585858")
        GymUser.machine_choice = 'Bench Machine'
        
    def change_scolor(self):
        self.ids['s_button'].background_normal= ""
        self.ids['s_button'].background_color = get_color_from_hex("#6200EE")
        self.ids['b_button'].background_normal = ""
        self.ids['b_button'].background_color = get_color_from_hex("#585858")
        self.ids['dl_button'].background_normal = ""
        self.ids['dl_button'].background_color = get_color_from_hex("#585858")
        GymUser.machine_choice = 'Squat Machine'      
        
    def check_machine_choice(self):
        if GymUser.machine_choice == '':
            show_popup(2)
            return
        else:
            # change & reset page
            self.manager.current = "Duration_screen"
            self.manager.transition.direction = "left"            
            self.ids['s_button'].background_normal= ""
            self.ids['s_button'].background_color = get_color_from_hex("#585858")
            self.ids['b_button'].background_normal = ""
            self.ids['b_button'].background_color = get_color_from_hex("#585858")
            self.ids['dl_button'].background_normal = ""
            self.ids['dl_button'].background_color = get_color_from_hex("#585858")
            
    
class  DurationScreen(Screen, GymUser):    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def book_button(self):
        '''
        Checks previous bookings, creates new GymUser object, 
        adds new item into booking_list
        '''
        if self.ids.ti_duration.text == '' or int(self.ids.ti_duration.text) > 20 or int(self.ids.ti_duration.text) == 0:
            show_popup(3)
            return
              
        machine_choice = GymUser.machine_choice
        duration = int(self.ids.ti_duration.text)
        card = GymUser.card_scanned
        sutdid = GymUser.sutdid_input
               
        # initialise start time
        n = len(GymUser.booking_dict[GymUser.machine_choice])
        if n == 0:
            # if the user is the first
            start_time = dt.datetime.now()
        else:
            # refer to last booking's end_time
            start_time = GymUser.booking_dict[GymUser.machine_choice][n-1].end_time
        end_time = start_time + dt.timedelta(minutes = duration)

        # check whether got previous bookings by same user
        if has_previous_bookings(sutdid, machine_choice) == True or has_concurrent_bookings(sutdid, machine_choice, start_time) == True:
            show_popup(4)
            return
        
        # change & reset page
        self.manager.current = "Queue_screen"
        self.manager.transition.direction = "left"
        self.ids.ti_duration.text = ''

        # create new GymUser object & add to machine's booking_list
        new_user = GymUser()
        GymUser.create_user(new_user,card,sutdid,machine_choice
                            ,duration,start_time,end_time)
        GymUser.booking_dict[machine_choice].append(new_user)
        
        # update Firebase
        
        bench_users =len(GymUser.booking_dict['Bench Machine'])
        deadlift_users = len(GymUser.booking_dict['Deadlift Machine'])
        squat_users = len(GymUser.booking_dict['Squat Machine'])
        machine_users = {'Bench Machine': bench_users,
                         'Deadlift Machine': deadlift_users, 
                         'Squat Machine': squat_users}
        #db.child("Machine Users").set(machine_users, user['idToken'])
        
def has_previous_bookings(sutdid, machine_choice):
    
    booking_list = GymUser.booking_dict[machine_choice]
    
    if len(booking_list) == 0:
        return False
    
    for user in booking_list:
        if user.sutdid == sutdid:
            prev_booking = True
            break
        prev_booking = False        
    return prev_booking

def has_concurrent_bookings(sutdid, machine_choice, new_start_time):
    for machine in GymUser.booking_dict:
        if machine != machine_choice:
            booking_list = GymUser.booking_dict[machine]      # loops through the other 2 machines
            for i in range(len(booking_list)):                # loops through the users in the booking_list
                user = booking_list[i]            
                if user.sutdid == sutdid:                     # if user has another booking
                    other_start_time = user.start_time 
                    other_end_time = user.end_time
                    if other_start_time < new_start_time and new_start_time < other_end_time:    # if booking overlaps
                        return True
    return False
    
class QueueScreen(Screen, GymUser):
    booking_notice = StringProperty()
    box1 = StringProperty()
    box2 = StringProperty()
    box3 = StringProperty()
    box4 = StringProperty()
    box5 = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.booking_notice = 'Press Display Queue'
        self.box1 = '-'
        self.box2 = '-'
        self.box3 = '-'
        self.box4 = '-'
        self.box5 = '-'
        
    def print_booking(self):
        booking_list = GymUser.booking_dict[GymUser.machine_choice]
        user = booking_list[len(booking_list)-1]
        
        start_time = user.start_time
        end_time = start_time + dt.timedelta(minutes = user.duration)
        
        # format timing to strings
        start_str = dt.datetime.strftime(start_time, '%H:%M')
        end_str = dt.datetime.strftime(end_time, '%H:%M')
        self.booking_notice = "{} has booked the {} for {} mins\n Your session is from {} to {}".format(user.sutdid,user.machine,user.duration,start_str,end_str)
        
        # fill up the display boxes for the queue
        for i in range(5):
            if i < len(booking_list):
                prev_user = booking_list[i]
                startstr = dt.datetime.strftime(prev_user.start_time, '%H:%M')
                endstr = dt.datetime.strftime(prev_user.end_time, '%H:%M')
                if i == 0:
                    self.box1 = "{}\n {} to {}".format(prev_user.sutdid,startstr,endstr)
                elif i == 1:
                    self.box2 = "{}\n {} to {}".format(prev_user.sutdid,startstr,endstr)
                elif i == 2:
                    self.box3 = "{}\n {} to {}".format(prev_user.sutdid,startstr,endstr)
                elif i == 3:
                    self.box4 = "{}\n {} to {}".format(prev_user.sutdid,startstr,endstr)
                elif i == 4:
                    self.box5 = "{}\n {} to {}".format(prev_user.sutdid,startstr,endstr)

GUI = Builder.load_file("kv/main.kv")

#--------Popup Error Messages--------#

class P1(FloatLayout):
    pass
          
class P2(FloatLayout):
    pass

class P3(FloatLayout):
    pass

class P4(FloatLayout):
    pass

def show_popup(n):
    if n==1:
        show = P1()
    elif n==2:
        show = P2()
    elif n==3:
        show = P3()
    elif n==4:
        show = P4()
    
    popupWindow = Popup(title="Error Message",
                        title_size="22sp",
                        content = show,
                        size_hint=(None, None),
                        size=(400,400))
    popupWindow.open()    
    

class GymNowApp(App):
    def build(self):
        return GUI

    def change_screen(self, screen_name):
        # print(self.root.ids)
        # screen_manager is a dictionary holding all the screen names
        screen_manager = self.root.ids['screen_manager'] 
        screen_manager.current = screen_name
        
# create sample queue: 3 for Bench, 2 for Deadlift, 3 for Squat
f = open('prev_profiles.txt',"r")
line = f.readline()
is_first_user = True
for i in range(5):
    if i < 3:
        machine_choice = 'Bench Machine'
    elif i < 5:
        machine_choice = 'Deadlift Machine'
    else:
        machine_choice = 'Squat Machine' 
    
    # if first user created for each machine
    if i == 0 or i == 3 or i == 5:
        start_time = dt.datetime.now()
    else:
        start_time = end_time
    end_time = start_time + dt.timedelta(minutes = 10)
    profile = line.split(',')
    card = profile[0]
    sutdid = profile[1].rstrip()

    new_user = GymUser()
    GymUser.create_user(new_user,card,sutdid,machine_choice,10,start_time,end_time)
    GymUser.booking_dict[machine_choice].append(new_user)
    line = f.readline()        
f.close()

GymNowApp().run()