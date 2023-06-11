import os

def build_req():
    """
    return extra_requires dict
    """
    extra = {}
    all : set = set()
    for i in os.listdir("requirements"):
        if i.endswith(".txt"):
            with open("requirements/"+i) as f:
                extra[i[:-4]] = f.read().splitlines()
                all.update(extra[i[:-4]])
    
    extra["all"] = list(all)

    return extra