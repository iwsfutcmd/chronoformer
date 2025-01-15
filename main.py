import json
import re

sem_hbo = open("sem-hbo_Latn.chrono")
sem_arb = json.load(open("sem-arb_Latn.json"))
sem_gez = open("sem-gez_Latn.chrono").read()

def parse_chrono(chrono):
    rules = {"inventory": {"from": [], "to": []}, "rules": []}
    entries = chrono.split(";")
    for entry in entries:
        if m := re.search(r"^\s*<\s*\{(.*)\}\s*$", entry):
            rules["inventory"]["from"] = re.split(r"\s+", m.group(1))
        elif m := re.search(r"^\s*>\s*\{(.*)\}\s*$", entry):
            rules["inventory"]["to"] = re.split(r"\s+", m.group(1))
        elif m := re.search(r"^\s*(.+?)\s*>\s*(.+?)\s*(?:/\s*(.+?)?_(.+?)?)?$", entry):
            rule = {"from": m.group(1), "to": m.group(2), "pre": m.group(3), "post": m.group(4)}
            rules["rules"].append(rule)
    return rules

def unparse_chrono(rules):
    chrono = ""
    chrono += "< {" + " ".join(rules["inventory"]["from"]) + "};\n"
    chrono += "> {" + " ".join(rules["inventory"]["to"]) + "};\n"
    for rule in rules["rules"]:
        chrono += rule["from"] + " > " + rule["to"]
        if rule["pre"] or rule["post"]:
            chrono += " / " + rule["pre"] or "" + "_" + rule["post"] or ""
        chrono += ";\n"
    return chrono

def make_inv(rules):
    from_inv = set()
    to_inv = set()
    for rule in rules["rules"]:
        from_inv.add(rule["from"])
        to_inv.add(rule["to"])
    rules["inventory"]["from"] = sorted(from_inv)
    rules["inventory"]["to"] = sorted(to_inv)


def tokenize(string, tokens):
    tokens = sorted(tokens + ["#"], key=len, reverse=True)

    output = []
    i = 0
    while i < len(string):
        match_found = False
        for token in tokens:
            if string[i : i + len(token)] == token:
                output.append(token)
                i += len(token)
                match_found = True
                break
        if not match_found:
            raise ValueError("string contains untokenizable elements")
    return tuple(output)


def transform_forward(string, rules):
    f_inv = rules["inventory"]["from"]
    t_inv = rules["inventory"]["to"]
    output = ("#", *tokenize(string, f_inv), "#")
    for rule in rules["rules"]:
        f = tokenize(rule["from"], f_inv)
        t = tokenize(rule["to"], t_inv)
        try:
            pre = tokenize(rule["pre"], t_inv)
        except KeyError:
            pre = ()
        try:
            post = tokenize(rule["post"], t_inv)
        except KeyError:
            post = ()
        i = 0
        while i < len(output):
            if i - len(pre) >= 0 and i + len(post) <= len(output) and output[i-len(pre):i+len(f)+len(post)] == pre + f + post:
                output = output[:i] + t + output[i+len(f):]
                i += len(t)
            else:
                i += 1
    output = output[1:-1]
    return "".join(output)


def transform_backward(string, rules, comprehensive=True):
    f_inv = rules["inventory"]["from"]
    t_inv = rules["inventory"]["to"]
    outputs = {tokenize(string, t_inv)}
    for rule in rules["rules"]:
        t = tokenize(rule["from"], f_inv)
        f = tokenize(rule["to"], t_inv)
        new_outputs = set()
        for output in outputs:
            i = 0
            while i < len(output):
                if output[i:i+len(f)] == f:
                    new_output = output[:i] + t + output[i+len(f):]
                    new_outputs.add(new_output)
                    i += len(t)
                else:
                    i += 1
        outputs.update(new_outputs)
    if comprehensive:
        outputs = {output for output in outputs if set(output) <= set(f_inv)}
    return {"".join(output) for output in outputs}


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


tokenizer_testcases = [("sʼpr", ("sʼ", "p", "r")), ("sʼpʼr", None), ("sʼfr", None)]


def test_tokenizer():
    for i, o in tokenizer_testcases:
        t = tokenize(i, sem_hbo["inventory"]["from"])
        if o != t:
            raise ValueError(f"{i} tokenized as {t}, should be {o}")
