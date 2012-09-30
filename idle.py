# -*- coding: utf-8 -*-
import idler
import inv
from menu import menu
from toaster import toaster
import os
import subprocess as sp
import sys
import time, datetime
now = datetime.datetime.now


if __name__ == '__main__':
    raise SystemExit("You're doing it wrong.")
    

class Log():
    def __init__(self, logfile, username):
        try:
            self.logfile = open(logfile, 'a')
        except IOError:
            self.logfile = open(logfile, 'w')
        except:
            raise SystemExit('Could not locate or open the log file. Check your preferences.')
        self.username = username

    def now(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S: ')

    def write(self, *message):
        '''
        Writes a message to Log without stdout.
        '''
        message = ' '.join(message)
        print message
        self.logfile.write('%s - %s %s\n' % (self.username, self.now(), message.strip()))
        self.logfile.flush()

    def stdout(self, *message):
        '''
        Writes a message to Log and echoes the message to stdout.
        '''
        message = ' '.join(message)
        sys.stdout.write(message)
        self.logfile.write('%s - %s%s\n' % (self.username, self.now(), message.strip()))
        self.logfile.flush()

    def close(self):
        self.logfile.close()


def isrunning(processname):
    '''
    Returns True or False depending on if processname is running or not.
    '''
    lines = sp.Popen(['tasklist'], stdout=sp.PIPE).stdout.read().lower().split('\r\n')
    return any(line.startswith(processname.lower()) for line in lines)


def kill(processname):
    '''
    Kills all instances of processname.
    '''
    os.system('taskkill /f /im %s >nul 2>&1' % processname) #>nul 2>&1 is to suppress stdout




class idle: #temporary name
    def __init__(self, username):
        self.username     = username
        self.config       = idler.Config()
        self.log          = Log(self.config['logfile'], self.username)


        steamid, password = self.config['accounts'][username].itervalues()
        steampath         = os.path.exists(self.config['steampath'])
        self.inventory    = inv.Backpack(self.config['accounts'][username]['steamcommunity'])
        self.tf2running   = False
        self.start        = now()


        self.idle()

    def startup(self):
        launchargs     =  [self.config['steampath'], '-silent', '-login']
        launchargs     += [self.username]
        launchargs     += [self.config['accounts'][self.username]['password']]
        launchargs     += ['-applaunch', '440', '-console', '-textmode', '-novid', '-nosound']
        launchargs     += ['-noipx', '-nopreload', '-nojoy', '-noshader', '+map_background', 'ctf_2fort']

        if isrunning('hl2.exe'):
            self.log.write('Team Fortress 2 is running. Killing...')
            kill('hl2.exe')
            time.sleep(5)

        if isrunning('steam.exe'):
            self.log.write('Steam is running. Killing...')
            kill('steam.exe')
            print 'Waiting for Steam to close...'
            time.sleep(5)

        self.steamprocess = sp.Popen(launchargs)

        try:
            for i in range(1, 101):
                sys.stdout.write('  %d%%\r' % i)
                time.sleep(0.1)                  # I don't like that this try:except repeats. TODO find some other way
        except KeyboardInterrupt:
            self.log.write('Countdown aborted!')

        try:
            while (isrunning('hl2.exe') and isrunning('steam.exe')) != True:
                sys.stdout.write('.',)
                time.sleep(5)

                if (now()-self.start).seconds > 60*5: # every 5 minutes # is also a hack but should do
                    sys.stdout.write("- it's taking more than it should, I'll try to restart the whole thing - ")
                    kill('hl2.exe')
                    kill('steam.exe')
                    steamprocess = sp.Popen(launchargs)
                    self.start = now()
        except KeyboardInterrupt:
            self.log.write('Countdown aborted!')

        self.log.write('done!')

        self.tf2running = True

        return True

    def idle(self):
        hours          = self.config['hours']
        apikey         = self.config['apikey']
        steamcommunity = self.config['accounts'][self.username]['steamcommunity']
        self.balloon   = toaster()
        timeleft       = self.start+datetime.timedelta(hours=hours)
        lastdrop       = now()  # set lastdrop time to startup time

        if not self.tf2running:
            self.startup()

        try: # check if there are any still unplaced items
            founditems = self.inventory(getunplaced=True)
            if len(founditems)>0:
                self.log.stdout('{0} - Last item found: {1}\n'.format(self.start.strftime('%H:%M:%S'), founditems[-1]))
        except ValueError: #503 unavailable
            self.log.stdout('- Backpack unavailable at startup. This may be temporary.\n')
            founditems = []

        self.log.write("Press Ctrl+C to finish idling. I'll be done at around %s" % timeleft.strftime('%H:%M:%S'))
        
        Continue = True

        while Continue: #while the current time is smaller than a fixed point in the future
            try:
                currenttime = str((timeleft-now())).split('.')[0]
                sys.stdout.write(currenttime+'  \r' )

                if not now().second %5: # checks if TF2 is running every 5 seconds
                    if not isrunning('hl2.exe'):
                        self.log.write('Team Fortress has stopped running. Exiting...')
                        break

                if not now().minute %10: #check every ten minutes (more or less)
                    try:
                        newunplaced = self.inventory(getunplaced=True)
                    except ValueError: #503 unavailable
                        newunplaced = []

                    for found in [item for item in newunplaced if item not in founditems]:
                        self.log.stdout('%s - Found %s\n' % (currenttime, item)) #change currenttime to reflect actual real time
                        self.balloon.show_balloon('Your account {} has found a {}'.format(self.username, found))
                        founditems.append(found) #test
                        lastdrop = lastdrop.now()

                    newunplaced = []

                    if (lastdrop.now()-lastdrop).seconds > 7200: #if time since last drop is 2 hours
                        self.log.write("It's been 2 hours since the last drop. I guess we're done here!")
                        break

                if not now() < timeleft:# and now() < lastdrop+datetime.timedelta(hours=2):
                    Continue = False

            except KeyboardInterrupt:
                print '\nTime of the last drop:    %s' % lastdrop.strftime('%H:%M:%S')
                print 'Drops found:              \n%s' % str(founditems)
                print 'Current time:               %s' % now().strftime('%H:%M:%S')
                print 'Time left until finished:   %s' % str((timeleft-now())).split('.')[0]
                print 'Will wait for more:         %s' % datetime.timedelta(seconds=7200 - (now()-lastdrop).seconds)

                print '\nWhat would you like to do?'
                options = ['Nothing',
                           'Finish idling with this account',
                           'Finish idling with all accounts']

                answer = menu(options, deletepreviouslines=7)[0]
                
                if options.index(answer) == 1:
                    timeleft = self.start+datetime.timedelta(seconds=1)
                    self.log.write('Idling with %s aborted!' % self.username)
                elif options.index(answer) == 2:
                    self.balloon.Destroy()
                    self.log.write('Idling aborted!')
                    kill('hl2.exe')
                    kill('steam.exe')
                    raise(SystemExit)
                else:
                    pass
        
        self.balloon.Destroy()

        if isrunning('hl2.exe'):
            self.log.write('Closing Team Fortress...',)
            kill('hl2.exe')
            self.log.write('Finished!')
        
        if isrunning('steam.exe'):
            self.log.write('Closing Steam...')
            kill('Steam.exe')

        self.log.write('Finished idling for account %s!' % self.username)