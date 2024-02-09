import math
import os
import string
import nltk
import sys

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)
    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    dictionnary = {}
    files = os.listdir(directory)
    for file in files:
        path = os.path.join(directory, file)
        if os.path.isfile(path) and os.path.splitext(file)[1] == ".txt":
            with open(path, 'r', encoding="utf-8") as f:
                content = f.read()
                dictionnary[file] = content
    return dictionnary


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    all_words = []
    for word in nltk.word_tokenize(document):
        word = word.lower()
        if word not in nltk.corpus.stopwords.words("english") and word not in string.punctuation:
            all_words.append(word)
    all_words.sort()

    return all_words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    new_dictionary = {}
    all_words_list = set()
    for file in documents:
        all_words_list.update(documents[file])
    for word in all_words_list:
        for file in documents:
            if word in documents[file]:
                new_dictionary[word] = new_dictionary[word] + 1 if word in new_dictionary.keys() else 1
    for word in new_dictionary:
        new_dictionary[word] = math.log(len(documents.keys()) / new_dictionary[word])

    return new_dictionary


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    assert n <= len(files)
    words_tf_in_files = {file: {word: 0 for word in query if word in files[file]} for file in files}
    files_scores = {file: 0 for file in files}

    for file in files:
        for word in words_tf_in_files[file]:
            words_tf_in_files[file][word] = files[file].count(word)


    for file in files:
        for word in words_tf_in_files[file]:
            files_scores[file] += words_tf_in_files[file][word] * idfs[word]

    priority_files = list(files_scores.keys())
    priority_files.sort(key=lambda x: files_scores[x], reverse=True)

    same_cost_files = [s for s in priority_files if
                       files_scores[s] == files_scores[priority_files[0]]]
    if len(same_cost_files) > 1:
        same_cost_files.sort(key=lambda x: 1, reverse=True)
    priority_files = priority_files[:n]

    return priority_files


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    assert n <= len(sentences)
    sentences_scores = {sentence: 0 for sentence in sentences}
    sentence_query_density = {sentence: 0 for sentence in sentences}
    for sentence in sentences:
        for word in query:
            if word in sentences[sentence]:
                sentences_scores[sentence] += idfs[word]
                sentence_query_density[sentence] += 1

    priority_sentences = list(sentences_scores.keys())
    priority_sentences.sort(key=lambda x: sentences_scores[x], reverse=True)

    same_cost_sentences = [s for s in priority_sentences if
                           sentences_scores[s] == sentences_scores[priority_sentences[0]]]
    if len(same_cost_sentences) > 1:
        same_cost_sentences.sort(key=lambda x: sentence_query_density[x] / len(sentences[x]), reverse=True)

    priority_sentences = same_cost_sentences[:n]
    return priority_sentences


if __name__ == "__main__":
    main()
