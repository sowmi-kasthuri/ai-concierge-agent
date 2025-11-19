import math
from agent.tools.notes_tool import list_notes
from agent.tools.tasks_tool import list_tasks

def _tokenize(text: str):
    """
    Splits text into lowercase words.
    Extremely simple tokenizer but enough for our local search.
    """
    return text.lower().split()

def _term_frequency(tokens):
    """
    Returns a dictionary:
    { word: count_in_document }
    """
    tf = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    return tf

def _inverse_document_frequency(all_docs):
    """
    Computes IDF for each word in the entire corpus.
    all_docs = list of token lists
    Returns a dict: { word: idf_value }
    """
    num_docs = len(all_docs)
    word_doc_count = {}

    # Count how many documents each word appears in
    for tokens in all_docs:
        unique_words = set(tokens)
        for w in unique_words:
            word_doc_count[w] = word_doc_count.get(w, 0) + 1

    idf = {}
    for w, count in word_doc_count.items():
        # Add 1 to denominator for safety to avoid division by zero
        idf[w] = math.log((num_docs + 1) / (count + 1)) + 1

    return idf

def _tfidf_vector(tokens, idf):
    """
    Creates a TF-IDF vector (dictionary) for a single document.
    tokens: list of words
    idf: global IDF dictionary
    Returns: { word: tfidf_value }
    """
    tf = _term_frequency(tokens)
    vector = {}

    for word, count in tf.items():
        vector[word] = count * idf.get(word, 0)

    return vector

def _cosine_similarity(vec1, vec2):
    """
    Computes cosine similarity between two TF-IDF vectors.
    Vectors are dicts {word: weight}.
    Returns a float between 0 and 1.
    """
    # Dot product
    dot = 0.0
    for word, weight in vec1.items():
        dot += weight * vec2.get(word, 0.0)

    # Magnitudes
    mag1 = math.sqrt(sum(w * w for w in vec1.values()))
    mag2 = math.sqrt(sum(w * w for w in vec2.values()))

    if mag1 == 0 or mag2 == 0:
        return 0.0

    return dot / (mag1 * mag2)

def search(query: str):
    """
    Performs TF-IDF search across notes and tasks.
    Returns sorted results with similarity scores.
    """

    # 1. Load documents (notes + tasks)
    notes = list_notes()
    tasks = list_tasks()

    documents = []
    doc_map = []  # to track what type and ID each document corresponds to

    # Notes
    for n in notes:
        documents.append(_tokenize(n["content"]))
        doc_map.append(("note", n["id"], n))

    # Tasks
    for t in tasks:
        documents.append(_tokenize(t["title"]))
        doc_map.append(("task", t["id"], t))

    # If no data, return empty
    if not documents:
        return []

    # 2. Compute IDF across all docs
    idf = _inverse_document_frequency(documents)

    # 3. TF-IDF vector for the query itself
    query_tokens = _tokenize(query)
    query_vec = _tfidf_vector(query_tokens, idf)

    # 4. Compute similarity for each document
    scored = []
    for tokens, meta in zip(documents, doc_map):
        doc_vec = _tfidf_vector(tokens, idf)
        sim = _cosine_similarity(query_vec, doc_vec)
        scored.append((sim, meta))

    # 5. Sort by similarity descending
    scored.sort(key=lambda x: x[0], reverse=True)

    # 6. Prepare readable results
    results = []
    for score, (dtype, id_, data) in scored:
        if score > 0:
            results.append({
                "type": dtype,
                "id": id_,
                "score": round(score, 4),
                "data": data
            })

    return results

