# Based on win32gui_taskbar demo

import win32api as api
# Try and use XP features, so we get alpha-blending etc.
try:
    import winxpgui as gui
except ImportError:
    import win32gui as gui
import win32con
import sys, os
import struct

class PyNOTIFYICONDATA:
    _struct_format = (
        "I" # DWORD cbSize;
        "I" # HWND hWnd;
        "I" # UINT uID;
        "I" # UINT uFlags;
        "I" # UINT uCallbackMessage;
        "I" # HICON hIcon;
        "128s" #    TCHAR szTip[128];
        "I" # DWORD dwState;
        "I" # DWORD dwStateMask;
        "256s" # TCHAR szInfo[256];
        "I" #    union {
            #    UINT  uTimeout;
            #    UINT  uVersion;
            #} DUMMYUNIONNAME;
        "64s" #    TCHAR szInfoTitle[64];
        "I" #  DWORD dwInfoFlags;
        #      GUID guidItem;
    )
    _struct = struct.Struct(_struct_format)

    hWnd = 0
    uID = 0
    uFlags = 0
    uCallbackMessage = 0
    hIcon = 0
    szTip = ''
    dwState = 0
    dwStateMask = 0
    szInfo = ''
    uTimeoutOrVersion = 0
    szInfoTitle = ''
    dwInfoFlags = 0

    def pack(self):
        return self._struct.pack(
            self._struct.size,
            self.hWnd,
            self.uID,
            self.uFlags,
            self.uCallbackMessage,
            self.hIcon,
            self.szTip,
            self.dwState,
            self.dwStateMask,
            self.szInfo,
            self.uTimeoutOrVersion,
            self.szInfoTitle,
            self.dwInfoFlags)

    def __setattr__(self, name, value):
        # avoid wrong field names
        if not hasattr(self, name):
            raise NameError, name
        self.__dict__[name] = value

class toaster:
    def __init__(self):
        message_map = {
               win32con.WM_DESTROY: self.OnDestroy,
               win32con.WM_COMMAND: self.OnCommand,
               win32con.WM_USER+20: self.OnTaskbarNotify,
        }
        # Register the Window class.
        wc = gui.WNDCLASS()
        hinst = wc.hInstance = api.GetModuleHandle(None)
        wc.lpszClassName = "IdlerPopupHandler"
        wc.lpfnWndProc = message_map # could also specify a wndproc.
        classAtom = gui.RegisterClass(wc)
        self.classAtom = classAtom
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = gui.CreateWindow( classAtom, "Idling Notifications", style,  \
               0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,     \
               0, 0, hinst, None)
        gui.UpdateWindow(self.hwnd)
        iconPathName = os.path.abspath(os.path.join( sys.prefix, "pyc.ico" ))
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        try: hicon = gui.LoadImage(hinst, iconPathName, win32con.IMAGE_ICON, 0, 0, icon_flags)
        except: hicon = gui.LoadIcon(0, win32con.IDI_APPLICATION)
        flags = gui.NIF_ICON | gui.NIF_MESSAGE | gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, hicon, "Idling Notifications")
        gui.Shell_NotifyIcon(gui.NIM_ADD, nid)
        #print "Ready. Click on the Python icon."

    def OnTaskbarNotify(self, hwnd, msg, wparam, lparam):
        if lparam==win32con.WM_LBUTTONUP or lparam==win32con.WM_RBUTTONUP: #if left or right click
            #print "Click."
            menu = gui.CreatePopupMenu()
            #gui.AppendMenu( menu, win32con.MF_STRING, 1024, "Generate balloon") # this is where you define the actions
            gui.AppendMenu( menu, win32con.MF_STRING, 1024, "Exit")             # for the right-click menu
            pos = gui.GetCursorPos()
            gui.SetForegroundWindow(self.hwnd)
            gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None)
            gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
            return 1

    def show_balloon(self, message):
        #timer.kill_timer(3) # one-shot timer!

        # For this message I can't use the win32gui structure because
        # it doesn't declare the new, required fields
        nid = PyNOTIFYICONDATA()
        nid.hWnd = self.hwnd
        nid.uFlags = gui.NIF_INFO
        # type of balloon and text are random  # not anymore
        # from random import choice
        # nid.dwInfoFlags = choice([NIIF_INFO, NIIF_WARNING, NIIF_ERROR])
        nid.dwInfoFlags = gui.NIIF_INFO
        # nid.szInfo = choice(["Balloon text.", "This text is nicer.", "Perl rulez! :)"])
        nid.szInfo = message
        nid.szInfoTitle = "New drop!"
        # Call the Windows function, not the wrapped one
        from ctypes import windll
        Shell_NotifyIcon = windll.shell32.Shell_NotifyIconA
        Shell_NotifyIcon(gui.NIM_MODIFY, nid.pack())

    def OnCommand(self, hwnd, msg, wparam, lparam):
        id = gui.LOWORD(wparam)
        if id == 1024:
            gui.DestroyWindow(self.hwnd)
        # if id == 1024:
            # self.enqueue_balloon()
        # elif id == 1025:
            # print "Goodbye"
            # gui.DestroyWindow(self.hwnd)
        # else:
            # print "OnCommand for ID", id

    def Destroy(self):
        gui.DestroyWindow(self.hwnd)
        gui.UnregisterClass(self.classAtom, None)

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        gui.Shell_NotifyIcon(gui.NIM_DELETE, nid)
        gui.PostQuitMessage(0) # Terminate the app.

def main():
    w = toaster()
    w.show_balloon('hello world!')
    #gui.PumpMessages()

if __name__=='__main__':
    main()