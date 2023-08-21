import kivy
kivy.require('1.8.0')
__version__ = '0.0.23'

import sqlite3
#import sphinx
from datetime import datetime
import hashlib

from kivy.utils import platform
plat = platform
if plat == 'android':
    filehome = ''
elif plat == 'ios':
    pass
else:
    from kivy.config import Config
    Config.set('graphics', 'width', '320')
    Config.set('graphics', 'height', '480')
    import inspect
    filehome = inspect.getfile(inspect.currentframe())[:-7]

import os
# Importing the kivy widgets used.
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import *
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import Image, AsyncImage
from kivy.uix.rst import RstDocument
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from shared import Banner, PopupSc
from profile import Profile
from content import LevelSelect
#from .sql.createdatabase import createdatabase
from updatedatabase import updatesatabase

# Active Popup
activepopup = False


class CreateAccount(Screen):

    def __init__(self, name):
        self.name = name
        # Creating the layout of create account screen.
        super(CreateAccount, self).__init__()
        self.canvas.add(Rectangle(source = 'images/createaccountpage.png', pos = (0, dp(30)), size = (Window.width, Window.height - dp(60))))
        box = BoxLayout(orientation = 'vertical')
        box.add_widget(Banner(False, 3, 0))
        box.add_widget(Label(text = ''))
        grid = GridLayout(cols = 2, size_hint_y = None, height = dp(120))
        grid.add_widget(Label(text = 'Username', size_hint_y = None, height = dp(40)))
        self.tbusername = TextInput(text = '', size_hint_y = None, height = dp(40), multiline = False, on_text_validate = self.on_enter_username)
        grid.add_widget(self.tbusername)
        grid.add_widget(Label(text = 'Password', size_hint_y = None, height = dp(40)))
        self.tbpassword1 = TextInput(text = '', password = True, size_hint_y = None, height = dp(40), multiline=False, on_text_validate = self.on_enter_password1)
        grid.add_widget(self.tbpassword1)
        grid.add_widget(Label(text = 'Confirm Password', size_hint_y = None, height = dp(40)))
        self.tbpassword2 = TextInput(text = '', password = True, size_hint_y = None, height = dp(40), multiline=False, on_text_validate = self.createuseraccount)
        grid.add_widget(self.tbpassword2)
        box.add_widget(grid)
        box.add_widget(Button(text = 'Submit', on_press = self.createuseraccount, background_normal = 'images/orange32030.png', background_down = 'images/blue32025.png', size_hint_y = None, height = dp(30)))
        self.add_widget(box)

    def on_enter_username(self, a):
        self.tbpassword1.focus = True 

    def on_enter_password1(self, a):
        self.tbpassword2.focus = True 
                
    def createuseraccount(self, a):
        if self.tbusername.text == '' or self.tbpassword1.text == '' or self.tbpassword2.text == '':
            PopupSc('Error', 'You have failed to enter all the required items, please try again.').open()
        elif self.tbpassword1.text != self.tbpassword2.text:
            PopupSc('Error', 'The entered passwords are not the same, please try again').open()
        elif len(self.tbpassword1.text) < 8:
            PopupSc('Error', 'The entered password is not long enough, please try again with a password of at least 8 characters.').open()
        else:
            hashpass = hashlib.sha512(self.tbpassword1.text.encode('utf-8')).hexdigest()
            conn = sqlite3.connect(filehome + 'database.db')
            c = conn.cursor()
            try:
                query = c.execute('''INSERT INTO users (username, password, datecreated) VALUES (?, ?, ?)''', (self.tbusername.text, hashpass, datetime.now()))  # Adding a new user to the database
                conn.commit()
                PopupSc('Account created', 'Your account has been created successfully, you may now login.').open()  # On app confirmation of a new user being added.
                self.parent.back()
            except Exception as error: 
                if str(error) == 'column username is not unique':
                    errormess = 'Username is taken use. Please try a different username.'
                elif str(error) == 'column email is not unique':
                    errormess = 'Email is used. Please try a different email.'
                else:
                    errormess = 'Unknown error: ' + str(error)
                PopupSc('Error', errormess).open()  # Displays an error message.
                conn.rollback()  # If an error occurs the pending changes to the database are discarded.
            conn.close()  # Closes the database connection.
            self.tbusername.text = ''
        self.tbpassword1.text = ''
        self.tbpassword2.text = ''
                
        
