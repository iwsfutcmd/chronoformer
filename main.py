import json

sem_hbo = json.load(open("sem-hbo_Latn.json"))

def tokenize(string, tokens):
    tokens = sorted(tokens, key=len, reverse=True)

    output = []
    i = 0
    while i < len(string):
        match_found = False
        for token in tokens:
            if string[i:i+len(token)] == token:
                output.append(token)
                i += len(token)
                match_found = True
                break
        if not match_found:
            return None
    return tuple(output)

def transform_forward(string, rules):
    f_inv = rules["inventory"]["from"]
    t_inv = rules["inventory"]["to"]
    output = tokenize(string, f_inv)
    for rule in rules["rules"]:
        f = tokenize(rule["from"], f_inv)
        t = tokenize(rule["to"], t_inv)
        i = 0
        while i < len(output):
            if output[i:i + len(f)] == f:
                output = output[:i] + t + output[i + len(f):]
                i += len(t)
            else:
                i += 1
    return "".join(output)

def transform_backward(string, rules):
    outputs = set([string])
    for rule in rules["rules"]:
        f = rule["from"]
        t = rule["to"]
        new_outputs = {output.replace(t, f) for output in outputs}
        outputs |= new_outputs
    # i = 0
    # while i < len(string):
    #     found = False
    #     for rule in rules:
    #         f = rule["from"]
    #         t = rule["to"]
    #         if string[i : i + len(t)] == t:
    #             outputs.append("")
    #             output += t
    #             i += len(f)
    #             found = True
    #     if not found:
    #         output += string[i]
    #         i += 1
    return outputs


forward_testcases = [("pʕl", "pʕl"), ("ɣwθ", "ʕwʃ")]


def test_transform_forward():
    for i, o in forward_testcases:
        t = transform_forward(i, sem_hbo)
        print(f"{i} -> {t}")
        if o != t:
            raise ValueError(f"{i} -> should be ({o}), is ({t})")


backward_testcases = [
    (
        "ʕwʃ",
        {
            "ʕwʃ",
            "ʕwθ",
            "ɣwʃ",
            "ɣwθ",
        },
    )
]


def test_transform_backward():
    for i, o in backward_testcases:
        t = transform_backward(i, sem_hbo)
        print(f"{i} -> {t}")
        if o != t:
            raise ValueError(f"{i} -> should be ({o}), is ({t})")

tokenizer_testcases = [
    ("sʼpr", ["sʼ", "p", "r"]),
    ("sʼpʼr", None),
    ("sʼfr", None)
]

def test_tokenizer():
    for i, o in tokenizer_testcases:
        t = tokenize(i, sem_hbo["inventory"]["from"])
        if o != t:
            raise ValueError(f"{i} tokenized as {t}, should be {o}")
