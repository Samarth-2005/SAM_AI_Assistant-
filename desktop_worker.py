"""Isolated hardware worker. Only authenticated commands reach execute()."""
import sys, json, queue, threading, re, os, time, builtins, socket, traceback, faulthandler
from pathlib import Path
os.chdir(Path(__file__).resolve().parent)
wire = sys.stdout
_event_socket = None
if os.environ.get('SAM_AI_EVENT_PORT'):
    _event_socket = socket.create_connection(('127.0.0.1', int(os.environ['SAM_AI_EVENT_PORT'])), timeout=10)
    _event_socket.settimeout(None)
    wire = _event_socket.makefile('w', encoding='utf-8')
    wire.write(json.dumps({'token': os.environ['SAM_AI_EVENT_TOKEN']}) + '\n'); wire.flush()
sys.stdout = sys.stderr
inbox = queue.Queue()
mic_enabled = threading.Event()

def emit(kind, **data):
    wire.write(json.dumps(dict(type=kind, **data)) + '\n'); wire.flush()

def reader():
    for line in sys.stdin:
        try:
            item = json.loads(line)
            if item.get('type') == 'mic':
                (mic_enabled.set if item.get('enabled') else mic_enabled.clear)()
            else:
                inbox.put(item)
        except ValueError:
            pass

def confirm(prompt):
    emit('confirm', text=prompt)
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            item = inbox.get(timeout=0.2)
            if item.get('type') == 'confirm':
                return bool(item.get('yes'))
        except queue.Empty:
            pass
    return False

class VoiceSession:
    """Wake once per authenticated worker; no speech is routed before waking."""
    def __init__(self):
        self.active = False

    def accept(self, text):
        text = text.strip()
        match = re.match(r'^\s*(?:hey\s+)?sam\b[\s,.!:-]*(.*)$', text, re.IGNORECASE)
        if not self.active and not match:
            return None, False
        activated = not self.active
        self.active = True
        command = match.group(1).strip() if match else text
        return command or None, activated

def main():
    emit('status', text='Loading face recognition…')
    from desktop_face import verify
    faulthandler.dump_traceback_later(60, repeat=True)
    try:
        verified = verify(emit)
    finally:
        faulthandler.cancel_dump_traceback_later()
    if not verified:
        emit('error', text='Face not verified. Check lighting, then choose Verify face again.'); return
    emit('status', text='Loading assistant…')
    import pythoncom
    pythoncom.CoInitialize()
    import modules.voice as voice
    original_speak = voice.speak
    def speak(text):
        emit('reply', text=str(text)); original_speak(text)
    voice.speak = speak
    from modules import actions
    # Existing deletion prompt now uses a desktop confirmation instead of stdin.
    builtins.input = lambda prompt='': 'yes' if confirm(prompt) else 'no'
    import speech_recognition as sr
    recognizer = sr.Recognizer(); recognizer.operation_timeout = 8
    emit('ready')
    session = VoiceSession()
    speak('Welcome SAM. Say Hey Sam once to start. Then speak your commands directly.')
    emit('status', text='Say Hey SAM once to start voice commands')
    source = None
    try:
        microphone = sr.Microphone(); source = microphone.__enter__()
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        mic_enabled.set(); emit('mic', enabled=True)
    except Exception as exc:
        emit('reply', text=f'Microphone unavailable: {exc}. You can type commands.')
    # Load native camera, numerical and audio libraries before blocking on piped stdin.
    threading.Thread(target=reader, daemon=True).start()
    try:
        while True:
            command = None
            try:
                item = inbox.get(timeout=0.1)
                if item.get('type') == 'command': command = item.get('text', '').strip()
            except queue.Empty:
                pass
            if command is None and source is not None and mic_enabled.is_set():
                try:
                    audio = recognizer.listen(source, timeout=0.6, phrase_time_limit=7)
                    if not mic_enabled.is_set(): continue
                    text = recognizer.recognize_google(audio, language='en-IN')
                    if not mic_enabled.is_set(): continue
                    command, activated = session.accept(text)
                    if activated:
                        emit('status', text='Voice session active • speak commands directly')
                        if not command:
                            speak('I am listening. You can speak your commands directly now.')
                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    pass
                except sr.RequestError:
                    mic_enabled.clear(); emit('mic', enabled=False)
                    emit('reply', text='Speech service unavailable. Check internet; use typing or enable the microphone again.')
                except Exception as exc:
                    mic_enabled.clear(); emit('mic', enabled=False)
                    emit('reply', text=f'Microphone error: {exc}')
            if not command: continue
            emit('heard', text=command)
            if command.lower() in ('exit', 'quit', 'stop', 'lock assistant'):
                emit('lock'); return
            emit('status', text='Working…')
            try:
                # Confirm commands that can overwrite files, close apps or affect the session.
                if re.search(r'\b(write|close|shutdown|restart|reboot|sleep|log out|sign out|lock computer)\b', command.lower()):
                    if not confirm('Run this command?\n\n' + command):
                        speak('Cancelled.'); continue
                actions.execute(command)
            except SystemExit:
                emit('lock'); return
            except Exception as exc:
                emit('reply', text=f'Task failed: {exc}')
            finally:
                emit('status', text='Speak your next command directly' if session.active else 'Say Hey SAM once to start voice commands')
    finally:
        if source is not None: microphone.__exit__(None, None, None)
        pythoncom.CoUninitialize()

if __name__ == '__main__':
    try: main()
    except Exception as exc:
        traceback.print_exc()
        emit('error', text=f'{type(exc).__name__}: {exc}')
