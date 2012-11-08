import requests
import zipfile
import os

def update():
    reponifo = 'https://api.github.com/repos/roddds/idler'
    download = 'https://github.com/roddds/idler/archive/master.zip'
    
    try:
        currentversion = open('lastversion.txt', 'r').read()    
    except IOError:
        currentversion = ''

    try:
        version = requests.get(reponifo).json['pushed_at']
    except requests.exceptions.ConnectionError:
        print "Updater couldn't connect to the update server (github.com)"
        return False

    if version != currentversion: #u'2012-09-10T13:49:24Z' as of now
        print 'Update found!'

        print 'Downloading new version'
        r = requests.get(download)


        with open('idler.zip', 'wb') as f:
            f.write(r.content)
        #zf = zipfile.ZipFile('idler.zip')

        with zipfile.ZipFile('idler.zip') as zf:
            for f in zf.filelist:
                f.filename = f.filename.split('/')[-1]
                if f.filename and f.filename != 'config.ini':
                    zf.extract(f, path='.')
                    print 'Updated %s' % f.filename
            print 'Finished!'
        
        with open('lastversion.txt', 'w') as lv:
            lv.write(version)
        os.remove('idler.zip') # cleanup
        try:
            os.remove('schema.en.json') # force schema update
        except WindowsError:
            pass
        return True

    else:
        print 'Idler is up to date with the current version.'
        return False

if __name__ == '__main__':
    update()