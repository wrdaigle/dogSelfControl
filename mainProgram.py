#!/usr/bin/env python3 #the script is python3
import sys
import random
import time

import tkinter as tk
from tkinter import messagebox
if sys.platform.startswith('win'):
    pass
else:
    import rpiParts
    rpiParts.setupGPIO()
    feeder1 = rpiParts.feeder(17,27,22,24,25)
    feeder2 = rpiParts.feeder(19,26,13,23,8)
    touchSensor = rpiParts.touchSensor()



import sqlite3

import os
import threading

LARGE_FONT= ("Verdana", 16)

homePath = os.path.split(os.path.realpath(__file__))[0]
dbPath = os.path.join(homePath,'data','selfControlData.sqlite3')
con = None


import pygame
pygame.init()
sound = pygame.mixer.Sound(os.path.join(homePath,'sounds','tada.wav'))


class selfControlApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (screenStart, screenRegister,screenTrial, screenTrialSetup, screenConfig):
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

        btnConfig = tk.Button(self, text="Update settings", command=lambda: controller.show_frame(screenConfig))
        btnConfig.pack(pady=10,padx=10)

        btnRunTrialSetup = tk.Button(self, text="Run a trial", command=lambda: controller.show_frame(screenTrialSetup))
        btnRunTrialSetup.pack(pady=10,padx=10)

class screenConfig(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)

        tk.Label(self, text="Update configuration", font=LARGE_FONT).grid(row=0,column=0,columnspan=2)


        con = sqlite3.connect(dbPath)
        cur = con.cursor()
        cur.execute('SELECT Description,Value,Units from Configuration')
        data =cur.fetchall()
        self.configurations = {}
        rownum=2
        for row in data:
            self.configurations.setdefault(row[0],{})
            self.configurations[row[0]]['value'] = row[1]
            self.configurations[row[0]]['units'] = row[2]
            self.configurations[row[0]]['var'] = tk.StringVar()
            tk.Label(self, text=row[0]+' ('+self.configurations[row[0]]['units']+')').grid(row=rownum,column=0,sticky='w')
            tk.Entry(self,textvariable=self.configurations[row[0]]['var']).grid(row=rownum,column=1,sticky='e')
            self.configurations[row[0]]['var'].set(self.configurations[row[0]]['value'])
            rownum +=1

        con.close()
##        print(self.configurations)
##        rownum=2
##        for configDesc, data in self.configurations.items():
##            tk.Label(self, text=configDesc+' ('+data['units']+')').grid(row=rownum,column=0,sticky='w')
##            tk.Entry(self,textvariable=data['value']).grid(row=rownum,column=1,sticky='e')
##            rownum +=1



