#ADDING CHECK TO MAKE SURE MIMIC CORRESPONDS TO ENERGY OF TARGET
#this is in hopes to identify completely wrong mimics that 
#happen to match better with the target than the background noise does



import numpy as np

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
