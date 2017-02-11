
import tkinter as tk
from tkinter import messagebox

from pygame import mixer

import sqlite3
import sys

LARGE_FONT= ("Verdana", 16)

dbPath = r'selfControlData.sqlite3'
con = None

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
        label = tk.Label(self, text="Testing Dog Self-Control", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        btnRegister = tk.Button(self, text="Register a Dog",command=lambda: controller.show_frame(screenRegister))
        btnRegister.pack(pady=10,padx=10)

        btnRunTrial = tk.Button(self, text="Run a trial", command=lambda: controller.show_frame(screenTrial))
        btnRunTrial.pack(pady=10,padx=10)

class screenRegister(tk.Frame):

    def __init__(self, parent, controller):
        self.controller = controller

        tk.Frame.__init__(self, parent)
        lblTitle = tk.Label(self, text="Register a Dog", font=LARGE_FONT).grid(row=0,column=0,columnspan=2)

        tk.Label(self, text="Dog Name:").grid(row=1,column=0,sticky='e')
        self.dogName = tk.StringVar()
        tk.Entry(self,textvariable=self.dogName).grid(row=1,column=1,sticky='w')

        tk.Label(self, text="Breed:").grid(row=2,column=0,sticky='e')
        self.dogBreed = tk.StringVar()
        tk.Entry(self,textvariable=self.dogBreed).grid(row=2,column=1,sticky='w')

        tk.Label(self, text="Approximate Age (yrs):").grid(row=3,column=0,sticky='e')
        self.dogAge = tk.IntVar()
        tk.Entry(self,textvariable=self.dogAge).grid(row=3,column=1,sticky='w')

        tk.Label(self, text="Affiliation:").grid(row=4,column=0,sticky='e')
        self.affiliation = tk.StringVar()
        self.affiliation.set("--") # default choice
        affiliationList = self.getAffilliationList()
        optMenu = tk.OptionMenu(self, self.affiliation, *affiliationList)
        optMenu.config(width=30)
        optMenu.grid(row=4,column=1,sticky='w')

        btnCommit = tk.Button(self, text="Submit",command=lambda: self.addRecord()).grid(row=6,column=1,pady=10)
        btnExit = tk.Button(self, text="Exit",command=lambda: controller.show_frame(screenStart)).grid(row=6,column=2,pady=10,padx=10)

    def validateForm(self):
        # check for missing values
        formErrors = []
        if self.dogName.get() == '':
            formErrors.append("Dog Name is required!")
        if self.dogBreed.get() == "":
            formErrors.append("Breed is required!")
        if self.dogAge.get() == 0:
            formErrors.append("Dog Age is required!")
        if self.affiliation.get() == "--":
            formErrors.append('Affiliation is required!')
        if len(formErrors)>0:
            errorString = '\n'.join(formErrors)
            messagebox.showerror('Missing Values',errorString)
            return False

        # check to make sure the name/breed combo is not in the database yet
        con = sqlite3.connect(dbPath)
        cur = con.cursor()
        cur.execute("SELECT * from Dog where name = '"+self.dogName.get()+"' and breed = '"+self.dogBreed.get()+"'")
        data =cur.fetchall()
        con.close()
        if len(data)>0:
            messagebox.showerror('Already Registered','A '+self.dogBreed.get()+' with the name '+self.dogName.get()+' has already been registered.  Please edit the name of the newly registered dog so you can distinguish the dogs')
            return False

        # if there are no problems
        return True

    def getAffilliationList(self):
        con = sqlite3.connect(dbPath)
        cur = con.cursor()
        cur.execute('SELECT * from AffiliationLU')
        data =cur.fetchall()
        affiliationList = []
        for row in data:
            affiliationList.append(row[0])
        con.close()
        return affiliationList

    def resetForm(self):
        self.dogName.set('')
        self.dogBreed.set('')
        self.dogAge.set(0)
        self.affiliation.set('--')

    def addRecord(self):
        if self.validateForm():
            con = sqlite3.connect(dbPath)
            cur = con.cursor()
            cur.execute(
                """
                    INSERT INTO Dog (
                            Name,
                            Registration_Date,
                            Breed,
                            Age_at_registration,
                            Affiliation
                    )
                    VALUES (
                        '"""+self.dogName.get()+"""',
                        DATETIME('now'),
                        '"""+self.dogBreed.get()+"""',
                        '"""+str(self.dogAge.get())+"""',
                        '"""+self.affiliation.get()+"""'
                    )
                """
            )
            con.commit()
            con.close()
            messagebox.showinfo('Dog Registered',self.dogName.get() + ' has been registered.')
            self.resetForm()
            self.controller.show_frame(screenStart)


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



