'''
Purpose of this script is to apply and compare equations examining prosody/pitch similarity from the following paper:

https://perso.limsi.fr/mareuil/publi/IS110831.pdf

Note: the pitch and power levels were calculated at each millisecond
'''



import numpy as np
import pandas as pd
import librosa
import time



def wave2stft(wavefile):
    print(wavefile)
    interval = 0.01
    start = time.time()
    y, sr = librosa.load(wavefile)
    if len(y)%2 != 0:
        y = y[:-1]
    stft = librosa.stft(y,hop_length=int(interval*sr))
    stft = np.transpose(stft)
    duration = time.time() - start
    print("Duration of STFT calculation with {} ms intervals: {} seconds".format(interval*1000,duration))
    return stft, y, sr

def stft2power(stft_matrix):
    stft = stft_matrix.copy()
    power = np.abs(stft)**2
    return(power)

def get_pitch2(y,sr):
    interval = 0.01
    start = time.time()
    pitches,mag = librosa.piptrack(y=y,sr=sr,hop_length=int(interval*sr))
    duration = time.time()-start
    print("Duration of pitch calculation with {} ms intervals: {} seconds".format(interval*1000,duration))
    return pitches,mag

def match_len(matrix_list):
    matrix_lengths = [len(matrix) for matrix in matrix_list]
    min_index = np.argmin(matrix_lengths)
    newlen = matrix_lengths[min_index]
    matched_matrix_list = []
    for item in matrix_list:
        item = item[:newlen]
        matched_matrix_list.append(item)
    return matched_matrix_list

def get_zscores(matrix):
    mean = np.mean(matrix)
    std = np.std(matrix)
    zscores = [(i-mean)/std for i in range(len(matrix))]
    return zscores

def long_term_info(y,sr):
    interval = 0.01
    window = 0.256
    start_stft = time.time()
    stft = librosa.stft(y,hop_length=int(interval*sr),n_fft=int(window*sr))
    end_stft = time.time()
    stft = np.transpose(stft)
    power = np.abs(stft)**2
    start_pitch = time.time()
    pitch, mag = librosa.piptrack(y=y,sr=sr,hop_length=int(interval*sr),n_fft=int(window*sr))
    end_pitch = time.time()
    duration_stft = end_stft - start_stft
    duration_pitch = end_pitch - start_pitch
    pitch = np.transpose(pitch)
    print("Duration of STFT calculation with {} ms intervals and {} ms windows: {} seconds".format(interval*1000,window*1000,duration_stft))
    print("Duration of pitch calculation with {} ms intervals and {} ms windows: {} seconds".format(interval*1000,window*1000,duration_pitch))
    return stft,power,pitch

def hermes_wc(pitch_list, sumpower):
    if len(pitch_list) != 2:
        print("2 pitch matrices are necessary to be compared.")
        return None
    coefficients = []
    for i in range(len(sumpower)):
        nom = sum(sumpower[i]*((pitch_list[0][i]-np.mean(pitch_list[0]))*(pitch_list[1][i]-np.mean(pitch_list[1]))))
        den = np.sqrt(sum(sumpower[i]*((pitch_list[0][i]-np.mean(pitch_list[0]))**2))*sum(sumpower[i]*((pitch_list[1][i]-np.mean(pitch_list[1]))**2)))
        coefficients.append(nom/den)
    return coefficients

mimic = './processed_recordings/cat_mimic.wav'
animal_sound = './soundfiles/beg_silence_removed/newstart_Cat_Meow_2-Cat_Stevens-2034822903.wav'
random = './processed_recordings/rooster_mimic_finalized.wav'


#get power and pitch of signals every millisecond

#compare first cat and cat mimic
mstft,m,sr = wave2stft(mimic)
mp,mmag = get_pitch2(m,sr)
mpitch = np.transpose(mp)
mpower = stft2power(mstft)

astft,a,sr = wave2stft(animal_sound)
print(animal_sound)
ap,amag = get_pitch2(a,sr)
apitch = np.transpose(ap)
apower = stft2power(astft)

pitch_list1 = match_len([mpitch,apitch])
power_list1 = match_len([mpower,apower])
sumpower1 = list(map(sum, power_list1))



#compare cat and rooster mimic (the first should result in a better score)
rstft,r,sr = wave2stft(random)
rp,rmag = get_pitch2(r,sr)
rpitch = np.transpose(rp)
rpower = stft2power(rstft)

pitch_list2 = match_len([rpitch,apitch])
power_list2 = match_len([rpower,apower])
sumpower2 = list(map(sum, power_list2))





#Hermes weighted correlation

#weight is the signal power of the signals: the sum of their signal powers

# nominator 
# sum of (weight(i)*((pitch of word 1(i) - mean of pitch of word 1)*(pitch of word 2(i) - mean of pitch of word 2)))



#comparing cat and cat mimic:
coefficients1 = hermes_wc(pitch_list1,sumpower1)
#comparing cat and rooster mimic
coefficients2 = hermes_wc(pitch_list2,sumpower2)





#Dynamic Time Warped 

#LOCAL VALUES
#prosody vector for each measurement:
#1)pitch, 2) power, 3) pitch z-score, 4) power z-score
mpitch_zscore = get_zscores(mpitch)
mpower_zscore = get_zscores(mpower)
apitch_zscore = get_zscores(apitch)
apower_zscore = get_zscores(apower)
#mprosody = [mpitch,mpower,mpitch_zscore,mpower_zscore]
#aprosody = [apitch,apower,apitch_zscore,apower_zscore]

#LONG-TERM INFORMATION
#256 ms window around each millisecond 
#1)pitch slope 2) kurtosis, 3) skewness 4) standard deviation, 5) mean, 6) 1st & 9th deciles

#I'm going to do a variation of this perhaps...
#first compare the difference of using local vs long-term information
mstft_long,mpower_long,mpitch_long = long_term_info(m,sr)
print(animal_sound)
astft_long,apower_long,apitch_long = long_term_info(a,sr)

powerlist_long = match_len([mpower_long,apower_long])
pitchlist_long = match_len([mpitch_long,apitch_long])

sumpower_long = list(map(sum, powerlist_long))

coefficients_long = hermes_wc(pitchlist_long,sumpower_long)


#compare with random mimic
rstft_long, rpower_long, rpitch_long = long_term_info(r,sr)
powerlist_long2 = match_len([rpower_long,apower_long])
pitchlist_long2 = match_len([rpitch_long,apitch_long])
sumpower_long2 = list(map(sum,powerlist_long2))
coefficients_long2 = hermes_wc(pitchlist_long2,sumpower_long2)

#scores:
print("Similarity score for the matched mimic: {}".format(sum(coefficients1)))
print("Similarity score for the random mimic: {}".format(sum(coefficients2)))
print("Similarity score for the matched mimic over longer intervals: {}".format(sum(coefficients_long)))
print("Similarity score for the random mimic over longer intervals: {}".format(sum(coefficients_long2)))



