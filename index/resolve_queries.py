#-------------------------------------------------------------------------------
# Name:        Resolving queries with an index
# Purpose:     Once the index is created, it is used for quick resolution of a 
#              series of queries. For each query, the 10 most relevant texts are 
#              returned.
#
# Author:      Sergio Murillo
#
# Created:     27/10/2022
#-------------------------------------------------------------------------------

import pickle
import random
from textblob import TextBlob
import math

# Auxiliary dictionary for the index
index = {}
# Auxiliary dictionary to save the texts
saved_texts = {}
# Auxiliary dictionary for the queries
queries = {}

def resolve_query(terms):
    """
    Given a query, returns the texts with their relevance value
    """
    global index

    # Dictionary with the values of B for all candidates
    candidates_b, candidates_b2 = get_candidates(terms) 
    a, a2 = calculate_a(terms)
    results = {}
    
    for candidate in candidates_b:
        num = 0
        for term in terms:
            # If the query term is in the document we perform A * B
            try:
                num +=  a[term] * index.get(term).idf * index.get(term).documents[candidate].tf_idf
            # Else A * B will be 0
            except:
                num += 0
              
        results[candidate] = calculate_value(a2, candidates_b2[candidate], num)
    
    return results

def calculate_value(a2, b2, num):
    """
    Given a candidate calculates its relevance value
    """
    value = num / (a2 * b2)

    return value
    
def calculate_a(terms):
    """
    Given a series of terms calculate the value of A^2 and A for each term
    """
    global index
    a2 = 0
    a = {}
    for term in terms:
        if (index.get(term) != None):
            a2 += math.pow(index.get(term).idf * terms[term], 2)
            a[term] =  index.get(term).idf * terms[term]
    
    a2 = math.sqrt(a2)
    return a, a2
        
def get_candidates(terms):
    """
    Given a set of terms of a query, returns all possible texts that can be a 
    result with value of B and B^2
    """
    global index
    candidates_b = {}
    candidates_b2 = {}
    aux = {}

    for term in terms:
        if index.get(term) != None:
            for document in index.get(term).documents:
                if candidates_b.get(document) == None:
                    candidates_b[document] = index.get(term).documents[document].tf_idf
                    candidates_b2[document] = math.pow(index.get(term).documents[document].tf_idf,2)
                else:
                    candidates_b[document] += index.get(term).documents[document].tf_idf
                    candidates_b2[document] += math.pow(index.get(term).documents[document].tf_idf,2)
    
    for item in candidates_b2:
        candidates_b2[item] = math.sqrt(candidates_b2[item])
    
    return candidates_b, candidates_b2

def weighting_tf(texts):
    """
    Given a dictionary with the texts, returns a dictionary with the weights of
    each word in each text
    """
    counters = counter_terms(texts)
    tfs = relative_frequency(counters)
            
    return tfs

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

def load_index():
    """
    Loads the index from a .pkl file
    """
    global index 

    index = pickle.load(open("index.pkl", "rb"))

def load_queries(filename):
    """
    Reads the queries from a .txt file
    """
    global queries

    with open(filename, 'r') as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]

    for line in lines:
        separator = line.split('\t')
        result = ''
        for i in range(1, len(separator)):
            result += separator[i] + " "
        queries[separator[0]] = result

def load_texts(filename):
    """
    Given a .txt file store the contents of each of its lines
    """
    global saved_texts

    with open(filename, 'r') as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]

    for line in lines:
        separator = line.split('\t')
        saved_texts[separator[0].rstrip()] = separator[1]

def get_results(tfs):
    """
    Stores possibly relevant texts in a .txt file 
    """
    with open("result.txt", 'w') as file:
        for term in tfs:
            file.writelines("Query" + term + "\n")
            ids = resolve_query(tfs[term])
            ids = sorted(ids.items(), key=lambda x: x[1], reverse=True)
            for i in range(10):
                file.writelines(saved_texts[ids[i][0]][0:280] + "\n\n")
            file.writelines("\n")

def main():
    """
    Resolves the queries from a .txt file and saves the results in a .txt file
    """
    global queries
    global saved_texts

    load_index()
    load_queries("cran-queries.txt")
    load_texts("cran-1400.txt")
    tfs = weighting_tf(queries)     # Calculate the weights of each word in 
                                    # each text
    get_results(tfs)                # Get the results of the queries
            
    

if __name__ == '__main__':
    main()
