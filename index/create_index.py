#-------------------------------------------------------------------------------
# Name:        Creation of an index for query resolution 
# Purpose:     Use of an index for the matching process between queries and 
#              documents. 
#
# Author:      Sergio Murillo
#
# Created:     24/10/2022
#-------------------------------------------------------------------------------

from index_structure import Index_Element
from index_structure import Document_Info
from textblob import TextBlob
import math
import pickle

# Auxiliary dictionary for the index
index = {}
# Auxiliary dictionary to save the texts
saved_texts = {}

def create_index(tfs):
    """
    Given a dictionary with the weights of each word in each text, creates the
    index and saves it in a .pkl file
    """
    counter_words = get_counter_words(tfs)
    fill_index(tfs, counter_words)
    calculate_fd_idf()
    #print_index()  # [OPTIONAL] Print the index
    save_index()

def save_index():
    """
    Saves the index in a .pkl file
    """
    pickle.dump(index, open("index.pkl", "wb"))

def print_index():
    """
    Prints the index
    """
    for term in index:
        print(term + " -> " + str(index.get(term)))

def calculate_fd_idf():
    """
    Calculates the tf-idf of each term in each text
    """
    for element in index:
        for term in index[element].documents:
            index[element].documents[term].tf_idf = index[element].documents[term].tf * index[element].idf

def fill_index(tfs, counter_words):
    """
    Given a dictionary with the weights of each word in each text and a dictionary
    with the counters of each word in each text, creates the index
    """
    global index
    
    for word in counter_words:
        aux = {}
        for text in tfs:
            if tfs[text].get(word) != None:
                aux[text] = (Document_Info(tfs[text].get(word), None))
        idf = math.log(len(tfs) / len(aux), 10)
        
        if (idf != 0):
            index[word] = Index_Element(idf, aux)
    

def get_counter_words(tfs):
    """
    Given a dictionary with the weights of each word in each text, returns a 
    dictionary with all words and number of occurrences 
    """
    words = {}
    for text in tfs:
        for word in tfs[text]:
            if words.get(word) == None:
                words[word] = 1
            else:
                words[word] += 1
    
    return words
                   
def relative_frequency(counters):
    """
    Given a dictionary with the counters of each word in each text, returns a
    dictionary with the relative frequency of each word in each text
    """
    tfs = {}
    for text in counters:
        aux = {}
        for word in counters[text]:
            aux[word] = counters[text][word] / len(counters[text])
        tfs[text] = aux
    return tfs

def counter_terms(texts):
    """
    Given a dictionary with the texts, returns a dictionary with the counters of
    each word in each text
    """
    counters = {}
    for text in texts:
        aux = {}
        blob = TextBlob(texts.get(text).lower())
        tokens = blob.words
        for token in tokens:
            # Apply the stemming to each of the tokens *Default: Porter Stemmer*
            token = token.stem()
            if aux.get(token) == None:
                    aux[token] = 1
            else:
                aux[token] += 1
        counters[text] = aux
    return counters

def weighting_tf(texts):
    """
    Given a dictionary with the texts, returns a dictionary with the weights of
    each word in each text
    """
    counters = counter_terms(texts)
    tfs = relative_frequency(counters)
            
    return tfs

def load_lines(filename):
    """
    Given a .txt file returns a list with the contents of each of its lines and
    saves the texts in a dictionary
    """
    global saved_texts

    with open(filename, 'r') as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]

    d = {}
    for line in lines:
        separator = line.split(' ')
        result = ''
        for i in range(1, len(separator)):
            result += separator[i] + " "
        d[separator[0]] = result
        to_save = line.split("\t")
        saved_texts[to_save[0]] = to_save[1]

    return d

def main():
    """
    Creates an index from a .txt file and saves it to a .pkl file
    """
    texts = load_lines("cran-1400.txt")  # Load the texts
    tfs = weighting_tf(texts)       # Calculate the weights of each word in 
                                    # each text
    create_index(tfs)          # Create the index

if __name__ == '__main__':
    main()
