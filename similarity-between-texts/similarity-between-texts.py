#-------------------------------------------------------------------------------
# Name:        Similarity between texts
# Purpose:     Use of text similarity to solve information needs (queries)
#
# Author:      Sergio Murillo
#
# Created:     30/09/2022
#-------------------------------------------------------------------------------

from textblob import TextBlob
import math

# Auxiliary list for stop words
stop_words = set()

class Check_results:
    """
    Data structure in which to store the data of the "cranqrel" file
    """
    def __init__(self, index, text, value):
        self.index = index
        self.text = text
        self.value = value

def find_best_text(query, texts, coefficient):
    """
    Returns the best text and its value for a query and a coefficient passed by
    parameter
    """
    if coefficient == "jaccard":
        return jaccard(query, texts)
    elif coefficient == "cosine":
        return cosine(query, texts)
    else:
        raise ModuleNotFoundError

def cosine(query, texts):
    """
    Cosine coefficient
    """
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
    """
    Jaccard coefficient
    """
    best_option = -1
    similar_text = None
    for text in texts:
        temp = interseccion(texts.get(text),query) / union(texts.get(text),query)
        if temp > best_option:
            best_option = temp
            similar_text = text
    return best_option, similar_text

def union(text1, text2):
    """
    Auxiliary method to make the union on two lists
    """
    result = set()
    for text in text1:
        result.add(text)
    for text in text2:
        result.add(text)
    return len(result)

def interseccion(text1, text2):
    """
    Auxiliary method to perform the intersection over two lists
    """
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

def load_relevancy_scale(filename):
    """
    Load the "cranqrel" file. Helps to evaluate the results obtained
    """
    result = []

    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.split(" ")
            one_relevancy = Check_results(line[0], line[1], line[2])
            result.append(one_relevancy)

    return result

def print_relevancy(size, total_size, coefficient):
    """
    Prints the results obtained with respect to the file "cranqrel"
    """
    prob = size / (total_size -1) * 100
    print("{0:.2f}".format(prob) + "% of the queries have a solution with a" +
        " relevance higher than 5.", size, "/", total_size-1, "documents for " +
        coefficient + " coefficient.")

def main():
    """
    Finds the most similar text for a set of queries
    """
    # Load the texts and queries
    texts = load_lines("cran-1400.txt")
    queries = load_lines("cran-queries.txt")

    # Load the stop words
    load_stop_words("stop-words.txt")

    # Load the cranqrel list to evaluate the results obtained later on.
    list_relevancy = load_relevancy_scale("cranqrel")

    # Get the bag of words of the texts and queries
    bow_texts = string_to_bag_of_words(texts)
    bow_queries = string_to_bag_of_words(queries)

    # Auxiliary variables for accessing dictionary positions and evaluating
    # results.
    counter = 1
    counter_cosine = 0
    counter_jaccard = 0

    # .txt where it saved the results with similarity and text obtained for each
    # query
    save_results = open("results.txt", "w")

    for q in bow_queries:
        text_result = "Query: " + q + " - " + queries.get(q) + "\n"
        save_results.write(text_result)

        # Query with cosine
        result = find_best_text(bow_queries.get(q), bow_texts, "cosine")
        text_result = "\t[COSINE] Similarity: " + str(result[0]) + "\n"
        text_result += "\t" + texts.get(result[1]) + "\n"
        save_results.write(text_result)

        best_value = 5
        for relevancy in list_relevancy:
            if int(relevancy.index) == counter:
                index = (str(result[1]))[1::]
                if (int(index)) == int(relevancy.text):
                    if int(relevancy.value) < best_value:
                        best_value = int(relevancy.value)

        if(best_value != 5):
            print("[COSINE] Query", q, "appears in similarity with", relevancy.text,
                "with a relevance of", best_value)
            counter_cosine += 1

        # Query with Jaccard
        result = find_best_text(bow_queries.get(q), bow_texts, "jaccard")
        text_result = "\t[JACCARD] Similarity: " + str(result[0]) + "\n"
        text_result += "\t" + texts.get(result[1]) + "\n"
        save_results.write(text_result)

        best_value = 5
        for relevancy in list_relevancy:
            if int(relevancy.index) == counter:
                index = (str(result[1]))[1::]
                if (int(index)) == int(relevancy.text):
                    if int(relevancy.value) < best_value:
                        best_value = int(relevancy.value)

        if(best_value != 5):
            print("[JACCARD] Query", q, "appears in similarity with", relevancy.text,
                "with a relevance of", best_value)
            counter_jaccard += 1

        counter += 1

    # Print the results of relevancy
    print_relevancy(counter_cosine, counter, "cosine")
    print_relevancy(counter_jaccard, counter, "jaccard")

if __name__ == '__main__':
    main()
