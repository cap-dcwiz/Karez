def sub_dict(dic, *keys, **renames):
    d1 = {k: v for k, v in dic.items() if k in keys}
    d2 = {renames[k]: v for k, v in dic.items() if k in renames.keys()}
    return d1 | d2
