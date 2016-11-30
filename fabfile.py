from fabric.api import *
from fabric.context_managers import *
import sources.shared as shared

langs = [
    'hu-HU',
    'en-EN',
    'de-DE'
    ]

source_files = [
    'EUROBet2016.py',
    'sources/BetScreen.py',
    'sources/BracketScreen.py',
    'sources/Dialogs.py',
    'sources/GroupScreen.py',
    'sources/ResultScreen.py',
    'sources/ScoreScreen.py'
]

def pyToTs():
    sources = ' '.join(source_files)
    for lang in langs:    
##        cmd = "pylupdate4 %s -ts -noobsolete sources/translations/%s.ts" % (sources, lang)
        cmd = "pylupdate4 %s -ts sources/translations/%s.ts" % (sources, lang)
        local(cmd)

def tsToQm():
    for lang in langs:
        cmd = "lrelease sources/translations/%s.ts -qm resources/translations/%s.qm" % (lang, lang)
        local(cmd)

def run():
    tsToQm()
    local("python EUROBet2016.py")

def build(version):
    """ call it like, fab build:version={NN.NN.NN} """
    tsToQm()
    shared.setCfgUsername('')
    shared.setCfgLang('en-EN')
    shared.setCfgVersionString(version)
    local("python setup.py py2exe")

def buildAdmin():
    local("python setup_admin.py py2exe")

def buildUpdater():
    local("python setup_updater.py py2exe")
