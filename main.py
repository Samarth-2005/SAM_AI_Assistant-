"""SAM AI desktop interface. Run using your existing Windows Python environment."""
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import math, queue, threading, subprocess, sys, json, base64, io, os, socket, secrets, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BG, PANEL, INK, MUTED, ACCENT = '#070e1b', '#101d30', '#edf5ff', '#8cabc8', '#59e1e8'

class Assistant:
    def __init__(self, root, preview=False):
        self.root=root; self.process=None; self.events=queue.Queue(); self.generation=0
        self.ready=False; self.mic=False; self.phase=0; self.preview=preview
        root.title('SAM AI · Personal desktop assistant'); root.geometry('1040x720'); root.minsize(900,650); root.configure(bg=BG)
        top=tk.Frame(root,bg=BG);top.pack(fill='x',padx=32,pady=(24,12))
        tk.Label(top,text='SAM  /  AI',font=('Segoe UI',24,'bold'),bg=BG,fg=INK).pack(side='left')
        self.button(top,'Startup settings',self.startup).pack(side='right',padx=(16,0))
        tk.Label(top,text='PERSONAL DESKTOP ASSISTANT',font=('Segoe UI',10),bg=BG,fg=MUTED).pack(side='right')
        body=tk.Frame(root,bg=BG);body.pack(fill='both',expand=True,padx=32)
        left=tk.Frame(body,bg=PANEL,width=420);left.pack(side='left',fill='both',padx=(0,20));left.pack_propagate(False)
        tk.Label(left,text='IDENTITY & VOICE',font=('Segoe UI',10,'bold'),bg=PANEL,fg=MUTED).pack(pady=(22,0))
        self.canvas=tk.Canvas(left,width=400,height=300,bg=PANEL,highlightthickness=0);self.canvas.pack(padx=10,pady=12)
        self.title=tk.Label(left,text='Your assistant. Ready when you are.',font=('Segoe UI',16,'bold'),bg=PANEL,fg=INK,wraplength=370);self.title.pack(padx=20,pady=8)
        self.status=tk.Label(left,text='Face verification required',font=('Segoe UI',11),bg=PANEL,fg=MUTED,wraplength=370);self.status.pack(padx=20,pady=8)
        self.verify_button=self.button(left,'Verify face',self.start);self.verify_button.pack(fill='x',padx=28,pady=12)
        self.mic_button=self.button(left,'Microphone off',self.toggle_mic);self.mic_button.pack(fill='x',padx=28,pady=4)
        self.button(left,'Stop & lock assistant',self.lock).pack(fill='x',padx=28,pady=8)
        right=tk.Frame(body,bg=BG);right.pack(side='left',fill='both',expand=True)
        tk.Label(right,text='Let’s get things done.',font=('Segoe UI',24,'bold'),bg=BG,fg=INK).pack(anchor='w',pady=(12,6))
        tk.Label(right,text='Say “Hey SAM” once, then speak commands directly.',font=('Segoe UI',11),bg=BG,fg=MUTED).pack(anchor='w',pady=(0,20))
        self.history=ScrolledText(right,bg=PANEL,fg=INK,font=('Segoe UI',11),wrap='word',height=8,relief='flat',padx=18,pady=18,state='disabled');self.history.pack(fill='both',expand=True)
        self.log('SAM AI','Verify your face to unlock voice and typed commands.\n\nSay “Hey SAM” once. Then try “open notepad” or “how is my system?”')
        self.entry=tk.Entry(right,bg=PANEL,fg=INK,insertbackground=ACCENT,font=('Segoe UI',12),relief='flat');self.entry.pack(fill='x',ipady=13,pady=(14,8));self.entry.bind('<Return>',lambda e:self.send_command())
        self.send_button=self.button(right,'Send command  →',self.send_command);self.send_button.pack(fill='x')
        footer=tk.Frame(root,bg=BG);footer.pack(fill='x',padx=32,pady=18)
        tk.Label(footer,text='Face check stays local • Voice transcription uses Google online',bg=BG,fg=MUTED,font=('Segoe UI',9)).pack(side='left')
        self.set_ready(False);root.protocol('WM_DELETE_WINDOW',self.close)
        self.tick();self.poll()
        if not preview: root.after(600,self.start)

    def button(self,parent,text,command):
        return tk.Button(parent,text=text,command=command,bg='#19334a',fg=INK,activebackground='#25516a',activeforeground=INK,relief='flat',font=('Segoe UI',10,'bold'),padx=16,pady=9,cursor='hand2')
    def log(self,who,text):
        self.history.configure(state='normal');self.history.insert('end',f'{who}\n{text}\n\n');self.history.see('end');self.history.configure(state='disabled')
    def set_ready(self,value):
        self.ready=value
        for widget in (self.entry,self.send_button,self.mic_button): widget.configure(state='normal' if value else 'disabled')
    def send(self,item):
        if self.process and self.process.poll() is None:
            try: self.process.stdin.write(json.dumps(item)+'\n');self.process.stdin.flush()
            except (OSError,ValueError): self.lock()
    def start(self):
        if self.preview: return
        self.lock();self.status.configure(text='Starting…');self.verify_button.configure(state='disabled')
        env=os.environ.copy();env['PYTHONIOENCODING']='utf-8'
        try:
            worker_python = Path(sys.executable)
            if worker_python.name.lower() == 'pythonw.exe': worker_python = worker_python.with_name('python.exe')
            listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listener.bind(('127.0.0.1', 0)); listener.listen(2); listener.settimeout(0.5)
            token = secrets.token_hex(32)
            env['SAM_AI_EVENT_PORT'] = str(listener.getsockname()[1])
            env['SAM_AI_EVENT_TOKEN'] = token
            # Keep native-library output away from the interface event channel.
            with (ROOT/'sam_ai_debug.log').open('w', encoding='utf-8') as debug:
                self.process=subprocess.Popen([str(worker_python),'-u','-X','faulthandler',str(ROOT/'desktop_worker.py')],cwd=ROOT,stdin=subprocess.PIPE,stdout=debug,stderr=debug,text=True,encoding='utf-8',env=env)
            proc=self.process;generation=self.generation
            def read():
                connected = False
                deadline = time.monotonic() + 30
                try:
                    while proc.poll() is None and time.monotonic() < deadline:
                        try: connection,_ = listener.accept()
                        except socket.timeout: continue
                        with connection:
                            connection.settimeout(5)
                            stream = connection.makefile('r',encoding='utf-8')
                            with stream:
                                hello = json.loads(stream.readline())
                                if hello.get('token') != token: continue
                                connected = True
                                connection.settimeout(None)
                                for line in stream:
                                    self.events.put((generation,json.loads(line)))
                        break
                    if not connected:
                        self.events.put((generation,{'type':'error','text':'Worker did not connect. Open sam_ai_debug.log in this project folder.'}))
                    elif proc.poll() is None:
                        proc.wait(timeout=3)
                except Exception as exc:
                    self.events.put((generation,{'type':'error','text':f'Worker connection: {exc}. See sam_ai_debug.log.'}))
                finally:
                    listener.close()
                    self.events.put((generation,{'type':'ended','code':proc.poll()}))
            threading.Thread(target=read,daemon=True).start()
        except Exception as exc:
            if 'listener' in locals(): listener.close()
            self.log('STARTUP ERROR',str(exc));self.status.configure(text=str(exc));self.verify_button.configure(state='normal')
    def lock(self):
        self.generation+=1
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:self.process.kill()
        self.process=None;self.set_ready(False);self.mic=False;self.photo=None
        self.canvas.delete('camera');self.verify_button.configure(state='normal');self.mic_button.configure(text='Microphone off')
        self.title.configure(text='Your assistant. Ready when you are.');self.status.configure(text='Face verification required')
    def close(self):self.lock();self.root.destroy()
    def toggle_mic(self):
        self.mic=not self.mic;self.send({'type':'mic','enabled':self.mic});self.mic_button.configure(text='Microphone on' if self.mic else 'Microphone off')
    def send_command(self):
        if not self.ready:return
        text=self.entry.get().strip()
        if text:self.send({'type':'command','text':text});self.entry.delete(0,'end')
    def poll(self):
        for _ in range(30):
            try:g,e=self.events.get_nowait()
            except queue.Empty:break
            if g!=self.generation:continue
            kind=e.get('type')
            if kind=='status':
                self.status.configure(text=e['text']);self.log('STATUS',e['text'])
            elif kind=='ready':
                self.set_ready(True);self.canvas.delete('camera');self.title.configure(text='Welcome back, SAM.');self.status.configure(text='Ready for your next command')
            elif kind=='mic':self.mic=e['enabled'];self.mic_button.configure(text='Microphone on' if self.mic else 'Microphone off')
            elif kind in ('reply','heard'):self.log('SAM AI' if kind=='reply' else 'YOU',e['text'])
            elif kind=='frame':
                try:
                    from PIL import Image,ImageTk
                    self.photo=ImageTk.PhotoImage(Image.open(io.BytesIO(base64.b64decode(e['data']))))
                    self.canvas.delete('camera');self.canvas.create_image(200,150,image=self.photo,tags='camera')
                except Exception:pass
            elif kind=='confirm':self.send({'type':'confirm','yes':messagebox.askyesno('Confirm action',e['text'],parent=self.root)})
            elif kind=='error':
                self.log('SETUP / ERROR',e['text']);self.status.configure(text=e['text']);self.set_ready(False);self.verify_button.configure(state='normal')
            elif kind=='lock':self.lock()
            elif kind=='ended':
                self.log('WORKER',f"Worker stopped (exit code {e.get('code')}). Details: sam_ai_debug.log");self.status.configure(text='Worker stopped. Check the conversation and sam_ai_debug.log.');self.set_ready(False);self.verify_button.configure(state='normal');self.mic_button.configure(text='Microphone off');self.canvas.delete('camera')
        self.root.after(80,self.poll)
    def tick(self):
        self.phase+=0.04;self.canvas.delete('orb')
        for radius,color,width in [(113,'#173b50',2),(98,'#235a70',2),(80,ACCENT,2),(62,'#213c62',1)]:
            r=radius+math.sin(self.phase*2)*3
            self.canvas.create_oval(200-r,150-r,200+r,150+r,outline=color,width=width,tags='orb')
        for i in range(32):
            a=i*math.tau/32+self.phase;r=91
            x,y=200+math.cos(a)*r,150+math.sin(a)*r
            self.canvas.create_oval(x-2,y-2,x+2,y+2,fill=ACCENT,outline='',tags='orb')
        self.canvas.create_text(200,145,text='SAM',fill=INK,font=('Segoe UI',26,'bold'),tags='orb')
        self.canvas.create_text(200,177,text='AI ASSISTANT',fill=MUTED,font=('Segoe UI',9),tags='orb')
        self.canvas.tag_raise('camera');self.root.after(50,self.tick)
    def startup(self):
        if self.preview:return
        answer=messagebox.askyesnocancel('Windows startup','Start SAM AI after Windows sign-in?\n\nYes: enable\nNo: remove startup shortcut\nCancel: leave unchanged',parent=self.root)
        if answer is None:return
        try:
            from startup import configure
            configure(answer);messagebox.showinfo('Startup','Startup enabled.' if answer else 'Startup disabled.')
        except Exception as exc:messagebox.showerror('Startup',str(exc))

if __name__=='__main__':
    root=tk.Tk();app=Assistant(root,preview='--preview' in sys.argv);root.mainloop()
