class Document_Info:
    """
    Data structure to store the data of a document
    """
    def __init__(self, tf, tf_idf):
        #self.reference = reference  # Reference of the document
        self.tf = tf                    # tf value of the document
        self.tf_idf = tf_idf          # tf * idf value
    
    def __str__(self):
        result = self.reference
        return result

class Index_Element:
    """
    Data structure to store the data of a element of the index
    """
    def __init__(self, idf, documents):
        self.idf = idf              # idf value of the word
        self.documents = documents  # List of documents in which the word appears

    def __str__(self):
        result = "idf: " + str(self.idf) + " Documents -> "
        for document in self.documents:
            result += str(document) + " "
        return result

