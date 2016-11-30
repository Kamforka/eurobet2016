#-*- coding: utf-8 -*-
from ConfigParser import ConfigParser
import os
import smtplib
from email.mime.text import MIMEText
import string
import random
import re

def openCfg(cfgFile='config.ini'):
    """ opens the specified config file for reading,
        by default 'config.ini' """
    config = ConfigParser()
    config.read(cfgFile)
    return config

def writeCfg(config, cfgFile='config.ini'):
    """ writes to the specified config file,
        by default 'config.ini' """
    with open(cfgFile, 'w') as cfgFile:
        config.write(cfgFile)


def getCfgLang(cfgFile='config.ini'):
    """ returns the language code from the specified
        config file, by default 'config.ini' """
    config = openCfg(cfgFile)
    return config.get('CONFIG', 'LANG')

def setCfgLang(lang, cfgFile='config.ini'):
    """ writes the specified language to the specified
        config file, by default 'config.ini' """
    config = openCfg(cfgFile)
    config.set('CONFIG', 'LANG', lang)
    writeCfg(config, cfgFile)

def getCfgCountryCode():
    """ returns the subcode from the language code
        e.g.: from 'en-US' returns 'US' """
    langCode = getCfgLang()
    countryCode = langCode.split('-')[1]
    return countryCode

def getCfgUsername(cfgFile = 'config.ini'):
    """ returns the username from the specified
        config file, by default 'config.ini' """
    config = openCfg(cfgFile)
    return config.get('CONFIG', 'USERNAME')

def setCfgUsername(username, cfgFile='config.ini'):
    """ writes the specified username to the specified
        config file, by default 'config.ini' """
    config = openCfg(cfgFile)
    config.set('CONFIG', 'USERNAME', username)
    writeCfg(config, cfgFile)

def getCfgVersionString(cfgFile = 'config.ini'):
    """ returns the version from the specified
        config file, by default 'config.ini' """
    config = openCfg(cfgFile)
    return config.get('CONFIG', 'VERSION')

def setCfgVersionString(version, cfgFile='config.ini'):
    """ writes the specified version to the specified
        config file, by default 'config.ini' """
    config = openCfg(cfgFile)
    config.set('CONFIG', 'VERSION', version)
    writeCfg(config, cfgFile)

def getExtFromFilename(filename):
    """ splits the filename by delimiter '.', reverse the splitted list,
        and returns the first token which is expected to be the extension """
    splits = filename.split('.')
    splits.reverse()
    ext = splits[0]
    return ext

def getLangFromFilename(filename):
    """ splits the filename by delimiter '.', and returns the first token
        which is expected to be the language code """
    splits = filename.split('.')
    lang = splits[0]
    return lang

def getTranslatedLangsFromDir(langDir = './resources/translations'):
    """ returns an array of available translated languages
        from the specified directory, by default ./translations"""
    langs = []
    for dirpath, dirs, files in os.walk(langDir):
        for filename in files:
            ext = getExtFromFilename(filename)
            if ext == 'qm':
                lang = getLangFromFilename(filename)
                langs.append(lang)
    if len(langs): # if at least one translation file found
        return langs
    else:           # if there is no translation file found at all then en-EN is the default    
        return ['en-EN']

def getCountryFlagPath(country):
    """ search for the specified country keyword in the flagpath dictionary
        if the keyword is listed then returns the corresponding flag path
        otherwise return the default flag path"""
    country = country.replace(' ', '').lower() #crops spaces, and lowercase string
    
    ''' the keys are coded as unicode strings,
    because the input from the database is in the format of unicode '''
    flagDict = {
        u"albania" : "resources/flags/albania.png",
        u"albánia" : "resources/flags/albania.png",
        u"albanien" : "resources/flags/albania.png",
        
        u"austria" : "resources/flags/austria.png",
        u"ausztria" : "resources/flags/austria.png",
        u"österreich" : "resources/flags/austria.png",
        
        u"belgium" : "resources/flags/belgium.png",
        u"belgien" : "resources/flags/belgium.png",
        
        u"croatia" : "resources/flags/croatia.png",
        u"horvátország" : "resources/flags/croatia.png",
        u"kroatien" : "resources/flags/croatia.png",
        
        u"czechrepublic" : "resources/flags/czechrepublic.png",
        u"csehország" : "resources/flags/czechrepublic.png",
        u"tschechien" : "resources/flags/czechrepublic.png",
        
        u"england" : "resources/flags/england.png",
        u"anglia" : "resources/flags/england.png",
        
        u"france" : "resources/flags/france.png",
        u"franciaország" : "resources/flags/france.png",
        u"frankreich" : "resources/flags/france.png",
        
        u"germany" : "resources/flags/germany.png",
        u"németország" : "resources/flags/germany.png",
        u"deutschland" : "resources/flags/germany.png",
        
        u"hungary" : "resources/flags/hungary.png",
        u"magyarország" : "resources/flags/hungary.png",
        u"ungarn" : "resources/flags/hungary.png",
        
        u"iceland" : "resources/flags/iceland.png",
        u"izland" : "resources/flags/iceland.png",
        u"island" : "resources/flags/iceland.png",
        
        u"italy" : "resources/flags/italy.png",
        u"olaszország" : "resources/flags/italy.png",
        u"italien" : "resources/flags/italy.png",
        
        u"northernireland" : "resources/flags/northernireland.png",
        u"észak-írország" : "resources/flags/northernireland.png",
        u"nordirland" : "resources/flags/northernireland.png",
        
        u"poland" : "resources/flags/poland.png",
        u"lengyelország": "resources/flags/poland.png",
        u"polen" : "resources/flags/poland.png",
        
        u"portugal" : "resources/flags/portugal.png",
        u"portugália" : "resources/flags/portugal.png",
        
        
        u"republicofireland" : "resources/flags/republicofireland.png",
        u"írország" : "resources/flags/republicofireland.png",
        u"irland" : "resources/flags/republicofireland.png",
        
        u"romania" : "resources/flags/romania.png",
        u"románia" : "resources/flags/romania.png",
        u"rumänien" : "resources/flags/romania.png",
        
        u"russia" : "resources/flags/russia.png",
        u"oroszország" : "resources/flags/russia.png",
        u"russland" : "resources/flags/russia.png",
        
        u"slovakia" : "resources/flags/slovakia.png",
        u"szlovákia" : "resources/flags/slovakia.png",
        u"slowakei" : "resources/flags/slovakia.png",
        
        u"spain" : "resources/flags/spain.png",
        u"spanyolország" : "resources/flags/spain.png",
        u"spanien" : "resources/flags/spain.png",
        
        u"sweden" : "resources/flags/sweden.png",
        u"svédország" : "resources/flags/sweden.png",
        u"schweden" : "resources/flags/sweden.png",
        
        u"switzerland" : "resources/flags/switzerland.png",
        u"svájc" : "resources/flags/switzerland.png",
        u"schweiz" : "resources/flags/switzerland.png",
        
        u"turkey" : "resources/flags/turkey.png",
        u"törökország" : "resources/flags/turkey.png",
        u"türkei" : "resources/flags/turkey.png",
        
        u"ukraine" : "resources/flags/ukraine.png",
        u"ukrajna" : "resources/flags/ukraine.png",
        
        u"wales" : "resources/flags/wales.png",
        }
    
    if country in flagDict.keys():
        return flagDict[country]
    else:
        return "resources/flags/default.png"


