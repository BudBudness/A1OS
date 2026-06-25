def validate(task):
    if not task: return False
    if "rm -rf" in str(task): return False
    if len(str(task)) > 10000: return False
    return True
