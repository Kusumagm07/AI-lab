import re
from collections import namedtuple

# --- AST node types ---
Var = namedtuple('Var', ['name'])          # predicate or atomic formula string
Not = namedtuple('Not', ['child'])
And = namedtuple('And', ['left', 'right'])
Or  = namedtuple('Or',  ['left', 'right'])
ForAll = namedtuple('ForAll', ['var', 'body'])
Exists = namedtuple('Exists', ['var', 'body'])
Implies = namedtuple('Implies', ['left', 'right'])

# ---------- Lexer ----------
TOKEN_REGEX = re.compile(r'\s*(∀|∃|¬|->|→|&|\^|\||∨|∧|\(|\)|\[|\]|,|[A-Za-z_][A-Za-z0-9_]*|\S)')

def tokenize(s):
    tokens = [t for t in TOKEN_REGEX.findall(s) if t.strip() != '']
    # normalize implication symbol
    tokens = ['->' if t in ('→', '->') else t for t in tokens]
    # normalize and/or
    tokens = ['∧' if t in ('&','^','∧') else '∨' if t in ('|','∨') else t for t in tokens]
    return tokens

# ---------- Parser (very small, handles quantifiers, unary ¬, binary ∧ ∨ ->, and atoms with arguments) ----------
class Parser:
    def __init__(self, tokens):
        self.toks = tokens
        self.i = 0

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else None

    def eat(self, tok=None):
        cur = self.peek()
        if tok is None or cur == tok:
            self.i += 1
            return cur
        raise SyntaxError(f"Expected {tok} but found {cur}")

    def parse(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.peek() == '∨':
            self.eat('∨')
            right = self.parse_and()
            left = Or(left, right)
        return left

    def parse_and(self):
        left = self.parse_impl()
        while self.peek() == '∧':
            self.eat('∧')
            right = self.parse_impl()
            left = And(left, right)
        return left

    def parse_impl(self):
        left = self.parse_unary()
        if self.peek() == '->':
            self.eat('->')
            right = self.parse_impl()
            return Implies(left, right)
        return left

    def parse_unary(self):
        tok = self.peek()
        if tok == '¬':
            self.eat('¬')
            return Not(self.parse_unary())
        if tok == '∀':
            self.eat('∀')
            var = self.eat()   # variable name token
            body = self.parse_unary()
            return ForAll(var, body)
        if tok == '∃':
            self.eat('∃')
            var = self.eat()
            body = self.parse_unary()
            return Exists(var, body)
        if tok == '(' or tok == '[':
            openb = self.eat()
            node = self.parse()
            # accept ) or ]
            if self.peek() in (')',']'):
                self.eat()
            return node
        # atom or predicate possibly with args like P(x,y)
        return self.parse_atom()

    def parse_atom(self):
        tok = self.eat()
        # if next is '(' then parse args and treat whole as Var with text
        if self.peek() == '(':
            self.eat('(')
            args = []
            while True:
                arg = self.eat()  # we keep arg token as string
                args.append(arg)
                if self.peek() == ',':
                    self.eat(',')
                    continue
                break
            if self.peek() == ')':
                self.eat(')')
            atom_text = f"{tok}({','.join(args)})"
            return Var(atom_text)
        else:
            return Var(tok)

# ---------- AST to string ----------
def ast_to_str(node):
    if isinstance(node, Var):
        return node.name
    if isinstance(node, Not):
        return f"¬({ast_to_str(node.child)})"
    if isinstance(node, And):
        return f"({ast_to_str(node.left)} ∧ {ast_to_str(node.right)})"
    if isinstance(node, Or):
        return f"({ast_to_str(node.left)} ∨ {ast_to_str(node.right)})"
    if isinstance(node, ForAll):
        return f"∀{node.var} {ast_to_str(node.body)}"
    if isinstance(node, Exists):
        return f"∃{node.var} {ast_to_str(node.body)}"
    if isinstance(node, Implies):
        return f"({ast_to_str(node.left)} -> {ast_to_str(node.right)})"
    return str(node)

# ---------- Eliminate implications (AST) ----------
def elim_impl(node):
    if isinstance(node, Implies):
        # A -> B  ===  ¬A ∨ B
        return Or(Not(elim_impl(node.left)), elim_impl(node.right))
    if isinstance(node, Not):
        return Not(elim_impl(node.child))
    if isinstance(node, And):
        return And(elim_impl(node.left), elim_impl(node.right))
    if isinstance(node, Or):
        return Or(elim_impl(node.left), elim_impl(node.right))
    if isinstance(node, ForAll):
        return ForAll(node.var, elim_impl(node.body))
    if isinstance(node, Exists):
        return Exists(node.var, elim_impl(node.body))
    return node  # Var

# ---------- Push negations inward to NNF ----------
def to_nnf(node):
    """Return NNF form (negation only on atoms)"""
    if isinstance(node, Not):
        child = node.child
        # double negation
        if isinstance(child, Not):
            return to_nnf(child.child)
        # De Morgan for And/Or
        if isinstance(child, And):
            return Or(to_nnf(Not(child.left)), to_nnf(Not(child.right)))
        if isinstance(child, Or):
            return And(to_nnf(Not(child.left)), to_nnf(Not(child.right)))
        # quantifiers: push negation inside and flip quantifier
        if isinstance(child, ForAll):
            # ¬∀x P  === ∃x ¬P
            return Exists(child.var, to_nnf(Not(child.body)))
        if isinstance(child, Exists):
            # ¬∃x P  === ∀x ¬P
            return ForAll(child.var, to_nnf(Not(child.body)))
        # atom
        return Not(to_nnf(child))
    elif isinstance(node, And):
        return And(to_nnf(node.left), to_nnf(node.right))
    elif isinstance(node, Or):
        return Or(to_nnf(node.left), to_nnf(node.right))
    elif isinstance(node, ForAll):
        return ForAll(node.var, to_nnf(node.body))
    elif isinstance(node, Exists):
        return Exists(node.var, to_nnf(node.body))
    else:
        return node  # Var

# ---------- Simple replacements for later pipeline (stubs) ----------
def standardize_variables(expr_str):
    # naive: replace first y with y1, second with y2, x->x
    s = expr_str
    s = s.replace(' y)', ' y1)')  # small try, not robust
    return s

def skolemize_string(nnf_str):
    # naive: just replace '∃y' with 'f(x)' occurrences for demonstration
    s = nnf_str.replace('∃y1','').replace('∃y2','')
    s = s.replace('∃y','f(x)')
    return s

# ---------- Wrapper: full move_negations replacement ----------
def move_negations_inward_full(expr_str):
    tokens = tokenize(expr_str)
    parser = Parser(tokens)
    ast = parser.parse()
    # eliminate implications
    ast_no_impl = elim_impl(ast)
    # push negations inside
    nnf_ast = to_nnf(ast_no_impl)
    return ast_to_str(nnf_ast)

# ---------- Full pipeline (uses your earlier functions where appropriate) ----------
def fol_to_cnf_with_proper_nnf(expr):
    print("Original Expression:")
    print(expr)
    # Step: eliminate implications (string-level), but we parse+elim in AST inside move_negations_inward_full
    print("\nStep (AST): Move negations inward (NNF) and eliminate implications:")
    nnf_str = move_negations_inward_full(expr)
    print(nnf_str)

    # Next steps - naive string operations to illustrate:
    print("\nStep: (naive) Rename variables if needed (example):")
    renamed = nnf_str.replace('y', 'y1', 1).replace('y', 'y2', 1)
    print(renamed)

    print("\nStep: (naive) Skolemize (demonstration):")
    skolem = skolemize_string(renamed)
    print(skolem)

    print("\nStep: (naive) Drop universal quantifiers (if present):")
    dropped = skolem.replace('∀x ', '').replace('∀x','')
    print(dropped)

    print("\nFinal (naive) CNF-like string (note: distribution not applied here):")
    final = dropped
    print(final)
    return final

# ---------- Usage ----------
if __name__ == "__main__":
    print("Enter your FOL expression (use symbols: ∀, ∃, ¬, ∨, ∧, -> ), e.g.:")
    print("∀x[¬∀y¬(Animal(y)∨Loves(x,y))]∨[∃yLoves(y,x)]")
    s = input("Expression: ").strip()
    try:
        fol_to_cnf_with_proper_nnf(s)
    except Exception as e:
        print("Parsing / conversion error:", e)
        print("Make sure parentheses and tokens are spaced properly or use parentheses around predicates.")
