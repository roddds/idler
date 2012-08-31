import WConio

# This whole thing is a hack. I should probably OOp it out and stuff.

def _sel():
    WConio.textbackground(WConio.LIGHTGREY)
    WConio.textcolor(WConio.BLACK)

def _otr():
    WConio.textbackground(WConio.BLACK)
    WConio.textcolor(WConio.LIGHTGREY)

def draw(options, d): #Spaghetti code. I'm not proud of it.
    '''
    Draws the menu with a list of options
    and highlights option [d].
    '''
    for i in options[0:d]:
        _otr()
        print(i)
    _sel()
    print(options[d])
    for i in options[d+1:]:
        _otr()
        print(i)

def menu(options):
    _sel()
    _otr() # Initialize terminal conditions

    home = WConio.wherey() # Gets original y coordinate
    y = 0
    draw(options, y)
    multiple = []
    escolha = ''
    while escolha != '\r':  #\r = enter
        escolha = WConio.getkey()

        if escolha == 'up':
                if y != 0:
                    y-=1

        if escolha == 'down':
                if y != len(options)-1:
                    y+=1

        if escolha == '+':
            multiple.append(options[y])
            if options[y][-1] != '+':
                options[y] += '+'

        # To do: add option to remove from list

        WConio.gotoxy(0, home)
        draw(options,y)

    _otr()
    if len(multiple)>0:
        return multiple
    else:
        return [options[y]]


if __name__ == '__main__':
    raise SystemExit("You're doing it wrong.")
