from distutils.core import setup
import py2exe
import os

""" build setup """
setup(
    name="EUROBet2016 Admin",
    version="01.00.00",
    description="Admin interface for EUROBet2016",
    author="sza2mc",
    windows=[{"script" : "EUROBet2016_Admin.py"}],
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
