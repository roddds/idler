import time, datetime
import os
import sys
import subprocess as sp
import inv


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


def continueidling(config):
    print 'Detecting who is idling right now...'

    try:
        import win32gui
    except ImportError:
        print 'To use the "continue" function you need the Python for Windows'
        print 'Extensions. You can download it at'
        print 'http://sourceforge.net/projects/pywin32/'
        sys.exit(0)
    import re

    if not isrunning('hl2.exe'):
        print 'Team Fortress 2 is not running.'
        raise SystemExit()

    def windowEnumerationHandler(hwnd, resultList):
        '''Pass to win32gui.EnumWindows() to generate list of window handle, window text tuples.'''
        resultList.append(win32gui.GetWindowText(hwnd))

    def playingaccount():
        processes = []
        win32gui.EnumWindows(windowEnumerationHandler, processes)
        hl2 = [x for x in processes if 'hl2.exe' in x][0]
        username = re.findall('s\\\\[a-z_]*\\\\t', hl2)[0].split('\\')[1]
        return username

    username       =  playingaccount()
    print 'Account %s is idling.' % username
    idle(username, config)


def startup(username, config):
    password       =  config['accounts'][username]['password']
    log            =  Log(config['logfile'], username)

    launchargs     =  [config['steampath'], '-silent', '-login']
    launchargs     += [username]
    launchargs     += [password]
    launchargs     += ['-applaunch', '440', '-console', '-textmode', '-novid', '-nosound']
    launchargs     += ['-noipx', '-nopreload', '-nojoy', '-noshader', '+map_background', 'ctf_2fort']


    log.write('\nLogging in with account %s...' % username)

    if isrunning('hl2.exe'):
        log.write('Team Fortress 2 is running. Killing...')
        kill('hl2.exe')
        time.sleep(5)

    if isrunning('steam.exe'):
        log.write('Steam is running. Killing...')
        kill('steam.exe')
        print 'Waiting for Steam to close...',
        time.sleep(5)


    steamprocess = sp.Popen(launchargs)

    sys.stdout.write('Waiting for Steam to startup, press Ctrl+C to skip this account.\n')
    start    = datetime.datetime.now()

    try:
        for i in range(1, 101):
            sys.stdout.write('  %d%%\r' % i)
            time.sleep(0.1)                  # I don't like that this try:except repeats. TODO find some other way
    except KeyboardInterrupt:
        log.write('Countdown aborted!')

    try:
        while (isrunning('hl2.exe') and isrunning('steam.exe')) != True:
            sys.stdout.write('.',)
            time.sleep(5)

            if (start.now()-start).seconds > 60*5: # every 5 minutes # is also a hack but should do
                sys.stdout.write("- it's taking more than it should, I'll try to restart the whole thing - ")
                kill('hl2.exe')
                kill('steam.exe')
                steamprocess = sp.Popen(launchargs)
                start = start.now()

    except KeyboardInterrupt:
        log.write('Countdown aborted!')
        
    log.write('done!')

    idle(username, config) #maybe change this to a return value?


def idle(username, config):
    from menu import menu
    hours          = config['hours']
    apikey         = config['apikey']
    log            = Log(config['logfile'], username)
    steamcommunity = config['accounts'][username]['steamcommunity']

    start          = datetime.datetime.now()
    timeleft       = start+datetime.timedelta(hours=hours)
    lastdrop       = datetime.datetime.now()  # set lastdrop time to startup time
    

    try: # check if there are any still unplaced items
        founditems = inv.viewinv(steamcommunity, apikey, getunplaced=True)
        if len(founditems)>0:
            log.stdout('{0} - Last item found: {1}\n'.format(start.strftime('%H:%M:%S'), founditems[-1]))
    except ValueError: #503 unavailable
        log.stdout('- Backpack unavailable at startup. This may be temporary.\n')
        founditems = []

    log.write("Press Ctrl+C to finish idling. I'll be done at around %s" % timeleft.strftime('%H:%M:%S'))
    
    while start.now() < timeleft and start.now() < lastdrop+datetime.timedelta(hours=2): #while the current time is smaller than a fixed point in the future
        try:
            currenttime = str((timeleft-start.now())).split('.')[0]
            sys.stdout.write(currenttime+'  \r' )

            if not datetime.datetime.now().second %5: # checks if TF2 is running every 5 seconds
                if not isrunning('hl2.exe'):
                    log.write('Team Fortress has stopped running. Exiting...')
                    break

            if not datetime.datetime.now().minute %10: #check every ten minutes (more or less)
                try:
                    newunplaced = inv.viewinv(steamcommunity, apikey, getunplaced=True)
                except ValueError: #503 unavailable
                    newunplaced = []

                for item in [item for item in newunplaced if item not in founditems]:
                    log.stdout('%s - Found %s\n' % (currenttime, item)) #change currenttime to reflect actual real time
                    balloon.show_balloon('Your account %s has found a %s' % (username, item))
                    founditems.append(item) #test
                    lastdrop = lastdrop.now()

                newunplaced = []

                if (lastdrop.now()-lastdrop).seconds > 7200: #if time since last drop is 2 hours
                    log.write("It's been 2 hours since the last drop. I guess we're done here!")
                    break

        except KeyboardInterrupt:
            print '\nTime of the last drop:    %s' % lastdrop.strftime('%H:%M:%S')
            print 'Drops found:              \n%s' % str(founditems)
            print 'Current time:               %s' % datetime.datetime.now().strftime('%H:%M:%S')
            print 'Time left until finished:   %s' % str((timeleft-start.now())).split('.')[0]
            print 'Will wait for more:         %s' % datetime.timedelta(seconds=7200 - (datetime.datetime.now()-lastdrop).seconds)

            print '\nWhat would you like to do?'
            options = ['Finish idling with this account',
                       'Finish idling with all accounts',
                       'Nothing']

            answer = menu(options, deletepreviouslines=7)[0]
            
            if options.index(answer) == 0:
                timeleft = start+datetime.timedelta(seconds=1)
                log.write('Idling with %s aborted!' % username)
            elif options.index(answer) == 1:
                log.write('Idling aborted!')
                kill('hl2.exe')
                kill('steam.exe')
                raise(SystemExit)
            else:
                pass

    if isrunning('hl2.exe'):
        log.write('Closing Team Fortress...',)
        kill('hl2.exe')
        log.write('Finished!')
    
    if isrunning('steam.exe'):
        log.write('Closing Steam...')
        kill('Steam.exe')

    log.write('Finished idling for account %s!' % username)
