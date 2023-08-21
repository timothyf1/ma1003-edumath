import sqlite3
from datetime import datetime
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.floatlayout import FloatLayout
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

from kivy.utils import platform
plat = platform
if plat == 'android':
    filehome = ''
elif plat == 'ios':
    pass
else:
    import inspect
    filehome = inspect.getfile(inspect.currentframe())[:-7]


class QuizScreen(Screen):

    def __init__(self, username, userid, level, name):
        super(QuizScreen, self).__init__()
        self.name = name
        self.username = username
        self.userid = userid
        self.quizid = level
        
        # Begin setting up the layout
        self.box = BoxLayout(orientation = 'vertical')
        self.box.add_widget(Banner('Quiz', 1, self.userid))
        self.quesboxa = BoxLayout(orientation = 'vertical')
        self.lblquestion = Label(text = '', text_size = (dp(300), None), halign = 'center')
        self.quesboxa.add_widget(self.lblquestion)
        grid = GridLayout(cols = 2)
        self.checkbox1 = CheckBox(group = 'Question', size_hint_x = None, width = 75)
        grid.add_widget(self.checkbox1)
        self.option1 = Label(text = '')
        grid.add_widget(self.option1)
        self.checkbox2 = CheckBox(group = 'Question', size_hint_x = None, width = 75)
        grid.add_widget(self.checkbox2)
        self.option2 = Label(text = '')
        grid.add_widget(self.option2)
        self.checkbox3 = CheckBox(group = 'Question', size_hint_x = None, width = 75)
        grid.add_widget(self.checkbox3)
        self.option3 = Label(text = '')
        grid.add_widget(self.option3)
        self.checkbox4 = CheckBox(group = 'Question', size_hint_x = None, width = 75)
        grid.add_widget(self.checkbox4)
        self.option4 = Label(text = '')
        grid.add_widget(self.option4)
        self.quesboxa.add_widget(grid)
        self.quesboxa.add_widget(Button(id = 'enter', text = 'Enter', on_press = self.enter, size_hint_y = None, height = dp(30), background_normal = 'images/orange32030.png', background_down = 'images/blue32025.png'))
        self.box.add_widget(self.quesboxa)
        self.add_widget(self.box)
        # End setting up layout
        
        # Getting the questions from the database
        conn = sqlite3.connect(filehome + 'database.db')
        c = conn.cursor()
        questions = c.execute('''SELECT question, optiona, optionb, optionc, optiond, correctanswer FROM quizquestions WHERE quizid = ? ORDER BY questionid ASC''', (level,))
        self.questions = [[a for a in i] for i in questions]
        conn.close()

    def on_pre_enter(self):    
        self.currentquestion = 0  # Python index's from 0 and not 1.
        self.correctanswers = 0  # Resets the number of correct answers to 0.
        self.quizenteredanswers = []  # Keeps a record of the users entered answers.
        
        if len(self.questions) > 0:  # Check to see if there are any questions.
            self.shownextquestion(self.questions[self.currentquestion])  # Display the first question.
        else:
            PopupSc('Error', 'There are no questions available for this quiz').open()  
            self.parent.current = self.parent.screenlist.pop()
                    
    def shownextquestion(self, question):
        # Displaying the question and options on the app
        self.lblquestion.text = question[0]
        self.option1.text = question[1]
        self.option2.text = question[2]
        self.option3.text = question[3]
        self.option4.text = question[4]
        # Clearing the checkboxes for the options so that there all inactive.
        self.checkbox1.active = False
        self.checkbox2.active = False
        self.checkbox3.active = False
        self.checkbox4.active = False
        
    def enter(self, a):
        # Finding which option the user has selected. If no option selected an error message is displayed.
        if self.checkbox1.active:
            enteredanswer = 'A'
        elif self.checkbox2.active:
            enteredanswer = 'B'
        elif self.checkbox3.active:
            enteredanswer = 'C'
        elif self.checkbox4.active:
            enteredanswer = 'D'
        else:
            PopupSc('No option selected', 'You have failed to choose an option. Please try again.').open()
            enteredanswer = False
        
        if enteredanswer != False:
            self.quizenteredanswers.append(enteredanswer)
            if enteredanswer == self.questions[self.currentquestion][5]:
                self.correctanswers += 1
            self.currentquestion += 1
            if self.currentquestion < len(self.questions):    
                self.shownextquestion(self.questions[self.currentquestion])
            else:
                self.endofquiz()
    
    def endofquiz(self):
        PopupSc('End of quiz', 'You have now finshed the quiz and your score is ' + str(self.correctanswers) + ' out of ' + str(len(self.questions)) + '.').open()
        
        # Saving the result to the database
        conn = sqlite3.connect(filehome + 'database.db')
        c = conn.cursor()
        query = c.execute('''INSERT INTO quizresults (quizid, userid, mark, date) VALUES (?, ?, ?, ?)''', (self.quizid, self.userid, self.correctanswers, datetime.now()))
        conn.commit()
        conn.close()

        # Creating a screen to display results to the user
        resultsscreen = QuizResults(self.questions, self.quizenteredanswers, self.userid)
        resultsscreen.name = 'Quiz Results'
        self.parent.add_widget(resultsscreen)
        self.parent.current = 'Quiz Results'
        

