#!/usr/bin/python
#-*- coding: utf-8-*-

#eb2016.py

import sys
from PyQt4 import QtGui, QtCore

import pymssql
from sources.credentials import connString

import sources.shared as shared

import math

#************************************************************************************************************************************************************#

class LoginDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.initUI()

    def initUI(self):

        self.username = shared.getCfgUsername()
        
        userLbl = QtGui.QLabel(self.tr('Username:'), self)
        userLbl.setMinimumWidth(184)
        self.userTxt = QtGui.QLineEdit(self)
        self.userTxt.setText(self.username)
        self.userTxt.setFocus()
        pwLbl = QtGui.QLabel(self.tr('Password:'), self)
        self.pwTxt = QtGui.QLineEdit(self)
        self.pwTxt.setEchoMode(QtGui.QLineEdit.Password)

        buttons = QtGui.QDialogButtonBox(self)
        self.logonBtn = buttons.addButton(self.tr('Logon'), QtGui.QDialogButtonBox.ActionRole)
        self.logonBtn.clicked.connect(self.onLogon)
        self.exitBtn = buttons.addButton(self.tr('Exit'), QtGui.QDialogButtonBox.RejectRole)
        self.exitBtn.clicked.connect(self.onExit)

        self.responseLbl = QtGui.QLabel(self)
        self.responseLbl.setText('')
        self.responseLbl.setObjectName('LogonResponse')

        
        self.form = QtGui.QFormLayout(self)
        self.form.addRow(userLbl, self.userTxt)
        self.form.addRow(pwLbl, self.pwTxt)
        self.form.addWidget(buttons)
        self.form.setAlignment(buttons, QtCore.Qt.AlignCenter)
        self.form.addRow(self.responseLbl)
        self.setLayout(self.form)

        self.setWindowTitle(self.tr('Login'))
        self.setWindowIcon(QtGui.QIcon('resources/icons/euro.png'))
        self.setFixedSize(500, 150)

    def onLogon(self):
        """ login to the application """
        login = str(self.userTxt.text())
        passw = str(self.pwTxt.text())
        
        try:
            conn = pymssql.connect(*connString)
            with conn:
                cur = conn.cursor()

                cur.callproc('eb_2016_login', (login, passw, ))
                self.returnCode = cur.returnvalue
        except:
            QtGui.QMessageBox.about(self, 'Database connection fault', 'Failed to connect to database.\nPlease try again later')
            sys.exit()

        print self.returnCode

        if self.returnCode == 10:
            ''' Successful login '''
            shared.setCfgUsername(login)  #writes login name to config.ini, for further use in application
            self.accept()
        elif self.returnCode == 0:
            ''' No admin rights '''
            self.responseLbl.setText('This username doesn\'t have admin rights')
            self.userTxt.setText('')
            self.pwTxt.setText('')
            self.userTxt.setFocus()
        elif self.returnCode == 1:
            ''' Invalid username or password '''
            self.responseLbl.setText(self.tr('Invalid username or password'))
            self.userTxt.setText('')
            self.pwTxt.setText('')
            self.userTxt.setFocus()
        

            
    def onExit(self):
        """ closes the dialog, and thus the application """
        self.close()


#************************************************************************************************************************************************************#        

