#!/usr/bin/python
#-*- coding: utf-8-*-

#updater.py

import sys
from PyQt4 import QtGui, QtCore

import sources.shared as shared

import os
import shutil


''' Source module imports '''

#**********************************************************************************************************************************************************

class CopyUpdateThread(QtCore.QThread):
    
    def __init__(self, tmpPath, updatePath, filename):
        super(CopyUpdateThread, self).__init__()

        self.tmpPath = tmpPath
        self.updatePath = updatePath
        self.filename = filename

    def __del__(self):
        self.wait()

    def copyUpdates(self):
        """ copy the update archive to folder tmp """
        print '\nCopying started ... '
        try:
            
            if not os.path.exists(self.tmpPath):
                print 'Creating [tmp] directory ...'
                os.makedirs(self.tmpPath)
                
            try:
                print 'Copying update [{}] to [tmp] ...'.format(self.filename)
                
                shutil.copy(r'{}\{}'.format(self.updatePath, self.filename),
                            self.tmpPath)
                print 'Copying finished'
            except Exception as e:
                print 'Unable to copy update. %s' % e
                sys.exit()
                
        except Exception as e:
            print "Unable to create directory. %s" % e

    def run(self):
        #logic        
        self.sleep(1)
        self.copyUpdates()        

class RemoveCurrentVersionThread(QtCore.QThread):
                            
    def __init__(self, appPath):
        super(RemoveCurrentVersionThread, self).__init__()
        self.appPath = appPath
        
        
    def __del__(self):
        self.wait()

    def wipeFolder(self):
        print '\nWiping started ...'
        dirExc = ['tmp']
        fileExc = ['EUROBet2016_Updater.exe']
        for dirpath, dirnames, filenames in os.walk(self.appPath):
                for dirname in dirnames:
                        
                        if dirname not in dirExc:
                                print r'Wiping directory {}\{} ...'.format(dirpath, dirname)
                                shutil.rmtree(r'{}\{}'.format(dirpath, dirname), ignore_errors=True)

                for filename in filenames:
                        
                        if filename not in fileExc:
                                print r'Wiping file {}\{} ...'.format(dirpath, filename)
                                try:
                                    os.remove(r'{}\{}'.format(dirpath, filename))
                                except:
                                    pass
                                
                break
        print 'Wiping finished ... '
    def run(self):
        #logic
        self.sleep(1)
        self.wipeFolder()

class CleanUpTmpThread(QtCore.QThread):

    

    def __init__(self, tmpPath):
        super(CleanUpTmpThread, self).__init__()
        self.tmpPath = tmpPath

    def __del__(self):
        self.wait()

    def cleanUpTmp(self):
        
        shutil.rmtree(self.tmpPath)

    def run(self):
        self.cleanUpTmp()
        

class Updater(QtGui.QWidget):

    
    ''' PATH constants '''
