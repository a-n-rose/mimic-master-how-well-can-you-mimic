import librosa
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment

from rednoise_fun_longwindow import rednoise, wave2stft, stft2power, get_mean_bandwidths, get_var_bandwidths, stft2wave, savewave, get_date, matchvol, get_pitch_wave,get_pitch_samples, get_pitch_mean, pitch_sqrt, sound_index, get_energy, get_energy_mean, wave2stft_long, get_pitch_wave_long, get_pitch_samples_long

def get_duration(start_index, end_index, len_samples,sr):
    start = start_index/len_samples
    start_time = (len_samples * start)/sr
    end = end_index/len_samples
    end_time = (len_samples*end)/sr
    return end_time-start_time
    
    
def wave2pitchmeansqrt(wavefile, target, noise):
    y_stft, y, sr = wave2stft(wavefile)
    y_power = stft2power(y_stft)
    y_energy = get_energy(y_stft)
    n_stft, ny, nsr = wave2stft(noise)
    n_power = stft2power(n_stft)
    n_energy = get_energy(n_stft)
    n_energy_mean = get_energy_mean(n_energy)

    t_stft, ty, tsr = wave2stft(target)
    t_power = stft2power(t_stft)
    t_energy = get_energy(t_stft)
    
    npow_mean = get_mean_bandwidths(n_power)
    #npow_mean = get_rms(n_power)
    npow_var = get_var_bandwidths(n_power)
    
    y_stftred = np.array([rednoise(npow_mean,npow_var,y_power[i],y_stft[i]) for i in range(y_stft.shape[0])])

    voice_start,voice = sound_index(y_energy,start=True,rms_mean_noise = n_energy_mean)
    if voice:
        #first save file before removing silence
        print("Index for when mimic starts: {}".format(voice_start))
        print("Sound start relative to length of signal: {}".format(voice_start/len(y_energy)))
        start = voice_start/len(y_energy)
        start_time = (len(y)*start)/sr
        print("Start time: {} sec".format(start_time))
        y_stftred = y_stftred[voice_start:]
        
        voice_end, voice = sound_index(y_energy,start=False,rms_mean_noise = n_energy_mean)
        print("Index for when mimic ends: {}".format(voice_end))
        print("Mimic end relative to length of signal: {}".format(voice_end/len(y_energy)))
        end = voice_end/len(y_energy)
        end_time = (len(y)*end)/sr
        print("End time: {} sec".format(end_time))
        
        print("Length of mimic: {} sec".format(end_time-start_time))
        mimic_len_ms = (end_time-start_time)*1000
        
    else:
        #handle no speech in recording, or too much background noise
        return None

    print('Now matching volume to target recording.')
    y_stftmatched = matchvol(t_power,y_power,y_stftred)
    
    #find start and end indices of sounds/speech:
    target_start,target = sound_index(t_energy,start=True,rms_mean_noise = None)
    target_end,target = sound_index(t_energy,start=False,rms_mean_noise = None)
    target_len = target_end - target_start
    #find start and end in milliseconds
    
    print("Index for when target sound starts: {}".format(target_start))
    print("Sound start relative to length of signal: {}".format(target_start/len(t_energy)))
    start = target_start/len(t_energy)
    start_time = (len(ty)*start)/sr
    print("Start time: {} sec".format(start_time))

    
    print("Index for when target sound ends: {}".format(target_end))
    print("Sound end relative to length of signal: {}".format(target_end/len(t_energy)))
    end = target_end/len(t_energy)
    end_time = (len(ty)*end)/sr
    print("End time: {} sec".format(end_time))
    
    print("Length of target sound: {} sec".format(end_time-start_time))
    target_len_ms = (end_time-start_time)*1000
    
    
    
    mimic_start,mimic = sound_index(y_energy,start=True,rms_mean_noise = n_energy_mean) 
    mimic_end, mimic = sound_index(y_energy,start=False,rms_mean_noise=n_energy_mean)
    mimic_len = mimic_end - mimic_start
    #mimic_end_match = mimic_start+target_len
    
    if mimic:
        date = get_date()
        
        t_stft_sound = t_stft[target_start:target_end]
        t_sound = stft2wave(t_stft_sound,len(ty))
        #only duration of sound present
        t_duration = get_duration(target_start,target_end,len(t_power),sr)
        #save file to check
        filename_targetsound = './processed_recordings/adjusted_targetsound_{}'.format(date)
        savewave(filename_targetsound+'.wav',t_sound,sr)
        
        #Clip the file (having issues w librosa)
        target_full = AudioSegment.from_wav("{}.wav".format(filename_targetsound))
        t_stop = t_duration*1000 #get into milliseconds
        target_slice = target_full[:target_len_ms]
        target_slice.export("{}_clipped.wav".format(filename_targetsound), format="WAV")
        
        t_sound_pitch,t_m = get_pitch_wave_long(filename_targetsound+'.wav')
        tp_mean = get_pitch_mean(t_sound_pitch)
        tpm_sqrt = pitch_sqrt(tp_mean)
        
        y_stft_mimic = y_stftmatched[mimic_start:mimic_end]
        y_mimic = stft2wave(y_stft_mimic,len(y))
        #only mimic preset

        filename_mimic = './processed_recordings/adjusted_mimic_{}'.format(date)
        savewave(filename_mimic+'.wav',y_mimic,sr)
        y_mimic_pitch,y_m = get_pitch_wave_long(filename_mimic+'.wav')
        m_duration = get_duration(mimic_start,mimic_end,len(y_power),sr)
        #clip mimic and save 
        mimic_full = AudioSegment.from_wav("{}.wav".format(filename_mimic))
        #m_stop = m_duration*1000 #get into milliseconds
        m_stop = mimic_end*1000
        mimic_slice = mimic_full[:mimic_len_ms]
        mimic_slice.export("{}_clipped.wav".format(filename_mimic), format="WAV")
        
        
        
        print("Target duration is: {}".format(t_duration))
        print("Target slice length is: {} ms".format(t_stop))
        print("Mimic duration is: {}".format(m_duration))
        print("Mimic slice length is: {} ms".format(m_stop))
        
        yp_mean = get_pitch_mean(y_mimic_pitch)
        ypm_sqrt = pitch_sqrt(yp_mean)
    
        
        n_pitch, n_m = get_pitch_wave_long(noise)
        np_mean = get_pitch_mean(n_pitch)
        npm_sqrt = pitch_sqrt(np_mean)
        
        #to get them on the same scale
        if np.max(tpm_sqrt) < np.max(ypm_sqrt):
            mag = np.max(tpm_sqrt)/np.max(ypm_sqrt)
            ypm_sqrt *= mag
        for index in range(len(npm_sqrt)):
            if npm_sqrt[index] > 0.0:
                npm_sqrt = npm_sqrt[index:]
                break
        return (ypm_sqrt, tpm_sqrt, npm_sqrt)
    else:
        print("No mimic found.")
        return None
    
