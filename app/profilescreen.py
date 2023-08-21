import sqlite3
import hashlib

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from kivy.utils import platform
plat = platform
if plat == 'android':
    filehome = ''
elif plat == 'ios':
    pass
else:
    import inspect
    filehome = inspect.getfile(inspect.currentframe())[:-16]


class Profile(Screen):

    def __init__(self, currentuserid, name):
        super(Profile, self).__init__()
        self.currentuserid = currentuserid 
        self.name = name
        # Getting data from the database
        conn = sqlite3.connect(filehome + 'database.db')
        c = conn.cursor()
        username = c.execute('''SELECT username FROM users WHERE userid = ?;''', (self.currentuserid,))
        self.username = username.fetchone()[0]
        quizresults = c.execute('''SELECT quizs.quizname, MAX(quizresults.mark) FROM quizs, quizresults WHERE quizs.quizid = quizresults.quizid AND quizresults.userid = ? GROUP BY quizs.quizname;''', (self.currentuserid,))
        self.quizresults = [[a for a in i] for i in quizresults]
        conn.close()
        
        self.box = BoxLayout(orientation = 'vertical')
        self.box.add_widget(Banner('Profile', 4, 0))
        
        self.box.add_widget(Label(text = 'Hello ' + self.username, size_hint_y = 0.5))
        self.box.add_widget(Button(text = 'Edit profile', on_press = self.editprofile, size_hint_y = None, height = dp(30), background_normal = 'images/orange32030.png', background_down = 'images/blue32025.png'))        

        self.box.add_widget(Label(text = 'Something else?'))

        self.quizbox = BoxLayout(orientation = 'vertical', size_hint_y = 1.5)
        self.quizbox.add_widget(Label(text = 'Quiz Results', size_hint_y = None, height = dp(30)))
        self.quizgridheader = GridLayout(cols = 2, size_hint_y = None, height = dp(30))
        self.quizgridheader.add_widget(Label(text = 'Level'))
        self.quizgridheader.add_widget(Label(text = 'Best Mark'))
        self.quizbox.add_widget(self.quizgridheader)
        self.quizgrid = GridLayout(cols = 2, size_hint_y = None, height = dp(30 * len(self.quizresults)))
        for a in self.quizresults:
            self.quizgrid.add_widget(Label(text = a[0]))
            self.quizgrid.add_widget(Label(text = str(a[1])))
        self.scroller = ScrollView()
        self.scroller.add_widget(self.quizgrid)
        self.quizbox.add_widget(self.scroller)
        self.box.add_widget(self.quizbox)

        self.box.add_widget(Button(text = 'Logout', on_press = self.logout, size_hint_y = None, height = dp(30), background_normal = 'images/blue32025.png', background_down = 'images/orange32030.png'))    
        self.add_widget(self.box)

    def logout(self, a):
        pass

    def editprofile(self, a):
        ChangePassword(self.currentuserid).open()

    #def on_leave(self):
        #self.parent.remove_widget(self)


class ChangePassword(Popup):

    def __init__(self, userid):
        super(ChangePassword, self).__init__()
        self.title = 'Change password'
        self.size_hint = (None, None)        
        self.size = (dp(300), dp(220))
        self.userid = userid
    
        grid = GridLayout(cols = 2)
        grid.add_widget(Label(text = 'Current Password', size_hint_y = None, height = dp(40)))
        self.tbcurrentpassword = TextInput(text = '', password = True, size_hint_y = None, height = dp(40), multiline=False, on_text_validate = self.on_enter_tbcurrentpassword)
        grid.add_widget(self.tbcurrentpassword)
        grid.add_widget(Label(text = 'New Password', size_hint_y = None, height = dp(40)))
        self.tbpassword1 = TextInput(text = '', password = True, size_hint_y = None, height = dp(40), multiline=False, on_text_validate = self.on_enter_tbpassword1)
        grid.add_widget(self.tbpassword1)
        grid.add_widget(Label(text = 'Confirm Password', size_hint_y = None, height = dp(40)))
        self.tbpassword2 = TextInput(text = '', password = True, size_hint_y = None, height = dp(40), multiline=False, on_text_validate = self.updatepass)
        grid.add_widget(self.tbpassword2)
        grid.add_widget(Button(text = 'Change Password', size_hiny_y = None, height = dp(30), background_normal = 'images/16038.png', background_down = 'images/16038.png', on_release = self.updatepass))
        grid.add_widget(Button(text = 'Close', size_hiny_y = None, height = dp(30), background_normal = 'images/16038.png', background_down = 'images/16038.png', on_release = self.dismiss))
        self.add_widget(grid)

    def on_enter_tbcurrentpassword(self, a):
        self.tbpassword1.focus = True

    def on_enter_tbpassword1(self, a):
        self.tbpassword2.focus = True

    def on_open(self):
        activepopup = self
        
    def on_leave(self):
        activepopup = False
        self.tbcurrentpassword.text = ''
        self.tbpassword1.text = ''
        self.tbpassword2.text = ''

    def updatepass(self, a):
        if self.tbcurrentpassword.text == '':
            PopupSc('Error', 'You have failed to enter all the required information, please try again').open()
        elif self.tbpassword1.text == '':
            PopupSc('Error', 'You have failed to enter all the required information, please try again').open()
        elif self.tbpassword2.text == '':
            PopupSc('Error', 'You have failed to enter all the required information, please try again').open()
        elif self.tbpassword1.text == self.tbpassword2.text:
            # Check current password is current
            hashcurrent = hashlib.sha512(self.tbcurrentpassword.text).hexdigest()
            conn = sqlite3.connect(filehome + 'database.db')
            c = conn.cursor()
            passcheck = c.execute('''SELECT password FROM users WHERE userid = ?;''', (self.userid,))
            a = passcheck.fetchone()
            if hashcurrent == a[0]:
                newhash = hashlib.sha512(self.tbpassword1.text).hexdigest()
                try:
                    c.execute('''UPDATE users SET password = ? WHERE userid = ?''', (newhash, self.userid))
                    conn.commit()
                    self.dismiss()
                    PopupSc('Message', 'You password has been changed.').open()
                except Exception as error:
                    PopupSc('Error', error).open()
            else:
                PopupSc('Error', 'The current password is incorrect, please try again').open()
            conn.close()
        else:    
            PopupSc('Error', 'The entered passwords are not the same, please try again').open()


from shared import Banner, PopupSc
