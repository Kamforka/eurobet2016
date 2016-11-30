from distutils.core import setup
import py2exe
import os

""" list of data_files to pass to setup """
files = []

""" list of directories to search for files """
dirs = ['.\\resources\\flags',
        '.\\resources\\icons',
        '.\\resources\\images',
        '.\\resources\\styles',
        '.\\resources\\translations']

""" loop through the list of directiories and create data_file entries """
for dirpath, dirnames, filenames in os.walk('.'):  
    if dirpath in dirs:
        for filename in filenames:
            filepath = dirpath + '\\' + filename
            fileEntry = (dirpath, [filepath])            
            files.append(fileEntry)

""" static entries go here"""            
files.append(('.', ['.\\config.ini']))

""" build setup """
setup(
    name="EUROBet 2016",
    version="01.00.00",
    description="A betting application for the sake of fun and brotherhood",
    author="sza2mc",
    windows=[{"script" : "EUROBet2016.py"}],
    data_files = files,
    options={
        "py2exe" : {
            "dist_dir" : ".\\bin",
            "includes" : ["sip", "pymssql", "_mssql", "decimal", "uuid"],
            "packages" : ["pymssql", "_mssql"],
            "dll_excludes" : ["MSVCP90.dll"],
            "bundle_files" : 1,
            "compressed" : True
            }
        },
    zipfile = None
    )

