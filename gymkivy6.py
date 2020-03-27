import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

import datetime as dt
import os

kivy.require("1.11.1")

################################################
#              GymUser Class                   #
################################################
        
class GymUser:
    card_scanned = ''
    sutdid_input = ''
    machine_choice = ''
    booking_dict = {'Bench Machine':[],'Squat Machine':[],'Deadlift Machine':[]}
    current_gym_users = 0                   # double counts 1 user with 2 machine bookings
    b_users = len(booking_dict['Bench Machine'])
    dl_users = len(booking_dict['Deadlift Machine'])
    s_users = len(booking_dict['Squat Machine'])
    
    def create_user(self,card,sutdid,machine,duration,start_time,end_time):
        self.card = card
        self.sutdid = sutdid
        self.machine = machine
        self.duration = duration
        self.start_time = start_time
        self.end_time = end_time
        
        GymUser.current_gym_users += 1
        print('Gym User Created! current_gym_users: ',GymUser.current_gym_users)
    
    @classmethod
    def from_string(cls, profile_str):
        
        '''
        Creates new GymUser object from a string
        profile_str1 = '222000000005555,1005555'
        new_user = GymUser.from_string(profile_str1)
        '''
        
        card, sutdid = profile_str.split(',')
        return cls(card,sutdid)

        
################################################
#                   SCREENS                    #
################################################

class WindowManager(ScreenManager):
    pass
            
    
