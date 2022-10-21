#-------------------------------------------------------------------------------
# Name:        Detection of quasi-duplicate documents
# Purpose:     Example of the use of simhasing for the detection of duplicate 
#              documents within a collection.
#
# Author:      Sergio Murillo
#
# Created:     14/10/2022
#-------------------------------------------------------------------------------

from textblob import TextBlob
from queue import PriorityQueue
import hashlib

# Auxiliary list for stop words
stop_words = set()
# Auxiliary list for expects duplicates
expected_duplicates = []
# Restrictive value (> 0)
restrictiveness = 4
# Text processing:
#   - Use "trigram" to calculate hashes on text trigrams
#   - Use "tokenization" to compute hashes on text tokens
processing = "tokenization"

def string_to_bag_of_words(text):
    """
    Given a list of texts returns a dictionary with the identifier of a text/
    query and the set of its terms with their frequency
    """
    global stop_words
    bow = {}

    for line in text:
        blob = TextBlob(text.get(line))
        tokens = blob.words
        aux = {}
        for token in tokens:
            # Apply the stemming to each of the tokens *Default: Porter Stemmer*
            token = token.stem()
            # Check that the token is not an empty word
            if token not in stop_words:
                if aux.get(token) == None:
                    aux[token] = 1
                else:
                    aux[token] += 1
        bow[line] = aux

    return bow

def string_to_trigrams(text):
    """
    Given a text returns a list with its trigrams
    """
    bot = {}
    for line in text:
        list_of_trigram = []
        # Divide the text of each line into words and convert them to lowercase.
        clean_line = text.get(line).lower().strip("\n").split(" ")
        # For each word in the line, create a list of trigrams
        for i in range(0, len(clean_line) - 3):
            trigram = clean_line[i] + clean_line[i + 1] + clean_line[i + 2]
            list_of_trigram.append(trigram)
        bot[line] = list_of_trigram
  
    return bot    

def load_stop_words(filename):
    """
    Loads a list of stop words from a .txt file. To be used auxiliary in the
    string_to_bag_of_words function
    """
    global stop_words

    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip("\n ")
            stop_words.add(line)

def load_lines(filename):
    """
    Given a .txt file returns a list with the contents of each of its lines
    """
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
    return d

def split_item_to_set(item):
    """
    Given the terms in a dictionary adds them to a set
    """
    result = set()
    for word in item:
        result.add(word)

    return result

def sim_hash(item, restrictiveness, processing):
    """
    Given a set, a restrictiveness and how to process the text, calculates its
    hash and returns it
    """
    if processing == "trigram":
        return sim_hash_trigram(item, restrictiveness)
    elif processing == "tokenization":
        return sim_hash_tokenization(item, restrictiveness)
    else:
        raise Exception("Invalid processing")
    
def sim_hash_trigram(item, restrictiveness):
    """
    Calculates the hash using the trigrams of a text
    """
    queue = PriorityQueue()
    for trigram in item:
        queue.put(hashlib.sha224(trigram.encode("utf-8")).hexdigest())
        simhash = 0
    for x in range(0, restrictiveness):
        simhash ^= int(queue.get(), base = 16)
    return simhash

def sim_hash_tokenization(item, restrictiveness):
    """
    Calculates the hash using the tokens of a text
    """
    result = split_item_to_set(item)
    queue = PriorityQueue()
    for x in result:
        queue.put(hashlib.sha224(x.encode("utf-8")).hexdigest())
        simhash = 0
    for x in range(0, restrictiveness):
        simhash ^= int(queue.get(), base = 16)
    return simhash

def check_results(compare_results):
    """
    Check the results I get with those expected in the file "articles_2500.truth"
    """
    global expected_duplicates
    global processing
    long = len(expected_duplicates)

    good_counter = 0
    bad_counter = 0
    for result in compare_results:
        if result in expected_duplicates:
            good_counter += 1
        else:
            bad_counter += 1
    print("{0:.2f}".format(good_counter  / long * 100) + "% effectiveness using", 
        processing, "with a restrictiveness of", restrictiveness)
    print("\t-", bad_counter, "more duplicates found than expected")
    print("\t-", long - good_counter, "less duplicates found than expected")

def load_results(filename):
    """
    Stores the expected results of the file "articles_2500.truth"
    """
    result = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            line = line.split(" ")
            first = line[0]
            second = line[1]
            first_n = int(first[1:])
            second_n = int(second[1:])
            if (first_n < second_n):
                result.append(first + " " + second)
            else:
                result.append(second + " " + first)
    return result

def save_results(results):
    """
    Saves the results in a file
    """
    with open("results.txt", 'w') as file:
        file.write("Duplicates found using " +
        processing + " with a restrictiveness of " + str(restrictiveness) + "\n")
        for result in results:
            file.write(result + "\n")

def main():
    """
    Find quasi-duplicate documents
    """
    global expected_duplicates
    global restrictiveness
    global processing
    # Load the documents
    texts = load_lines("articles_2500.train")

    # Load the expected duplicates
    expected_duplicates = load_results("articles_2500.truth")

    # Choose a way to process the texts (trigrams or tokenization).
    if(processing == "trigram"):
        # Get the trigrams of the documents
        terms = string_to_trigrams(texts)
    elif(processing == "tokenization"):
        # Load the stop words
        load_stop_words("stop-words.txt")
        # Get the bag of words of the documents
        terms = string_to_bag_of_words(texts)
    else:
        raise Exception("Invalid processing")

    # Dictionary in which we store duplicate texts
    repeated = {}
    compare_results = []
    for item in terms:
        actual_hash = (sim_hash(terms.get(item), restrictiveness, processing))
        # If the hash does not exist, a new entry is created with the current text
        if (repeated.get(actual_hash) == None):
            repeated[actual_hash] = item
        # If the hash exists, the entry is modified by adding the index of the
        # new text
        else:
            earlier = repeated[actual_hash]
            repeated[actual_hash] = str(earlier) + " " + str(item)

    # We go through the dictionary
    for key in repeated:
        result = repeated.get(key).split(" ")
        # If an entry has more than one result, it means that there are repeated
        # texts.
        if len(result) > 1:
            compare_results.append(repeated.get(key))
    
    save_results(compare_results)
    check_results(compare_results)

if __name__ == '__main__':
    main()
