from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.app import App

class Banner(BoxLayout):
    '''
        The banner class is of the form of a horizontal box layout. 
        The box widget contains a label on the left and button on the right.
        The button serves as the main backwards navigation throughout the app and as the logout button on the main menu.
        The label is to give a title for which level you are on. 
    '''
    title = StringProperty('')
    buttontext = StringProperty('')
    
    def __init__ (self, title, buttonlabel, userid):
        '''
            The instantiation of the banner is to set the text of the button and the screen the button will switch the app to. 
            
            Arguments:
                title - Used for the text in the label.
                buttonlabel - Used to determine the text on the button.
        '''
        super(Banner, self).__init__()
        if title != False:
            self.title = title
        else:
            self.title = ''

        self.userid = userid        
        if userid != 0:
            self.buttontext = 'Profile'
        else:
            # To determine the text of the button.
            if buttonlabel == 1:
                self.buttontext = 'Back'
            elif buttonlabel == 2:
                self.buttontext = 'Logout'
            elif buttonlabel == 3:
                self.buttontext = 'Back'    
            elif buttonlabel == 4:
                self.buttontext = 'Close'    
            else:
                self.buttontext = ''


    def back(self):
        '''
            This function will run when the button is pressed. 
            Firstly it changes the direction of transition, then it changes the screen,
            then sets the direction of transition back to what it was.
            Then the screen is removed from the screen manager.
        '''    
        self.get_root_window().children[0].back()

    def showprofile(self):
        if self.userid != 0:
            self.get_root_window().children[0].changescreen(Profile(str(self.userid), 'ProfileScreen'))
        
        
class PopupSc(Popup):

    def __init__ (self, popuptitle, popuptxt):
        super(PopupSc, self).__init__()
        self.title = popuptitle
        self.size_hint = (None, None)
        self.size = (300, 300)
        box = BoxLayout(orientation = 'vertical')
        box.add_widget(Label(text = popuptxt, text_size = (dp(250), None)))
        box.add_widget(Button(background_normal = 'images/green20030.png', text = 'Close', on_release = self.dismiss, size_hint_y = None, height = dp(30)))
        self.add_widget(box)
        
    def on_open(self):
        activepopup = self
        
    def on_leave(self):
        activepopup = False
        

from profilescreen import Profile
