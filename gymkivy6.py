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
    
    def create_user(self,card,sutdid,machine,duration,end_time):
        self.card = card
        self.sutdid = sutdid
        self.machine = machine
        self.duration = duration
        self.end_time = end_time
        
        GymUser.current_gym_users += 1
        print('Gym User Created!\ncurrent_gym_users: ',GymUser.current_gym_users)
    
    @classmethod
    def from_string(cls, profile_str):
        
        '''
        Creates new GymUser object from a string
        profile_str1 = '222000000005555,1005555'
        new_user = GymUser.from_string(profile_str1)
        '''
        
        card, sutdid = profile_str.split(',')
        return cls(card,sutdid)

'''
different booking lists
display queue
'''    

        
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
                    print(profile)
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
               
        machine_choice = GymUser.machine_choice
        duration = int(self.ids.ti_duration.text)
        card = GymUser.card_scanned
        sutdid = GymUser.sutdid_input

        # create new GymUser object
        end_time = dt.datetime.now() + dt.timedelta(minutes = duration)
        new_user = GymUser()
        GymUser.create_user(new_user,card,sutdid,machine_choice,duration,end_time)
        
        # check whether got previous bookings by same user
        if no_previous_bookings(new_user, machine_choice) == False:
            print('Error Message that got previous bookings')
            return 
        
        # add user to the machine's booking_list
        GymUser.booking_dict[machine_choice].append(new_user)
        print(GymUser.booking_dict[machine_choice])
        
#         if machine_choice == 'Bench Machine':
#             GymUser.booking_list[0].append(new_user)
#             print('Bench booking_list:', GymUser.booking_list[0])
#         elif machine_choice == 'Deadlift Machine':
#             GymUser.booking_list[1].append(new_user)
#             print('DL booking_list:', GymUser.booking_list[1])
#         elif machine_choice == 'Squat Machine':
#             GymUser.booking_list[2].append(new_user)
#             print('Squat booking_list:', GymUser.booking_list[2])
        
        
        # reset MachinePage
        self.ids.ti_duration.text = ''
        self.ids['dl_button'].background_color = 1,1,1,1
        self.ids['s_button'].background_color = 1,1,1,1
        self.ids['b_button'].background_color = 1,1,1,1
        
def no_previous_bookings(user, machine_choice):
    check = GymUser.booking_dict[machine_choice]
    
    
class QueuePage(Screen, GymUser):
    booking_notice = StringProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.booking_notice = 'Hello!'
                
    def print_booking(self):
        # access last booking in the machine's booking_list
        if GymUser.machine_choice == 'Bench Machine':
            booking_list = GymUser.booking_list[0]
        elif GymUser.machine_choice == 'Deadlift Machine':
            booking_list = GymUser.booking_list[1]
        elif GymUser.machine_choice == 'Squat Machine':
            booking_list = GymUser.booking_list[2]
        
        n = len(booking_list)
        user = booking_list[n-1]
        sutdid = user.sutdid
        machine = user.machine
        duration = user.duration
                
        # initialise start time
        if n == 0:
            start_time = dt.datetime.now()
        else:
            # refer to last booking's end_time
            start_time = booking_list[n-2].end_time
        
        # convert datetime object to a string that can be formatted
        start_str = dt.datetime.strftime(start_time, '%H:%M')
        
        end_time = start_time + dt.timedelta(minutes = duration)
        end_str = dt.datetime.strftime(end_time, '%H:%M')
        
        self.booking_notice = "{} has booked the {} for {} mins\n Your session is from {} to {}".format(sutdid,machine,duration,start_str, end_str)
        
            
    
    
class GymApp(App):
    def build(self):             
        return kv    
        
kv = Builder.load_file("gym4.kv")
    
if __name__ == "__main__":
        gym_app = GymApp()
        gym_app.run()