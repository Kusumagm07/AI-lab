import re
from collections import deque, namedtuple

# ---------------------------
# Utilities: parsing & types
# ---------------------------
Literal = namedtuple("Literal", ["pred", "args", "neg"])  # neg kept for possible extension

_VAR_RE = re.compile(r'^[a-z][a-zA-Z0-9_]*$')     # variable: starts with lowercase
_PRED_RE = re.compile(r'^([A-Za-z][A-Za-z0-9_]*)\((.*)\)$')

def is_variable(token):
    return bool(_VAR_RE.match(token))

def parse_literal(s):
    """Parse a predicate string like 'Loves(x,y)' into Literal(pred, [args])"""
    s = s.strip()
    m = _PRED_RE.match(s)
    if not m:
        raise ValueError(f"Bad literal format: {s}")
    pred = m.group(1)
    args = [a.strip() for a in m.group(2).split(',')] if m.group(2).strip() else []
    return Literal(pred=pred, args=args, neg=False)

def literal_to_str(lit):
    return f"{lit.pred}({', '.join(lit.args)})"

# ---------------------------
# Unification
# ---------------------------
def unify(x, y, theta=None):
    """Unify two terms (variables/constants or lists) with substitution theta."""
    if theta is None:
        theta = {}
    # if identical after applying theta
    x = substitute_term(x, theta)
    y = substitute_term(y, theta)

    # variable cases
    if isinstance(x, str) and is_variable(x):
        return unify_var(x, y, theta)
    if isinstance(y, str) and is_variable(y):
        return unify_var(y, x, theta)

    # compound (list) case
    if isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        for xi, yi in zip(x, y):
            theta = unify(xi, yi, theta)
            if theta is None:
                return None
        return theta

    # constants / atoms
    if x == y:
        return theta
    return None

def unify_var(var, x, theta):
    if var in theta:
        return unify(theta[var], x, theta)
    if isinstance(x, str) and x in theta:
        return unify(var, theta[x], theta)
    # occurs check: variable should not appear in x
    if occurs_check(var, x, theta):
        return None
    theta2 = dict(theta)
    theta2[var] = x
    return theta2

def occurs_check(var, x, theta):
    x = substitute_term(x, theta)
    if var == x:
        return True
    if isinstance(x, list):
        return any(occurs_check(var, xi, theta) for xi in x)
    return False

def substitute_term(term, theta):
    """Apply substitution theta to a term (str or list)."""
    if isinstance(term, list):
        return [substitute_term(t, theta) for t in term]
    if isinstance(term, str) and term in theta:
        return substitute_term(theta[term], theta)
    return term

def apply_substitution_literal(lit, theta):
    """Return a new Literal with substitution applied to args."""
    new_args = [str(substitute_term(arg, theta)) for arg in lit.args]
    return Literal(pred=lit.pred, args=new_args, neg=lit.neg)

# ---------------------------
# Rule representation
# ---------------------------
Rule = namedtuple("Rule", ["antecedents", "consequent"])  # antecedents: list of Literals, consequent: Literal

def parse_rule(s):
    """Parse a rule string like 'A(x) & B(x,y) -> C(x)' or a fact 'Fact(a)'"""
    s = s.strip()
    if "->" in s:
        left, right = s.split("->", 1)
        ants = [parse_literal(part) for part in re.split(r'\s*&\s*', left.strip()) if part.strip()]
        cons = parse_literal(right.strip())
        return Rule(antecedents=ants, consequent=cons)
    else:
        # treat as fact with zero antecedents rule
        lit = parse_literal(s)
        return Rule(antecedents=[], consequent=lit)

