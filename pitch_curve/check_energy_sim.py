#ADDING CHECK TO MAKE SURE MIMIC CORRESPONDS TO ENERGY OF TARGET
#this is in hopes to identify completely wrong mimics that 
#happen to match better with the target than the background noise does



import numpy as np

def collect_items_threshold(list_items,value,greater = True):
    if greater == True:
        list_items = [list_items[i] for i in range(len(list_items)) if list_items[i] > value]
    else:
        list_items = [list_items[i] for i in range(len(list_items)) if list_items[i] < value]
    return list_items

def find_peaks_valleys(energy_list1,energy_list2):
    '''
    find the peaks and valleys of energy in the signals
    Still have problem of how to say the two signals have similar patterns of peaks and valleys.
    
    Work in progress
    '''
    #threshold = 10%
    maxmin_perc = 10
    maxmin_perc *= 0.01
    
    #get max energy levels:
    max_l1 = np.max(energy_list1)
    max_l2 = np.max(energy_list2)
    
    #get min energy levels:
    min_l1 = np.min(energy_list1)
    min_l2 = np.min(energy_list2)
    
    diff_l1 = max_l1 - min_l1
    diff_l2 = max_l2 - min_l2
    
    top_l1 = diff_l1-(diff_l1*maxmin_perc)
    low_l1 = diff_l1*maxmin_perc
    top_l2 = diff_l2-(diff_l2*maxmin_perc)
    low_l2 = diff_l2*maxmin_perc
    
    #collect values above or below these values
    items_highl1 = collect_items_threshold(energy_list1,top_l1,greater=True)
    items_highl2 = collect_items_threshold(energy_list2,top_l2,greater=True)
    items_lowl1 = collect_items_threshold(energy_list1,low_l1,greater=False)
    items_lowl2 = collect_items_threshold(energy_list2,low_l2,greater=False)
    
    #check if numbers of 'peaks' and 'values' are approximately the same (+- 2):
    if len(items_highl2) == len(items_highl1) or len(items_highl2) == len(items_highl1)+1 or len(items_highl2) == len(items_highl1) +2 or len(items_highl2) == len(items_highl1)-1 or len(items_highl2) == len(items_highl1)-2:
        score = 1
    elif len(items_lowl2) == len(items_lowl1) or len(items_lowl2) == len(items_lowl1)+1 or len(items_lowl2) == len(items_lowl1) +2 or len(items_lowl2) == len(items_lowl1)-1 or len(items_lowl2) == len(items_lowl1)-2:
        score = 1
    else:
        score = 0
    print("items of high points in first energy array: {}".format(items_highl1))
    print("items of high points in second energy array: {}".format(items_highl2))
    print("items of low points in first energy array: {}".format(items_lowl1))
    print("items of low points in first energy array: {}".format(items_lowl2))
    return score


def check_energy(energy_list1,energy_list2):
    '''
    I will do this by dividing the mimic and target into four sections and see that the energy changes follow similar patterns
    
    Just tried this for fun real quick...
    
    Doesn't work at all.
    '''
    num_sections = 5
    mimic_len = len(energy_list1)
    mimic_steps = int(mimic_len/num_sections)
    target_len = len(energy_list2)
    target_steps = int(target_len/num_sections)
    
    mim_sections = []
    for i in range(num_sections):
        start = mimic_steps*i
        end = mimic_steps*i+mimic_steps
        mim_sect = sum(energy_list1[start:end])
        mim_sections.append(mim_sect)
    
    
    target_sections = []
    for i in range(num_sections):
        start = target_steps*i
        end = target_steps*i+target_steps
        targ_sect = sum(energy_list2[start:end])
        target_sections.append(targ_sect)
        
    mim_max = np.argmax(mim_sections)
    targ_max = np.argmax(target_sections)
    
    mimic_order = []
    for item in mim_sections:
        value = mim_sections[mim_max]/item
        if value == float("inf") or value == float("-inf"):
            value = 0
        else:
            value = int(value)
        mimic_order.append(value)
    
    target_order = []
    for item in target_sections:
        value = target_sections[targ_max]/item
        if value == float("inf") or value == float("-inf"):
            value = 0
        else:
            value = int(value)
        target_order.append(value)
        
                
    score = 1
        
    if len(np.unique(target_order)) == len(np.unique(target_order)) or len(np.unique(target_order)) == len(np.unique(target_order))+1 or len(np.unique(target_order)) == len(np.unique(target_order))-1:
        targ_min = np.argmax(target_order)
        mim_min = np.argmax(mimic_order)
        if targ_max == mim_max+1 or targ_max== abs(mim_max-1) or targ_max == mim_max or targ_min == mim_min or targ_min == abs(mim_min-1) or targ_min == mim_min+1: 
            print("Hmmmm did you try mimicking this sound or rather another sound?")
            score = 0
            print("targmax = {}".format(targ_max))
            print("mimmax = {}".format(mim_max))
            print("targmin = {}".format(targ_min))
            print("mimmin = {}".format(mim_min))
    print("Mimic energy levels: {}".format(mim_sections))
    print("Mimic order: {}".format(mimic_order))
    print("Target energy levels: {}".format(target_sections))
    print("Target order: {}".format(target_order))
    return score


