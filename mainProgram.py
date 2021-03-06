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
##    try:
##        rpiParts.setupGPIO()
##        feeder1 = rpiParts.feeder(
##            20,   #gpio_step
##            21,   #gpio_direction
##            16,   #gpio_sleep
##            23,   #gpio_full
##            24,   #gpio_empty
##            18,   #gpio_bowllight
##            4,    #gpio_touchlight
##            10,   #gpio_touchpad
##            'left'   #side
##            )
##        feeder2 = rpiParts.feeder(
##            19,   #gpio_step
##            26,   #gpio_direction
##            13,   #gpio_sleep
##            5,    #gpio_full
##            6,    #gpio_empty
##            22,   #gpio_bowllight
##            27,   #gpio_touchlight
##            7,    #gpio_touchpad
##            'right'   #side
##            )
##    except:
##        print('Trouble initializing feeders')
##    try:
##        touchSensor = rpiParts.touchSensor()
##    except:
##        print('Trouble initializing touch sensors')


#import sqlite3

import os
import threading

LARGE_FONT= ("Verdana", 16)

homePath = os.path.split(os.path.realpath(__file__))[0]


import pygame



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

        tk.Label(self, text="Touch Sensor Height:").grid(row=4,column=0,sticky='e')
        self.height = tk.IntVar()
        tk.Entry(self,textvariable=self.height).grid(row=4,column=1,sticky='w')

        tk.Label(self, text="Affiliation:").grid(row=5,column=0,sticky='e')
        self.affiliation = tk.StringVar()
        self.affiliation.set("--") # default choice
        affiliationList = dataHelper.getAffilliationList()
        optMenu = tk.OptionMenu(self, self.affiliation, *affiliationList)
        optMenu.config(width=30)
        optMenu.grid(row=5,column=1,sticky='w')

        btnCommit = tk.Button(self, text="Submit",command=lambda: self.addRecord()).grid(row=7,column=1,pady=10)
        btnExit = tk.Button(self, text="Exit",command=lambda: controller.show_frame(screenStart)).grid(row=7,column=2,pady=10,padx=10)

    def validateForm(self):
        # check for missing values
        formErrors = []
        if self.dogName.get() == '':
            formErrors.append("Dog Name is required!")
        if self.dogBreed.get() == "":
            formErrors.append("Breed is required!")
        if self.dogAge.get() == 0:
            formErrors.append("Dog Age is required!")
        if self.height.get() == 0:
            formErrors.append("Touch Sensor Height is required!")
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
        self.height.set(0)
        self.affiliation.set('--')

    def addRecord(self):
        if self.validateForm():

            dataHelper.addDogRecord(self.dogName.get(),self.dogBreed.get(),self.dogAge.get(),self.affiliation.get(),self.height.get())
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

        # add a "cancel" button
        def onCancel():
            #self.dogName.set(self.dogChoice_default)
            controller.show_frame(screenStart)
            #btnRunTrial.config(state="disabled")
        btnCancel = tk.Button(self, text="Cancel", command=onCancel )
        btnCancel.grid(pady=10,row=5,column=2)
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

        self.feeder1 = None
        self.feeder2 = None
        self.touchSensor = None

        self.dogName = ''
        self.controller = controller
        tk.Label(self, text="Current trial", font=LARGE_FONT).grid(row=0,column=1)
        tk.Label(self, text="Dog Name:").grid(row=1,column=1,sticky='e')
        tk.Label(self, text="Dog Breed:").grid(row=2,column=1,sticky='e')
        tk.Label(self, text="Large Reward Side:").grid(row=3,column=1,sticky='e')
        tk.Label(self, text="Touch Sensor Height:").grid(row=4,column=1,sticky='e')