class QuizResults(Screen):

    def __init__(self, questions, quizenteredanswers, userid):    
        super(QuizResults, self).__init__()    
        self.questions = questions
        self.quizenteredanswers = quizenteredanswers
        self.userid = userid
        self.box = BoxLayout(orientation = 'vertical')
        self.box.add_widget(Banner('Quiz', 1, self.userid))

        # Building the results table
        self.resultsgrid = GridLayout(cols = 3, size_hint_y = None, height = dp(40) + len(self.questions) * dp(40))
        self.resultsgrid.add_widget(Label(text = 'Question\nNumber', size_hint_y = None, height = dp(40)))
        self.resultsgrid.add_widget(Label(text = 'Your\nanswer', size_hint_y = None, height = dp(40)))
        self.resultsgrid.add_widget(Label(text = 'Correct\n answer', size_hint_y = None, height = dp(40)))
        for a in range(0, len(self.questions)):
            self.resultsgrid.add_widget(Button(text = str(a+1), size_hint_y = None, height = dp(40), on_press = self.questionpopup, id = str(a)))
            if self.questions[a][5] == self.quizenteredanswers[a]:
                self.resultsgrid.add_widget(Label(text = str(self.quizenteredanswers[a]), color = (0, 1, 0, 1), size_hint_y = None, height = dp(40)))
            else:
                self.resultsgrid.add_widget(Label(text = str(self.quizenteredanswers[a]), color = (1, 0, 0, 1), size_hint_y = None, height = dp(40)))
            self.resultsgrid.add_widget(Label(text = str(self.questions[a][5]), size_hint_y = None, height = dp(40)))
            
        # If there are enough questions then the results table won't fit, so scrollview is used to scroll through the results 
        self.scroller = ScrollView()
        self.scroller.add_widget(self.resultsgrid)
        self.box.add_widget(self.scroller)  # Adds the results table to the screen
        self.add_widget(self.box)

    def questionpopup(self, button):
        QuizQuestionResultPop(self.questions[int(button.id)], self.quizenteredanswers[int(button.id)], int(button.id)).open()

    def on_leave(self):
        self.parent.remove_widget(self)
        
        
class QuizQuestionResultPop(Popup):    

    def __init__(self, question, usersanswer, title):
        super(QuizQuestionResultPop, self).__init__()
        self.title = "Question %i" % (title + 1)
        self.question = question[0]
        self.optiona = question[1]
        self.optionb = question[2]
        self.optionc = question[3]
        self.optiond = question[4]
        self.correctanswer = question[5]
        self.enteredanswer = usersanswer
        self.box = BoxLayout(orientation = 'vertical')
        self.box.add_widget(Label(text = self.question, size_hint_y = 0.6))
        self.grid = GridLayout(cols = 2)
        self.grid.add_widget(Label(text = 'A'))
        self.grid.add_widget(Label(text = self.optiona))
        self.grid.add_widget(Label(text = 'B'))
        self.grid.add_widget(Label(text = self.optionb))
        self.grid.add_widget(Label(text = 'C'))
        self.grid.add_widget(Label(text = self.optionc))
        self.grid.add_widget(Label(text = 'D'))
        self.grid.add_widget(Label(text = self.optiond))
        self.grid.add_widget(Label(text = 'Your choice'))
        self.grid.add_widget(Label(text = self.enteredanswer))
        self.grid.add_widget(Label(text = 'Correct Answer'))
        self.grid.add_widget(Label(text = self.correctanswer))
        self.box.add_widget(self.grid)
        self.box.add_widget(Button(text = 'Close', on_press = self.dismiss, size_hint_y = None, height = dp(30), background_normal = 'images/green20030.png'))
        self.add_widget(self.box)
        
    def on_open(self):
        activepopup = self
        
    def on_leave(self):
        activepopup = False

