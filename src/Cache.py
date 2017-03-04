# Completely rewritten with SQL in mind
import MySQLdb
import time
from src.Config import Config 

class Handler:
    def __init__(self):
        self.config = Config()
        sqluser = self.config.Get("sql_user")
        sqlpass = self.config.Get("sql_pass")
        self.sqltable = self.config.Get("sql_db")
        
        #sqluser = "root"
        #sqlpass = ""
        #sqldb = "platypus"

        self.db = MySQLdb.connect(user=sqluser,passwd=sqlpass,db="platypus")
        self.c = self.db.cursor()

    def Get(self,server="all",offline="all"):
        self.db.ping()
        if server == "all":
            self.c.execute("SELECT * FROM "+self.sqltable)
            return self.c.fetchall()
        if offline == "only":
            self.c.execute("SELECT * FROM "+self.sqltable+" WHERE online=false")
            return self.c.fetchall()
        else:
            self.c.execute("SELECT * FROM "+self.sqltable+" WHERE id="+str(server))
            return self.c.fetchall()

    def SetStatus(self,panel,online,cpu,memory,disk):
        print("Setting...")
        self.db.ping()
        self.c.execute("SELECT * FROM "+self.sqltable+" WHERE id="+str(panel))
        wasup = self.c.fetchone()[4]
        udtime = 0

        if online == False and wasup == 1:
            print("Set offline")
            # Server just went offline
            self.c.execute("UPDATE "+self.sqltable+" SET online=false, udtime=0 WHERE id="+str(panel))
            self.db.commit()
            
        if online == True and wasup == 1:
            # Refresh stats (online)
            print("Still online")
            self.c.execute("UPDATE "+self.sqltable+" SET online=true, udtime="+
                str(udtime + self.config.Get("scan_interval"))+", cpu="+ 
                cpu + ", memory="+memory+",disk="+disk+" WHERE id="+str(panel))
            self.db.commit()

        if online == False and wasup == 0:
            print("Still offine")
            # Do nothing (offline)
            self.c.execute("UPDATE "+self.sqltable+" SET online=false, udtime="+
                str(udtime - self.config.Get("scan_interval"))+
                " WHERE id="+str(panel))
            self.db.commit()
        

        if online == True and wasup == 0:
            print("Set online")
            # Panel just went onlie
            self.c.execute("UPDATE "+self.sqltable+" SET online=true, udtime=0, cpu="+ 
                cpu + ", memory="+memory+",disk="+disk+" WHERE id="+str(panel))
            self.db.commit()

    def RemoveServer(self, panel):
        self.c.execute("DELETE FROM "+self.sqltable+" WHERE id="+str(panel))
        self.db.commit()
        return True
    def CreateServer(self, panel, form):
        # Insert new server into database
        self.c.execute("INSERT INTO "+self.sqltable+" (id,name,hostname,location) VALUES (%s,%s,%s,%s)",
            (int(form['id']),form['name'],form['hostname'],form['location']))
        self.db.commit()
        return True
    def ModServer(self, panel, form):
        # Edit server
        self.c.execute("UPDATE "+self.sqltable+" SET name=%s,hostname=%s WHERE id=%s",
            (form['name'], form['hostname'], panel))
        self.db.commit()
        return True

    def GetAsJson(self,server="all",offline="all"):
        raw = self.Get(server,offline)
        res = {}
        for s in raw:
            print(s)
            res[s[0]] = {"name": s[1],
                      "online": s[4],
                      "location": s[3],
                      "cpu": s[6],
                      "memory":s[7],
                      "disk":s[8]}
        return res