##    APP_PATH = r'bin_0'
##    TMP_PATH = r'bin_0\tmp'
    APP_PATH = r'.'
    TMP_PATH = r'.\tmp'
    UPDATE_PATH = r'P:\public\TEMP\AntalSzabolcs\update'

    ''' Progress Bar Ratio Constants '''
    CHECK_PROG_RATIO = 0.1
    COPY_PROG_RATIO = 0.2
    WIPE_PROG_RATIO = 0.2
    EXTRACT_PROG_RATIO = 0.4
    CLEAN_UP_PROG_RATIO = 0.1

    ''' Progress Bar Range Constant '''
    PROG_RANGE = 100

    def __init__(self, parent=None):
        super(Updater, self).__init__(parent)
        self.initUI()

    def initUI(self):

        self.checkServerAvailable()

        self.filename = shared.getNewestVersionFilename()

        ''' WIDGETS '''
        headerLbl = QtGui.QLabel('Updating to V{}'.format(shared.getNewestVersionString()), self)
        self.progBar = QtGui.QProgressBar(self)
        self.progBar.setRange(0, self.PROG_RANGE)
        self.progBar.setValue(0)


        ''' PROCESSES '''
        self.extractProcess = QtCore.QProcess(self)
        
        self.startProcess = QtCore.QProcess(self)

        ''' THREADS '''
        self.copyThread = CopyUpdateThread(self.TMP_PATH, self.UPDATE_PATH, self.filename)
        
        self.removeThread = RemoveCurrentVersionThread(self.APP_PATH)
        

        self.cleanUpThread = CleanUpTmpThread(self.TMP_PATH)
        
        
        ''' SEQUENCE '''
        
        self.updateSequence()

        ''' LAYOUT '''

        container = QtGui.QVBoxLayout()
        container.addWidget(headerLbl, alignment=QtCore.Qt.AlignCenter)
        container.addWidget(self.progBar)
        self.setLayout(container)

    def updateSequence(self):
        """ update sequence"""
        
        self.copyThread.start()
        
        self.copyThread.finished.connect(self.removeCurrent)
        
        self.removeThread.finished.connect(self.extractUpdates)
        
        self.extractProcess.finished.connect(self.cleanUpTmp)
        
        self.cleanUpThread.finished.connect(self.startEUROBet)

        

    def checkServerAvailable(self):
        """ checks server accessibility """
        if shared.checkUpdateServerAvailable(self.UPDATE_PATH):
            print 'Server OK...'
            
            
        else:
            print 'Server NOK... Quit'
            msg = 'Update server is not available. Please try again later'
            QtGui.QMessageBox.warning(self, "EUROBet Updater", msg, QtGui.QMessageBox.Ok)
            sys.exit()

    def removeCurrent(self):
        """ starts remove thread and set progress """
        self.setProgress(self.CHECK_PROG_RATIO)
        self.removeThread.start()
   
    def extractUpdates(self):
        """ Extracts update to the location of the application from tmp """
        self.setProgress(self.EXTRACT_PROG_RATIO)
        print '\nExtracting update [{}] ...'.format(self.filename)
        self.extractProcess.start(r'cmd /v:on /c 7z x {}\{} -o{} -y'.format(self.TMP_PATH, self.filename, self.APP_PATH))
        
    def cleanUpTmp(self):
        """ Starts clean up thread and set progress for extract """
        print 'Extracting finished ...'
        print '\nClean up temp ...'
        
        self.setProgress(self.EXTRACT_PROG_RATIO)
        self.cleanUpThread.start()

    def startEUROBet(self):
        """ starts the EUROBet2016 executable, then quits updater """
        print 'Clean up finished ...'
        print '\nEUROBet2016.exe started'
        print '\nUpdater terminated ... '
        self.setProgress(self.CLEAN_UP_PROG_RATIO)
        
        self.startProcess.start(r'{}\EUROBet2016.exe'.format(self.APP_PATH))
        QtGui.qApp.quit()

    def setProgress(self, ratio):
        """ increments the actual value of progress bar by the ratio range """
        if self.progBar.value() + self.PROG_RANGE * ratio < self.PROG_RANGE:
            self.progBar.setValue(self.progBar.value() + self.PROG_RANGE * ratio)
        else:
            self.progBar.setValue(self.PROG_RANGE)
                                  
        

#************************************************************************************************************************************************************#

class EUROBetUpdater(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(EUROBetUpdater, self).__init__(parent)
        self.initUI()

    def initUI(self):

        updater = Updater(self)

        self.setCentralWidget(updater)
        
        self.setWindowTitle('EUROBetUpdater V01.00.00')
        self.setWindowIcon(QtGui.QIcon('resources/icons/euro.png'))
        self.setFixedSize(300, 100)
        self.show()

        self.setFixedSize(300, 100)
        self.show()

def main():
        
        app = QtGui.QApplication(sys.argv)
        
        if '-u' in sys.argv:
            
            with open('resources/styles/default.css', 'r') as appStyle:
                app.setStyleSheet(appStyle.read())
                
            updater = EUROBetUpdater()

            sys.exit(app.exec_())
            
        else:
            
            msg = 'The updater is not a stand-alone executable. It\'s used together with the main application'
            QtGui.QMessageBox.warning(None, "EUROBet Updater", msg, QtGui.QMessageBox.Ok)
            sys.exit(0)
            
        
    
if __name__ == '__main__':

    main()
        
