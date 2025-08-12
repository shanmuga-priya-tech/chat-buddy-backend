def is_loan_related(query):
    keywords = ["loan","emi","interest","mortgage","principal","repayment","tenure","prepayment","disbursal","rate of interest","processing fee","foreclosure","home loan","car loan","personal loan","educational loan","paid","amount"]
    q = query.lower()
    return any(k in q for k in keywords)
