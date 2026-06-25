def score(output):
    return min(len(str(output))/200,1.0)

def improve(output,score):
    if score < 0.5:
        return f"IMPROVED:{output}"
    return output
