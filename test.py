#-*- coding:utf-8-*-
import sys
import unittest
import sources.shared as shared
from PyQt4 import QtGui, QtCore, QtTest


from sources.Dialogs import LoginDialog, ChangePasswordDialog

app = QtGui.QApplication(sys.argv)

with open('resources/styles/default.css', 'r') as appStyle:
    app.setStyleSheet(appStyle.read())

class LoginDialogTest(unittest.TestCase):
    """ Test the LoginDialog class """

    def setUp(self):
        """ Creates the GUI """
        shared.setCfgLang('en-EN')
        shared.setCfgUsername('Username')
        self.login = LoginDialog()

    def setDefaults(self):
        """ Sets up default values """
        shared.setCfgUsername('Username')
        shared.setCfgLang('en-EN')
        self.login.pwTxt.setText('password')
        
    def test_defaults(self):
        """ Tests defaults """
        self.setDefaults()
        self.assertEqual(self.login.language, 'en-EN')
        self.assertEqual(self.login.userTxt.text(), QtCore.QString('Username'))
        self.assertEqual(self.login.pwTxt.text(), QtCore.QString('password'))
        self.assertEqual(self.login.responseLbl.text(), QtCore.QString(''))
        print 'LoginDialog Defaults OK '

    def test_invalid_response(self):
        """ Tests invalid response """
        self.setDefaults()
        
        QtTest.QTest.mouseClick(self.login.logonBtn, QtCore.Qt.LeftButton)
        self.assertEqual(self.login.userTxt.text(), QtCore.QString(''))
        self.assertEqual(self.login.pwTxt.text(), QtCore.QString(''))
        self.assertEqual(self.login.returnCode, 1)
        self.assertEqual(self.login.responseLbl.text(), QtCore.QString('Invalid username or password'))
        print 'LoginDialog Invalid Login OK '
        
    def setValidLogin(self):
        """ Sets up a valid user input """
        self.login.userTxt.setText('sza2mc')
        self.login.pwTxt.setText('cobra')

    def test_valid_response(self):
        """ Tests valid response """
        self.setValidLogin()
        
        QtTest.QTest.mouseClick(self.login.logonBtn, QtCore.Qt.LeftButton)
        self.assertEqual(self.login.userTxt.text(), QtCore.QString('sza2mc'))
        self.assertEqual(self.login.pwTxt.text(), QtCore.QString('cobra'))
        self.assertEqual(self.login.returnCode, 10)
        print 'LoginDialog Valid Login OK '

class ChangePasswordDialogTest(unittest.TestCase):
    """ Tests the change password dialog """

    def setUp(self):
        """ Creates the GUI """
        shared.setCfgLang('en-EN')
        shared.setCfgUsername('sza22mc')
        self.cpd = ChangePasswordDialog()

    def setDefaults(self):
        """ Sets up defaults  """
        self.cpd.resetMode = False

    def test_defaults(self):
        """ Tests Default settings """
        self.assertEqual(self.cpd.nickTxt.text(), QtCore.QString(''))
        self.assertEqual(self.cpd.newPwTxt1.text(), QtCore.QString(''))
        self.assertEqual(self.cpd.newPwTxt2.text(), QtCore.QString(''))
        print 'ChangePasswordDialog Defaults OK'

    def test_unidentical_password(self):
        """ Tests unidentical passwords """
        self.cpd.newPwTxt1.setText('pw1')
        self.assertEqual(self.cpd.newPwTxt1.text(), QtCore.QString('pw1'))
        self.cpd.newPwTxt2.setText('pw2')
        self.assertEqual(self.cpd.newPwTxt2.text(), QtCore.QString('pw2'))
        
        QtTest.QTest.mouseClick(self.cpd.changeBtn, QtCore.Qt.LeftButton)
        self.assertEqual(self.cpd.nickTxt.text(), QtCore.QString(''))
        self.assertEqual(self.cpd.newPwTxt1.text(), QtCore.QString(''))
        self.assertEqual(self.cpd.newPwTxt2.text(), QtCore.QString(''))
##        self.assertEqual(self.cpd.newPwTxt1.hasFocus(), True)
        self.assertEqual(self.cpd.responseLbl.text(), QtCore.QString('Passwords are not matching'))
        print 'ChangePasswordDialog unidentical password OK'

    def test_taken_nickname(self):
        """ Tests for taken nickname """
        
        self.cpd.nickTxt.setText('brahm')
        self.assertEqual(self.cpd.nickTxt.text(), QtCore.QString('brahm'))
        
        self.cpd.newPwTxt1.setText('pw1')
        self.assertEqual(self.cpd.newPwTxt1.text(), QtCore.QString('pw1'))
        self.cpd.newPwTxt2.setText('pw1')
        self.assertEqual(self.cpd.newPwTxt2.text(), QtCore.QString('pw1'))

        QtTest.QTest.mouseClick(self.cpd.changeBtn, QtCore.Qt.LeftButton)
        self.assertEqual(self.cpd.nickTxt.text(), QtCore.QString(''))
        self.assertEqual(self.cpd.newPwTxt1.text(), QtCore.QString(''))
        self.assertEqual(self.cpd.newPwTxt2.text(), QtCore.QString(''))
##        self.assertEqual(self.cpd.newPwTxt1.hasFocus(), True)
        self.assertEqual(self.cpd.responseLbl.text(), QtCore.QString('Nickname is already taken'))
        print 'ChangePasswordDialog taken nickname OK'


        

    
        

if __name__ == '__main__':
    unittest.main()
