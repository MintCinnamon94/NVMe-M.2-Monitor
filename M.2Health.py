# Program for checking M.2 health
import tkinter as tk
from pynput import keyboard
import psutil
from time import sleep
import random

class M2Health():
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.focus_force()


        self.root.config(bg='black')
        self.canvas = tk.Canvas(self.root, width= 371, height= 70, bg='Black', highlightthickness=0)
        self.neon_rect = self.createroundrect(5, 5, 367, 65, radius=30, outline='#00f3ff', width=2)

        self.p_text = self.canvas.create_text(185, 25, text="Primary | Loading...", fill='#00f3ff', font=('Arial', 10, 'bold'))
        self.s_text = self.canvas.create_text(185, 45, text="Secondary | Loading...", fill='#ff00ff', font=('Arial', 10, 'bold'))
        self.canvas.pack()


        self.canvas.bind('<Button-1>', self.startmove)
        self.canvas.bind('<B1-Motion>', self.domove)

        self.root.wait_visibility(self.root)
        self.root.attributes('-type', 'dock')
        self.root.attributes('-alpha', 0.6)

        self.listener = keyboard.Listener(on_press = self.closeprogram)
        self.listener.start()

        self.neon = ['#00f3ff', # Neon Cyan
                     '#ff00ff', # Hot Pink
                     '#9d00ff', # Electric Purple
                     '#0055ff', # Deep Blue
                     '#001a1a', # Dim Cyan
                     '#1a001a', # Dim Pink
                     '#0d001a'] # Dim Purple
        self.animatedborder()
        self.initialRW()
        self.updatem2data()

    def createroundrect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius, x2,
                  y1 + radius, x2, y2 - radius, x2, y2 - radius, x2, y2, x2 - radius, y2, x2 - radius, y2, x1 + radius,
                  y2, x1 + radius, y2, x1, y2, x1, y2 - radius, x1, y2 - radius, x1, y1 + radius, x1, y1 + radius, x1,
                  y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def animatedborder(self):
        colour = random.choice(self.neon)
        self.canvas.itemconfig(self.neon_rect, outline=colour)
        flicker = random.randint(50,500)
        self.root.after(flicker, self.animatedborder)

    def closeprogram(self, key):
        if key == keyboard.Key.esc:
            print('Closing program')
            self.root.destroy()
            return False

    def startmove(self, event):
        self.x = event.x
        self.y = event.y

    def domove(self, event):
        delta_x = event.x - self.x
        delta_y = event.y - self.y

        new_x = self.root.winfo_x() + delta_x
        new_y = self.root.winfo_y() + delta_y
        self.root.geometry(f'+{new_x}+{new_y}')

    def initialRW(self):
        io = psutil.disk_io_counters(perdisk=True)
        self.lastread = io['nvme0n1'].read_bytes
        self.lastwrite = io['nvme0n1'].write_bytes
        if 'nvme1n1' in io:
            self.s_lastread = io['nvme1n1'].read_bytes
            self.s_lastwrite = io['nvme1n1'].write_bytes
        else:
            self.canvas.itemconfig(self.s_text, state='hidden')
            self.s_lastread = 0
            self.s_lastwrite = 0

    def m2data(self):
        io = psutil.disk_io_counters(perdisk=True)
        temps = psutil.sensors_temperatures()

        PreadMB = (io['nvme0n1'].read_bytes - self.lastread) / 1024**2
        PwriteMB = (io['nvme0n1'].write_bytes - self.lastwrite) / 1024**2
        primarym2 = temps['nvme'][0].current if 'nvme' in temps else 0

        if 'nvme1n1' in io and len(temps['nvme']) > 1:
            SreadMB = (io['nvme1n1'].read_bytes - self.s_lastread) / 1024**2
            SwriteMB = (io['nvme1n1'].write_bytes - self.s_lastwrite)/ 1024**2
            secondarym2 = temps['nvme'][1].current
        else:
            SreadMB = SwriteMB = secondarym2 = 0

        self.initialRW()
        return PreadMB, PwriteMB, SreadMB, SwriteMB, primarym2, secondarym2

    def updatem2data(self):
        try:
            (PreadMB, PwriteMB, SreadMB, SwriteMB, primarym2, secondarym2) = self.m2data()

            pstring= f'Primary | Read: {PreadMB:.0f} Mb | Write: {PwriteMB:.0f} Mb | Temp: {primarym2:.2f} °C'
            sstring= f'Secondary | Read: {SreadMB:.0f} Mb | Write: {SwriteMB:.0f} Mb | Temp: {secondarym2:.2f} °C'

            self.canvas.itemconfig(self.p_text, text=pstring)
            self.canvas.itemconfig(self.s_text, text=sstring)
        except Exception as e:
            print(f'Something went wrong {e}')
            sleep(0.1)
            self.canvas.itemconfig(self.p_text, text='Hardware Error')

        self.root.after(100, self.updatem2data)
if __name__ == '__main__':
    app = M2Health()
    app.root.mainloop()
