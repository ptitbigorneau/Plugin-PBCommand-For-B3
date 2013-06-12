# PBcommand Plugin

__author__  = 'PtitBigorneau www.ptitbigorneau.fr'
__version__ = '1.3'


import b3, time, threading, thread, re
import b3.plugin
import b3.events
from time import gmtime, strftime
import calendar

class PbcommandPlugin(b3.plugin.Plugin):

    _adminPlugin = None
    _putteamlevel = 20
    _currentmaplevel = 1
    _pbcyclemaplevel = 1
    _infoserverlevel = 1
    _mplevel = 2
    _adminlevel = 100
    _test = None
    _listmap = []

    def onStartup(self):
        
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            self.error('Could not find admin plugin')
            return False

        self._adminPlugin.registerCommand(self, 'putteam',self._putteamlevel, self.cmd_putteam)
        self._adminPlugin.registerCommand(self, 'currentmap',self._currentmaplevel, self.cmd_currentmap, 'cmap')
        self._adminPlugin.registerCommand(self, 'pbmapcycle',self._pbcyclemaplevel, self.cmd_pbmapcycle, 'mapcycle')
        self._adminPlugin.registerCommand(self, 'infoserver',self._infoserverlevel, self.cmd_infoserver, 'iserver')
        self._adminPlugin.registerCommand(self, 'statserver',self._infoserverlevel, self.cmd_statserver)
        self._adminPlugin.registerCommand(self, 'messageprivate',self._mplevel, self.cmd_messageprivate, 'mp')

    def onLoadConfig(self):
        
        try:
            self._putteamlevel = self.config.getint('settings', 'putteamlevel')
        except Exception, err:
            self.warning("Using default value %s for putteamlevel. %s" % (self._putteamlevel, err))
        self.debug('putteamlevel : %s' % self._putteamlevel)

        try:
            self._currentmaplevel = self.config.getint('settings', 'currentmaplevel')
        except Exception, err:
            self.warning("Using default value %s for currentmaplevel. %s" % (self._currentmaplevel, err))
        self.debug('currentmaplevel : %s' % self._currentmaplevel)

        try:
            self._pbcyclemaplevel = self.config.getint('settings', 'pbcyclemaplevel')
        except Exception, err:
            self.warning("Using default value %s for pbcyclemaplevel. %s" % (self._pbcyclemaplevel, err))
        self.debug('pbcyclemaplevel : %s' % self._pbcyclemaplevel)

        try:
            self._infoserverlevel = self.config.getint('settings', 'infoserverlevel')
        except Exception, err:
            self.warning("Using default value %s for infoserverlevel. %s" % (self._infoserverlevel, err))
        self.debug('infoserverlevel : %s' % self._infoserverlevel)

        try:
            self._adminlevel = self.config.getint('settings', 'adminlevel')
        except Exception, err:
            self.warning("Using default value %s for adminlevel. %s" % (self._adminlevel, err))
        self.debug('adminlevel : %s' % self._adminlevel)

        try:
            self._mplevel = self.config.getint('settings', 'mplevel')
        except Exception, err:
            self.warning("Using default value %s for mplevel. %s" % (self._mplevel, err))
        self.debug('mplevel : %s' % self._mplevel)

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

        map = self.console.game.mapName

        if map[:4] == 'ut4_': map = map[4:]
        
        elif map[:3] == 'ut_': map = map[3:]

        client.message('^3Current Map is : ^5%s^7'%(map))
        
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

        if gametype==9:
            
            gametype='Jump'
            
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
                
                if self._test == None:
            
                    if "{" in map:
                        self._test = "test"
                        continue
            
                    else:
                        self._listmap.append(map)
        
                if self._test != None:
            
                    if "}" in map:
                        self._test = None

        thread.start_new_thread(self.mapcycle, ())

        fichier.close()

    def mapcycle(self):

        maps = ""

        for map in self._listmap:

            if map != "":
            
                if map[:4] == 'ut4_': map = map[4:]
                elif map[:3] == 'ut_': map = map[3:]

                if maps != "":
                    maps = maps + ", " + "^5%s^7"%(map)

                else:
                    maps = "^5%s^7"%(map)

        self.client.message('%s'%(maps))

    def cmd_messageprivate(self, data, client, cmd=None):
        
        """\
        <client> <message> - private message
        """
        
        if data:
            
            input = self._adminPlugin.parseUserCmd(data)
        
        else:
            
            client.message('!messageprivate <playername> <message>')
            return
        
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        
        message = input[1]
        
        if not sclient:
            
            return False
        
        if not message:
            
            client.message('!messageprivate <playername> <message>')
            return False
               
        if sclient:

            sclient.message('%s^3[pm]^7: %s'%(client.exactName, message))
        
        else:
            return False
