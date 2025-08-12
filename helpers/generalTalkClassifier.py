def is_small_talk(query):
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    casuals = ["can you help me", "how are you", "what can you do", "who are you"]
    q = query.lower().strip()
    return any(q.startswith(g) for g in greetings) or any(c in q for c in casuals)