class CreateUserScreen(QtGui.QWidget):

    def __init__(self, parent=None):
        super(CreateUserScreen, self).__init__(parent)
        self.initUI()

    def initUI(self):

        userLbl = QtGui.QLabel('Username:', self)
        self.userEdit = QtGui.QLineEdit(self)
        emailLbl = QtGui.QLabel('E-mail:', self)
        self.emailEdit = QtGui.QLineEdit(self)
        passwLbl = QtGui.QLabel('Password', self)
        self.passwEdit = QtGui.QLineEdit(self)
        self.passwEdit.setText(shared.passwGen())

        createUserBtn = QtGui.QPushButton('Create', self)
        createUserBtn.clicked.connect(self.onCreate)

        form = QtGui.QFormLayout()
        form.addRow(userLbl, self.userEdit)
        form.addRow(emailLbl, self.emailEdit)
        form.addRow(passwLbl, self.passwEdit)
        form.addRow(createUserBtn)
        form.setAlignment(createUserBtn, QtCore.Qt.AlignLeft)
        form.setContentsMargins(100, 100, 0, 0)

        container = QtGui.QVBoxLayout()
        container.addLayout(form)
        container.setAlignment(createUserBtn, QtCore.Qt.AlignBottom)

        self.setLayout(container)
        
    def createUser(self, username, passw, email):
        """ creates the specified user on the server """
        try:
            conn = pymssql.connect(*connString)

            with conn:
                cur = conn.cursor()
                cur.callproc('eb_2016_create_user', (username, passw, email))
                conn.commit()
                returnCode = cur.returnvalue
                return returnCode
        except:
            print sys.exc_info()
            QtGui.QMessageBox.about(self, 'Database connection fault', 'Failed to connect to database.\nPlease try again later')
            QtGui.qApp.quit()
            
    def onCreate(self):
        """ gets the text from the username, email and passw entry,
            then calls createUser method """
        username = str(self.userEdit.text())
        email = str(self.emailEdit.text())
        password = str(self.passwEdit.text())
        returnCode = -1
        if username:
            ''' username entered '''
            if email:
                ''' email entered '''
                if password:
                    ''' password entered '''
                    returnCode = self.createUser(username, password, email)
                else:
                    QtGui.QMessageBox.about(self, 'Create user', 'No password entered')
            else:
                QtGui.QMessageBox.about(self, 'Create user', 'No email address entered')
        else:
            QtGui.QMessageBox.about(self, 'Create user', 'No username entered')
        print returnCode
        if returnCode == 0:
            ''' User created successfully, send registration email '''
            shared.sendRegEmail(username, email, password)
            QtGui.QMessageBox.about(self, 'Create user', 'Successfully created user: %s' % (username))
            self.reinitUI()
        if returnCode == 1:
            ''' User already exists on the server '''
            QtGui.QMessageBox.about(self, 'Create user', 'User already exists on the server')
            

    def reinitUI(self):
        self.userEdit.setText('')
        self.emailEdit.setText('')
        self.passwEdit.setText(shared.passwGen())
        
        

#************************************************************************************************************************************************************#        

class DeleteUserScreen(QtGui.QWidget):

    def __init__(self, parent=None):
        super(DeleteUserScreen, self).__init__(parent)
        self.initUI()

    def initUI(self):
        ################
        # Widgets      #
        ################   

        userLbl = QtGui.QLabel('Username:', self)
        self.userList = QtGui.QComboBox(self)
        self.userList.setView(QtGui.QListView())        # must be set, in order to adjust stlye in stylesheet *BUG*
        self.setUserList()

        
        deleteUserBtn = QtGui.QPushButton('Delete', self)
        deleteUserBtn.clicked.connect(self.onDelete)
        
        ################
        # Layouts      #
        ################   

        form = QtGui.QFormLayout()
        form.addRow(userLbl, self.userList)
        form.addRow(deleteUserBtn)
        form.setAlignment(deleteUserBtn, QtCore.Qt.AlignLeft)
        form.setContentsMargins(100, 100, 0, 0)

        container = QtGui.QVBoxLayout()
        container.addLayout(form)
        container.setAlignment(deleteUserBtn, QtCore.Qt.AlignBottom)

        self.setLayout(container)

    def getUsernames(self):
        """ fetches and returns usernames from server """
        usernames = []
        try:
            conn = pymssql.connect(*connString)

            with conn:
                cur = conn.cursor(as_dict=True)
                cur.execute("SELECT Username FROM EB_2016_users")

                for row in cur:
                    usernames.append(row['Username'])
            return usernames
        except:
            QtGui.QMessageBox.about(self, 'Database connection fault', 'Failed to connect to database.\nPlease try again later')
            sys.exit()

    def setUserList(self):
        """ populates listbox with usernames """
        usernames = self.getUsernames()

        self.userList.clear()
        
        for user in usernames:
            self.userList.addItem(user)

    def deleteUser(self, username):
        """ deletes the specified user from the server """
        try:
            conn = pymssql.connect(*connString)

            with conn:
                cur = conn.cursor()
                cur.callproc('eb_2016_user_delete', (username,))
                conn.commit()
            QtGui.QMessageBox.about(self, 'Delete user', 'Successfully deleted user: %s' % (username))
        except:
            QtGui.QMessageBox.about(self, 'Database connection fault', 'Failed to connect to database.\nPlease try again later')
            sys.exit()

            
        
    def onDelete(self):
        """ gets the selected username from the user list,
            calls deleteUser method then calls setUserList method """
        username = str(self.userList.currentText())
        self.deleteUser(username)
        self.setUserList()

    def reinitUI(self):
        self.setUserList()
        
