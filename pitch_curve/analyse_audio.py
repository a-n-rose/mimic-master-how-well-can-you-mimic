#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 16:14:17 2018

Goal: trying to mimic what Audacity does in noise reduction
https://wiki.audacityteam.org/wiki/
Using same FFT window size as Audacity: 2048
Which leads to 1025 frequency bands

Other research using fft to capture speech features have used 25ms windows w 10ms window shifts

#with scipy.signal.istft I am having issues maintaining 25ms windows w 10 ms shifts... for now leaving out NFFT = 2048, and using 50ms windows instead. COLA constraints have failed otherwise. Will continue working on that tho... in the future

@author: airos
"""

import numpy as np
import librosa
import datetime

interval = 0.01

def get_date():
    time = datetime.datetime.now()
    time_str = "{}y{}m{}d{}h{}m{}s".format(time.year,time.month,time.day,time.hour,time.minute,time.second)
    return(time_str)

def wave2stft(wavefile):
    y, sr = librosa.load(wavefile)
    if len(y)%2 != 0:
        y = y[:-1]
    stft = librosa.stft(y)
    stft = np.transpose(stft)
    return stft, y, sr

def wave2stft_long(wavefile):
    y, sr = librosa.load(wavefile)
    if len(y)%2 != 0:
        y = y[:-1]
    stft = librosa.stft(y,hop_length=int(interval*sr),n_fft=int(0.256*sr))
    stft = np.transpose(stft)
    return stft, y, sr

def stft2wave(stft,len_origsamp):
    sr=22050
    istft = np.transpose(stft.copy())
    samples = librosa.istft(istft,length=len_origsamp)
    return samples

def stft2power(stft_matrix):
    if stft_matrix is not None:
        if len(stft_matrix) > 0:
            stft = stft_matrix.copy()
            power = np.abs(stft)**2
            return power
        else:    
            raise TypeError("STFT Matrix is empty. Function 'stft2power' needs a non-empty matrix.")
    else:
        raise TypeError("STFT Matrix does not exist. Function 'stft2power' needs an existing matrix.")

def get_energy_rms(stft_matrix):
    #stft.shape[1] == bandwidths/frequencies
    #stft.shape[0] pertains to the time domain
    rms_list = [np.sqrt(sum(np.abs(stft_matrix[row])**2)/stft_matrix.shape[1]) for row in range(len(stft_matrix))]
    return rms_list

def get_energy_ms(stft_matrix):
    #stft.shape[0] pertains to the time domain
    energy_list = [sum(np.abs(stft_matrix[row])**2)/stft_matrix.shape[1] for row in range(len(stft_matrix))]
    return energy_list

def get_energy_mean(energy_list):
    mean = sum(energy_list)/len(energy_list)
    return mean

def get_power_mean(power):
    mean = sum(power)/len(power)
    return mean

def get_pitch_wave(wavefile):
    y, sr = librosa.load(wavefile)
    if len(y)%2 != 0:
        y = y[:-1]
    pitches,mag = librosa.piptrack(y=y,sr=sr)
    return pitches,mag

def get_pitch_samples(y,sr):
    pitches,mag = librosa.piptrack(y=y,sr=sr)
    return pitches,mag

def get_pitch_wave_long(wavefile):
    y,sr = librosa.load(wavefile)
    if len(y)%2 != 0:
        y = y[:-1]
    pitches,mag = librosa.piptrack(y=y,sr=sr,hop_length=int(interval*sr),n_fft=int(0.256*sr))
    return pitches,mag

def get_pitch_samples_long(y,sr):
    pitches,mag = librosa.piptrack(y=y,sr=sr,hop_length=int(interval*sr),n_fft=int(0.256*sr))
    return pitches,mag

def get_pitch_mean(matrix_pitches):
    p = matrix_pitches.copy()
    p_mean = [np.mean(p[:,time_unit]) for time_unit in range(p.shape[1])]
    p_mean = np.transpose(p_mean)
    #remove beginning and ending artifacts:
    start = int(len(p_mean)*0.07)
    end = len(p_mean)-start
    pmean = p_mean[int(len(p_mean)*0.07):end]
    return pmean
              
def pitch_sqrt(pitch_mean):
    psqrt = np.sqrt(pitch_mean)
    return psqrt
    
def get_mean_bandwidths(matrix_bandwidths):
    bw = matrix_bandwidths.copy()
    bw_mean = [np.mean(bw[:,bandwidth]) for bandwidth in range(bw.shape[1])]
    return bw_mean

def get_var_bandwidths(matrix_bandwidths):
    if len(matrix_bandwidths) > 0:
        bw = matrix_bandwidths.copy()
        bw_var = [np.var(bw[:,bandwidth]) for bandwidth in range(bw.shape[1])]
        return bw_var
    return None

def rednoise(noise_powerspec_mean,noise_powerspec_variance, speech_powerspec_row,speech_stft_row):
    npm = noise_powerspec_mean
    npv = noise_powerspec_variance
    spr = speech_powerspec_row
    stft_r = speech_stft_row.copy()
    for i in range(len(spr)):
        if spr[i] <= npm[i] + npv[i]:
            stft_r[i] = 1e-3
    return stft_r
    
    
def matchvol(target_powerspec, speech_powerspec, speech_stft):
    tmp = np.max(target_powerspec)
    smp = np.max(speech_powerspec)
    stft = speech_stft.copy()
    if smp > tmp:
        mag = tmp/smp
        stft *= mag
    return stft


def suspended_energy(speech_energy,row,speech_energy_mean,start):
    try:
        if start == True:
            if speech_energy[row+1] and speech_energy[row+2] and speech_energy[row+3] and speech_energy[row+4]> speech_energy_mean: #
                return True
        else:
            if speech_energy[row-1] and speech_energy[row-2] and speech_energy[row-3] and speech_energy[row-4]> speech_energy_mean: #
                return True
    except IndexError as ie:
        return False


def sound_index(speech_energy, speech_energy_mean,start = True,):
    if start == True:
        side = 1
        beg = 0
        end = len(speech_energy)
    else:
        side = -1
        beg = len(speech_energy)-1
        end = -1
    for row in range(beg,end,side):
        if speech_energy[row] > speech_energy_mean:
            if suspended_energy(speech_energy,row,speech_energy_mean,start=start):
                if start==True:
                    #to catch plosive sounds
                    while row >= 0:
                        row -= 1
                        row -= 1
                        if row < 0:
                            row = 0
                        break
                    return row,True
                else:
                    #to catch quiet consonant endings
                    while row <= len(speech_energy):
                        row += 1
                        row += 1
                        if row > len(speech_energy):
                            row = len(speech_energy)
                        break
                    return row,True
    else:
        print("No speech detected.")
    return beg,False

        
def savewave(filename,samples,sr):
    librosa.output.write_wav(filename,samples,sr)
    print("File has been saved")
