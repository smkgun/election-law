
import argparse, pickle, numpy as np
import pandas as pd
from pathlib import Path

def load_artifacts(indir):
    with open(Path(indir)/"artifacts.pkl", "rb") as f:
        return pickle.load(f)

def tfidf_query(obj, query, topk=5):
    vec = obj["vectorizer"]
    nn = obj["nn"]
    qv = vec.transform([query])
    dists, idxs = nn.kneighbors(qv, n_neighbors=topk)
    idxs = idxs[0]; dists = dists[0]
    out = []
    for rank, (i,d) in enumerate(zip(idxs, dists), start=1):
        row = obj["rows"][i]
        out.append({"rank":rank,"score":1-float(d),"id":row.get("id",""),
                    "law":row.get("law",""),"article":row.get("article",""),
                    "penalty":row.get("penalty",""),"fact":row.get("fact","")[:140]})
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--indexdir", default="./index")
    args = ap.parse_args()
    obj = load_artifacts(args.indexdir)
    if obj["backend"]=="tfidf":
        res = tfidf_query(obj, args.query, args.topk)
    else:
        # cosine via matrix
        from sklearn.metrics.pairwise import cosine_similarity
        # NOTE: For openai/sbert branch, we didn't store vectorizer; use matrix
        # Not implemented here for brevity.
        raise SystemExit("Only tfidf demo implemented in search_demo.")
    for r in res:
        print(f"{r['rank']:>2}. {r['id']} | {r['law']} {r['article']} | score={r['score']:.3f}")
        print(f"    {r['fact']}...")

if __name__ == "__main__":
    main()