##        #add a "reset pumps" button
##        def onPumpFill():
##            feeder1.returnToFull()
##            feeder2.returnToFull()
##        def purgeAir():
##            feeder1.dispense(5)
##            feeder2.dispense(5)

        tk.Button(self, text="Reset pumps" ,command=self.onPumpFill).grid(pady=10,row=5,column=2,sticky='w')
        tk.Button(self, text="Purge air" ,command=self.purgeAir).grid(padx=10,pady=10,row=5,column=3,sticky='w')

        self.btnStartFeeders_forced1 = tk.Button(self, bg='lightblue', command=lambda:self.startFeeders_forced1(), text="Start Forced Trial")
        self.btnStartFeeders_forced1.grid(row=6,column=2,pady=2)
        self.btnStartFeeders_forced2 = tk.Button(self, bg='lightblue', command=lambda:self.startFeeders_forced_alternating(), text="Start Forced Trial (alternating)")
        self.btnStartFeeders_forced2.grid(row=7,column=2,pady=2)
        self.btnStartFeeders_choice = tk.Button(self, bg='lightgreen', command=lambda:self.startFeeders_choice(), text="Start Choice Trial")
        self.btnStartFeeders_choice.grid(row=8,column=2,pady=2)
        self.btnQuit = tk.Button(self, bg='red', fg='white', command=lambda:self.quitTrial(), text="Quit")
        self.btnQuit.grid(row=10,column=3,padx=100)

        tk.Label(self, text="Elapsed time:").grid(row=10,column=1,sticky='e')

        self.statusVar = tk.StringVar()
        tk.Label(self, textvariable = self.statusVar, fg='red').grid(row=11,column=0,columnspan=3)

        self.dogNameVar = tk.StringVar()
        tk.Label(self, textvariable = self.dogNameVar).grid(row=1,column=2,sticky='w')
        self.dogBreedVar = tk.StringVar()
        tk.Label(self, textvariable = self.dogBreedVar).grid(row=2,column=2,sticky='w')
        self.largeRewardSideVar = tk.StringVar()
        tk.Label(self, textvariable = self.largeRewardSideVar).grid(row=3,column=2,sticky='w')
        self.touchSensorHeightVar = tk.StringVar()
        tk.Label(self, textvariable = self.touchSensorHeightVar).grid(row=4,column=2,sticky='w')
        self.timeVar = tk.StringVar()
        self.timer = tk.Label(self, textvariable = self.timeVar).grid(row=10,column=2,sticky='w')



    def setupParts(self):
        try:
            rpiParts.setupGPIO()
            self.feeder1 = rpiParts.feeder(
                20,   #gpio_step
                21,   #gpio_direction
                16,   #gpio_sleep
                23,   #gpio_full
                24,   #gpio_empty
                18,   #gpio_bowllight
                4,    #gpio_touchlight
                10,   #gpio_touchpad
                'left'   #side
                )
            self.feeder2 = rpiParts.feeder(
                19,   #gpio_step
                26,   #gpio_direction
                13,   #gpio_sleep
                5,    #gpio_full
                6,    #gpio_empty
                22,   #gpio_bowllight
                27,   #gpio_touchlight
                7,    #gpio_touchpad
                'right'   #side
                )
        except:
            print('Trouble initializing feeders')
        try:
            self.touchSensor = rpiParts.touchSensor()
        except:
            print('Trouble initializing touch sensors')
        try:
            pygame.mixer.pre_init(44100, -16, 1, 512)
            pygame.init()
            self.sound_start = pygame.mixer.Sound(os.path.join(homePath,'sounds','chimes.wav'))
            self.sound_timeout = pygame.mixer.Sound(os.path.join(homePath,'sounds','chord.wav'))
            self.sound_touched = pygame.mixer.Sound(os.path.join(homePath,'sounds','tada.wav'))
            self.sound_done = pygame.mixer.Sound(os.path.join(homePath,'sounds','chord.wav'))
        except:
            print('Trouble initializing sounds')

    def teardownParts(self):
        rpiParts.cleanup()
        pygame.quit()
        self.btnStartFeeders_forced1.config(state="normal")
        self.btnStartFeeders_forced2.config(state="normal")
        self.btnStartFeeders_choice.config(state="normal")


    #add a "reset pumps" button
    def onPumpFill(self):
        self.setupParts()
        self.feeder1.returnToFull()
        self.feeder2.returnToFull()
        self.teardownParts()
    def purgeAir(self):
        self.setupParts()
        self.feeder1.dispense(5)
        self.feeder2.dispense(5)
        self.teardownParts()


    def newTrial(self,dogName,trialId):
        self.setupParts()
        self.btnStartFeeders_forced1.config(state="normal")
        self.btnStartFeeders_forced2.config(state="normal")
        self.btnStartFeeders_choice.config(state="normal")
        dataHelper.logEvent(trialId,'New trial initiated')
        self.trialId = trialId
        dogID = dogName.split('(')[1].split(')')[0]
        dogData = dataHelper.getDogData(dogID)
        self.dogNameVar.set(dogData[0])
        self.dogBreedVar.set(dogData[1])
        self.largeRewardSideVar.set(dogData[2])
        self.touchSensorHeightVar.set(dogData[3])

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
        self.teardownParts()

    def startFeeders_forced1(self):
        self.setupParts()
        trialLength = 240
        iterationLength = dataHelper.getConfigValue('Iteration Length')['value']
        timeBetweenIterations = dataHelper.getConfigValue('Time Between Iterations')['value']


        dataHelper.logEvent(self.trialId,'F1:Forced trial started')

        # randomize the order
        feeders = [self.feeder1,self.feeder2]
        random.shuffle(feeders)

        for feeder in feeders:

            startTime = time.time()
            self.btnStartFeeders_forced1.config(state="disabled")
            self.btnStartFeeders_forced2.config(state="disabled")
            self.btnStartFeeders_choice.config(state="disabled")

            n = 0
            done = False
            numOfIterations = 5
            if n == numOfIterations:
                self.updateText('Dog made 10 selectins on side')
            while n < numOfIterations and done == False:

                if (time.time() - startTime) > trialLength/2:
                    self.updateText('Time is up for side')
                    self.sound_done.play()
                    done = True
                    return
                dataHelper.logEvent(self.trialId,'F1:Forced trial in progress -- {} is enabled'.format(feeder.side))
                feeder.toggleLight('touch',True)
                self.updateText('Forced trial in progress -- {} is enabled'.format(feeder.side))
                self.sound_start.play()

                out = self.touchSensor.listenForFirstTouch_specific(iterationLength,feeder.gpio_touchpad)
                feeder.toggleLight('touch',False)

                if out['action'] == 'timeout':
                    self.sound_timeout.play()
                    self.updateText('{} seconds passed without a selection. Next trial will start in {} seconds.'.format(iterationLength,timeBetweenIterations))
                if out['action'] == 'touch':
                    if out['sensor'] == feeder.gpio_touchpad:
                        feeder.toggleLight('bowl',True)
                        self.updateText('{} pad touched. Next trial with start in {} seconds.'.format(feeder.side,timeBetweenIterations))
                        self.distributeReward(feeder.side,'F1')
                        feeder.toggleLight('bowl',False)
                self.updateText('Next forced iteration will start in {} seconds'.format(timeBetweenIterations))
                time.sleep(timeBetweenIterations)
                n+=1
        self.teardownParts()

    def startFeeders_forced_alternating(self):
        self.setupParts()
        trialLength = 240
        iterationLength = dataHelper.getConfigValue('Iteration Length')['value']
        timeBetweenIterations = dataHelper.getConfigValue('Time Between Iterations')['value']

        dataHelper.logEvent(self.trialId,'F2:Forced trial started')

        # randomize the order
        feeders = [self.feeder1,self.feeder2]
        random.shuffle(feeders)

        startTime = time.time()
        self.btnStartFeeders_forced1.config(state="disabled")
        self.btnStartFeeders_forced2.config(state="disabled")
        self.btnStartFeeders_choice.config(state="disabled")

        n = 0
        done = False
        while n < 4 and done == False:
            for feeder in feeders:
                if (time.time() - startTime) > trialLength:
                    self.updateText('Time is up')
                    self.sound_done.play()
                    done = True
                    return
                dataHelper.logEvent(self.trialId,'F2:Forced trial in progress -- {} is enabled'.format(feeder.side))
                feeder.toggleLight('touch',True)
                self.updateText('Forced trial in progress -- {} is enabled'.format(feeder.side))
                self.sound_start.play()

                out = self.touchSensor.listenForFirstTouch_specific(iterationLength,feeder.gpio_touchpad)
                feeder.toggleLight('touch',False)

                if out['action'] == 'timeout':
                    self.sound_timeout.play()
                    self.updateText('{} seconds passed without a selection. Next trial will start in {} seconds.'.format(iterationLength,timeBetweenIterations))
                if out['action'] == 'touch':
                    if out['sensor'] == feeder.gpio_touchpad:
                        feeder.toggleLight('bowl',True)
                        self.updateText('{} pad touched. Next trial with start in {} seconds.'.format(feeder.side,timeBetweenIterations))
                        self.distributeReward(feeder.side,'F2')
                        feeder.toggleLight('bowl',False)
                self.updateText('Next forced iteration will start in {} seconds'.format(timeBetweenIterations))
                time.sleep(timeBetweenIterations)
                n+=1
        self.teardownParts()

    def startFeeders_choice(self):
        self.setupParts()
        trialLength = dataHelper.getConfigValue('Trial Length')['value']
        iterationLength = dataHelper.getConfigValue('Iteration Length')['value']
        timeBetweenIterations = dataHelper.getConfigValue('Time Between Iterations')['value']

        dataHelper.logEvent(self.trialId,'C1:Trial started')

        startTime = time.time()
        self.btnStartFeeders_forced1.config(state="disabled")
        self.btnStartFeeders_forced2.config(state="disabled")
        self.btnStartFeeders_choice.config(state="disabled")
