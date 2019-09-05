#!/usr/bin/env python3 #the script is python3

# ###################################
# To Do
#
# Link configuration setting to trials
# Set up logging
# Start sending data to database
# Add a backup function
# turn off wifi



import sys
import time
import dataHelper
import random

import tkinter as tk
from tkinter import messagebox
if sys.platform.startswith('win'):
    pass
else:
    try:
        import rpiParts
    except:
        print('Trouble importing rpiPart')
    try:
        rpiParts.setupGPIO()
        feeder1 = rpiParts.feeder(20,21,16,23,24,22,4,7,'right')
        feeder2 = rpiParts.feeder(19,26,13,5,6,18,27,10,'left')
    except:
        print('Trouble initializing feeders')
    try:
        touchSensor = rpiParts.touchSensor()
    except:
        print('Trouble initializing touch sensors')


#import sqlite3

import os
import threading

LARGE_FONT= ("Verdana", 16)

homePath = os.path.split(os.path.realpath(__file__))[0]


import pygame
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
sound_start = pygame.mixer.Sound(os.path.join(homePath,'sounds','chimes.wav'))
sound_timeout = pygame.mixer.Sound(os.path.join(homePath,'sounds','chord.wav'))
sound_touched = pygame.mixer.Sound(os.path.join(homePath,'sounds','tada.wav'))
sound_done = pygame.mixer.Sound(os.path.join(homePath,'sounds','chord.wav'))

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

        def showTrialSetup():
            #refresh the form elements
            controller.frames[screenTrialSetup].resetForm()
            #show the form
            controller.show_frame(screenTrialSetup)

        btnRunTrialSetup = tk.Button(self, text="Run a trial", command=lambda: showTrialSetup())
        btnRunTrialSetup.pack(pady=10,padx=10)

class screenConfig(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)

        tk.Label(self, text="Update configuration", font=LARGE_FONT).grid(row=0,column=0,columnspan=2)

        #add a row for each configuration
        rownum=2
        self.configurations = {}
        self.configDescriptions = ['Small Reward Delay','Large Reward Delay','Small Reward Quantity','Large Reward Quantity', 'Trial Length', 'Iteration Length','Time Between Iterations']
        for settingDesc in self.configDescriptions:
            self.configurations.setdefault(settingDesc,{})
            self.configurations[settingDesc]['var'] = tk.StringVar()
            settingData = dataHelper.getConfigValue(settingDesc)
            tk.Label(self, text=settingDesc+' ('+settingData['units']+')').grid(row=rownum,column=0,sticky='w')
            tk.Entry(self,textvariable=self.configurations[settingDesc]['var']).grid(row=rownum,column=1,sticky='e')
            self.configurations[settingDesc]['var'].set(settingData['value'])
            rownum +=1

        # add an exit button
        tk.Button(self, text="Save",command=lambda:self.updateDatabaseUsingForm()).grid(row=rownum,column=0)
        tk.Button(self, text="Exit without saving",command=lambda:self.updateFormUsingDatabase()).grid(row=rownum,column=1)

    def updateFormUsingDatabase(self):
        for settingDesc in self.configDescriptions:
            settingData = dataHelper.getConfigValue(settingDesc)
            self.configurations[settingDesc]['var'].set(settingData['value'])
        self.controller.show_frame(screenStart)
    def updateDatabaseUsingForm(self):
        for settingDesc in self.configDescriptions:
            newValue = self.configurations[settingDesc]['var'].get()
            settingData = dataHelper.setConfigValue(settingDesc,newValue)
        self.controller.show_frame(screenStart)



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
        affiliationList = dataHelper.getAffilliationList()
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
        if dataHelper.dogyAlreadyRegistered(self.dogName.get(),self.dogBreed.get()) == True:
            messagebox.showerror('Already Registered','A '+self.dogBreed.get()+' with the name '+self.dogName.get()+' has already been registered.  Please edit the name of the newly registered dog so you can distinguish the dogs')
            return False

        # if there are no problems
        return True


    def resetForm(self):
        self.dogName.set('')
        self.dogBreed.set('')
        self.dogAge.set(0)
        self.affiliation.set('--')

    def addRecord(self):
        if self.validateForm():

            dataHelper.addDogRecord(self.dogName.get(),self.dogBreed.get(),self.dogAge.get(),self.affiliation.get())
            messagebox.showinfo('Dog Registered',self.dogName.get() + ' has been registered.')

            self.resetForm()
            self.controller.show_frame(screenStart)