#************************************************************************************************************************************************************#        

class ResetUserScreen(QtGui.QWidget):

    def __init__(self, parent=None):
        super(ResetUserScreen, self).__init__(parent)
        self.initUI()

    def initUI(self):
        ################
        # Widgets      #
        ################   

        userLbl = QtGui.QLabel('Username:', self)
        self.userList = QtGui.QComboBox(self)
        self.userList.setView(QtGui.QListView()) # must be set, in order to adjust stlye in stylesheet *BUG*
        self.setUserList()

        passwLbl = QtGui.QLabel('New Password:', self)
        self.passwEntry = QtGui.QLineEdit('test', self)
        self.passwEntry.setText(shared.passwGen())
        
        resetUserBtn = QtGui.QPushButton('Reset', self)
        resetUserBtn.clicked.connect(self.onReset)

        ################
        # Layouts      #
        ################   

        form = QtGui.QFormLayout()
        form.addRow(userLbl, self.userList)
        form.addRow(passwLbl, self.passwEntry)
        form.addRow(resetUserBtn)
        form.setAlignment(resetUserBtn, QtCore.Qt.AlignLeft)
        form.setContentsMargins(100, 100, 0, 0)

        container = QtGui.QVBoxLayout()
        container.addLayout(form)
        container.setAlignment(resetUserBtn, QtCore.Qt.AlignBottom)

        self.setLayout(container)
        
    def getUsernames(self):
        """ fetches and returns usernames from server """
        usernames = []
        try:
            conn = pymssql.connect(*connString)

            with conn:
                cur = conn.cursor(as_dict=True)
                cur.execute("SELECT Username FROM EB_2016_users")

                for row in cur:
                    usernames.append(row['Username'])
            return usernames
        except:
            print 'username'
            QtGui.QMessageBox.about(self, 'Database connection fault', 'Failed to connect to database.\nPlease try again later')
            sys.exit()
            
    def setUserList(self):
        """ populates listbox with usernames """
        usernames = self.getUsernames()

        self.userList.clear()
        
        for user in usernames:
            self.userList.addItem(user)

    def getUserEmail(self, username):
        """ fetches and returns the email address for the specified user """
        try:
            conn = pymssql.connect(*connString)
            with conn:
                cur = conn.cursor(as_dict=True)
                cur.callproc('eb_2016_get_user_email', (username,)) #works only without conn.commit()
                
                for row in cur:
                    return row['Email']
                
        except:
            print sys.exc_info()
            
    def resetUser(self, username, password):
        """ gets the new password from the password entry,
            then resets the password of the specified user on the server """
        try:
            conn = pymssql.connect(*connString)
            with conn:
                cur = conn.cursor()
                cur.callproc('eb_2016_user_password_reset', (username, password,))
                conn.commit()
            
            QtGui.QMessageBox.about(self, 'Password reset', 'Password reset was successful for user: %s' % (username))
        except:
            QtGui.QMessageBox.about(self, 'Database connection fault', 'Failed to connect to database.\nPlease try again later')
            sys.exit()
            
    def onReset(self):
        """ gets the selected username from the user list,
            calls the resetUser method then calls the setUserList method """
        username = str(self.userList.currentText())
        password = str(self.passwEntry.text())
