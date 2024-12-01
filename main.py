import json

sem_hbo = json.load(open("sem-hbo.json"))
# backwards_test_rules = json.load(open("backwards_test_ruleset.json"))
input_string = "abcdef"


def transform_forward(string, rules):
    output = string
    i = 0
    while i < len(output):
        found = False
        for rule in rules:
            f = rule["from"]
            t = rule["to"]
            if output[i : i + len(f)] == f:
                output = output[:i] + t + output[i + len(f) :]
                i += len(t)
                found = True
        if not found:
            i += 1
    return output


def transform_backward(string, rules):
    outputs = set([string])
    for rule in rules:
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


forward_testcases = [("pʕl", "פעל"), ("ɣwθ", "עושׁ")]


def test_transform_forward():
    for i, o in forward_testcases:
        t = transform_forward(i, sem_hbo)
        print(f"{i} -> {t}")
        if o != t:
            raise ValueError(f"{i} -> should be ({o}), is ({t})")


backward_testcases = [
    (
        "עושׁ",
        {
            "ʕwʃ",
            "ʕwθ",
            "ɣwʃ",
            "ɣwθ",
        },
    )
]


def test_transform_forward():
    for i, o in backward_testcases:
        t = transform_backward(i, sem_hbo)
        print(f"{i} -> {t}")
        if o != t:
            raise ValueError(f"{i} -> should be ({o}), is ({t})")
