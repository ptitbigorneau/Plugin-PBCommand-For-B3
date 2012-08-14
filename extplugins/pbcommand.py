# PBcommand Plugin

__author__  = 'PtitBigorneau www.ptitbigorneau.fr'
__version__ = '1.0.6'


import b3, time, threading, thread, re
import b3.plugin
import b3.events
from time import gmtime, strftime
import calendar

class PbcommandPlugin(b3.plugin.Plugin):

    _adminPlugin = None
    
    def onStartup(self):
        
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            self.error('Could not find admin plugin')
            return False

        self._adminPlugin.registerCommand(self, 'putteam',self._putteamlevel, self.cmd_putteam)
        self._adminPlugin.registerCommand(self, 'currentmap',self._currentmaplevel, self.cmd_currentmap, 'cmap')
        self._adminPlugin.registerCommand(self, 'pbmapcycle',self._currentmaplevel, self.cmd_pbmapcycle, 'mapcycle')
        self._adminPlugin.registerCommand(self, 'infoserver',self._infoserverlevel, self.cmd_infoserver, 'iserver')
        self._adminPlugin.registerCommand(self, 'statserver',self._infoserverlevel, self.cmd_statserver)

    def onLoadConfig(self):
        
        self._putteamlevel = self.config.getint('settings', 'putteamlevel')
        self._currentmaplevel = self.config.getint('settings', 'currentmaplevel')
        self._pbmapcycle = self.config.getint('settings', 'pbmapcyclelevel')
        self._infoserverlevel = self.config.getint('settings', 'infoserverlevel')
        self._adminlevel = self.config.getint('settings', 'adminlevel')
        self._modolevel = self.config.getint('settings', 'modolevel') 
    
    def cmd_putteam(self, data, client, cmd=None):
        
        """\
        <name> <team> - Put a player in red, blue or spectator
        """
        
        if data:
            
            input = self._adminPlugin.parseUserCmd(data)
        
        else:
            
            client.message('!putteam <playername> <red, blue or spectator>')
            return
        
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        
        steam = input[1]
        
        if not sclient:
            
            return False
        
        if not steam:
            
            client.message('!putteam <playername> <red, blue or spectator>')
            return False
               
        if (steam == "red") or (steam == "blue") or (steam == "spec") or (steam == "spectator"):
            
            if steam == 'spec':
                steam = 'spectator'
        
        else:
            
            client.message('!putteam <playername> <red, blue or spectator>')
            return False
                    
        if sclient:
                
                self.verbose('Putteam client: %s to team: %s' % (sclient.cid, steam))
                self.console.write('forceteam %s %s' % (sclient.cid, steam))
        
        else:
            return False

    def cmd_currentmap(self, data, client, cmd=None):
        
        """\
        Current map
        """
        
        client.message('^3Current Map is : ^5%s^7'%(self.console.game.mapName))
        
    def cmd_infoserver(self, data, client, cmd=None):
        
        """\
        info server
        """
        
        gametype = self.console.getCvar('g_gametype').getInt()
        
        if gametype==0:
            
            gametype='FreeForAll'

        if gametype==1:
            
            gametype='LastManStanding'

        if gametype==3:
            
            gametype='TeamDeathMatch'

        if gametype==4:
            
            gametype='Team Survivor'

        if gametype==7:
            
            gametype='Capture The Flag'
        
        if gametype==8:
            
            gametype='Bombmode'
            
        cursor = self.console.storage.query("""
        SELECT *
        FROM clients
        ORDER BY time_edit
        """)
        
        tp = 0
        
        if cursor.EOF:

            cursor.close()            
            return False
        
        while not cursor.EOF:
        
            sr = cursor.getRow()
            
            cursor.moveNext()
            
            tp += 1
            
        cursor.close()
        
        map = self.console.game.mapName
                
        if map[:4] == 'ut4_': map = map[4:]
        
        elif map[:3] == 'ut_': map = map[3:]

        client.message('^3Name Server is : ^5%s^7'%(self.console.getCvar('sv_hostname').getString()))

        client.message('^3Adresse : ^5%s^7'%(self.console._publicIp +':'+ str(self.console._port)))
        client.message('^3GameType : ^5%s^3'%(gametype))
        client.message('^3TimeLimit : ^5%s minutes^7'%( self.console.getCvar('timelimit').getInt()))
        client.message('^3Map : ^5%s^7'%(map))
        client.message('^3Total Players : ^5%s^7'%(tp))
                
    def cmd_statserver(self, data, client, cmd=None):
        
        """\
        info stat server
        """
        
        cursor = self.console.storage.query("""
        SELECT *
        FROM clients
        ORDER BY time_edit
        """)
        
        tp = 0
        tpd = 0
        tph = 0
        
        time_epoch = time.time() 
        time_struct = time.gmtime(time_epoch)
        date = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
        mysql_time_struct = time.strptime(date, '%Y-%m-%d %H:%M:%S') 
        mdate = calendar.timegm( mysql_time_struct)
        
        if cursor.EOF:

            cursor.close()            
            return False
        
        while not cursor.EOF:
            sr = cursor.getRow()
            
            dbdate = sr['time_edit']
    
            if mdate - 86400 <= dbdate:
            
                tpd += 1
            
            if mdate - 3600 <= dbdate:
            
                tph += 1
            
            cursor.moveNext()
            tp += 1
            
        cursor.close()
    
        client.message('^3Total Players : ^5%s^7'%(tp))
        client.message('^3Total Players in the last 24 hours : ^5%s^7'%(tpd))
        client.message('^3Total Players in last hour : ^5%s^7'%(tph))

    def cmd_pbmapcycle(self, data, client, cmd=None):
        
        """\
        mapcycle
        """
        
        mapcycletxt = self.console.getCvar('g_mapcycle').getString()
        homepath = self.console.getCvar('fs_homepath').getString()
        gamepath = self.console.getCvar('fs_game').getString()
        mapcyclefile = homepath + "/" + gamepath + "/" + mapcycletxt

        fichier = open(mapcyclefile, "r")
        self.maps = ""
        self.client = client
        for map in fichier:
       
            map = map.replace(" ","")
            map = map.replace("\n","")
            map = map.replace("\r","")
            
            if map != "":
            
                if map[:4] == 'ut4_': map = map[4:]
                elif map[:3] == 'ut_': map = map[3:]

                if self.maps != "":
                    self.maps = self.maps + ", " + map

                else:
                    self.maps = map

        thread.start_new_thread(self.mapcycle, ())

        fichier.close()

    def mapcycle(self):

        self.client.message('^5%s'%(self.maps))

