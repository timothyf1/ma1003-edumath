import sqlite3
from kivy.metrics import dp
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import AsyncImage
from kivy.uix.rst import RstDocument
from kivy.uix.screenmanager import Screen

from kivy.utils import platform
plat = platform
if plat == 'android':
    filehome = ''
elif plat == 'ios':
    pass
else:
    import inspect
    filehome = inspect.getfile(inspect.currentframe())[:-10]

from shared import Banner, PopupSc
from quiz import QuizScreen


class LevelSelect(Screen):

    def __init__(self, username, userid, name):
        """

        """
        self.name = name
        self.username = username
        self.userid = userid
        super(LevelSelect, self).__init__()

        conn = sqlite3.connect(filehome + 'database.db')  # Opens the connection to the database.
        c = conn.cursor()
        levels = c.execute('''SELECT levelid, levelname, leveldesc FROM level''')  # Gets the levels from the database

        box = BoxLayout(orientation = 'vertical')
        box.add_widget(Banner(False, 2, self.userid))  # Adds the top banner, as this is the main menu we need a logout button and not a back button. 
        lvlAccordion = Accordion(orientation = 'vertical', min_space = dp(25), anim_duration = 1)
        for i in levels:
            item = AccordionItem(title = i[1], min_space = dp(25), background_normal='images/blue32025.png', background_selected='images/orange32025.png')    
            boxa = BoxLayout(orientation = 'vertical')
            lbl = Label(text = i[2], text_size = (300, None))
            boxa.add_widget(lbl)
            btn = Button(text = 'Go', id = str(i[0])+','+i[1], on_press = self.selectlevel, background_normal = 'images/orange32030.png', background_down = 'images/blue32025.png', size_hint_y = None, height = dp(30))
            boxa.add_widget(btn)
            item.add_widget(boxa)
            lvlAccordion.add_widget(item)
        box.add_widget(lvlAccordion)  # Adds the Accordion to the box
        self.add_widget(box)  # Adds the box widget to the screen
        conn.close()

    def selectlevel(self, levelid):
        '''
            levelid - This is the id of the button which was pressed, which is unique for each level. 
        '''
        lvl = levelid.id.split(',')
        if self.parent.has_screen('LevelListlevel' + lvl[0]):
            self.parent.changeexistingscreen('LevelListlevel' + lvl[0])
        else:
            self.parent.changescreen(LevelListScreen(self.username, self.userid, lvl[0], lvl[1], name = 'LevelListlevel' + lvl[0]))


class LevelListScreen(Screen):

    def __init__(self, username, userid, level, levelname, name):
        self.name = name
        self.username = username
        self.userid = userid
        self.level = level
        self.levelname = levelname
        super(LevelListScreen, self).__init__()
        
        # Get level sections from database.
        conn = sqlite3.connect(filehome + 'database.db')
        c = conn.cursor()
        levelsections = c.execute('''SELECT levelsectionid, levelsectionname, levelsectionimage FROM levelsection WHERE levelid = ?''', (level,))
        box = BoxLayout(orientation = 'vertical')
        box.add_widget(Banner(self.levelname, 1, self.userid))
        topAccordion = Accordion(orientation = 'vertical', min_space = dp(25), anim_duration = 1)
        
        # Adding an accordion item for each of the levelsections
        for i in levelsections:
            item = AccordionItem(title = i[1], min_space = dp(25), background_normal='images/blue32025.png', background_selected = 'images/orange32025.png')
            boxa = BoxLayout(orientation = 'vertical')
            boxa.add_widget(AsyncImage(source = i[2]))
            
            # Get topics for the current level section from the database.
            c1 = conn.cursor()
            levelsectiontopics = c1.execute('''SELECT topicid, topicname, topicpage FROM topics WHERE levelsectionid = ?''', (i[0],))
            
            # Add a button for each topic within the section
            for j in levelsectiontopics:
                boxa.add_widget(Button(text=j[1], id= j[1] + ',' + j[2], on_press = self.selecttopic, background_normal = 'images/orange32030.png', background_down = 'images/blue32025.png', size_hint_y = None, height = dp(30)))
            item.add_widget(boxa)
            topAccordion.add_widget(item)
        
        quizitem = AccordionItem(title = 'Quiz', min_space = dp(25), background_normal = 'images/blue32025.png', background_selected = 'images/orange32025.png')
        boxb = BoxLayout(orientation = 'vertical')
        boxb.add_widget(Label(text = 'Want to test your knowledge for this level?'))
        boxb.add_widget(Button(text = 'Quiz here', on_press = self.quiz, id = level, background_normal = 'images/orange32030.png', background_down = 'images/blue32025.png', size_hint_y = None, height = dp(30)))
        quizitem.add_widget(boxb)
        topAccordion.add_widget(quizitem)
        box.add_widget(topAccordion)
        self.add_widget(box)
        conn.close()
        
    def quiz(self, a):
        if self.parent.has_screen('Quiz' + a.id):
            self.parent.changeexistingscreen('Quiz' + a.id)
        else:
            self.parent.changescreen(QuizScreen(self.username, self.userid, a.id, name='Quiz' + a.id))

    def selecttopic(self, topicid):
        if topicid.id.split(',')[1] != '':
            if self.parent.has_screen('Topic' + topicid.id):
                self.parent.changeexistingscreen('Topic' + topicid.id)
            else:
                self.parent.changescreen(TopicScreen(topicid.id.split(',')[0], topicid.id.split(',')[1], self.userid, name='Topic' + topicid.id))
        else:
            PopupSc('Content unavailable', 'The selected topic, ' + topicid.id + ' is currently unavailable.').open()


class TopicScreen(Screen):    

    def __init__(self, topicname, topicfile, userid, name):
        super(TopicScreen, self).__init__()
        self.name = name
        self.userid = userid
        self.title = topicname
        # Creating the RstDocument render to load the file with the content in. 
        self.rstdoc = RstDocument(source = filehome + topicfile)
        # Setting the display colours
        self.rstdoc.colors.update({'background':'535353', 'paragraph':'ffffff', 'title':'27b1e1', 'bullet':'ffffff'})
        
        # Creating the box layout for the screen
        self.box = BoxLayout(orientation = 'vertical')
        # Adding the banner to the box layout
        self.box.add_widget(Banner(False, 1, self.userid))
        # Adding the RstDocument with the content to the box layout
        self.box.add_widget(self.rstdoc)
        # Add the box layout to the screen.
        self.add_widget(self.box)

