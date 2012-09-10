# -*- coding: utf-8 -*-
#!/usr/bin/env python
""" TF2 Web API class v0.0.1.2
-----------------------------------------------------------------------
Foreword:

 * Remember the API restrictions if you are using this online!
  (i.e. remember to put the Valve logo, etc., where you should!)

 * Remember, if you want to distribute this, abide by the license below.
  (It's free to use, all I ask is for attribution.)

-----------------------------------------------------------------------
Copyright (c) 2010, A.W. 'Swixel' Stanley 
All rights reserved. 

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions 
are met: 

 * Redistributions of source code must retain the above copyright 
   notice, this list of conditions and the following disclaimer. 
 * Redistributions in binary form must reproduce the above copyright 
   notice, this list of conditions and the following disclaimer in 
   the documentation and/or other materials provided with the 
   distribution. 
 * Neither the name of swixel.net nor the names of its contributors 
   may be used to endorse or promote products derived from this 
   software without specific prior written permission. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""

""" What's needed -- all in Python 2.6 """
import json, codecs, urllib2, os, datetime


""" Some globals to make this neater """ 
def _read_local(f):
    """ Open a local file """
    try: rtn = codecs.open(f,'r','utf-8').read()
    except Exception: rtn = None
    return rtn

def _get_remote(r,l):
    """ Get Remote resource, save as Local resource """
    try:
        o = codecs.open(l,'w','utf-8')
        q = urllib2.urlopen(r).read().decode('utf-8')
        o.write(q)
        o.close()
        del q
        rtn = _read_local(l)
    except Exception: rtn = False
    return rtn

def _decimal_to_binary(i):
    """ take binary, return decimal - looks complex, isn't """
    b=0;i=int(i)
    while(i>1):m=i%2;i=i/2;b=(b*10)+m
    b=(b*10)+i;b=str(b)[::-1]
    if(len(b)<32):b=str(b)+str('0')*(32-len(b))
    return b

def _binary_to_decimal(b):
    """ simple, and yet fun """
    b=str(b);d=0;l=len(b)
    for i in xrange(l):d=d+(int(b[i])*pow(2,((l-i)-1)))
    return d

class Loadout(object):
    """ Just a small wrapper """
    def __init__(self,role=None):
        """ Assign 'class' (role, due to protected word).
        Assume that 'None' on the slots is default. """
        self.ROLE = role
        self.PRIMARY = None
        self.MELEE = None
        self.HEAD = None
        self.MISC = None
        if(role == 'Spy'):
            self.PDA2 = None
        else:
            self.SECONDARY = None

    def load(self,slot=None,item=None):
        """ Load an item """
        try: self.__setattr__(slot.upper(),item)
        except Exception: pass

    def __str__(self): return "<%s Loadout>" % self.ROLE
    def __repr__(self): return self.__str__()

class Backpack(object):
    """ Meet the Backpack <insert interlude here>
    It does not care who carries it (and it eats the Sandvich for breakfast).
    It's a basic class, does very little, but could be expanded if you want.
    I've made it a self-contained class so you can have roaming backpacks
    instead of using the main API construction. """

    def __init__(self,schema=None,data=None,lang='en'):
        """ Location of schema file, language used, and Steam API key """
        self.schema = schema
        self.data = data
        self.lang = lang
        self.matrix = {}
        self.unplaced = []
        self.count = 0
        self.loadouts = {'Engineer':Loadout('Engineer'),
                         'Spy':Loadout('Spy'),
                         'Pyro':Loadout('Pyro'),
                         'Heavy':Loadout('Heavy'),
                         'Medic':Loadout('Medic'),
                         'Demoman':Loadout('Demoman'),
                         'Soldier':Loadout('Soldier'),
                         'Sniper':Loadout('Sniper'),
                         'Scout':Loadout('Scout')}
        self._process_items()

    def _bin_to_class(self,b):
        """ Take substring 7 through 16 as binary, find classes
        which are carrying this item.  Return it. """
        e = []
        for i in xrange(-1,8):
            if(int(b[i]) == 1):
                e.append(['Engineer','Spy','Pyro','Heavy','Medic','Demoman','Soldier','Sniper','Scout'][i])
        return e

    def _loc_to_xy(self,b):
        """ Returns Slot ID """
        return _binary_to_decimal(b)

    def _get_schema_item(self,id):
        """ Pull the item out of the schema """
        items = self.schema['result']['items']['item']
        for item in items:
            if(item['defindex'] == id):
                break;
        return item

    def _process_items(self):
        """ Internal process function """
        try:
            items = self.data['result']['items']['item'] # wtf valve? items->item?
        except KeyError:
            raise ValueError('Private or empty backpack')

        self.count = len(items)
        for item in items:
            d = {}
            del item['id'] # yep...
            schema_data = self._get_schema_item(item['defindex'])
            d['item_name'] = schema_data['item_name']

            if d['item_name'] == u"Mann Co. Supply Crate": #added by roddds
                d['item_name'] += ' #%s' % int(item['attributes']['attribute'][0]['float_value'])

            d['item_slot'] = schema_data['item_slot']
            i = _decimal_to_binary(item['inventory'])
            equipped = self._bin_to_class(i[7:16])
            for c in equipped:
                self.loadouts[c].load(d['item_slot'],d['item_name'])
            d['equipped'] = True if(len(equipped)>0) else False
            pos = self._loc_to_xy(i[16:])
            d['slot'] = pos
            d['quantity'] = item['quantity']
            d['quality'] = item['quality']
            d['level'] = item['level']
            d['img'] = schema_data['image_inventory'].split("/")[-1]
            if(pos == 0):
                self.unplaced.append(d)
            else:
                self.matrix["Slot %s" % str(pos).rjust(3,'0')] = {'data':d,'position':{'page': pos/50,'row':pos/10,'column':pos%10}}

    def JSONOut(self):
        """ Mmm, human readable and useful without this file ... """
        pass

    def HTMLTable(self):
        """ Another option """
        pass

    def HTMLDiv(self,divclass='item',slotattr='id'):
        """ Output divs """
        pass

    def __repr__(self):
        return("<Backpack(%s/100)>" % str(self.count))


