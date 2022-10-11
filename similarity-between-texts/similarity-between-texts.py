#-------------------------------------------------------------------------------
# Name:        Similarity between texts
# Purpose:
#
# Author:      Sergio Murillo
#
# Created:     30/09/2022
#-------------------------------------------------------------------------------

from textblob import TextBlob
import math

# Auxiliary list for stop words
stop_words = set()

def find_best_text(query, texts, coefficient):
    if coefficient == "jaccard":
        return jaccard(query, texts)
    elif coefficient == "cosine":
        return cosine(query, texts)
    else:
        raise ModuleNotFoundError

def cosine(query, texts):
    best_option = -1
    similar_text = None
    for text in texts:
        len1 = len(texts.get(text))
        len2 = len(query)
        temp = interseccion(texts.get(text),query) / math.sqrt(len1 * len2)
        if temp > best_option:
            best_option = temp
            similar_text = text
    return best_option, similar_text

def jaccard(query, texts):
    best_option = -1
    similar_text = None
    for text in texts:
        temp = len(query.items() & texts.get(text).items()) / len(query.items() | texts.get(text).items())
        #temp = interseccion(texts.get(text),query) / union(texts.get(text),query)
        if temp > best_option:
            best_option = temp
            similar_text = text
    return best_option, similar_text

def union(text1, text2):
    result = set()
    for text in text1:
        result.add(text)
    for text in text2:
        result.add(text)
    return len(result)

def interseccion(text1, text2):
    count = 0
    if len(text1) > len(text2):
        for text in text2:
            if text in text1:
                count += 1
    else :
        for text in text2:
            if text in text1:
                count += 1
    return count

def string_to_bag_of_words(text):
    """
    Given a list of texts returns a dictionary with the identifier of a text/
    query and the set of its terms with their frequency
    """
    global stop_words
    bow = {}

    for line in text:
        #result = str(line).split('\t')
        #key = result[0].rstrip()
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

def load_lines(filename):
    """
    Given a .txt file returns a list with the contents of each of its lines
    """
    with open(filename, 'r') as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]

    d = {}
    for line in lines:
        separator = line.split('\t')
        d[separator[0]] = separator[1]

    return d

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

def main():
    """
    Finds the most similar text for a set of queries
    """
    # Load the texts and queries
    texts = load_lines("cran-1400.txt")
    queries = load_lines("cran-queries.txt")

    # Load the stop words
    load_stop_words("stop-words.txt")

    # Get the bag of words of the texts and queries
    bow_texts = string_to_bag_of_words(texts)
    bow_queries = string_to_bag_of_words(queries)
    print(bow_texts)

    counter = 1
    for q in bow_queries:
        result = find_best_text(bow_queries.get(q), bow_texts, "jaccard")
        print(result[1])

        result = find_best_text(bow_queries.get(q), bow_texts, "cosine")
        print(counter, result[1])
        counter += 1

if __name__ == '__main__':
    main()
