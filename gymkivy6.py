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

import datetime
import os

kivy.require("1.11.1")

################################################
#              GymUser Class                   #
################################################

card = '222000000002222'    

class GymUser:
    booking_details = [None,None,None,None]
    current_gym_users = 0
    
    def create_user(self, card, sutdid):
        self.card = card
        self.sutdid = sutdid
        self.machine = ''
        self.duration = ''
        
        GymUser.current_gym_users += 1
    
    @classmethod
    def from_string(cls, profile_str):
        
        '''
        Creates new GymUser object from a string
        profile_str1 = '222000000005555,1005555'
        new_user = GymUser.from_string(profile_str1)
        '''
        
        card, sutdid = profile_str.split(',')
        return cls(card,sutdid)
    
class SquatUser(GymUser):
    squat_users = 0
    '''
    Work in progress
    '''
    
    def __init__(self,card,sutdid,duration):
        super().__init__(card,sutdid)        
        self.duration = duration
        
        squat_users += 1
        
################################################
#                   SCREENS                    #
################################################

class WindowManager(ScreenManager):
    booking_details = ['','','','']  
            
        
        
        
class HomePage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def next_button(self):
        # function to scan card on RFID reader
        pass
    
    
        
class IDPage(Screen):   
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
                    # print(profile)
                    if card == profile[0]:
                        self.ti_card.text = profile[0]
                        self.ti_sutdid.text = profile[1]                      
                        break
                    line = f.readline()              
        else:
            f = open("prev_profiles.txt","w")
            f.close()
        
        
               
            
    def proceed_button(self):
        '''
        Creates a new profile if card num non-existent in prev_profiles.txt
        Clears the entries for Card & SUTD ID
        '''
        
        card = self.ti_card.text
        sutdid = self.ti_sutdid.text
        
        if card == '' or sutdid == '':
            return
        
        # create new profile if non-existent
        f = open("prev_profiles.txt", "r+")
        line = f.readline()
        exist = False
        while line:
            profile = line.split(',')
        # profile elements are strings
            if card == profile[0]:
                exist = True
                break
            else:
                line = f.readline()    
        if exist == False:
            f.write(f"{card},{sutdid}" + '\n')
        f.close()
                    
        # clear entries
        self.ti_card.text = ""
        self.ti_sutdid.text = ""                
        
        
        
        
class MachinePage(Screen, GymUser):
    machine_choice = ''
    
    def change_dlcolor(self):
        self.ids['dl_button'].background_color = 0,1,0,1
        self.ids['b_button'].background_color = 1,1,1,1
        self.ids['s_button'].background_color = 1,1,1,1
        MachinePage.machine_choice = 'deadlift'
        
    def change_bcolor(self):
        self.ids['dl_button'].background_color = 1,1,1,1
        self.ids['b_button'].background_color = 0,1,0,1
        self.ids['s_button'].background_color = 1,1,1,1
        MachinePage.machine_choice = 'bench'
        
    def change_scolor(self):
        self.ids['dl_button'].background_color = 1,1,1,1
        self.ids['s_button'].background_color = 0,1,0,1
        self.ids['b_button'].background_color = 1,1,1,1
        MachinePage.machine_choice = 'squat'
            
    def book_button(self):
        
        # take TextInput from ti_duration
        # booking_list = card + sutdid + machine_choice + ti_duration
        
        machine_choice = MachinePage.machine_choice
        duration = self.ids.ti_duration.text
        
        # create new GymUser object
        with open("prev_profiles.txt","r") as f:
            line = f.readline()
            while line:
                profile = line.split(',')
                if card == profile[0]:
                    sutdid = profile[1].rstrip()
                    break
                line = f.readline()
        
        new_user = GymUser()
        GymUser.create_user(new_user,card,sutdid)
        GymUser.booking_details = [card, sutdid, machine_choice, duration]
               
        print('Machine print:', GymUser.booking_details)
        
        
        
        
class QueuePage(Screen, GymUser):
    booking_notice = StringProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.booking_notice = 'Hello!'
                
    def print_booking(self):
        details = GymUser.booking_details
        sutdid = details[1]
        machine = details[2]
        duration = details[3]
        self.booking_notice = "{} has booked {} for {} mins".format(sutdid,machine,duration)
        
            
    
    
class GymApp(App):
    def build(self):             
        return kv    
        
        
        
        
kv = Builder.load_file("gym4.kv")
    
if __name__ == "__main__":
        gym_app = GymApp()
        gym_app.run()