class API(object):
    """ TF2 Global API Wrapper """

    """ No, really ... I love these """
    __jd = json.JSONDecoder()
    __je = json.JSONEncoder()

    def __init__(self,lang='en',key=""):
        """ Initialise! """
        self.key = key
        self.lang = lang
        """ users = for users; _users = raw source data if you want it later """
        self.users = {} # Useful/Metal
        self._users = {} # JSON/jarate
        # n.b. self.users = {'user':{'backpack':Backpack()}, ...}
        self._get_schema(os.path.join(os.getcwd(),'schema.%s.json' % lang), self.__get_schema_link())

    def __init_user(self,s):
        """ Simple function to ensure users exist in both dicts """
        if(s not in list(self.users.keys())): self.users[s] = {}
        if(s not in list(self._users.keys())): self._users[s] = {}

    def __get_schema_link(self):
        """ NEED A DISPENSER HERE! (no, really: get schema link) """
        return "http://api.steampowered.com/ITFItems_440/GetSchema/v0001/?key=%s&format=json&language=%s" % (self.key,self.lang)

    def __get_playeritems_link(self,s):
        """ NEED A DISPENSER HERE! (no, really: get a player's item data link) """
        return "http://api.steampowered.com/ITFItems_440/GetPlayerItems/v0001/?key=%s&SteamID=%s&lang=%s" % (self.key,s,self.lang)

    def __get_profile_base(self):
        """ NEED A SENTRY HERE! (... seriously) """
        return "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0001/?key=%s&lang=%s&steamids=" % (self.key,self.lang)


    def _get_schema(self,f,r):
        """ Check if the schema file exists, if not, fetch it. """
        j =_read_local(f)
        if(j == None):
            j = _get_remote(r,f)
        if(j == None):
            raise ImportError("[JARATE] Cannot download or open a local copy of the schema json file.")
        try:
            self.schema = self.__jd.decode(j)
        except Exception:
            raise ImportError("[JARATE] Your schema isn't in JSON, time for some jarate son! *splash*")

    def _update_schema(self):
        """ Whack the schema with your wrench (upgrade/repair) """
        self.schema = self.__jd.decode(_get_remote(self.__get_schema_link(),os.path.join(os.getcwd(),'schema.%s.json' % lang)))

    def selectUser(self,sid):
        """ This just changes the focus - pointless, except it makes it pretty (like hats)! """
        self.focus = sid

    def getProfile(self,s=None):
        """ Can load one of many ... just CSV the s if you want many."""
        if(s == None):
            raise ImportError("[JARATE] Profile for whom?!")
        data = self.__jd.decode(urllib2.urlopen("%s%s" % (self.__get_profile_base(),s)).read().decode('utf-8'))
        extracted = data['response']['players']['player']
        for i in xrange(len(extracted)):
            data = extracted[i-1]
            s = str(data['steamid']) # We want this to be consistent ...
        self.__init_user(s)
        self._users[s]['_steam_profile'] = {'data':data,'last_update':datetime.datetime.now()} # Woo, duplicates!
        self.users[s]['profile'] = data # I need to make this 'cooler', but I'm releasing it now to meet demand.

    def getBackpack(self,s=None):
        """ Load the backpack for the user """
        if(s == None):
            raise ImportError("[JARATE] Cannot import a backpack with no carrier?!")
        self.focus = s
        data = self.__jd.decode(urllib2.urlopen(self.__get_playeritems_link(s)).read().decode('utf-8'))
        self.__init_user(s)
        self._users[s]['_player_items'] = {'data':data,'last_update':datetime.datetime.now()}
        self.users[s]['backpack'] = Backpack(schema=self.schema,data=data,lang=self.lang)

    def delUser(self,sid):
        """ Bloody hell you're awful. """
        del self.users[sid]
        del self._users[sid]
