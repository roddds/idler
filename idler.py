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
#!/usr/bin/env python

import time, datetime
import os
import sys
import subprocess as sp

def isrunning(processname):
    '''Returns True or False depending on if processname is running or
    not. Case-sensitive.'''
    lines = sp.Popen(['tasklist'], stdout=sp.PIPE).stdout.read().split('\r\n')
    if any(line.startswith(processname) for line in lines):
        return True
    return False
        
def kill(processname):
    '''Kills processname. If the subprocess launch fails, the function
    will try to kill it with os.system, which may cause output to stdout.'''
    try:
        p = sp.Popen(['taskkill', '/f', '/im', processname], stdout=sp.PIPE)
    except WindowsError:
        os.system('taskkill /f /im %s' % processname)
        
if __name__ == '__main__':
    #startup
    config = open('config.ini').read().split('\n')
    steampath = config[0].split('=')[1]
    credentials = {}
    for pair in config[1].split('=')[1].split(';'):
        pair = pair.split(':')
        try:
            credentials[pair[0]] = pair[1]
        except IndexError:
            print 'Malformed credentials list. The correct format is:'
            print 'accounts=username:password;username2:password2'
            sys.exit(0)
    os.chdir(steampath)
    
    print len(credentials), 'account(s) identified.'
    
    for username in credentials:
        password = credentials[username]
        steamargs = 'steam.exe -silent -login {0} {1}'.format(username, password).split(' ')
        tf2args   = 'steam.exe -applaunch 440 -console -textmode -novid -nosound -nopreload -nojoy -noshader +map_background ctf_2fort'.split(' ')

        print 'Logging in with account', username
        
        if isrunning('Steam.exe'):
            print 'Steam is running. Killing...'
            os.system('taskkill /f /im steam.exe')

        steamprocess = sp.Popen(steamargs)

        print 'Waiting for Steam to startup, press Ctrl+C to abort everything.'
        
        try:
            for i in range(1, 101):
                sys.stdout.write('%d%%\r  ' % i)
                time.sleep(0.1)
                
            if isrunning('Steam.exe'):
                pass
            else:
                print 'Steam has failed to startup. Check your account credentials and your internet connection.'
                print 'Leaving...'
                sys.exit(0)
        except KeyboardInterrupt:
            print 'Leaving...'
            sys.exit(0)
            
        try:
            print '\nWaiting for TF2 to launch. . .',
            tf2process = sp.Popen(tf2args)
            timewaiting = 0
            while isrunning('hl2.exe') == False:
                print '.',
                time.sleep(1)
                timewaiting += 1
                if timewaiting > 60:
                    print '- it seems that Steam took to long to startup or something went wrong. I will try to launch TF2 again -'
                    kill('hl2.exe')
                    tf2process = sp.Popen(tf2args)
            print 'done!'
        except KeyboardInterrupt:
            print 'Countdown aborted!'
            sys.exit()
        
        try:
            print 'Press Ctrl+C to finish idling. Hours until finished:'
            
            timeleft = 12*60*60 #12 hours

            while (timeleft > 0):
                sys.stdout.write( str(datetime.timedelta(0, timeleft))+'\r' )
                if timeleft%5==0:
                    if isrunning('hl2.exe'):
                        pass
                    else:
                        print 'Team Fortress has stopped running. Exiting...'
                        break
                timeleft -= 1
                time.sleep(1.0)
        except KeyboardInterrupt:
            print 'Idling aborted!'

        if isrunning('hl2.exe'):
            print 'Closing Team Fortress...',
            kill('hl2.exe')
            print 'Finished!'
        
        if isrunning('Steam.exe'):
            print 'Closing Steam...'
            try:
                steamprocess.kill()
            except WindowsError:
                kill('Steam.exe')
        print 'Finished idling for account %s!' % username

    print 'Finished idling for all accounts!'