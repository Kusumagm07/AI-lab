def unify(x, y, substitutions=None):
    if substitutions is None:
        substitutions = {}

    # If both are same, return current substitutions
    if x == y:
        return substitutions

    # If x is a variable
    elif is_variable(x):
        return unify_var(x, y, substitutions)

    # If y is a variable
    elif is_variable(y):
        return unify_var(y, x, substitutions)

    # If both are compound expressions (lists or tuples)
    elif isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)) and len(x) == len(y):
        for a, b in zip(x, y):
            substitutions = unify(a, b, substitutions)
            if substitutions is None:
                return None
        return substitutions

    # If cannot unify
    else:
        return None


def unify_var(var, x, substitutions):
    if var in substitutions:
        return unify(substitutions[var], x, substitutions)
    elif x in substitutions:
        return unify(var, substitutions[x], substitutions)
    elif occurs_check(var, x, substitutions):
        return None
    else:
        substitutions[var] = x
        return substitutions


def occurs_check(var, x, substitutions):
    if var == x:
        return True
    elif isinstance(x, (list, tuple)):
        return any(occurs_check(var, xi, substitutions) for xi in x)
    elif x in substitutions:
        return occurs_check(var, substitutions[x], substitutions)
    return False


def is_variable(term):
    # variable is a lowercase string
    return isinstance(term, str) and term[0].islower()


# -----------------------------------------------
# ✅ Example usage (you can replace with your own)
# -----------------------------------------------
x1 = ['P', 'f(x)', 'g(y)', 'y']
x2 = ['P', 'f(g(z))', 'g(f(a))', 'f(a)']

result = unify(x1, x2)
if result:
    print("Unification Successful! Substitutions:", result)
else:
    print("Unification Failed!")
