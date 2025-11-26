import itertools

# Logical implication
def implies(a, b):
    return (not a) or b

def truth_table():
    rows = list(itertools.product([False, True], repeat=3))

    print(f"{'P':^3}{'Q':^3}{'R':^3} | {'Q->P':^5}{'P->¬Q':^6}{'Q∨R':^5} | {'KB':^3} || {'R':^3}{'R->P':^6}{'Q->R':^6}")
    print("-"*65)

    kb_rows = []  # rows where KB is true

    for row in rows:
        P, Q, R = row

        expr1 = implies(Q, P)         # Q -> P
        expr2 = implies(P, not Q)     # P -> ¬Q
        expr3 = Q or R                # Q ∨ R
        KB = expr1 and expr2 and expr3

        # Queries
        query_R = R
        query_R_implies_P = implies(R, P)
        query_Q_implies_R = implies(Q, R)

        print(f"{int(P):^3}{int(Q):^3}{int(R):^3} | "
              f"{int(expr1):^5}{int(expr2):^6}{int(expr3):^5} | "
              f"{int(KB):^3} || "
              f"{int(query_R):^3}{int(query_R_implies_P):^6}{int(query_Q_implies_R):^6}")

        if KB:
            kb_rows.append((P, Q, R))

    return kb_rows


def check_entailments(kb_rows):
    def query_R(P, Q, R): return R
    def query_R_implies_P(P, Q, R): return implies(R, P)
    def query_Q_implies_R(P, Q, R): return implies(Q, R)

    def entails(query_func):
        return all(query_func(P, Q, R) for P, Q, R in kb_rows)

    print("\nEntailment Results:")
    print("KB ⊨ R:", "YES" if entails(query_R) else "NO")
    print("KB ⊨ (R → P):", "YES" if entails(query_R_implies_P) else "NO")
    print("KB ⊨ (Q → R):", "YES" if entails(query_Q_implies_R) else "NO")


if __name__ == "__main__":
    kb_rows = truth_table()
    check_entailments(kb_rows)