class LoginScreen(Screen):
    
    def userlogin(self):
        '''
            This function checks to see if a valid username and password have been entered.
        '''
        if self.ids.tbUsername.text == '':  # Check to see if a username has been entered.
            PopupSc('Username not entered', 'A user name was not entered, please try again.').open()  # Error message if username is not entered.
        elif self.ids.tbPassword.text == '':  # Check to see if a password has been entered.
            PopupSc('Password not entered', 'A passwords was not entered, please try again.').open()  # Error message if password is not entered.
        else:
            hashedpassword = hashlib.sha512(self.ids.tbPassword.text.encode('utf-8')).hexdigest()
            self.ids.tbPassword.text = ''
            conn = sqlite3.connect(filehome + 'database.db')
            c = conn.cursor()
            query1 = c.execute('''SELECT COUNT(*) FROM users WHERE username = ?''', (self.ids.tbUsername.text,))
            usercount = query1.fetchone()[0]
            if usercount == 1:
                query = c.execute('''SELECT userid, username, password FROM users WHERE username = ?''', (self.ids.tbUsername.text,))
                a = query.fetchone()
                if hashedpassword == a[2]:  # Checks the password with the password found in the database.
                    c1 = conn.cursor()
                    query = c1.execute('''UPDATE users SET lastlogin = ? WHERE userid = ?''', (datetime.now(), a[0]))
                    conn.commit()
                    if self.parent.has_screen('menu'):
                        self.parent.changeexistingscreen('menu')
                    else:
                        self.parent.changescreen(LevelSelect(a[1], a[0], name = 'menu'))
                else:
                    PopupSc('Incorrect password', 'The entered password was incorrect, please try again.').open()
            else:
                # If no records are returned then the username doesn't exist.
                PopupSc('User does not exists', 'The entered username does not exist, please try again.').open()
            conn.close()  # Close the database connection. 
        
    def on_leave(self):
        '''
            For security reasons the text boxes are empted when the user moves away from the login screen.
        '''
        self.ids.tbUsername.text = ''
        self.ids.tbPassword.text = ''

    def createaccount(self):
        '''
            createaccount will create an instance of the createaccount screen and add it to the screen manager and display the screen on the app.
        '''
        #CreateAccountScreen = CreateAccount(name = 'CreateAccount')
        self.parent.changescreen(CreateAccount(name = 'CreateAccount'))


class ScrMan(ScreenManager):
    screenlist = []
    
    def back(self):
        self.transition = SlideTransition(direction = 'right')
        self.current = self.screenlist.pop().name
        self.transition = SlideTransition(direction = 'left')  # When the user logs off we need to remove all the screens that the user used. 
        
        if self.current_screen.name == 'login':
            for i in self.screens[1:]:  # The first screen in the list is the login screen, we don't want to remove this. 
                self.remove_widget(i)
                
    def changescreen(self, screen):
        self.add_widget(screen)
        self.screenlist.append(self.current_screen)
        self.current = screen.name
                        
    def changeexistingscreen(self, screenname):
        self.screenlist.append(self.current_screen)
        self.current = screenname
        

class Main(App):

	def on_start(self):
		if os.path.isfile('version.txt'):	
			file = open('version.txt', 'r')
			versionfile = file.readline()
			print(versionfile)
			file.close()
			if __version__ != versionfile:
				updatesatabase(versionfile)
				file = open('version.txt', 'w')
				file.write(__version__)
				file.close()
		else:
			updatesatabase('NewInstall')
			file = open('version.txt', 'w')
			file.write(__version__)
			file.close()
	
	def on_pause(self):
		return True

	def on_resume(self):
		pass

	def build(self):
		self.icon = 'images/appicon.png'
		self.title = 'EduMath'
		Clock.max_iteration = 40
		Window.bind(on_keyboard=self.hook_keyboard) 	
		Window.clearcolor = (0.3254, 0.3254, 0.3254, 1)
		print(App.get_application_config(self))
		# Declare the screen manager
		self.sm = ScrMan() 
		self.sm.add_widget(LoginScreen(name='login'))  # Adds the login screen to the screen manager
		return self.sm  # The screen manager is returned as the root widget. As the login screen is the only screen then it is displayed when the app starts.

	def hook_keyboard(self, window, key, *largs):
		'''
			Function to allow the android back button
		'''
		if key == 27: # BACK
			if activepopup == False:
				self.sm.back()
			else:
				activepopup.dismiss
		#elif key in (282, 319): # SETTINGS
		#	pass
		return True


if __name__ == '__main__':
    Main().run()
