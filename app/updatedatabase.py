import sqlite3

from kivy.utils import platform
plat = platform
if plat == 'android':
    filehome = ''
elif plat == 'ios':
    pass
else:
    import inspect
    filehome = inspect.getfile(inspect.currentframe())[:-7]


def updatesatabase(existingversion):
    if existingversion == 'NewInstall':
        qry1 = open('sql/new_database_createtable.sql', 'r').read()
        conn = sqlite3.connect(filehome + 'database.db')
        c = conn.cursor()
        c.executescript(qry1)
        conn.commit()
        qry2 = open('sql/new_database_data.sql', 'r').read()
        c.executescript(qry2)
        conn.commit()
        c.close()
        conn.close()    
    elif existingversion == '0.0.16':
        pass
    elif existingversion == '0.0.14':
        pass
    elif existingversion == '0.0.11':
        pass
