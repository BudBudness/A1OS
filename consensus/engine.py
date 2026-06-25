from collections import Counter

def consensus(results):
    votes=[r["node"] for r in results]
    return Counter(votes).most_common(1)[0][0] if votes else None