class screenTrialSetup(tk.Frame):

    def __init__(self, parent, controller):
        self.controller = controller

        #setup the frame
        tk.Frame.__init__(self, parent)
        lblTitle = tk.Label(self, text="Configure Trial", font=LARGE_FONT).grid(row=0,column=0,columnspan=2)
        lblTitle = tk.Label(self, text="Note: Complete this step before bringing dog in room. Make sure pump is full!").grid(row=1,column=0,columnspan=2)

        #add a the "select a dog" option list
        tk.Label(self, text="Select a dog:").grid(row=2,column=0,sticky='e')
        self.dogChoice_default = '--'
        self.dogName = tk.StringVar()
        self.currentDogSelection = None
        self.dogName.set(self.dogChoice_default) # default choice
        dogList = dataHelper.getDogList()

        self.optMenu = tk.OptionMenu(self, self.dogName, *dogList)
        self.optMenu.config(width=30)
        self.optMenu.grid(pady=10,row=2,column=1,sticky='w')


        #add an observers field
        tk.Label(self, text="Observers:").grid(row=3,column=0,sticky='e')
        self.observers = tk.StringVar()
        tk.Entry(self,textvariable=self.observers).grid(row=3,column=1,sticky='w')

        #add a hours since last feeding field
        tk.Label(self, text="Hours since last feeding:").grid(row=4,column=0,sticky='e')
        self.hoursSinceLastFeeding = tk.StringVar()
        tk.Entry(self,textvariable=self.hoursSinceLastFeeding).grid(row=4,column=1,sticky='w')

        #add a "run a trial" button
        def onTrialRun():
            if self.validateForm():
                dogId = self.dogName.get().split('(')[1].split(')')[0]
                trialId = dataHelper.logNewTrialRecord(dogId,self.observers.get(),self.hoursSinceLastFeeding.get())
                controller.show_frame(screenTrial)
                controller.frames[screenTrial].newTrial(self.dogName.get(), trialId)
        btnRunTrial = tk.Button(self, text="Start trial", command=onTrialRun)
        btnRunTrial.grid(pady=10,row=5,column=1,sticky='w')

        #add a "reset pumps" button
        def onPumpFill():
            feeder1.returnToFull()
            feeder2.returnToFull()
        tk.Button(self, text="Reset pumps" ,command=onPumpFill).grid(pady=10,row=6,column=1,sticky='w')

        # add a "cancel" button
        def onCancel():
            #self.dogName.set(self.dogChoice_default)
            controller.show_frame(screenStart)
            #btnRunTrial.config(state="disabled")
        btnCancel = tk.Button(self, text="Cancel", command=onCancel )
        btnCancel.grid(pady=10,row=6,column=2)
    def resetForm(self):
        self.dogName.set(self.dogChoice_default)
        self.hoursSinceLastFeeding.set('')
        self.observers.set('')
        self.optMenu['menu'].delete(0,'end')
        newDogList = dataHelper.getDogList()
        for dog in newDogList:
            self.optMenu['menu'].add_command(label=dog, command=tk._setit(self.dogName, dog))

    def validateForm(self):
        # check for missing values
        formErrors = []
        if self.dogName.get() == '--':
            formErrors.append("You must select a dog!")
        if self.observers.get() == '':
            formErrors.append("Observers is required!")
        if self.hoursSinceLastFeeding.get() == '':
            formErrors.append("Hours since last feeding is required!")
        if len(formErrors)>0:
            errorString = '\n'.join(formErrors)
            messagebox.showerror('Missing Values',errorString)
            return False

        # if there are no problems
        return True

