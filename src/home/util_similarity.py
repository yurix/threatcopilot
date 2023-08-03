from scipy.spatial import distance
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic

brown_ic = wordnet_ic.ic('ic-brown.dat')

separators_chars = [' ', '-','_']

def lin_similarity(name_a, name_b):
        synset_a = wn.synsets(name_a)
        synset_b = wn.synsets(name_b)
        if synset_a is None or synset_b is None or len(synset_a) == 0 or len(synset_b) == 0:
            return 0
        synset_a = synset_a[0]
        synset_b = synset_b[0]
        return synset_a.lin_similarity(synset_b, brown_ic)

def clean(name):
    for char in separators_chars:
        name = name.replace(char,'')
    return name

def split_compound_name(compound_name):
    compund_names = []
    actual_word = ''
    tam_string = len(compound_name)
    acron = True
    for i, char in enumerate(compound_name):
        if char.isupper():
            if i > 0 and i < tam_string - 1: 
                next_char = compound_name[i + 1]
                last_char = compound_name[i - 1]
                if next_char.isupper():                            
                    if last_char.islower() and actual_word:                      
                        compund_names.append(clean(actual_word))
                        actual_word = ''
                    if not acron and actual_word:
                        compund_names.append(clean(actual_word))
                        actual_word = ''
                    acron = True               
                elif not next_char in separators_chars and actual_word:
                    compund_names.append(clean(actual_word))
                    actual_word = ''
                    acron = False

            actual_word += char
        elif char in separators_chars:
            if actual_word:
                compund_names.append(clean(actual_word))
                actual_word = ''
            acron = False
        else:
            actual_word += char
    if actual_word:
        compund_names.append(clean(actual_word))
    return compund_names

def print_compound_name_array(composed_name_array):
    result = ''
    for part in composed_name_array: 
        result = result + " " + part
    return result[1:]

def compound_lin_similarity(name_a, name_b):
    a_array = split_compound_name(name_a)
    b_array = split_compound_name(name_b)

    a_len = len(a_array)      
    b_len = len(b_array)
    
    if b_len < a_len:
        temp_array = a_array
        temp_len = a_len
        a_array = b_array
        a_len = b_len
        b_array = temp_array
        b_len = temp_len

    msum = 0
    sim_max = 0 
    for a in a_array:
        max_sim = 0
        word_to_remove = ''
        for b in b_array:
            pair_similarity = lin_similarity(a,b)
            #print('['+a+ ','+b+'] = ' + str(pair_similarity))
            if (pair_similarity>max_sim):
                max_sim = pair_similarity
                word_to_remove = b
        
        msum = msum + max_sim
        #print ('msum = ' + str(msum))
        #print ('word to remove =' + word_to_remove)
        if word_to_remove in b_array: 
            b_array.remove(word_to_remove)
    
    max_len_a_or_b = a_len if a_len > b_len else b_len

    return msum / max_len_a_or_b


#print ( compound_lin_similarity('sensorID', 'getSensorID') )
