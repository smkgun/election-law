# search_tfidf.py
from pathlib import Path
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

class TfidfSearcher:
    def __init__(self, index_dir: str = "./index"):
        with open(Path(index_dir) / "artifacts.pkl", "rb") as f:
            obj = pickle.load(f)
        if obj.get("backend") != "tfidf":
            raise ValueError("This helper supports only TF-IDF backend.")
        self.vec: TfidfVectorizer = obj["vectorizer"]
        self.nn: NearestNeighbors = obj["nn"]
        self.rows = obj["rows"]

    def query(self, text: str, topk: int = 10):
        qv = self.vec.transform([text])
        dists, idxs = self.nn.kneighbors(qv, n_neighbors=topk)
        out = []
        for rank, (i, d) in enumerate(zip(idxs[0], dists[0]), start=1):
            row = self.rows[i]
            out.append({
                "rank": rank,
                "score": round(1 - float(d), 3),
                "id": row.get("id", ""),
                "law": row.get("law", ""),
                "article": row.get("article", ""),
                "penalty": row.get("penalty", ""),
                "fact": (row.get("fact", "") or "")[:180],
                "source_url": row.get("source_url", ""),
            })
        return out
