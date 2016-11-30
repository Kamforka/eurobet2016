import os

if os.environ['COMPUTERNAME'] == 'MACKO-PC':
    server = ".\SQLEXPRESS"
    host = "89.147.79.173:1433"
    user = "eb_user"
    password = "kobramaszat"
    db = "eb_2016"
else:
    server = "***confidental***"
    user = "***confidental***"
    password = "***confidental***"
    db = "***confidental***"

connString = [server, user, password, db]





