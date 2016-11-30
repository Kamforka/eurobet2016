#!/usr/bin/python
#-*- coding: utf-8-*-

#dialogs.py

''' PyQt imports '''
import sys
from PyQt4 import QtGui, QtCore

''' Database Imports '''
import pymssql
from credentials import connString

''' Shared functions imports '''
import shared

#************************************************************************************************************************************************************#

class AboutDialog(QtGui.QDialog):

    def __init__(self):
        super(AboutDialog, self).__init__()
        self.initUI()

    def initUI(self):        
        header = QtGui.QLabel()
        info = QtGui.QLabel()
        footer = QtGui.QLabel()
        version = shared.getCfgVersionString()

        header.setWordWrap(True)
        header.setText('EURO Bet 2016\nV{}'.format(version))
        headerFont = QtGui.QFont("Arial", 12, QtGui.QFont.Bold)
        header.setFont(headerFont)
        
        info.setWordWrap(True)
        info.setText(self.tr('''Frontend: Szabolcs Antal
Backend: Mate Lapis'''))
        infoFont = QtGui.QFont("Arial", 12)
        info.setFont(infoFont)


        footer.setWordWrap(True)
        footer.setText(self.tr('2016 MaSzaT Team'))
        footerFont = QtGui.QFont("Arial", 8, QtGui.QFont.Bold)
        footer.setFont(footerFont)
        
        self.container = QtGui.QVBoxLayout()
        self.container.addWidget(header)
        self.container.addStretch(1)
        self.container.addWidget(info)
        self.container.addStretch(1)
        self.container.addWidget(footer)
        self.setLayout(self.container)

        self.setWindowTitle(self.tr('About'))
        self.setWindowIcon(QtGui.QIcon('resources/icons/euro.png'))
        self.setFixedSize(500, 500) 
        self.exec_()

#************************************************************************************************************************************************************#

class ChangePasswordDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        super(ChangePasswordDialog, self).__init__(parent)
        self.initUI()

    def initUI(self):

        ''' Init translations '''
        self.language = shared.getCfgLang()
        self.translator = QtCore.QTranslator()
        self.translator.load('resources/translations/%s.qm' % (self.language) )
        QtGui.qApp.installTranslator(self.translator)

        self.resetMode = False # False: Shows Nickname + Password | True: Shows Password Only
        
        self.nickLbl = QtGui.QLabel(self.tr('Nickname:'), self)
        self.nickLbl.setMinimumWidth(160)
        self.nickLbl.setToolTip(self.tr('The name you\'d like to be displayed in the application!'))
        
        self.nickTxt = QtGui.QLineEdit(self)
        self.nickTxt.setFocus()
        self.nickTxt.setToolTip(self.tr('The name you\'d like to be displayed in the application!'))

        newPwLbl = QtGui.QLabel(self.tr('New password:'), self)
        self.newPwTxt1 = QtGui.QLineEdit(self)
        self.newPwTxt1.setEchoMode(QtGui.QLineEdit.Password)
        self.newPwTxt2 = QtGui.QLineEdit(self)
        self.newPwTxt2.setEchoMode(QtGui.QLineEdit.Password)
        
        buttons = QtGui.QDialogButtonBox(self)
        self.changeBtn = buttons.addButton(self.tr('Change'), QtGui.QDialogButtonBox.ActionRole)
        self.changeBtn.clicked.connect(self.onChange)
        self.cancelBtn = buttons.addButton(self.tr('Cancel'), QtGui.QDialogButtonBox.RejectRole)
        self.cancelBtn.clicked.connect(self.onCancel)

        self.responseLbl = QtGui.QLabel(self)
        self.responseLbl.setObjectName('PasswordResponse')
        self.responseLbl.hide()
                    
        self.container = QtGui.QFormLayout(self)
        self.container.addRow(self.nickLbl, self.nickTxt)
        self.container.addRow(newPwLbl, self.newPwTxt1)
        self.container.addRow('', self.newPwTxt2)
        self.container.addRow(self.responseLbl, buttons)
        self.container.setAlignment(buttons, QtCore.Qt.AlignCenter)

        self.setLayout(self.container)

        self.setWindowTitle(self.tr('Change password'))
        self.setWindowIcon(QtGui.QIcon('resources/icons/euro.png'))
        self.setFixedSize(500, 150) 

    def setNickPass(self, nick, passw):
        """ for an unactivated user, sets the nickname and the new password """
        username = shared.getCfgUsername()
        try:
            conn = pymssql.connect(*connString)
            with conn:
                cur = conn.cursor()
                cur.callproc('eb_2016_update_user', (username, nick, passw,))
                conn.commit()

                returnCode = cur.returnvalue
        except:
            QtGui.QMessageBox.about(self, self.tr('Database connection fault'), self.tr('Failed to connect to database.\nPlease try again later'))
            QtGui.qApp.quit()
            
        return returnCode

    def resetPass(self, passw):
        """ for the first login after password reset, sets the new password for the user """
        username = shared.getCfgUsername()
        print username
        try:
            conn = pymssql.connect(*connString)
            with conn:
                cur = conn.cursor()
                cur.callproc('eb_2016_new_password_after_reset', (username, passw,))
                conn.commit()
                returnCode = cur.returnvalue
        except:
            print sys.exc_info()
            QtGui.QMessageBox.about(self, self.tr('Database connection fault'), self.tr('Failed to connect to database.\nPlease try again later'))
            QtGui.qApp.quit()

        return returnCode
                
    def onChange(self):
        """ checks that the passwords are identicals and the nickname hasn't been taken yet
            then calls setNickPass """
        nickName = unicode(self.nickTxt.text())
        newPw1 = unicode(self.newPwTxt1.text())
        newPw2 = unicode(self.newPwTxt2.text())
        
        if newPw1 == newPw2 and len(newPw1):
            ''' the passwords are identical and their length is greater than 0'''
            if self.resetMode:
                returnCode = self.resetPass(newPw1) # calls the resetPass method if resetMode is True
            else:
                returnCode = self.setNickPass(nickName, newPw1) # calls setNickPass method if resetMode is False
            
            if returnCode == 0:
                ''' resetMode False : user activated, nickname and new password set'''
                ''' resetMode True : user activated, and new password set'''
                self.accept()
                QtGui.qApp.removeTranslator(self.translator)
                print 'Passwords are matching'
            elif returnCode == 3:
                ''' nickname already taken '''
                self.responseLbl.setText(self.tr('Nickname is already taken'))
                self.nickTxt.clear()
                self.newPwTxt1.clear()
                self.newPwTxt2.clear()
                self.nickTxt.setFocus()
        else:
            ''' the passwords are not identical, or their length is 0 '''
            self.responseLbl.setText(self.tr('Passwords are not matching'))
            self.newPwTxt1.clear()
            self.newPwTxt2.clear()
            self.newPwTxt1.setFocus()

        self.responseLbl.show()
        
    def onCancel(self):
        """ closes the dialog """
        self.close()

    def setResetMode(self, reset):
        """ hides the nickname label and nickname entry """
        if reset:
            self.resetMode = True
            self.nickLbl.hide()
            self.nickTxt.hide()
        else:
            self.resetMode = False
            self.nickLbl.show()
            self.nickTxt.show()
            

