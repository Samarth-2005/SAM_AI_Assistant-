from pathlib import Path
import os,sys

def configure(enabled):
    if os.name != 'nt': raise RuntimeError('Startup setup is for Windows only.')
    import win32com.client
    folder=Path(os.environ['APPDATA'])/'Microsoft/Windows/Start Menu/Programs/Startup'
    shortcut=folder/'SAM_AI_Desktop.lnk'
    if not enabled:
        shortcut.unlink(missing_ok=True);return
    folder.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parent
    pythonw=Path(sys.executable).with_name('pythonw.exe')
    shell=win32com.client.Dispatch('WScript.Shell')
    link=shell.CreateShortcut(str(shortcut))
    link.TargetPath=str(pythonw if pythonw.exists() else Path(sys.executable))
    link.Arguments='"'+str(root/'main.py')+'"'
    link.WorkingDirectory=str(root);link.Description='SAM AI desktop assistant';link.Save()
