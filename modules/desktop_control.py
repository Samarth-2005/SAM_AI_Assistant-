"""Explicit Notepad typing and foreground activation for Windows."""
import os
import re
import time
import subprocess
from pathlib import Path


def bring_forward(hwnd):
    import ctypes
    import win32gui
    import win32process
    import win32con
    user32 = ctypes.windll.user32
    if not win32gui.IsWindow(hwnd): return False
    current = user32.GetCurrentThreadId() if hasattr(user32, 'GetCurrentThreadId') else ctypes.windll.kernel32.GetCurrentThreadId()
    foreground = win32gui.GetForegroundWindow()
    target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]
    foreground_thread = win32process.GetWindowThreadProcessId(foreground)[0] if foreground else 0
    attached = []
    try:
        for thread in set([target_thread, foreground_thread]):
            if thread and thread != current and user32.AttachThreadInput(current, thread, True): attached.append(thread)
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.BringWindowToTop(hwnd)
        try: win32gui.SetForegroundWindow(hwnd)
        except Exception: pass
    finally:
        for thread in attached: user32.AttachThreadInput(current, thread, False)
    time.sleep(0.2)
    return win32gui.GetForegroundWindow() == hwnd


def _notepad_windows():
    import psutil
    import win32gui
    import win32process
    found = []
    def collect(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd): return
        try:
            pid = win32process.GetWindowThreadProcessId(hwnd)[1]
            if psutil.Process(pid).name().lower() == 'notepad.exe': found.append(hwnd)
        except (OSError, psutil.Error): pass
    win32gui.EnumWindows(collect, None)
    return found


def _type_unicode(hwnd, text):
    """Send Unicode keyboard input only while the verified Notepad window has focus."""
    import ctypes
    from ctypes import wintypes
    import win32gui
    ULONG_PTR = ctypes.c_size_t
    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [('wVk', wintypes.WORD), ('wScan', wintypes.WORD), ('dwFlags', wintypes.DWORD), ('time', wintypes.DWORD), ('dwExtraInfo', ULONG_PTR)]
    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [('dx', wintypes.LONG), ('dy', wintypes.LONG), ('mouseData', wintypes.DWORD), ('dwFlags', wintypes.DWORD), ('time', wintypes.DWORD), ('dwExtraInfo', ULONG_PTR)]
    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [('uMsg', wintypes.DWORD), ('wParamL', wintypes.WORD), ('wParamH', wintypes.WORD)]
    class INPUTUNION(ctypes.Union):
        _fields_ = [('ki', KEYBDINPUT), ('mi', MOUSEINPUT), ('hi', HARDWAREINPUT)]
    class INPUT(ctypes.Structure):
        _anonymous_ = ('u',)
        _fields_ = [('type', wintypes.DWORD), ('u', INPUTUNION)]
    send = ctypes.windll.user32.SendInput
    send.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
    send.restype = wintypes.UINT
    encoded = text.encode('utf-16-le')
    for i in range(0, len(encoded), 2):
        if win32gui.GetForegroundWindow() != hwnd:
            raise RuntimeError('Typing stopped because another window took focus. Some text may already be typed.')
        unit = int.from_bytes(encoded[i:i+2], 'little')
        events = (INPUT * 2)()
        for event, flags in zip(events, (0x0004, 0x0004 | 0x0002)):
            event.type = 1; event.ki = KEYBDINPUT(0, unit, flags, 0, 0)
        if send(2, events, ctypes.sizeof(INPUT)) != 2:
            raise RuntimeError('Windows blocked keyboard input. Run Notepad normally, without administrator mode.')


def parse_notepad_command(command):
    match = re.fullmatch(r'\s*(?:please\s+)?(?:open|start|launch)\s+(?:notepad|notpad|note\s*pad)(?:\s+and\s+type\s+(.+))?\s*', command, re.IGNORECASE)
    if match: return 'open', match.group(1)
    match = re.fullmatch(r'\s*type\s+(.+)', command, re.IGNORECASE)
    if match: return 'type', match.group(1)
    return None


def handle_notepad(command):
    parsed = parse_notepad_command(command)
    if parsed is None: return None
    mode, text = parsed
    if text and len(text) > 2000: return 'Please type at most 2000 characters at a time.'
    import win32gui
    if mode == 'open':
        before = _notepad_windows()
        subprocess.Popen(['notepad.exe'])
        deadline = time.monotonic() + 8
        hwnd = None
        while time.monotonic() < deadline:
            windows = _notepad_windows()
            new = [w for w in windows if w not in before]
            foreground = win32gui.GetForegroundWindow()
            if new: hwnd = new[0]; break
            if foreground in windows: hwnd = foreground; break
            time.sleep(0.2)
        if hwnd is None:
            windows = _notepad_windows()
            if len(windows) == 1: hwnd = windows[0]
        if hwnd is None: return 'Notepad was launched, but I could not identify its window. Click it and try typing again.'
        if not bring_forward(hwnd): return 'Notepad opened, but Windows did not bring it forward. Click Notepad, then say type followed by your text.'
    else:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd not in _notepad_windows():
            return 'Click inside Notepad first, or say open Notepad and type followed by your text.'
    if text:
        time.sleep(0.4)
        _type_unicode(hwnd, text)
        return 'Typed your text in Notepad.'
    return 'Opened Notepad.'


def open_folder_visible(path):
    """Open an existing folder and find that exact Explorer location before focusing."""
    import win32com.client
    from urllib.parse import urlsplit, unquote
    os.startfile(str(path))
    wanted = os.path.normcase(os.path.realpath(path))
    shell = win32com.client.Dispatch('Shell.Application')
    deadline = time.monotonic() + 6
    while time.monotonic() < deadline:
        for window in shell.Windows():
            try:
                url = urlsplit(str(window.LocationURL))
                if url.scheme != 'file': continue
                candidate = unquote(url.path).replace('/', '\\')
                if url.netloc: candidate = '\\\\' + url.netloc + candidate
                elif re.match(r'^\\[a-zA-Z]:', candidate): candidate = candidate[1:]
                if os.path.normcase(os.path.realpath(candidate)) == wanted:
                    if bring_forward(int(window.HWND)): return True
            except Exception: continue
        time.sleep(0.2)
    return False