class HomePage(Screen, GymUser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def next_button(self):
        # simulate the scanning of the card
        # error message if unsuccessful scan
        GymUser.card_scanned = self.ti_next.text
    
    
class IDPage(Screen, GymUser):   
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
               
    def checkdb_button(self):
        
        '''
        Checks existence of ti_card in prev_profiles.txt
        Set the ti_card & ti_sutdid attribute for next page
        '''
        
        if os.path.isfile("prev_profiles.txt"):
            with open("prev_profiles.txt","r") as f:
                line = f.readline()
                while line:
                    profile = line.split(',')
                    if GymUser.card_scanned == profile[0]:
                        self.ti_card.text = profile[0]
                        self.ti_sutdid.text = profile[1].rstrip()                     
                        break
                    line = f.readline()              
        else:
            # should show error message, 'Profile Not Found'
            self.ti_card.text = GymUser.card_scanned
                    
                    
    def proceed_button(self):
        '''
        Creates a new profile if card num non-existent in prev_profiles.txt
        Clears the entries for Card & SUTD ID
        '''
        
        GymUser.card_scanned = self.ti_card.text
        GymUser.sutdid_input = self.ti_sutdid.text
        
        if GymUser.card_scanned == '' or GymUser.sutdid_input == '':
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
        self.ti_card.text = ""
        self.ti_sutdid.text = ""                        
        
        
class MachinePage(Screen, GymUser):
    
    def change_bcolor(self):
        self.ids['dl_button'].background_color = 1,1,1,1
        self.ids['b_button'].background_color = 0,1,0,1
        self.ids['s_button'].background_color = 1,1,1,1
        GymUser.machine_choice = 'Bench Machine'
    
    def change_dlcolor(self):
        self.ids['dl_button'].background_color = 0,1,0,1
        self.ids['b_button'].background_color = 1,1,1,1
        self.ids['s_button'].background_color = 1,1,1,1
        GymUser.machine_choice = 'Deadlift Machine'
        
    def change_scolor(self):
        self.ids['dl_button'].background_color = 1,1,1,1
        self.ids['s_button'].background_color = 0,1,0,1
        self.ids['b_button'].background_color = 1,1,1,1
        GymUser.machine_choice = 'Squat Machine'
            
    def book_button(self):
        '''
        Checks previous bookings, creates new GymUser object, adds new item into booking_list
        '''
        if self.ids.ti_duration.text == '' or no_machine_choice(self):
            return
        
        machine_choice = GymUser.machine_choice
        duration = int(self.ids.ti_duration.text)
        card = GymUser.card_scanned
        sutdid = GymUser.sutdid_input
        
        # check whether got previous bookings by same user
        if has_previous_bookings(sutdid, machine_choice) == True:
            print('Error Message: User has made a previous booking')
            return
               
        # initialise start time
        n = len(GymUser.booking_dict[GymUser.machine_choice])
        if n == 0:
            # if the user is the first user
            start_time = dt.datetime.now()
        else:
            # refer to last booking's end_time
            start_time = GymUser.booking_dict[GymUser.machine_choice][n-1].end_time

        # create new GymUser object
        end_time = start_time + dt.timedelta(minutes = duration)
        new_user = GymUser()
        GymUser.create_user(new_user,card,sutdid,machine_choice,duration,start_time,end_time)
        
        # add user to the machine's booking_list
        GymUser.booking_dict[machine_choice].append(new_user)
        
        # change page
        self.manager.current = "Queue"
        self.manager.transition.direction = "left"
        
        # reset MachinePage
        self.ids.ti_duration.text = ''
        self.ids['dl_button'].background_color = 1,1,1,1
        self.ids['s_button'].background_color = 1,1,1,1
        self.ids['b_button'].background_color = 1,1,1,1
        
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

def no_machine_choice(self):
    if self.ids['dl_button'].background_color == (1,1,1,1):
        if self.ids['s_button'].background_color == (1,1,1,1):
            if self.ids['b_button'].background_color == (1,1,1,1):
                return True
    else:
        return False
        
class QueuePage(Screen, GymUser):
    # convert all the labels StringProperty objects
    booking_notice = StringProperty()
    pos1 = StringProperty()
    pos2 = StringProperty()
    pos3 = StringProperty()
    pos4 = StringProperty()
    pos5 = StringProperty()
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.booking_notice = 'Hello!'
        self.pos1 = '-'
        self.pos2 = '-'
        self.pos3 = '-'
        self.pos4 = '-'
        self.pos5 = '-'
                
    def print_booking(self):

        booking_list = GymUser.booking_dict[GymUser.machine_choice]
        user = booking_list[len(booking_list)-1]
        
        start_time = user.start_time
        end_time = start_time + dt.timedelta(minutes = user.duration)
        
        # format timing to strings
        start_str = dt.datetime.strftime(start_time, '%H:%M')
        end_str = dt.datetime.strftime(end_time, '%H:%M')
        
        self.booking_notice = "{} has booked the {} for {} mins\n Your session is from {} to {}".format(user.sutdid,user.machine,user.duration,start_str,end_str)
        
        for i in range(5):
            if i < len(booking_list):
                prev_user = booking_list[i]
                startstr = dt.datetime.strftime(prev_user.start_time, '%H:%M')
                endstr = dt.datetime.strftime(prev_user.end_time, '%H:%M')
                if i == 0:
                    self.pos1 = "{}\n {} to {}".format(prev_user.sutdid,startstr,endstr)
                elif i == 1:
                    self.pos2 = "{}\n {} to {}".format(prev_user.sutdid,startstr,endstr)
                elif i == 2:
                    self.pos3 = "{}\n {} to {}".format(prev_user.sutdid,startstr,endstr)
                elif i == 3:
                    self.pos4 = "{}\n {} to {}".format(prev_user.sutdid,startstr,endstr)
                elif i == 4:
                    self.pos5 = "{}\n {} to {}".format(prev_user.sutdid,startstr,endstr)
                
#         for i,pos in enumerate([self.pos1,self.pos2,self.pos3,self.pos4,self.pos5]):
#             print(i,pos)
#             prev_user = booking_list[i]
#             startstr = dt.datetime.strftime(prev_user.start_time, '%H:%M')
#             endstr = dt.datetime.strftime(prev_user.end_time, '%H:%M')
#             pos = "{}\n {} to {}".format(prev_user.sutdid,startstr,endstr)
            
    def reset(self):
        self.booking_notice = 'Hello!'
        
            
class GymApp(App):
    def build(self):             
        return kv    
    
# sample queue for Squat
f = open('prev_profiles.txt',"r")
line = f.readline()
for i in range(2):
    if i == 0:
        start_time = dt.datetime.now()
    else:
        start_time = end_time
    end_time = start_time + dt.timedelta(minutes = 10)
    
    profile = line.split(',')
    card = profile[0]
    sutdid = profile[1].rstrip()
    
    new_user = GymUser()
    GymUser.create_user(new_user,card,sutdid,'Squat Machine',10,start_time,end_time)
    GymUser.booking_dict['Squat Machine'].append(new_user)
    line = f.readline()
f.close()

# # create sample queue for Bench
# f = open('prev_profiles.txt',"r")
# for i in range(6):
#     line = f.readline()
    
# for i in range(3):
#     if i == 0:
#         start_time = dt.datetime.now()
#     else:
#         start_time = end_time
#     end_time = start_time + dt.timedelta(minutes = 10)
    
#     profile = line.split(',')
#     card = profile[0]
#     sutdid = profile[1].rstrip()
    
#     new_user = GymUser()
#     GymUser.create_user(new_user,card,sutdid,'Bench Machine',10,start_time,end_time)
#     GymUser.booking_dict['Bench Machine'].append(new_user)
#     line = f.readline()
# f.close()
        
kv = Builder.load_file("gym4.kv")
    
if __name__ == "__main__":
        gym_app = GymApp()
        gym_app.run()