# ---------------------------
# Forward chaining algorithm
# ---------------------------
def forward_chain(rules, facts, query=None, verbose=True):
    """
    rules: list of Rule objects
    facts: list of Literal objects (ground facts)
    query: string such as 'Mortal(Marcus)' or None
    Returns (entailed_bool, derived_facts_set)
    """
    # store facts as strings for quick membership; but also keep Literal objects
    derived = set(literal_to_str(f) for f in facts)
    fact_objs = {literal_to_str(f): f for f in facts}

    agenda = deque(facts)  # facts to consider (Literal objects)
    new_inferred = True

    if verbose:
        print("Initial Facts:")
        for f in facts:
            print("  ", literal_to_str(f))
        print("---- rules ----")
        for r in rules:
            ants = " & ".join(literal_to_str(a) for a in r.antecedents) if r.antecedents else "TRUE"
            print(f"  {ants} -> {literal_to_str(r.consequent)}")
        print("---------------\n")

    while agenda:
        fact = agenda.popleft()
        if verbose:
            print("Processing fact:", literal_to_str(fact))
        # Try to apply each rule whose antecedents can be unified with known facts
        for rule in rules:
            # For rules with no antecedent (facts as rules), check if consequent already known
            if not rule.antecedents:
                cons_subst = {}
                # consequent may contain variables; but a fact-rule would normally be ground
                cons = apply_substitution_literal(rule.consequent, cons_subst)
                cons_str = literal_to_str(cons)
                if cons_str not in derived:
                    derived.add(cons_str)
                    fact_objs[cons_str] = cons
                    agenda.append(cons)
                    if verbose:
                        print("Inferred (from fact-rule):", cons_str)
                continue

            # For rules with antecedents, we attempt to find substitutions that make all antecedents true.
            # We perform a backtracking search over antecedents, building substitutions using unification
            def backtrack(idx, theta):
                if idx == len(rule.antecedents):
                    # all antecedents unified under theta => infer consequent
                    cons = apply_substitution_literal(rule.consequent, theta)
                    cons_str = literal_to_str(cons)
                    if cons_str not in derived:
                        derived.add(cons_str)
                        fact_objs[cons_str] = cons
                        agenda.append(cons)
                        if verbose:
                            ant_strs = [literal_to_str(apply_substitution_literal(a, theta)) for a in rule.antecedents]
                            print(f"Inferred: {cons_str}  from {', '.join(ant_strs)} using θ={theta}")
                    return

                antecedent = rule.antecedents[idx]
                # We need to try to unify this antecedent with any known fact (derived)
                for known_str, known_lit in list(fact_objs.items()):
                    if antecedent.pred != known_lit.pred or len(antecedent.args) != len(known_lit.args):
                        continue
                    # attempt to unify antecedent.args with known_lit.args under current theta
                    theta_try = unify(list(antecedent.args), list(known_lit.args), dict(theta))
                    if theta_try is not None:
                        backtrack(idx + 1, theta_try)

            # Start backtracking with current fact as a potential match for antecedents[0]
            # (We could try all known facts; backtrack function already does that by iterating fact_objs)
            backtrack(0, {})

        # optional early stopping if query found
        if query is not None and query in derived:
            if verbose:
                print("\nQuery found early:", query)
            return True, derived

    # finished
    entailed = (query in derived) if query is not None else None
    if verbose:
        print("\n--- Derivation complete ---")
        print(f"Total derived facts: {len(derived)}")
        for d in sorted(derived):
            print("  ", d)
        if query is not None:
            print("\nQuery:", query, "=>", "ENTAILLED" if entailed else "NOT ENTAILED")
    return entailed, derived

# ---------------------------
# Demo / Example usage
# ---------------------------
if __name__ == "__main__":
    # Example: Marcus / Pompeian problem
    fact_strs = [
        "Man(Marcus)",
        "Pompeian(Marcus)"
    ]
    rule_strs = [
        "Pompeian(x) -> Roman(x)",
        "Roman(x) -> Loyal(x)",
        "Man(x) -> Person(x)",
        "Person(x) -> Mortal(x)"
    ]

    facts = [parse_literal(s) for s in fact_strs]
    rules = [parse_rule(s) for s in rule_strs]

    query = "Mortal(Marcus)"
    entails, derived = forward_chain(rules, facts, query=query, verbose=True)
    # entails is True/False; derived is the set of derived fact strings

    # You can try custom inputs:
    # facts2 = [parse_literal("Cat(Tom)")]
    # rules2 = [parse_rule("Cat(x) -> Animal(x)"), parse_rule("Animal(x) -> Loves(x,Food)")]
    # forward_chain(rules2, facts2, query="Loves(Tom,Food)")