##        print self.getUserEmail(username)
        if username:
            ''' username entered '''
            print 'username'
            print username
            if password:
                ''' password entered '''
                print password
                
                print 'resetuser'
                self.resetUser(username, password)
                print 'getemail'
                email = self.getUserEmail(username)
                print email
                print 'send reset email'
                shared.sendResetEmail(username, email, password)
            else:
                QtGui.QMessageBox.about(self, 'Password reset', 'No password entered')
        else:
            QtGui.QMessageBox.about(self, 'Password reset', 'No username entered')
        

    def reinitUI(self):
        self.passwEntry.setText(shared.passwGen())
        self.setUserList()
        
        

#************************************************************************************************************************************************************#        

class UserScreen(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(UserScreen, self).__init__(parent)
        self.initUI()

    def initUI(self):


        ################
        # Navigation   #
        ################   

        self.backBtn = QtGui.QPushButton('Back', self)
        self.backBtn.setObjectName('BackButton')
        
        ################
        # Options      #
        ################

        self.createUserBtn = QtGui.QPushButton('New User', self)
        self.createUserBtn.setObjectName('UserButton')
        self.createUserBtn.setCheckable(True)
        self.createUserBtn.setChecked(True)
        self.createUserBtn.clicked.connect(self.switchToCreateScreen)
        
        self.deleteUserBtn = QtGui.QPushButton('Delete User', self)
        self.deleteUserBtn.setObjectName('UserButton')
        self.deleteUserBtn.setCheckable(True)
        self.deleteUserBtn.clicked.connect(self.switchToDeleteScreen)
        
        self.resetUserBtn = QtGui.QPushButton('Reset User', self)
        self.resetUserBtn.setObjectName('UserButton')
        self.resetUserBtn.setCheckable(True)
        self.resetUserBtn.clicked.connect(self.switchToResetScreen)

        btnGroup = QtGui.QButtonGroup(self)
        btnGroup.setExclusive(True)    # restricts the group to have only one button checked at a time
        btnGroup.addButton(self.createUserBtn)
        btnGroup.addButton(self.deleteUserBtn)
        btnGroup.addButton(self.resetUserBtn)
    

        ################
        # Sub-Screens  #
        ################

        self.createScreen = CreateUserScreen(self)
        self.deleteScreen = DeleteUserScreen(self)
        self.resetScreen = ResetUserScreen(self)

        self.stack = QtGui.QStackedWidget(self)
        self.stack.addWidget(self.createScreen)
        self.stack.addWidget(self.deleteScreen)
        self.stack.addWidget(self.resetScreen)
        
        ################
        # Layouts      #
        ################   
        optContainer = QtGui.QHBoxLayout()

        optContainer.addWidget(self.createUserBtn, alignment=QtCore.Qt.AlignLeft)
        optContainer.addWidget(self.deleteUserBtn, alignment=QtCore.Qt.AlignCenter)
        optContainer.addWidget(self.resetUserBtn, alignment=QtCore.Qt.AlignRight)
        optContainer.setAlignment(QtCore.Qt.AlignBottom)
        optContainer.setContentsMargins(100,0,100,0)
        

        btnContainer = QtGui.QHBoxLayout()
        btnContainer.addWidget(self.backBtn)
        btnContainer.setAlignment(self.backBtn, QtCore.Qt.AlignLeft)
        btnContainer.setAlignment(QtCore.Qt.AlignBottom)
        
        container = QtGui.QVBoxLayout()
        container.addWidget(self.stack)
        container.addLayout(optContainer)
        container.addLayout(btnContainer)
        
        self.setLayout(container)

    def switchToCreateScreen(self):
        self.createScreen.reinitUI()
        self.stack.setCurrentWidget(self.createScreen)
    def switchToDeleteScreen(self):
        self.deleteScreen.reinitUI()
        self.stack.setCurrentWidget(self.deleteScreen)
    def switchToResetScreen(self):
        self.resetScreen.reinitUI()
        self.stack.setCurrentWidget(self.resetScreen)
        
#************************************************************************************************************************************************************#
        
class ResultValueEntry(QtGui.QLineEdit):

    def __init__(self, parent=None):
        super(ResultValueEntry, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.oldText = ''
        self.setInputMask("99; ")
        self.setMaximumWidth(50)
        self.setPlaceholderText(" -")
        self.setMaxLength(2)

    def mousePressEvent(self, event):
        super(ResultValueEntry, self).mousePressEvent(event)
        ''' The current text is saved and then deleted'''
        self.oldText = self.text()
        self.setText('')
        self.setCursorPosition(1)

    def keyPressEvent(self, event):
        super(ResultValueEntry, self).keyPressEvent(event)
        ''' The current text is copied and shifted by one space to the left
            after the first character entered '''
        if len(self.text()) == 1:
            self.setText(self.text() + ' ')
            self.setCursorPosition(1)
            

    def focusOutEvent(self, event):
        super(ResultValueEntry, self).focusOutEvent(event)
        ''' When there is no change to the widget, the current text is
            replaced by the old text '''
        print len(self.text())
        if (self.text() == ''):
            self.setText(self.oldText)
            
        
#************************************************************************************************************************************************************#
        
class ResultEntry(QtGui.QWidget):

    def __init__(self, parent=None):
        super(ResultEntry, self).__init__(parent)
        self.initUI()
        
    def initUI(self):

        self.matchId = 0
    
        self.homeBtn = QtGui.QPushButton("Home")
        self.homeBtn.setIcon(QtGui.QIcon('flags/default.png'))
        self.homeBtn.setObjectName('HomeTeam')

        self.homeTxt = ResultValueEntry(self)
    
        self.visitorBtn = QtGui.QPushButton("Visitor")
        self.visitorBtn.setIcon(QtGui.QIcon('flags/default.png'))
        self.visitorBtn.setObjectName('VisitorTeam')

        self.visitorTxt = ResultValueEntry(self)

        colon = QtGui.QLabel(':')
        colon.setMaximumWidth(20)

        container = QtGui.QGridLayout()
        container.addWidget(self.homeBtn, 0, 0)
        container.addWidget(self.homeTxt, 0, 1)
        container.addWidget(colon, 0, 2)
        container.addWidget(self.visitorTxt, 0, 3)
        container.addWidget(self.visitorBtn, 0, 4)
     
        self.setLayout(container)

    def setMatchId(self, ID):
        self.matchId = ID
    
    def setHomeBtnText(self, country):
        self.homeBtn.setText(country)
        icon = shared.getCountryFlagPath(country)
        self.homeBtn.setIcon(QtGui.QIcon(icon))

    def getHomeBtnText(self):
        return str(self.homeBtn.text())
    
    def setVisitorBtnText(self, country):
        self.visitorBtn.setText(country)
        icon = shared.getCountryFlagPath(country)
        self.visitorBtn.setIcon(QtGui.QIcon(icon))

    def getVisitorBtnText(self):
        return str(self.visitorBtn.text())

    def setHomeGoals(self, goals):
        self.homeTxt.setText(str(goals))

    def getHomeGoals(self):
        return int(self.homeTxt.text())

    def setVisitorGoals(self, goals):
        self.visitorTxt.setText(str(goals))

    def getVisitorGoals(self):
        return int(self.visitorTxt.text())
        
#************************************************************************************************************************************************************#

class ResultMatchScreen(QtGui.QWidget):

    def __init__(self, parent=None):
        super(ResultMatchScreen, self).__init__(parent)
        self.initUI()

    def initUI(self):

        self.date = '06.10'
        
        self.header = QtGui.QLabel('06.10')
        self.header.setMaximumHeight(50)

        self.matchEntries = self.createMatchEntries() # array to contain match entries
        
        
        ################
        # Navigation   #
        ################
        
        self.backBtn = QtGui.QPushButton(self)
        self.backBtn.setObjectName('BackButton')

        
        ################
        # Controls     #
        ################

        self.submitBtn = QtGui.QPushButton('Submit', self)
        self.submitBtn.setObjectName('SubmitButton')
        self.submitBtn.clicked.connect(self.onSubmit)

        ################
        # Layouts      #
        ################   

        self.matchContainer = QtGui.QVBoxLayout()
        self.setMatchContainer()

        headerContainer = QtGui.QHBoxLayout()
        headerContainer.addWidget(self.header, alignment=QtCore.Qt.AlignRight)
        headerContainer.addWidget(self.backBtn, alignment=QtCore.Qt.AlignRight)
        headerContainer.setContentsMargins(100, 0, 0, 0)
        
        
        btnContainer = QtGui.QHBoxLayout()
        btnContainer.addWidget(self.submitBtn)
        btnContainer.setAlignment(self.submitBtn, QtCore.Qt.AlignRight)
        btnContainer.setAlignment(QtCore.Qt.AlignBottom)


        container = QtGui.QVBoxLayout()
        container.addLayout(headerContainer)
        container.addLayout(self.matchContainer)
        container.addLayout(btnContainer)
        container.setContentsMargins(100, 0, 100, 0)
        self.setLayout(container)

    def onSubmit(self):
        """ updates match result in database"""
        try:
            conn = pymssql.connect(*connString)
            with conn:
                cur = conn.cursor()    
                for entry in self.matchEntries:
                    ID = entry.matchId
                    try:
                        HGol = entry.getHomeGoals()
                        VGol = entry.getVisitorGoals()
                        cur.callproc('eb_2016_match_result_update', (ID, HGol, VGol,))
                        QtGui.QMessageBox.about(self, 'Submit', 'Match result of\n%s - %s\nsubmitted successfully' % (entry.getHomeBtnText(), entry.getVisitorBtnText()))
                    except ValueError:
                        QtGui.QMessageBox.about(self, 'Result error', 'No result provided for match #%d' % (ID) )
                        cur.callproc('eb_2016_match_result_update', (ID, None, None,))
                    conn.commit()
        except:
            print sys.exc_info()
            QtGui.QMessageBox.about(self, 'Database connection fault', 'Failed to connect to database.\nPlease try again later')
            sys.exit()
        
    
    def getMatchesForDate(self):
        """ fetches and returns matches for the given date """
        matches = []
        date = '2016-%s-%s' % (self.date.split('.')[0], self.date.split('.')[1])
        print date

        try:
            conn = pymssql.connect(*connString)
            with conn:
                cur = conn.cursor(as_dict=True)
                cur.execute("SELECT [ID], [Home], [H-Gol], [Visitor], [V-Gol] from [dbo].[EB_2016_matches] WHERE DATE = '%s'" % date)

                for row in cur:
                    matches.append(
                                    {'id' : row['ID'],
                                     'Home' : row['Home'],
                                     'H-Goal' : row['H-Gol'],
                                     'V-Goal' : row['V-Gol'],
                                     'Visitor' :row['Visitor']
                                     }
                                    )
            return matches
        except:
            QtGui.QMessageBox.about(self, 'Database connection fault', 'Failed to connect to database.\nPlease try again later')
            sys.exit()

    def createMatchEntries(self):
        """ creates match entries from matches """
        matches = self.getMatchesForDate()
        matchEntries = []
        for match in matches:
            entry = ResultEntry(self)
            entry.setMatchId(match['id'])
            entry.setHomeGoals(match['H-Goal'])
            entry.setHomeBtnText(match['Home'])
            entry.setVisitorGoals(match['V-Goal'])
            entry.setVisitorBtnText(match['Visitor'])
            matchEntries.append(entry)
        return matchEntries

    def clearMatchEntries(self):
        """ removes entries from match container, deletes entries, wipes match entries"""
        for entry in self.matchEntries:
            self.matchContainer.removeWidget(entry)
            entry.setParent(None)
            entry.deleteLater()
        self.matchEntries = []
        
    def setMatchContainer(self):
        """ populates the match container with match entries """
        for entry in self.matchEntries:
            self.matchContainer.addWidget(entry)

    def reinitUI(self, date):
        """ reinitialize UI, sets date, clears match entries and match container,
            recreates match entries, reloads match container """
        self.date = date
        self.header.setText(date)
        self.clearMatchEntries()
        self.matchEntries = self.createMatchEntries()
        self.setMatchContainer() 

        

#************************************************************************************************************************************************************#

class ResultDatesScreen(QtGui.QWidget):

    toMatches = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(ResultDatesScreen, self).__init__(parent)
        self.initUI()

    def initUI(self):
        
        self.dates = self.getDates() #list that will contain date of matches


        ################
        # Layouts      #
        ################   
                
        self.dateContainer = QtGui.QGridLayout()
        self.setDateContainer(cols=4)
        
        container = QtGui.QVBoxLayout()
        container.addLayout(self.dateContainer)
        container.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(container)
        
    def getMonthDayFromDate(self, date):
        """ returns the month and day in the format of 'mm.dd',
            from the original datetime format 'yyyy-mm-dd' """
        year, month, day = date.split('-')
        monthDayFormat = str(month) + '.' + str(day)
        return monthDayFormat

    def getDates(self):
        """ fetches and returns match dates in the format of mm.dd """
        matchDates = []
        try:
            conn = pymssql.connect(*connString)
            with conn:
                cur = conn.cursor(as_dict=True) #as_dict to access row element by column name
                cur.execute('SELECT [Date] FROM [dbo].[EB_2016_matches]')
                for row in cur:

                    date = self.getMonthDayFromDate(row['Date'])
                    if date not in matchDates:
                        matchDates.append(date)

            return matchDates
        except:
            QtGui.QMessageBox.about(self, 'Database connection fault', 'Failed to connect to database.\nPlease try again later')
            sys.exit()


    def setDateContainer(self, cols=4):
        """ creates buttons with the corresponding date text """
        rows = int(math.ceil(float(len(self.dates)) / cols)) #calculates the number of needed rows
    
        positions = [(row, col) for row in range(rows) for col in range(cols)] # creates an array of (row, col) coordinates for the grid layout
        
        for date, position in zip(self.dates, positions):   # creates the date picking buttons and add them to the container layout
            btn = QtGui.QPushButton(date)
            btn.setMaximumWidth(150)
            btn.clicked.connect(self.onDatePick)
            self.dateContainer.addWidget(btn, *position)
        
    def onDatePick(self):
        """ triggers toMatches signal, with the text of the clicked button """
        self.toMatches.emit(str(self.sender().text()))
  
#************************************************************************************************************************************************************#
        
class ResultScreen(QtGui.QWidget):

    def __init__(self, parent=None):
        super(ResultScreen, self).__init__(parent)
        self.initUI()

    def initUI(self):

        ################
        # Navigation   #
        ################   
        self.backBtn = QtGui.QPushButton('Back', self)
        self.backBtn.setObjectName('BackButton')

        ################
        # Sub-Screens  #
        ################

        self.dateScreen = ResultDatesScreen(self)
        self.dateScreen.toMatches.connect(self.onToMatchScreen)
        self.matchScreen = ResultMatchScreen(self)
        self.matchScreen.backBtn.clicked.connect(self.onToDateScreen)
        

        self.stack = QtGui.QStackedWidget(self)
        self.stack.addWidget(self.dateScreen)
        self.stack.addWidget(self.matchScreen)
        self.stack.setCurrentWidget(self.dateScreen)
        
        ################
        # Layouts      #
        ################   
        btnContainer = QtGui.QHBoxLayout()
        btnContainer.addWidget(self.backBtn)
        btnContainer.setAlignment(self.backBtn, QtCore.Qt.AlignLeft)
        btnContainer.setAlignment(QtCore.Qt.AlignBottom)
        
        container = QtGui.QVBoxLayout()
        container.addWidget(self.stack)
        container.addLayout(btnContainer)
        
        self.setLayout(container)

    def onToDateScreen(self):
        self.stack.setCurrentWidget(self.dateScreen)

    def onToMatchScreen(self, date):
        print date
        self.matchScreen.reinitUI(date)
        self.stack.setCurrentWidget(self.matchScreen)
    
    

#************************************************************************************************************************************************************#   

class MainMenu(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MainMenu, self).__init__(parent)
        self.initUI()

    def initUI(self):
        
        ################
        # Screens      #
        ################   
        self.userBtn = QtGui.QPushButton('User Management', self)
        self.resultBtn = QtGui.QPushButton('Result Management', self)
        
        ################
        # Layouts      #
        ################   
        container = QtGui.QVBoxLayout()
        container.addWidget(self.userBtn)
        container.addWidget(self.resultBtn)
        container.setAlignment(QtCore.Qt.AlignTop)
        
        self.setLayout(container)

#************************************************************************************************************************************************************#

class AdminGui(QtGui.QMainWindow):

    def __init__(self):
        super(AdminGui, self).__init__()
        self.initUI()

    def initUI(self):

        ################
        # Widgets      #
        ################   
        self.mainMenu = MainMenu(self)
        self.mainMenu.userBtn.clicked.connect(self.onToUserScreen)
        self.mainMenu.resultBtn.clicked.connect(self.onToResultScreen)

        self.userScreen = UserScreen(self)
        self.userScreen.backBtn.clicked.connect(self.onToMain)

        self.resultScreen = ResultScreen(self)
        self.resultScreen.backBtn.clicked.connect(self.onToMain)

        ################
        # Screen stack #
        ################        
        self.mainWidget = QtGui.QStackedWidget(self)
        self.mainWidget.addWidget(self.mainMenu)
        self.mainWidget.addWidget(self.userScreen)
        self.mainWidget.addWidget(self.resultScreen)
        self.mainWidget.setCurrentWidget(self.mainMenu)

        ################
        # Actions      #
        ################
        self.exitAction = QtGui.QAction(self)
        self.exitAction.setIcon(QtGui.QIcon('resources/icons/exit.png'))
        self.exitAction.setShortcut('Ctrl+X')
        self.exitAction.triggered.connect(QtGui.qApp.quit)      
        
        ################
        #   Menus      #
        ################
        self.statusBar()   

        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.setIconSize(QtCore.QSize(36, 36))
        self.toolbar.setMovable(False)
        
        self.toolbar.addAction(self.exitAction)
        
        ##########################
        # Window settings        #
        ##########################
        versionString = 'V01.00.00'

        self.setCentralWidget(self.mainWidget)
        self.setWindowTitle('EURObet Admin 2016 ' + versionString )
        self.setWindowIcon(QtGui.QIcon('resources/icons/euro.png'))
        self.setGeometry(300, 300, 1000, 512)

        self.setFixedSize(1175, 512)

        self.trayIcon = QtGui.QSystemTrayIcon(QtGui.QIcon('resources/icons/euro.png'))
        self.trayIcon.activated.connect(self.restoreWindow)
        
        self.show()

    ##########################
    # Slots                  #
    ##########################
    
    def onToMain(self):
        self.mainWidget.setCurrentWidget(self.mainMenu)

    def onToUserScreen(self):
        self.mainWidget.setCurrentWidget(self.userScreen)

    def onToResultScreen(self):
        self.mainWidget.setCurrentWidget(self.resultScreen)
    

    ##########################
    # Methods                #
    ##########################   
        
    def keyPressEvent(self, event):
        """ watching for escape key press to hide app and start notepad"""
        print event.key()
        if event.key() == (QtCore.Qt.Key_Escape):
            self.hide()
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.Tool)
            self.trayIcon.show()

    def restoreWindow(self, reason):
        """ restores main window if the tray icon is double clicked"""
        if reason == QtGui.QSystemTrayIcon.DoubleClick:
            self.trayIcon.hide()
            self.showNormal()


def main(app = QtGui.QApplication(sys.argv)):
    """ app is an input parameter for main,
        to be able to call it recursively, after logouts"""
    
    with open('resources/styles/admin.css', 'r') as appStyle:
            app.setStyleSheet(appStyle.read())

    """ Login screen """
    login = LoginDialog()

    if login.exec_() == QtGui.QDialog.Accepted:
        """ Successful login """
        """ Start GUI """
        gui = AdminGui()

        """ Save application return code on exit """
        appReturnCode = app.exec_()    
        if appReturnCode == 0:
            """ Normal Quit from application """
            sys.exit()
    else:
        """ Exit from login screen """
        sys.exit()

if __name__ == '__main__':
    main()
