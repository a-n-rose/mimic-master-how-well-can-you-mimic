#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 15 22:22:15 2018

@author: airos
"""
import numpy as np

from process_speech import wave2fingerprint
from voice_master import Mimic_Game
import os

from my_logger import start_logging, get_date
logger = logging.getLogger(__name__)
#for logging:
script_purpose = 'trainLanguageClassifer' #will name logfile 
current_filename = os.path.basename(__file__)
session_name = get_date() #make sure this session has a unique identifier - link to model name and logging information

  

if __name__ == '__main__':
    try:
        start_logging(script_purpose)
        logging.info("Running script: {}".format(current_filename))
        logging.info("Session: {}".format(session_name))
        
        currgame = Mimic_Game()
        #username = currgame.start_game('start', username = True)
        username = 'Aislyn'
        currgame.username = username
        max_points = 1000
        directory_mim = './soundfiles/'
        directory_user = './user_recordings/'
        directory_processed_speech = './processed_recordings/'
        if not os.path.exists(directory_user):
            os.makedirs(directory_user)
        if not os.path.exists(directory_processed_speech):
            os.makedirs(directory_processed_speech)
        if not os.path.exists(directory_mim):
            print("No recordings found. Please create a directory called 'soundfiles' and save wavefiles of different sounds for your users to mimic.")
            currgame.cont_game = False
            currgame.close_game()
        if username:
            sec = 5
    #        print("\n\nDuring the next step, we need you stay as quiet as you can - we need to measure the background noise for {} seconds.\n\n".format(sec))

            print("\nThis next step will take just {} seconds\n".format(sec))
            test_mic = currgame.start_game('test your mic')
            if test_mic:
                print("Now recording. Please stay quiet as we measure the background noise.")
            mictest = currgame.test_mic(sec)
            if mictest == False:
                print("We couldn't test your mic..")
            while currgame.cont_game == True:
                while currgame.points < max_points:
                    currgame.cont_game = currgame.start_game('listen to a sound')
                    if currgame.cont_game:
                        print("After the sound plays, you will be signaled when to start your mimic. Ready?")
                        mim_filename = directory_mim+currgame.rand_sound2mimic()
                        duration = currgame.get_duration(mim_filename)
                        #max_amp = currgame.get_max_amp(mim_filename)
                        currgame.play_go()
                        #extend duration to allow for user delay
                        rep_mim = currgame.record_user(duration+1)

                        #save the recording
                        time_str = currgame.get_date()
                        usr_recfilename = directory_user+username+'_'+time_str+'.wav'
                        currgame.save_rec(usr_recfilename,rep_mim,fs=22050)
                        
                        #subtract noise, remove silence
                        
                        
                        fingerprint_similarity = wave2fingerprint(usr_recfilename,mim_filename,currgame.noisefile)
                        
                        
                        if fingerprint_similarity:
                            
                            score = fingerprint_similarity
                        
                            if score > 0:
                                print("Not bad! You earned {} points.".format(score))
                                currgame.points += score
                            else:
                                print("You call that a mimic? No points earned. Try again!")
                                
                        else:
                            print("Hmmmm... something funny happened. Can you try another mimic?")
                        print("Total points earned: {}".format(currgame.points))
                    else:
                        print("Thanks for playing!")
                        currgame.points = max_points
                        currgame.close_game()
                if currgame.cont_game:
                    print("\nCongratulations!!! You're a MIMIC MASTER!!")
                currgame.cont_game = False
                currgame.close_game()
    except Exception as e:
        print(e)