def compare_sim(pitch_mean1, pitch_mean2):
    pm1 = pitch_mean1.copy()
    pm2 = pitch_mean2.copy()
    if len(pm1) != len(pm2):
        index_min = np.argmin([len(pm1),len(pm2)])
        if index_min > 0:
            pm1 = pm1[:len(pm2)]
        else:
            pm2 = pm2[:len(pm1)]
    corrmatrix = np.corrcoef(pm1,pm2)
    return(corrmatrix)


def get_score(mimic_sound,mimic_noise):
    mimic_sound = mimic_sound[0][1]
    mimic_noise = mimic_noise[0][1]
    score = mimic_sound - mimic_noise
    if np.isnan(score):
        pass
    else:
        score = int(score*100)
        return score
    return None

#def hermes_wc(pitch_list, sumpower):
    #if len(pitch_list) != 2:
        #print("2 pitch matrices are necessary to be compared.")
        #return None
    #coefficients = []
    #for i in range(len(sumpower)):
        #nom = sum(sumpower[i]*((pitch_list[0][i]-np.mean(pitch_list[0]))*(pitch_list[1][i]-np.mean(pitch_list[1]))))
        #den = np.sqrt(sum(sumpower[i]*((pitch_list[0][i]-np.mean(pitch_list[0]))**2))*sum(sumpower[i]*((pitch_list[1][i]-np.mean(pitch_list[1]))**2)))
        #coefficients.append(nom/den)
    #return coefficients
