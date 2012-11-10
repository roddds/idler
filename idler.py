# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        idler.py
# Purpose:     Cycles through a set list of Team Fortress 2 accounts
#              
#
# Author:      roddds
#
# Created:     01/02/2012
# Licence:     Public Domain, except when noted otherwise.
#-------------------------------------------------------------------------------

import os
import sys
import idle
import json
import updater
from menu import menu
import WConio

class Config():
    '''
    Reads from the configuration file and returns an object that can be
    accessed like a dictionary.
    '''
    def __init__(self):
        with open('config.ini') as f:
            self.options = json.load(f)
    
    def __call__(self):
        return self.options
    def __getitem__(self, i):
        return self.options[i]
    def __enter__(self):
        return self
    def __exit__(self, *exc_info):
        pass

class Idler:
    def __init__(self):
        self.config = Config()
       
        if not os.path.exists(self.config['steampath']):
            raise SystemExit('steam.exe not found. Did you check your preferences?\n')

        if '-login' in sys.argv:
            import subprocess as sp

            username = sys.argv[-1]
            try:
                password = self.config['accounts'][sys.argv[-1]]['password']
            except KeyError:
                print "\nNo login information for that account found. Did you type your username in"
                print "correctly? You might be typing in the SteamCommunity name, but we need the"
                print "actual login name for the account."
                sys.exit(0)
            
            if idle.isrunning('hl2.exe'):
               idle.kill('hl2.exe')
            if idle.isrunning('steam.exe'):
               idle.kill('steam.exe')        #kills Steam and TF2 wether they're running or not

            launchargs = self.config['steampath'] + ' -login {0} {1}'.format(username, password)
            print 'Launching account %s...' % username
            sp.Popen(launchargs)

        elif '-start' in sys.argv:
            import subprocess as sp

            if not idle.isrunning('steam.exe'):
                raise SystemExit("Steam is not running. Please run this without arguments to select an account.")

            launchargs = self.config['steampath']+' -applaunch 440 -console -textmode -novid -nosound -noipx -nopreload -nojoy -noshader +map_background ctf_2fort'
            print 'Launching idler'
            sp.Popen(launchargs)

        elif '-continue' in sys.argv:
            idle.continueidling(self.config)

        elif '-infinite' in sys.argv: #very rough implementation
            print len(self.config['accounts']), 'account(s) identified.\n'
            
            while True:
                for username in sorted(list(self.config['accounts'].iterkeys())):
                    idle.idle(username, self.config)

        else: #no valid arguments
            WConio.setcursortype(0)
            print len(self.config['accounts']), 'account(s) identified.\n'

            usernames = menu( ['Idle with all accounts'] + sorted(list(self.config['accounts'].iterkeys())) + ['Exit'] )

            if usernames == ['Idle with all accounts']:
                for name in [name for name in self.config['accounts'].iterkeys()]:
                    idle.idle(name, self.config)

                print 'Finished idling for all accounts!'
            elif (usernames == 'Exit') or ('Exit' in usernames):
                pass
            else:
                for name in usernames:
                    idle.idle(name)
            
            WConio.setcursortype(1)

if __name__ == '__main__':
    try:
        updater.update()
    except Exception as e:
        print 'Error found while trying to download update:'
        print e.message

    Idler()