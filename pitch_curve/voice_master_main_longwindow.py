#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 15 22:22:15 2018

@author: airos
"""
import numpy as np

from rednoise_run_longwindow import wave2pitchmeansqrt, compare_sim, get_score
from voice_master import Mimic_Game
import os

import logging
import logging.handlers
logger = logging.getLogger(__name__)

#import shutil


if __name__ == '__main__':
    try:
        
        #default format: severity:logger name:message
        #documentation: https://docs.python.org/3.6/library/logging.html#logrecord-attributes 
        log_formatterstr='%(levelname)s , %(asctime)s, "%(message)s", %(name)s , %(threadName)s'
        log_formatter = logging.Formatter(log_formatterstr)
        logging.root.setLevel(logging.DEBUG)
        #logging.basicConfig(format=log_formatterstr,
        #                    filename='/tmp/tradinglog.csv',
        #                    level=logging.INFO)
        #for logging infos:
        file_handler_info = logging.handlers.RotatingFileHandler('MM_loginfo.csv',
                                                                  mode='a',
                                                                  maxBytes=1.0 * 1e6,
                                                                  backupCount=200)
        #file_handler_debug = logging.FileHandler('/tmp/tradinglogdbugger.csv', mode='w')
        file_handler_info.setFormatter(log_formatter)
        file_handler_info.setLevel(logging.INFO)
        logging.root.addHandler(file_handler_info)
        
        
        #https://docs.python.org/3/library/logging.handlers.html
        #for logging errors:
        file_handler_error = logging.handlers.RotatingFileHandler('MM_logerror.csv', mode='a',
                                                                  maxBytes=1.0 * 1e6,
                                                                  backupCount=200)
        file_handler_error.setFormatter(log_formatter)
        file_handler_error.setLevel(logging.ERROR)
        logging.root.addHandler(file_handler_error)
        
        #for logging infos:
        file_handler_debug = logging.handlers.RotatingFileHandler('MM_logdbugger.csv',
                                                                  mode='a',
                                                                  maxBytes=2.0 * 1e6,
                                                                  backupCount=200)
        #file_handler_debug = logging.FileHandler('/tmp/tradinglogdbugger.csv', mode='w')
        file_handler_debug.setFormatter(log_formatter)
        file_handler_debug.setLevel(logging.DEBUG)
        logging.root.addHandler(file_handler_debug)


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
                        rep_mim = currgame.record_user(duration+3)

                        #save the recording
                        time_str = currgame.get_date()
                        usr_recfilename = directory_user+username+'_'+time_str+'.wav'
                        currgame.save_rec(usr_recfilename,rep_mim,fs=22050)
                        
                        #subtract noise, match target recording
                        # get and compare pitch means (sqrt)
                        #pitches = wave2pitchmeansqrt(usr_recfilename,mim_filename,currgame.noisefile)
                        
                        #if pitches:
                            #pitchsqrt_speech,pitchsqrt_target,pitchsqrt_noise = pitches[0],pitches[1],pitches[2]
                            ##compare similarities
                            #sp2noise = compare_sim(pitchsqrt_speech,pitchsqrt_noise)
                            #sp2target = compare_sim(pitchsqrt_speech,pitchsqrt_target)
                            
                            #score = get_score(sp2target,sp2noise)
                        
                            #if score and score > 0:
                                #print("Not bad! You earned {} points.".format(score))
                                #currgame.points += score
                            #else:
                                #print("You call that a mimic? No points earned. Try again!")
                        #else:
                            #print("No response detected. No points earned. Try again!")
                                
                        score = wave2pitchmeansqrt(usr_recfilename,mim_filename,currgame.noisefile)
                        if score and score > 0:
                            print("Not bad! You earned {} points.".format(score))
                            currgame.points += score
                        else:
                            print("You call that a mimic? No points earned. Try again!")

                        print("Total points earned: {}".format(currgame.points))
                    else:
                        print("Thanks for playing!")
                        currgame.points = max_points
                        currgame.close_game()
                if currgame.cont_game:
                    print("\nCongratulations!!! You're a MIMIC MASTER!!")
                currgame.cont_game = False
                currgame.close_game()
                #shutil.rmtree(directory_user)
    except Exception as e:
        print("Error occurred: {}".format(e))
        logging.exception("Error occurred: %s" % e)