#************************************************************************************************************************************************************#

class LoginDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.initUI()

    def initUI(self):

        self.username = shared.getCfgUsername()
        ''' Init translations '''
        self.language = shared.getCfgLang()
        self.translator = QtCore.QTranslator()
        self.translator.load('resources/translations/%s.qm' % (self.language) )
        QtGui.qApp.installTranslator(self.translator)

        
        userLbl = QtGui.QLabel(self.tr('Username:'), self)
        userLbl.setMinimumWidth(184)
        self.userTxt = QtGui.QLineEdit(self)
        self.userTxt.setText(self.username)
        
        pwLbl = QtGui.QLabel(self.tr('Password:'), self)
        self.pwTxt = QtGui.QLineEdit(self)
        self.pwTxt.setEchoMode(QtGui.QLineEdit.Password)

        ''' set focus to password field if no username saved as default, otherwise the username is in focus '''
        self.pwTxt.setFocus() if len(self.username) else self.userTxt.setFocus() 

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
        passw = unicode(self.pwTxt.text())
        
        try:
            conn = pymssql.connect(*connString)
            with conn:
                cur = conn.cursor()

                cur.callproc('eb_2016_login', (login, passw, ))
                self.returnCode = cur.returnvalue
        except:
            QtGui.QMessageBox.about(self, self.tr('Database connection fault'), self.tr('Failed to connect to database.\nPlease try again later'))
            QtGui.qApp.quit()

        print self.returnCode
   
        if self.returnCode == 0 or self.returnCode == 10:
            ''' Successful login '''
            shared.setCfgUsername(login)  #writes login name to config.ini, for further use in application

            ''' Move to returnCode == 2 section '''
            self.accept()
            QtGui.qApp.removeTranslator(self.translator)
                
        elif self.returnCode == 1:
            ''' Invalid username or password '''
            self.responseLbl.setText(self.tr('Invalid username or password'))
            self.userTxt.setText('')
            self.pwTxt.setText('')
            self.userTxt.setFocus()
            
        elif self.returnCode == 2:
            ''' Successfull login for the first time
                add a nickname, change default password '''
            shared.setCfgUsername(login) #writes login name to config.ini, for further use in application
            if ChangePasswordDialog().exec_() == QtGui.QDialog.Accepted:
                self.accept()
                QtGui.qApp.removeTranslator(self.translator)
            else:
                self.userTxt.setText('')
                self.pwTxt.setText('')
                self.userTxt.setFocus()

        elif self.returnCode == 3:
            ''' Successfull login after password reset '''
            shared.setCfgUsername(login) #writes login name to config.ini, for further use in application
            cpd = ChangePasswordDialog()
            cpd.setResetMode(True)
            if cpd.exec_() == QtGui.QDialog.Accepted:
                self.accept()
                QtGui.qApp.removeTranslator(self.translator)

    def onExit(self):
        """ closes the dialog, and thus the application """
        self.close()
