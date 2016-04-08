#
# Simple Win32 system tray app.
# by chopsueysensei <chopsueysensei@gmail.com>
# Based on http://www.brunningonline.net/simon/blog/archives/SysTrayIcon.py.html
#

import os
import sys
import win32api
import win32con
import win32gui_struct

try:
    import winxpgui as win32gui
except ImportError:
    import win32gui


class SysTrayApp(object):
    QUIT_ACTION = '_quit_action'

    def __init__(self, menu_entries, icon_path='', hover_text='',
            on_quit=None, default_menu_action_index=None, window_class_name=None):
        '''
        self.hover_text = hover_text
        self.on_quit = on_quit
        '''
        self._icon_path = icon_path
        self._hover_text = hover_text
        self._default_menu_action_index = default_menu_action_index
        window_class_name = window_class_name or 'SysTrayApp'

        self._special_actions = {
            SysTrayApp.QUIT_ACTION: self._quit_action
        }

        # Menu options
        menu_entries = menu_entries + (('Quit', None, SysTrayApp.QUIT_ACTION),)
        self._init_menu_entries(menu_entries)

        # Window messages
        message_map = {
            win32gui.RegisterWindowMessage('TaskbarCreated'): self._restart,
            win32con.WM_DESTROY: self._destroy,
            win32con.WM_COMMAND: self._command,
            win32con.WM_USER+20: self._notify,
        }

        # Register window class
        window_class = win32gui.WNDCLASS()
        window_class.hInstance = win32gui.GetModuleHandle(None)
        window_class.lpszClassName = window_class_name
        window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        window_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        window_class.hbrBackground = win32con.COLOR_WINDOW
        window_class.lpfnWndProc = message_map
        classAtom = win32gui.RegisterClass(window_class)

        # Create the window
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hWnd = win32gui.CreateWindow(classAtom,
                                          window_class_name,
                                          style,
                                          0,
                                          0,
                                          win32con.CW_USEDEFAULT,
                                          win32con.CW_USEDEFAULT,
                                          0,
                                          0,
                                          window_class.hInstance,
                                          None)

        win32gui.UpdateWindow(self.hWnd)
        self._refresh_icon(True)

        win32gui.PumpMessages()

    def _init_menu_entries(self, menu_entries, next_id=0):
        '''
        Receives a list of (text, icon, action) tuples, appends an id to each
        entry, and builds a dictionary of ids to entries. The 'action' in each
        tuple can itself be a list of entries (for submenus).
        '''
        pass

    def _refresh_icon(self, first_run=False):
        # Try to load app icon
        hInst = win32gui.GetModuleHandle(None)
        if os.path.isfile(self._icon_path):
            flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hIcon = win32gui.LoadImage(hInst,
                                       self._icon_path,
                                       win32con.IMAGE_ICON,
                                       0,
                                       0,
                                       flags)
        else:
            print('Cannot find app icon! Using default..')
            hIcon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        msg = win32gui.NIM_ADD if first_run else win32gui.NIM_MODIFY
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        notification = (self.hWnd,
                        0,
                        flags,
                        win32con.WM_USER + 20,
                        hIcon,
                        self._hover_text)

        win32gui.Shell_NotifyIcon(msg, notification)

    def _restart(self, hWnd, msg, wparam, lparam):
        self._refresh_icon()

    def _quit_action(self):
        if self._on_quit:
            self._on_quit()

        nid = (self.hWnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)

    def _destroy(self, hWnd, msg, wparam, lparam):
        self._quit_action()

    def _execute_menu_action(self, id):
        _, _, menu_action, _ = self._ids_to_menu_entries[id]

        if menu_action in self._special_actions:
            self._special_actions[menu_action]()
        else:
            menu_action()

    def _command(self, hWnd, msg, wparam, lparam):
        id = win32gui.LOWORD(wparam)
        self._execute_menu_action(id)

    def _notify(self, hWnd, msg, wparam, lparam):
        if lparam == win32con.WM_LBUTTONDBLCLK:
            if self._default_menu_action_index:
                self._execute_menu_action(self._default_menu_action_index)
        elif lparam == win32con.WM_RBUTTONUP:
            self._show_menu()

        return True

    def _show_menu(self):
        menu = win32gui.CreatePopupMenu()
        self._create_menu_entries(menu, self._menu_entries)

        if self._default_menu_action_index:
            win32gui.SetMenuDefaultItem(menu,
                                        self._default_menu_action_index,
                                        0)

        pos = win32gui.GetCursorPos()
        # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
        win32gui.SetForegroundWindow(self.hWnd)
        win32gui.TrackPopupMenu(menu,
                                win32con.TPM_LEFTALIGN,
                                pos[0],
                                pos[1],
                                0,
                                self.hWnd,
                                None)
        win32gui.PostMessage(self.hWnd, win32con.WM_NULL, 0 ,0)

    def _create_menu_entries(self, menu, menu_entries):
        pass








# Minimal selft test
if __name__ == '__main__':
    SysTrayApp(())
