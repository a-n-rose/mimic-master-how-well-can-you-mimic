'''
Runs game that plays target sound and records user mimicking the sound.

Analyses are conducted to first reduce noise, clip beginning and ending silences, and adjust volume to 'match' that of the target (needs some work tho... sometimes volume levels are brought down quite low)

Then pitch and power levels are used to compare similarity using long-term windows (256ms) at small window shifts (10ms). The values are compared using the Hermes weighted correlation coefficient (HWCC).

Scores are calculated by getting the difference between the HWCCs of the mimic and target and those of background noise and the target. If the mimic values are higher than the background noise, points are earned. 

Problems: 
Sometimes a random mimic can outperform background noise. That means that while they would get a higher score for actually mimicking the sound vs a random sound, they might still earn points for making random sounds. Therefore, the game relies on the good nature of the user in actually mimicking the sounds they should mimic. I'm working on ways to check if the user is actually trying to mimic the sound. 
'''
import os
import numpy as np

from mimic_master import Mimic_Game
from compare_signals import wave2pitchcompare

import logging.handlers
from my_logger import start_logging, get_date
logger = logging.getLogger(__name__)

#for logging:
script_purpose = 'mimic_master_game' #will name logfile 
current_filename = os.path.basename(__file__)
session_name = get_date() #make sure this session has a unique identifier - link to model name and logging information

if __name__ == '__main__':
    try:
        currgame = Mimic_Game()
        
        start_logging(script_purpose)
        logging.info("Running script: {}".format(current_filename))
        logging.info("Session: {}".format(session_name))
        
        username = currgame.start_game('start', username = True)
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
                        score = wave2pitchcompare(usr_recfilename,mim_filename,currgame.noisefile)
                        if score and score > 0:
                            print("Not bad! You earned {} points.".format(score))
                            currgame.points += score
                        else:
                            print("You call that a mimic? No points earned. Try again!")

                        print("Total points earned: {}".format(currgame.points))
                        logging.info("Sound to mimic: \n{}".format(mim_filename))
                        logging.info("User's mimic: \n{}".format(usr_recfilename))
                        logging.info("Score user earned: \n{}".format(score))
                        logging.info("Total points earned: \n{}".format(currgame.points))
                    else:
                        print("Thanks for playing!")
                        currgame.points = max_points
                        currgame.close_game()
                if currgame.cont_game:
                    print("\nCongratulations!!! You're a MIMIC MASTER!!")
                    logging.info("Congratulations!!! You're a MIMIC MASTER!!")
                currgame.cont_game = False
                #shutil.rmtree(directory_user)
    except TypeError as te:
        logging.error("TypeError: %s" % te)
    except Exception as e:
        logging.exception("Error occurred: %s" % e)
    finally: 
        if currgame:
            currgame.close_game()