##        self.updateText('Start a trial at any time')

        done = False
        maxNumberOfChoices=10
        numOfChoices = 0
        while done == False:
            if (time.time() - startTime) > trialLength:
                self.updateText('Trial is done. Time is up')
                self.sound_done.play()
                done = True
                return
            if numOfChoices==maxNumberOfChoices:
                self.updateText('Trial is done. {} choices were made'.format(maxNumberOfChoices))
                self.sound_done.play()
                done = True
                return

            dataHelper.logEvent(self.trialId,'C1:Feeders enabled')
            self.feeder1.toggleLight('touch',True)
            self.feeder2.toggleLight('touch',True)
            self.updateText('Feeders enabled. Trial in progress')
            self.sound_start.play()
            out = self.touchSensor.listenForFirstTouch_any(iterationLength)
            self.feeder1.toggleLight('touch',False)
            self.feeder2.toggleLight('touch',False)
            if out['action'] == 'timeout':
                self.sound_timeout.play()
                self.updateText('{} seconds passed without a selection. Next trial will start in {} seconds.'.format(iterationLength,timeBetweenIterations))
            if out['action'] == 'touch':
                if out['sensor'] == 7:
                    self.feeder2.toggleLight('bowl',True)
                    self.updateText('Right pad touched. Next trial with start in {} seconds.'.format(iterationLength,timeBetweenIterations))
                    self.distributeReward('right','C1')
                    self.feeder2.toggleLight('bowl',False)
                if out['sensor'] == 10:
                    self.feeder1.toggleLight('bowl',True)
                    self.updateText('Left pad touched. Next trial with start in {} seconds.'.format(iterationLength,timeBetweenIterations))
                    self.distributeReward('left','C1')
                    self.feeder1.toggleLight('bowl',False)
            self.updateText('Next iteration will start in {} seconds'.format(timeBetweenIterations))
            time.sleep(timeBetweenIterations)
            numOfChoices+=1
        self.teardownParts()

    def updateText(self,newText):
        self.statusVar.set(newText)
        self.update()

    def quitTrial(self):
        self.controller.show_frame(screenStart)

    def distributeReward(self,sideSelected,trialType):

        dataHelper.logEvent(self.trialId,sideSelected+' side selected')
        self.sound_touched.play()
        if sideSelected == 'left':
            self.updateText('Left side selected. Reward will be distributed after a '+str(self.leftSideDelay)+' second delay.')
            time.sleep(self.leftSideDelay)
            dataHelper.logEvent(self.trialId,trialType+':Left reward distributed.')
            self.updateText('Left reward distriuted. Start another run at any time.')
            self.feeder1.dispense(self.leftSideQuantity)
        else:
            self.updateText('Right side selected. Reward will be distributed after a '+str(self.rightSideDelay)+' second delay.')
            time.sleep(self.rightSideDelay)
            dataHelper.logEvent(self.trialId,trialType+':Right reward distributed.')
            self.updateText('Right reward distriuted. Start another run at any time.')
            self.feeder2.dispense(self.rightSideQuantity)


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        if sys.platform.startswith('win') == False:
            rpiParts.cleanup()
        app.destroy()


app = selfControlApp()
app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()