class screenTrial(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.dogName = ''
        self.controller = controller
        tk.Label(self, text="Current trial", font=LARGE_FONT).grid(row=0,column=1)
        tk.Label(self, text="Dog Name:").grid(row=1,column=1,sticky='e')
        tk.Label(self, text="Dog Breed:").grid(row=2,column=1,sticky='e')
        tk.Label(self, text="Large Reward Side:").grid(row=3,column=1,sticky='e')

        self.btnStartFeeders_forced = tk.Button(self, command=lambda:self.startFeeders_forced(), text="Start Forced Trial")
        self.btnStartFeeders_forced.grid(row=4,column=1)
        self.btnStartFeeders_choice = tk.Button(self, command=lambda:self.startFeeders_choice(), text="Start Choice Trial")
        self.btnStartFeeders_choice.grid(row=4,column=2)
        self.btnQuit = tk.Button(self, command=lambda:self.quitTrial(), text="Quit")
        self.btnQuit.grid(row=4,column=3,padx=10)

        tk.Label(self, text="Elapsed time:").grid(row=6,column=1,sticky='e')


        self.statusVar = tk.StringVar()
        tk.Label(self, textvariable = self.statusVar, fg='red').grid(row=7,column=0,columnspan=3)

        self.dogNameVar = tk.StringVar()
        tk.Label(self, textvariable = self.dogNameVar).grid(row=1,column=2,sticky='w')
        self.dogBreedVar = tk.StringVar()
        tk.Label(self, textvariable = self.dogBreedVar).grid(row=2,column=2,sticky='w')
        self.largeRewardSideVar = tk.StringVar()

        tk.Label(self, textvariable = self.largeRewardSideVar).grid(row=3,column=2,sticky='w')
        self.timeVar = tk.StringVar()
        self.timer = tk.Label(self, textvariable = self.timeVar).grid(row=6,column=2,sticky='w')

    def newTrial(self,dogName,trialId):
        self.btnStartFeeders_forced.config(state="normal")
        self.btnStartFeeders_choice.config(state="normal")
        dataHelper.logEvent(trialId,'New trial initiated')
        self.trialId = trialId
        dogID = dogName.split('(')[1].split(')')[0]
        dogData = dataHelper.getDogData(dogID)
        self.dogNameVar.set(dogData[0])
        self.dogBreedVar.set(dogData[1])
        self.largeRewardSideVar.set(dogData[2])

        if dogData[2] == 'right':
            self.rightSideDelay = dataHelper.getConfigValue('Large Reward Delay')['value']
            self.rightSideQuantity = dataHelper.getConfigValue('Large Reward Quantity')['value']
            self.leftSideDelay = dataHelper.getConfigValue('Small Reward Delay')['value']
            self.leftSideQuantity = dataHelper.getConfigValue('Small Reward Quantity')['value']
        else:
            self.leftSideDelay = dataHelper.getConfigValue('Large Reward Delay')['value']
            self.leftSideQuantity = dataHelper.getConfigValue('Large Reward Quantity')['value']
            self.rightSideDelay = dataHelper.getConfigValue('Small Reward Delay')['value']
            self.rightSideQuantity = dataHelper.getConfigValue('Small Reward Quantity')['value']

    def startFeeders_forced(self):

        trialLength = dataHelper.getConfigValue('Trial Length')['value']
        iterationLength = dataHelper.getConfigValue('Iteration Length')['value']
        timeBetweenIterations = dataHelper.getConfigValue('Time Between Iterations')['value']

        dataHelper.logEvent(self.trialId,'Forced trial started')

        # randomize the order
        feeders = random.shuffle([feeder1,feeder2])

        for feeder in feeders:

            startTime = time.time()
            self.btnStartFeeders_forced.config(state="disabled")
            self.btnStartFeeders_choice.config(state="disabled")

            n = 0
            done = False
            while n < 10 and done == False:

                if (time.time() - startTime) > trialLength:
                    self.updateText('Time is up')
                    sound_done.play()
                    done = True
                    return
                dataHelper.logEvent(self.trialId,'Forced trial in progress -- {} is enabled'.format(feeder.side))
                feeder.toggleLight('touch',True)
                self.updateText('Forced trial in progress -- {} is enabled')
                sound_start.play()

                out = touchSensor.listenForFirstTouch(iterationLength)
                feeder.toggleLight('touch',False)

                if out['action'] == 'timeout':
                    sound_timeout.play()
                    self.updateText('{} seconds passed without a selection. Next trial will start in {} seconds.'.format(iterationLength,timeBetweenIterations))
                if out['action'] == 'touch':
                    if out['sensor'] == feeder.gpio_touchpad:
                        feeder.toggleLight('bowl',True)
                        self.updateText('{} pad touched. Next trial with start in {} seconds.'.format(feeder.side,timeBetweenIterations))
                        self.distributeReward(feeder.side)
                        feeder.toggleLight('bowl',False)
                self.updateText('Next forced iteration will start in {} seconds'.format(timeBetweenIterations))
                time.sleep(timeBetweenIterations)
                n+=1

    def startFeeders_choice(self):

        trialLength = dataHelper.getConfigValue('Trial Length')['value']
        iterationLength = dataHelper.getConfigValue('Iteration Length')['value']
        timeBetweenIterations = dataHelper.getConfigValue('Time Between Iterations')['value']

        dataHelper.logEvent(self.trialId,'Trial started')

        startTime = time.time()
        self.btnStartFeeders_forced.config(state="disabled")
        self.btnStartFeeders_choice.config(state="disabled")
##        self.updateText('Start a trial at any time')

        done = False
        while done == False:
            if (time.time() - startTime) > trialLength:
                self.updateText('Trial is done')
                sound_done.play()

                done = True
                return
            dataHelper.logEvent(self.trialId,'Feeders enabled')
            feeder1.toggleLight('touch',True)
            feeder2.toggleLight('touch',True)
            self.updateText('Feeders enabled. Trial in progress')
            sound_start.play()
            out = touchSensor.listenForFirstTouch(iterationLength)
            feeder1.toggleLight('touch',False)
            feeder2.toggleLight('touch',False)
            if out['action'] == 'timeout':
                sound_timeout.play()
                self.updateText('{} seconds passed without a selection. Next trial will start in {} seconds.'.format(iterationLength,timeBetweenIterations))
            if out['action'] == 'touch':
                if out['sensor'] == 10:
                    feeder2.toggleLight('bowl',True)
                    self.updateText('Left pad touched. Next trial with start in {} seconds.'.format(iterationLength,timeBetweenIterations))
                    self.distributeReward('left')
                    feeder2.toggleLight('bowl',False)
                if out['sensor'] == 7:
                    feeder1.toggleLight('bowl',True)
                    self.updateText('Right pad touched. Next trial with start in {} seconds.'.format(iterationLength,timeBetweenIterations))
                    self.distributeReward('right')
                    feeder1.toggleLight('bowl',False)
            self.updateText('Next iteration will start in {} seconds'.format(timeBetweenIterations))
            time.sleep(timeBetweenIterations)

    def updateText(self,newText):
        self.statusVar.set(newText)
        self.update()

    def quitTrial(self):
        self.controller.show_frame(screenStart)

    def distributeReward(self,sideSelected):

        dataHelper.logEvent(self.trialId,sideSelected+' side selected')
        sound_touched.play()
        if sideSelected == 'left':
            self.updateText('Left side selected. Reward will be distributed after a '+str(self.leftSideDelay)+' second delay.')
            time.sleep(self.leftSideDelay)
            dataHelper.logEvent(self.trialId,'Left reward distributed.')
            self.updateText('Left reward distriuted. Start another run at any time.')
            feeder1.dispense(self.leftSideQuantity)
        else:
            self.updateText('Right side selected. Reward will be distributed after a '+str(self.rightSideDelay)+' second delay.')
            time.sleep(self.rightSideDelay)
            dataHelper.logEvent(self.trialId,'Right reward distributed.')
            self.updateText('Right reward distriuted. Start another run at any time.')
            feeder2.dispense(self.rightSideQuantity)


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        if sys.platform.startswith('win') == False:
            rpiParts.cleanup()
        app.destroy()


app = selfControlApp()
app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()



