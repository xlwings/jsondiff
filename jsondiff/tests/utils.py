def generate_random_string(rng):
    return ''.join(rng.choice('abcdefg098765$&.()[]{}\n') for _ in range(rng.randint(0, 6)))


def generate_random_json(rng, max_depth=4, sets=False, hashable=False):
    types = [None, bool, float, str]
    if max_depth > 1:
        types += [tuple]
        if not hashable:
            types += [list, dict]
            if sets:
                types += [set]
    ty = rng.choice(types)
    if ty is None:
        return None
    if ty is bool:
        return rng.randint(0, 1) == 1
    if ty is float:
        return round(rng.random(), 2)
    if ty is str:
        return generate_random_string(rng)
    if ty is list or ty is tuple:
        return ty(
            generate_random_json(rng, max_depth-1, sets=sets, hashable=hashable)
            for _ in range(rng.randint(0, 7))
        )
    if ty is set:
        return {
            generate_random_json(rng, max_depth-1, hashable=True)
            for _ in range(rng.randint(0, 7))
        }
    return {
        generate_random_string(rng): generate_random_json(rng, max_depth-1, sets=sets, hashable=hashable)
        for _ in range(5)
    }


def pertubate_string(s, rng):
    if rng.random() < 0.6:
        return s
    else:
        return generate_random_string(rng)


def perturbate_json(obj, rng, max_depth=4, sets=False, hashable=False):
    if rng.random() < 0.8:
        if type(obj) is dict:
            return {
                pertubate_string(k, rng): perturbate_json(v, rng, max_depth-1, sets=sets, hashable=hashable)
                for k, v in obj.items()
            }
        if type(obj) is set:
            return {
                perturbate_json(v, rng, max_depth-1, sets=sets, hashable=True)
                for v in obj
                if rng.random() < 0.9
            }
        if isinstance(obj, (tuple, list)):
            return type(obj)(
                perturbate_json(v, rng, max_depth-1, sets=sets, hashable=hashable)
                for v in obj
                if rng.random() < 0.9
            )
    if rng.random() > max_depth / 5.0:
        return type(obj)(obj) if obj is not None else None
    return generate_random_json(rng, max_depth, sets=sets, hashable=hashable)
