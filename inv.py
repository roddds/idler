import tf2 as tf2webappy
import urllib2 #for exception catching
import requests
import json

ignored = [u'Mann Co. Supply Crate',            # You can add to this list items that you don't
           u'Noise Maker - Winter Holiday',     # care about if they're on your inventory or not
           u'Seal Mask',
           u'Mann Co. Cap',
           u'Mercenary',
           u'Spirit Of Giving']


def vanity(vanity_id, APIKEY): #modified from https://github.com/VMDX/tf2toolbox
    '''
    Given a Steam Community vanity ID, get the 64 bit Steam ID.
    '''
    if len(vanity_id) == 17 and vanity_id.isdigit():
        return vanity_id #it was already a 64 bit Steam ID

    api_call = 'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?vanityurl=%s&key=%s' % (vanity_id, APIKEY)
    

    try:
        req = requests.get(api_call, timeout=5)
        req.encoding = 'latin1'
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        raise ValueError("We were unable to retrieve that player's info. The SteamAPI may be down - please try again shortly.")
        

    if not req.ok:
        raise ValueError("We were unable to retrieve that user's backpack. The URL may be wrong or the SteamAPI may be down.")

    api_json = json.loads(str(req.content), 'latin1')    # Needs to be latin1 due to funky character names for usernames.

    status = api_json['response']['success']
    if status == 1:
        return api_json['response']['steamid']
    elif status == 42:
        raise ValueError("Sorry, %s is not a valid SteamCommunity ID." % vanity_id)
        
    else:
        raise ValueError("There is a problem with Valve's API.")


def viewinv(username, APIKEY, getunplaced=False, everything=False):
    '''Gets the FIRST page of a user's inventory. If the getunplaced
    flag is set to True, it'll only retrieve the items in the "unplaced"
    position, i.e. items that just dropped. The 'getunplaced' flag makes
    it only return items in the 'unplaced' slot. If the flag 'everything'
    is set to True it'll return every item in the backpack, instead of
    only the first page.
    '''
    
    try:
        API = tf2webappy.API(key=APIKEY) # I'm not sure what this is here for.
    except:
        raise ValueError('\n'.join(['Unknown response from Steam API. Exiting...',
                                    'Was using API Key %s' % APIKEY ]))
    
    USER = vanity(username, APIKEY)

    try:
        API.getBackpack(USER)
    except urllib2.HTTPError as error:
        raise ValueError('503: Service Unavailable')

    weapons = [x['item_name'] for x in API.schema['result']['items']['item'] if x.get('craft_class') == 'weapon' or x.get('craft_material_type') == 'weapon']

    items = API.users[USER]['backpack'].matrix

    if everything == True:
        backpack = [items[slot]['data']['item_name'] for slot  in items]
    else:
        backpack = [items[slot]['data']['item_name'] for slot  in items if items[slot]['position']['page']==0]
    
    unplaced = [items['item_name'] for items in API.users[USER]['backpack'].unplaced]

    if getunplaced == True:
        bp = filter(lambda x: x not in ignored, unplaced)
    else:
        bp = filter(lambda x: x not in ignored, backpack+unplaced)

    bp = sorted(['* %s' % hat if hat not in weapons else '  %s' % hat for hat in bp]) #adds an asterisk to the name if it's not a normal weapon
    bp = [item.encode('latin') for item in bp]
    return bp


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        raise SystemExit("You're doing it wrong")

    if '-full' in sys.argv:
        everything = True
    else:
        everything = False

    from idler import Config  # gets list of steamcommunity IDs from configuration file
    config = Config()

    if sys.argv[1] == '-all':
        
        for account in config['accounts']:
            print "\n%s's first page inventory:" % account,
            try:
                items = viewinv(config['accounts'][account]['steamcommunity'], config['apikey'], everything=everything)
            except ValueError as error:
                raise SystemExit(error.message)
            if len(items) > 0:
                print "%d items" % len(items)
                try:
                    print '\n'.join(items)
                except UnicodeError:
                    print '\n'.join(items).encode('utf8')
            else:
                print '0 items'

    else:
        account = sys.argv[1]
        print "%s's first page inventory:" % account
        try:
            items = viewinv(account, config['apikey'], everything=everything)
        except ValueError as error:
            print error.message
            sys.exit(0)


        if len(items) > 0:
            print "%d items" % len(items)

            if '-best' in sys.argv:
                items = [x for x in items if x[0] == '*']

            try:
                print '\n'.join(items)
            except UnicodeError:
                print '\n'.join(items).encode('utf8')

        else:
            print '0 items'
