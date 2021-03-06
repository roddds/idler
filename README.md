Team Fortress 2 Idler
=====================

This is a simple script that makes it easier to idle with several accounts.
Launch it through the command-line or via the `idler.py` file.

What this does:
---------------

`> idler`
---------

1. Shows you a list of every account you added to the config file and lets
you choose one (or several) for sequencial idling.  
1.1 You can also press the `+` key on your keyboard to add accounts to a
queue.
2. Kills Steam, if it is running.
3. Shows you a list of all your accounts, and an option to idle with all
accounts.
4. Starts Steam again, with the selected account.
5. Starts Team Fortress 2 in text mode. (You can change the parameters by
editing the code).
6. Waits for the amount of hours that were set up at config.ini. A countdown
will be shown, along with information about recent drops. Most of the screen
output is also saved to a log file, default "`idling.log`".
7. Kills Team Fortress 2.
8. Kills Steam.
9. Repeats the whole process with the next account.

Also, because of how the drop system in Team Fortress 2 works, the program is 
able to detect if the account is drop-capped for this week and then skips to
the next.


`> idler -login [accountname]`
------------------------------

Kills Steam if it's running, and starts it with the account specified at
[accountname].

`> idler -start`
----------------

Starts idling with the currently logged in account.

`> idler -continue`
-------------------

Starts an idling session based on an already running TF2 session. The
logged-in account is detected automatically.

`> idler -infinite`
-------------------

Idles with all of your accounts, in succession, until cancelled. Good if you
have a large number of accounts.

`> inv [account | -all] [-full]`
--------------------------------

Shows the contents of the first page of 'account's inventory, or use `-all`
to see the inventories of all accounts in your config file. You can also add
the `-full` argument to see the whole inventory instead of only the first
page. Special drops like hats will have an asterisk preceding them. This
command also accepts multiple account names, separated by space.

`> inv -all`
------------

Shows what's on the first page of all of your accounts' inventories.

`> inv -watch [account]`
------------------------

Watches for new drops at [account]'s inventory. You can also specify several
different accounts.
 
`> inv -count [account | -all]`
-------------------------------

Shows the amount of every item in `[account]`'s backpack.


-------------------
What this does not:
-------------------

1. Transfer items from one account to another.
2. Scrap banking.
3. Crafting weapons into scrap metal.


WARNING: The script is provided 'as is' without any guarantees
whatsoever as to the actual coolness from Valve about you running this.
anything you wouldn't be able to do with simple batch files, but if you
This does not interfere with any Team Fortress 2 files and doesn't do
want to stay on the safe side, don't run it.


Files:

    \idler.py          The actual script, plus some other functions. Launch
                       this file.
    \idle.py           The launcher script.
    \inv.py            Tools for snooping on people's inventories.
    \tf2.py            Swixel's interface for Valve's TF2 Web API.
    \config.ini        Write the path to Steam, your API key and your
                       username:passwords here.
    \menu.py           Renders the menu you see after running idler.py.
    \idling.log        Stores information about drops and other activity
                       on idler.
    \README            This file.
    \ignorelist.txt    Add to this file names of items you don't care about
                       (e.g Crates). Comes with a few examples you can
                       delete or add your own.
    \updater.py        Retrieves the latest version of this program from
                       github.com.
    \lastversion.txt   Contains information about the latest version of this
                       program.

------------------------------
Dependencies and Requirements:  
------------------------------

- A Steam Web API key. You can get one at:
http://steamcommunity.com/dev/apikey  

- WConio
http://newcenturycomputers.net/projects/wconio.html

- Python Win32 Extensions
http://sourceforge.net/projects/pywin32/

- The Requests Library
http://docs.python-requests.org/en/latest/index.html

- This software uses the `tf2webappy` library by Swixel (already included).
https://github.com/swixel/tf2webappy

---------------------------------
Example output from the log file:
---------------------------------

    2012-08-31 05:32:50:  Logging in with account roddds...
    2012-08-31 05:34:27:  done!
    2012-08-31 05:34:27:  Press Ctrl+C to finish idling. Hours until finished:
    2012-08-31 06:40:01: 6:54:27 - Found   Scottish Handshake
    2012-08-31 07:10:01: 6:24:27 - Found   Soda Popper
    2012-08-31 07:50:01: 5:44:27 - Found   Equalizer
    2012-08-31 08:50:01: 4:44:27 - Found * Dead Cone
    2012-08-31 09:40:01: 3:54:27 - Found   Southern Hospitality
    2012-08-31 11:20:01: 2:14:27 - Found   Red-Tape Recorder
    2012-08-31 12:20:01: 1:14:27 - Found   Ali Baba's Wee Booties
    2012-08-31 13:20:01: 0:14:27 - Found   Gunslinger
    2012-08-31 13:34:28:  Closing Team Fortress...
    2012-08-31 13:34:28:  Finished!
    2012-08-31 13:34:28:  Closing Steam...
    2012-08-31 13:34:28:  Finished idling for account roddds!