def passwGen(length=8):
    """ generates a random password with the specified length,
        by default 8 """
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))

def sendRegEmail(user, email, passw):
    """ Sends a registration email to the  specified user and email address """
    
    mime ="""
    Dear %s,

    Your registration was successful to the EURO Bet 2016 app!
    You can login to the application with the following:

        Username: %s
        Password: %s

    To finish your registration, at your first login a prompt will ask you to change the following:

        Nickname, the name that will be displayed as an ID within the app
        Password, the new password instead of the initially generated one

    Thank you for using our service!
    We wish you a productive betting session!

    Copyright  2016 MaSzaT Team
    """ % (user, user, passw)


    msg = MIMEText(mime)

    From = 'noreply@eurobet2016.hu.bosch.com'
    To = email

    msg['Subject'] = 'EURO Bet 2016 registration notification'
    msg['From'] = From
    msg['To'] = To

    s = smtplib.SMTP('msxsmtp.server.bosch.com')
    s.sendmail(From, [To], msg.as_string())
    s.quit()
    
def sendResetEmail(user, email, passw):
    """ Sends a password reset email to the specified user and email address """
    
    mime ="""
    Dear %s,

    Your password reset was successful to the EURO Bet 2016 app!
    You can login to the application with the following:

        Username: %s
        Password: %s

    At your next login you have to change this generated password!

    Thank you for using our service!
    We wish you a productive betting session!

    Copyright  2016 MaSzaT Team
    """ % (user, user, passw)


    msg = MIMEText(mime)

    From = 'noreply@eurobet2016.hu.bosch.com'
    To = email

    msg['Subject'] = 'EURO Bet 2016 password reset notification'
    msg['From'] = From
    msg['To'] = To
    
    s = smtplib.SMTP('msxsmtp.server.bosch.com')
    s.sendmail(From, [To], msg.as_string())
    s.quit()


def checkUpdateServerAvailable(path=r'P:\public\TEMP\AntalSzabolcs\update'):
    return os.access(path, os.R_OK)
        

def getVersionStringFromFilename(filename):
    """ returns the versionstring from filename """
    versionString = filename.lower().replace('v', '').replace('.7z', '')
    return  versionString
    
def getVersionStringValue(versionString):
    """ returns the calculated value of the version string """
    regex = '[0-9]{2}.[0-9]{2}.[0-9]{2}$'
    match = re.match(regex, versionString)
    if match:
        return int(versionString.replace('.', ''))
    else:
        return -1

def getNewestVersionFilename(path = r"P:\public\TEMP\AntalSzabolcs\update"):
    """ returns the newest version filename from the specified directory path """
    regex = 'V[0-9]{2}.[0-9]{2}.[0-9]{2}.7z$'
    versions = []
    for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                match = re.match(regex, filename, re.IGNORECASE)
                if match:
                    versions.append(filename)
    versions.sort()
    if versions:
        return versions[len(versions)-1]
    else:
        return ''

def getNewestVersionString(path = r"P:\public\TEMP\AntalSzabolcs\update"):
    """ returns the newest version string from the specified directory path """
    regex = 'V[0-9]{2}.[0-9]{2}.[0-9]{2}.7z$'
    
    versions = []
    for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                match = re.match(regex, filename, re.IGNORECASE)
                if match:
                    versions.append(getVersionStringFromFilename(filename))
    versions.sort()
    if versions:
        return versions[-1]
    else:
        return ''

def wipeDirContent(path = r"update"):
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        try:
            if os.path.isfile(filepath) or os.path.isdir(filepath):
                os.unlink(filepath)
        except Exception as e:
            print e
                    