##            self.dogName = tk.StringVar()
##            tk.Entry(self,textvariable=self.dogName).grid(row=1,column=1,sticky='w')

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
                            Affiliation,
                            Large_reward_side
                    )
                    VALUES (
                        '"""+self.dogName.get()+"""',
                        DATETIME('now'),
                        '"""+self.dogBreed.get()+"""',
                        '"""+str(self.dogAge.get())+"""',
                        '"""+self.affiliation.get()+"""',
                        '"""+random.choice(['left','right'])+"""'
                    )
                """
            )
            con.commit()
            con.close()
            messagebox.showinfo('Dog Registered',self.dogName.get() + ' has been registered.')

            self.resetForm()
            self.controller.show_frame(screenStart)



class screenTrialSetup(tk.Frame):

    def __init__(self, parent, controller):
        self.controller = controller

        #setup the frame
        tk.Frame.__init__(self, parent)
        lblTitle = tk.Label(self, text="Configure Trial", font=LARGE_FONT).grid(row=0,column=0,columnspan=2)

        #add a the "select a dog" option list
        tk.Label(self, text="Select a dog:").grid(row=2,column=0,sticky='e')
        self.dogChoice_default = '--'
        self.dogName = tk.StringVar()
        self.currentDogSelection = None
        self.dogName.set(self.dogChoice_default) # default choice
        dogList = self.getDogList()
        def onDogSelect(val):
            btnRunTrial.config(state="normal")
            self.currentDogSelection = val
        self.optMenu = tk.OptionMenu(self, self.dogName, *dogList, command=onDogSelect)
        self.optMenu.config(width=30)
        self.optMenu.grid(row=2,column=1,sticky='w')

        # add a "cancel" button
        def onRefresh():
            self.dogName.set(self.dogChoice_default)
            self.optMenu['menu'].delete(0,'end')
            newDogList = self.getDogList()
            for dog in newDogList:
                self.optMenu['menu'].add_command(label=dog, command=tk._setit(self.dogName, dog))
        btnRefreshDogList = tk.Button(self, text="Refresh", command=onRefresh )
        btnRefreshDogList.grid(row=2,column=2)

        #add a "run a trial" button
        def onTrialRun():
            controller.show_frame(screenTrial)
            controller.frames[screenTrial].newTrial(self.currentDogSelection)
        btnRunTrial = tk.Button(self, text="Run a trial", state=tk.DISABLED,command=onTrialRun)

        btnRunTrial.grid(pady=40,row=3,column=1,sticky='w')

        # add a "cancel" button
        def onCancel():
            self.dogName.set(self.dogChoice_default)
            controller.show_frame(screenStart)
            btnRunTrial.config(state="disabled")
        btnCancel = tk.Button(self, text="Cancel", command=onCancel )
        btnCancel.grid(row=3,column=2)

    def getDogList(self):
        con = sqlite3.connect(dbPath)
        cur = con.cursor()
        cur.execute('SELECT DogID, Name, Breed from Dog order by Name, Breed')
        data =cur.fetchall()
        dogList = []
        for row in data:
            dogList.append(row[1]+' - '+row[2]+' ('+str(row[0])+')')
        con.close()
        return dogList

class screenTrial(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.dogName = ''
        self.controller = controller
        tk.Label(self, text="Trial in progress", font=LARGE_FONT).grid(row=0,column=1)
        tk.Label(self, text="Dog Name:").grid(row=1,column=1,sticky='e')
        tk.Label(self, text="Dog Breed:").grid(row=2,column=1,sticky='e')
        tk.Label(self, text="Large Reward Side:").grid(row=3,column=1,sticky='e')
        tk.Label(self, text="Elapsed time:").grid(row=4,column=1,sticky='e')

        self.dogNameVar = tk.StringVar()
        tk.Label(self, textvariable = self.dogNameVar).grid(row=1,column=2,sticky='w')
        self.dogBreedVar = tk.StringVar()
        tk.Label(self, textvariable = self.dogBreedVar).grid(row=2,column=2,sticky='w')
        self.largeRewardSideVar = tk.StringVar()
        tk.Label(self, textvariable = self.largeRewardSideVar).grid(row=3,column=2,sticky='w')
        self.timeVar = tk.StringVar()
        self.timer = tk.Label(self, textvariable = self.timeVar).grid(row=4,column=2,sticky='w')

        #button2 = tk.Button(self, text="Play Sound",command=playSound).grid(row=3,column=2)
    def newTrial(self,dogName):
        dogID = dogName.split('(')[1].split(')')[0]
        dogData = self.getDogData(dogID)
        self.dogNameVar.set(dogData[0])
        self.dogBreedVar.set(dogData[1])
        self.largeRewardSideVar.set(dogData[2])
        startTime = time.time()

        def setTime():
            self.timeVar.set(str(round(time.time() - startTime))+ ' seconds')
            self.controller.after(1000,setTime)
        setTime()

    def getDogData(self,dogID):
        con = sqlite3.connect(dbPath)
        cur = con.cursor()
        cur.execute('SELECT Name,Breed,Large_reward_side from Dog where dogID = '+dogID)
        data =cur.fetchall()
        dogData = data[0]
        con.close()
        return dogData



def playSound():
    sound.play()

def dispense():
    feeder2.dispense(100)
def fill():
    feeder2.returnToFull()

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        if sys.platform.startswith('win') == False:
            rpiParts.cleanup()
        app.destroy()

if sys.platform.startswith('win') == False:
    sensorWatcher = threading.Thread(target=touchSensor.watch)
    sensorWatcher.start()

app = selfControlApp()
app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()



