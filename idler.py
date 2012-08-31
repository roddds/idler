#-------------------------------------------------------------------------------
# Name:        idler.py
# Purpose:     Cycles through a set list of Team Fortress 2 accounts
#              
#
# Author:      roddds
#
# Created:     01/02/2012
# Licence:     Public Domain
#-------------------------------------------------------------------------------

import os
import sys
import idle
import json

class Config():
    '''
    Reads from the configuration file and returns an object that can be
    accessed like a dictionary.
    '''
    def __init__(self):
        cfg =  open('config.ini').read()
        self.options = json.loads(cfg)
    
    def __call__(self):
        return self.options
    def __getitem__(self, i):
        return self.options[i]
    def __enter__(self):
        return self
    def __exit__(self, *exc_info):
        pass


if __name__ == '__main__':
    from menu import menu
    import WConio; WConio.setcursortype(0)

    config = Config()
   
    if not os.path.exists(config['steampath']):
        raise SystemExit('steam.exe not found. Did you check your preferences?\n')

    if '-login' in sys.argv:
        import subprocess as sp

        if idle.isrunning('hl2.exe'):
           idle.kill('hl2.exe')
        if idle.isrunning('steam.exe'):
           idle.kill('steam.exe')        #kills Steam and TF2 wether they're running or not
        
        username = sys.argv[-1]
        try:
            password = config['accounts'][sys.argv[-1]]['password']
        except KeyError:
            print "\nNo login information for that account found. Did you type your username in"
            print "correctly? You might be typing in the SteamCommunity name, but we need the actual"
            print "login name for the account."
            sys.exit(0)

        launchargs = config['steampath'] + ' -silent -login {0} {1}'.format(username, password)
        print 'Launching account %s...' % username
        sp.Popen(launchargs)

    elif '-start' in sys.argv:
        import subprocess as sp

        if not idle.isrunning('steam.exe'):
            raise SystemExit("Steam is not running. Please run this without arguments to select an account.")

        launchargs = config['steampath']+' -applaunch 440 -console -textmode -novid -nosound -noipx -nopreload -nojoy -noshader +map_background ctf_2fort'
        print 'Launching idler'
        sp.Popen(launchargs)

    elif '-continue' in sys.argv:
        idle.continueidling(config)

    else: #no valid arguments
        print len(config['accounts']), 'account(s) identified.\n'

        usernames = menu( ['Idle with all accounts'] + sorted(list(config['accounts'].iterkeys())) + ['Exit'] )

        if usernames == 'Idle with all accounts':
            for name, password in [(name, config['accounts'][name]['password']) for name in config['accounts']]:
                idle.startup(name, config)

            print 'Finished idling for all accounts!'
        elif (usernames == 'Exit') or ('Exit' in usernames):
            pass
        else:
            for name in usernames:
                idle.startup(name, config)
        
        WConio.setcursortype(1)