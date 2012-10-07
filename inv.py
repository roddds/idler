# -*- coding: utf-8 -*-
import collections
import itertools
import idler
import sys
import json
import requests
import tf2
import urllib2 #for exception catching

ignorelist = [x for x in [line.strip() for line in open('ignorelist.txt', 'r').readlines() if line[0] != '#'] if x]


class Backpack:
    def __init__(self, username):
        self.config = idler.Config()

        self.username = username
        self.apikey   = self.config['apikey']
        self.API      = tf2.API(key=self.apikey)
        self.steamid  = self.vanity(username)

    def __repr__(self):
        return '<inventory instance of "%s">' % self.username

    def __call__(self, **kwargs):
        return self.inventory(**kwargs)

    def __str__(self):
        return self.username

    def vanity(self, username): #modified from https://github.com/VMDX/tf2toolbox
        '''
        Given a Steam Community vanity ID, get the 64 bit Steam ID.
        '''
        #import pdb; pdb.set_trace()
        if len(username) == 17 and username.isdigit():
            return username #it was already a 64 bit Steam ID

        api_call = 'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?vanityurl=%s&key=%s' % (username, self.apikey)
        
        try:
            req = requests.get(api_call, timeout=5)
            req.encoding = 'latin1'
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            raise ValueError("We were unable to retrieve %s's info. The SteamAPI may be down - please try again shortly." % username)
            
        if not req.ok:
            raise ValueError("We were unable to retrieve that user's backpack. The URL may be wrong or the SteamAPI may be down.")

        api_json = json.loads(str(req.content), 'latin1')    # Needs to be latin1 due to funky character names for steamids.

        status = api_json['response']['success']
        if status == 1:
            return api_json['response']['steamid']
        elif status == 42:
            raise ValueError("Sorry, %s is not a valid SteamCommunity ID." % username)
        else:
            raise ValueError("There is a problem with Valve's API.")

    def inventory(self, getunplaced=False, everything=False):
        '''Gets the FIRST page of a user's inventory. If the getunplaced
        flag is set to True, it'll only retrieve the items in the "unplaced"
        position, i.e. items that just dropped. The 'getunplaced' flag makes
        it only return items in the 'unplaced' slot. If the flag 'everything'
        is set to True it'll return every item in the backpack, instead of
        only the first page.
        '''

        try:
            self.API.getBackpack(self.steamid)
        except urllib2.HTTPError as error:
            raise ValueError('503: Service Unavailable')
        except urllib2.URLError:
            raise ValueError('The remote host closed the connection.')

        weapons = [x['item_name'] for x in self.API.schema['result']['items']['item'] if x.get('craft_class') == 'weapon' or x.get('craft_material_type') == 'weapon']
        items = self.API.users[self.steamid]['backpack'].matrix

        if everything == True:
            backpack = [items[slot]['data']['item_name'] for slot  in items]
        else:
            backpack = [items[slot]['data']['item_name'] for slot  in items if items[slot]['position']['page']==0]
        
        unplaced = [items['item_name'] for items in self.API.users[self.steamid]['backpack'].unplaced]

        if getunplaced == True:
            bp = unplaced
        else:
            bp = backpack+unplaced

        bp = [z for z in bp if z not in [x for x in bp for y in ignorelist if y in x]]

        self.bp = bp
        self.items = sorted(['* %s' % hat if hat not in weapons else '  %s' % hat for hat in bp]) #adds an asterisk to the name if it's not a normal weapon
        return self.items


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        raise SystemExit("You're doing it wrong")

    if '-full' in sys.argv:
        everything = True
        sys.argv.remove('-full')
    else:
        everything = False

    if '-count' in sys.argv:
        count = True
        sys.argv.remove('-count')

    if '-all' in sys.argv:
        config = idler.Config()
        accounts = [config['accounts'][steamid]['steamcommunity'] for steamid in config['accounts']]
    else:
        accounts = sys.argv[1:]
        if len(accounts) <= 0:
            raise SystemExit("We need some accounts here, bro.")

    if count:
        items = [Backpack(steamid).inventory(everything=True) for steamid in accounts]
        items = list(itertools.chain.from_iterable(items))
        counter = collections.Counter()
        for item in items:
            counter[item] += 1

        print "Item count: %d" % len(items)
        import pdb; pdb.set_trace()
        for k, v in iter(sorted(counter.items(), reverse=True, key=lambda x: x[1])):
            print "%d %s" % (v, k.replace('*', '').strip())
    else:
        for steamid in accounts:
            try:
                items = Backpack(steamid).inventory(everything=everything)
            except ValueError as error:
                raise SystemExit(error.message)

            print "\n%s's inventory:" % steamid
            if len(items) > 0:
                print "%d items" % len(items)
                try:
                    print '\n'.join(items)
                except UnicodeError:
                    print '\n'.join(items).encode('utf8')
            else:
                print '0 items'
