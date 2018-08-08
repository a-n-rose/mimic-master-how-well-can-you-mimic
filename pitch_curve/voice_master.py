 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 14 16:13:28 2018

@author: airos
"""

import glob
import os
import datetime
import matplotlib.pyplot as plt
import random
import numpy as np
import sounddevice as sd
import soundfile as sf
import pygame
import librosa



class Mimic_Game:
    def __init__(self):
        print(
                '''
                Welcome to the game: Mimic Master
                
                We will present to you sounds and you must try to sound as much like them as you can. 
                
                The better you are, the more points you collect.
                
                If you earn 1000 points, you will be titled
                MIMIC MASTER
                                
                '''
                )
        self.username = None
        self.cont_game = True
        self.points = 0


        
    def enter_username(self):
        username = input("Please enter your username: ")
        if username:
            return username
        else:
            self.enter_username()
    
    def get_date(self):
        time = datetime.datetime.now()
        time_str = "{}y{}m{}d{}h{}m{}s".format(time.year,time.month,time.day,time.hour,time.minute,time.second)
        return(time_str)
    
    def start_game(self,action,username = None):
        user_ready = input("Press ENTER to {} or type 'exit' to leave: ".format(action))
        if user_ready == '':
            if username:
                print("Great!")
                self.username = self.enter_username()
                return self.username
            else:
                return True
        elif 'exit' in user_ready.lower():
            return False
        else:
            self.start_game('start')
    
    def record_user(self,duration):
        duration = duration
        fs = 22050
        user_rec = sd.rec(int(duration*fs),samplerate=fs,channels=1)
        sd.wait()   
        return(user_rec)
    
    def check_rec(self,user_rec):
        '''
        Need to see if recording worked and meausre the amount of background noise
        '''
        if user_rec.any():
            return True
        return False
    
    def play_rec(self,recording):
        fs = 22050
        sd.play(recording, fs)
        sd.wait()
        return None
    
    def test_record(self,sec):
        '''
        The user will need to do a test record to analyze natural voice.
        Perhaps read a sentence aloud?
        '''

        user_rec = self.record_user(sec)

        if self.check_rec(user_rec):
            filename = './user_recordings/testrec_{}.wav'.format(self.username+'_'+self.get_date())
            self.noisefile = filename
            self.save_rec(filename,user_rec,fs=22050)
            return user_rec
        else:
            print(
                    '''
                    Hmmmmmm there seems to be a problem.
                    Is your mic connected and/or activated?
                    
                    Sorry for the inconvenience.
                    '''
                    )
        
        return None
    
    def test_mic(self,sec):
        user_rec = self.test_record(sec)
        sd.wait()
        if user_rec.any():
            sd.wait()
            print("Thanks!")
            #self.play_rec(user_rec)
            #sd.wait()
        else:    
            print("Hmmmmm.. something went wrong. Check your mic and try again.")
            if self.start_game('test your mic'):
                self.test_mic(sec)
            else:
                return False
     
    def rand_sound2mimic(self):
        os.chdir('./soundfiles/')
        try:
            sounds = [wave for wave in glob.glob('*.wav')]
            rand_ind = random.randint(0,len(sounds)-1)
            filename = sounds[rand_ind]
            pygame.init()
            rand_sound = pygame.mixer.Sound(filename)
            rand_sound.play()
            while pygame.mixer.get_busy():
                pass
            return(filename)
        except ValueError:
            print("Value Error!")
        finally:
            os.chdir('..')
        return None
        
    def play_go(self):
        go_sound = pygame.mixer.Sound('./soundfiles/231277__steel2008__race-start-ready-go.wav')
        go_sound.play()
        while pygame.mixer.get_busy():
            pass
        print("And... mimic!")
        return None
        
    def get_duration(self,wavefile):
        y, fs = librosa.load(wavefile)
        duration = len(y)/fs
        return(duration)
        
    def get_max_amp(self,wavefile):
        y, fs = librosa.load(wavefile)
        return(max(y))
        
    def match_amp(self,wavefile,max_amp):
        y, fs = librosa.load(wavefile)
        new_amplitude = y*(max_amp/max(y))
        self.save_rec(wavefile,new_amplitude,fs)
        return None
    
    def get_fingpr(self,filename):
        duration, fp_encoded = acoustid.fingerprint_file(filename)
        fingerprint, version = chromaprint.decode_fingerprint(fp_encoded)
        return(fingerprint)

    def save_rec(self,filename,rec,fs):
        sf.write(filename,rec,fs)
        return None
    
    def play_wav(self,filename):
        pygame.init()
        sound = pygame.mixer.Sound(filename)
        sound.play()
        while pygame.mixer.get_busy():
            pass
        return None
    
    def comp_fingpr(self,fingerprint1,fingerprint2):
        similarity = fuzz.ratio(fingerprint1,fingerprint2)
        return(similarity)
    
    def vis_fingpr(self,fingerprint):
        plt.figure()
        bitmap = np.transpose(np.array([[b=='1' for b in list('{:32b}'.format(i & 0xffffffff))]for i in fingerprint]))
        plt.imshow(bitmap)    
        return(None)
        
        
    def close_game(self):
        '''
        close and save anything that was open during the game
        '''
        pygame.quit()
