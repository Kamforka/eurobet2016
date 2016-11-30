#-*-coding:utf-8-*-
from credentials import connString
import pymssql
##
##conn = pymssql.connect(*connString)
##with conn:
##    cur = conn.cursor(as_dict=True)
####    cur.execute('SELECT * FROM eb_2016_bet_view WHERE ID=42')
##    cur.execute("UPDATE eb_2016_matches SET [Hazai]='Németország',\
##                                            [Home]= 'Germany',\
##                                            [Zuhause]='Deutschland',\
##                                            [Vendeg]='GY48',\
##                                            [Visitor]='W48',\
##                                            [Gast]='S48'\
##                                            WHERE ID = 50")
##    conn.commit()
####    for row in cur:
######        for col in row:
####        if(row['V-Goal'] == row['H-Goal'] or row['Nickname'] == ''):
####            print '%s\t\t%s\t:%s' % (row['Nickname'], row['H-Goal'], row['V-Goal'])

            
def setBracketText(ID, hazai, vendeg, home, visitor, zuhause, gast):

    conn = pymssql.connect(*connString)
    with conn:
        cur = conn.cursor(as_dict=True)
        query_string = "UPDATE eb_2016_matches SET [Hazai]='{1}', [Home]= '{2}', [Zuhause]='{3}', [Vendeg]='{4}', [Visitor]='{5}', [Gast]='{6}' WHERE ID = {0}".format(ID, hazai, home, zuhause, vendeg, visitor, gast)
##        print unicode(query_string)
        cur.execute("UPDATE eb_2016_matches SET [Hazai]='Németország', [Home]= 'Germany', [Zuhause]='Deutschland', [Vendeg]='Franciaország', [Visitor]='France', [Gast]='Frankreich' WHERE ID = 50")
##        cur.execute(query_string)
        conn.commit()
    
def setResult(id, hGoal, vGoal):
    pass

def setPenalty(id, hPen, vPen):
    pass
