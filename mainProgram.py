
import tkinter as tk
from pygame import mixer

LARGE_FONT= ("Verdana", 12)


class selfControlApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (screenStart, screenRegister, screenTrial):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(screenStart)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


class screenStart(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Testing Dog Self Control", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        btnRegister = tk.Button(self, text="Register a Dog",command=lambda: controller.show_frame(screenRegister))
        btnRegister.pack(pady=10,padx=10)

        btnRunTrial = tk.Button(self, text="Run a trial", command=lambda: controller.show_frame(screenTrial))
        btnRunTrial.pack(pady=10,padx=10)

class screenRegister(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        lblTitle = tk.Label(self, text="Register a Dog", font=LARGE_FONT).grid(row=0,column=0,columnspan=2)

        lblDogName = tk.Label(self, text="Dog Name:", font=LARGE_FONT).grid(row=1,column=0)
        entDogName = tk.Entry(self).grid(row=1,column=1)

        btnCommit = tk.Button(self, text="Commit",command=lambda: controller.show_frame(screenStart)).grid(row=4,column=0)
        btnExit = tk.Button(self, text="Exit",command=lambda: controller.show_frame(screenStart)).grid(row=4,column=1)



class screenTrial(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page One!!!", font=LARGE_FONT).grid(row=0,column=1)
        #label.pack(pady=10,padx=10)

        #button1 = tk.Button(self, text="Back to Home",command=lambda: controller.show_frame(OpeningScreen)).grid(row=1,column=1)

        #button2 = tk.Button(self, text="Page Two",command=lambda: controller.show_frame(TrialScreen)).grid(row=2,column=1,pady=10,padx=10)

        slider1 = tk.Scale(self, from_=100, to=0).grid(row=1,column=0,rowspan=3)
        slider2 = tk.Scale(self, from_=100, to=0)
        slider2.grid(row=1,column=3,rowspan=3)
        slider2.set(30)
        slider2.config(state="disabled")


        button2 = tk.Button(self, text="Play Sound",command=playSound).grid(row=2,column=2)


def playSound():
    mixer.init()
    sound = mixer.Sound(r"C:\Python27\Lib\test\audiodata\pluck-pcm8.wav")
    sound.play()



app = selfControlApp()
app.mainloop()

