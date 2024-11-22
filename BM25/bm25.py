import numpy as np
import math
from collections import Counter, defaultdict

class BM25:
    def __init__(self, documents, k1=1.5, b=0.75):
        self.documents = documents
        self.k1 = k1
        self.b = b
        self.avgdl = np.mean([len(doc) for doc in documents])
        
        # Initialize term frequencies, document frequencies, and document lengths
        self.term_freqs = []
        self.doc_lengths = np.array([len(doc) for doc in documents])
        self.document_freqs = defaultdict(int)

        for doc in documents:
            term_freq = Counter(doc)
            self.term_freqs.append(term_freq)
            for term in term_freq:
                self.document_freqs[term] += 1

        self.N = len(documents)
        self.idf_cache = {}

    def idf(self, term):
        """Calculate IDF for a term with caching to avoid recomputation."""
        if term not in self.idf_cache:
            doc_freq = self.document_freqs.get(term, 0)
            idf_value = math.log((self.N - doc_freq + 0.5) / (doc_freq + 0.5) + 1)
            self.idf_cache[term] = idf_value
        return self.idf_cache[term]

    def score(self, query, index):
        """Calculate the BM25 score for a specific document against a query."""
        doc_len = self.doc_lengths[index]
        score = 0.0
        term_freq = self.term_freqs[index]

        for term in query:
            if term in term_freq:
                f = term_freq[term]
                idf = self.idf(term)
                score += idf * (f * (self.k1 + 1)) / (f + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl))

        return score

    def rank(self, query):
        """Rank all documents against the query and return sorted scores."""
        scores = np.array([self.score(query, i) for i in range(self.N)])
        ranked_indices = np.argsort(scores)[::-1]  # Sort in descending order
        return ranked_indices, scores[ranked_indices]