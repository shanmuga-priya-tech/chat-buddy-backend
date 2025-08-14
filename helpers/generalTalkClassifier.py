def is_small_talk(query):
    small_talk_phrases = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "how are you",
        "how are you doing",
        "how is it going",
        "what's up",
        "whats up",
        "can you help me",
        "hi,can you help me",
        "hi,can u help me",
        "can u help me",
        "i need help",
        "help me",
        "help",
        "what can you do",
        "who are you",
        "tell me about yourself",
        "what do you do",
        "nice to meet you",
        "pleased to meet you",
        "good to see you",
        "thanks",
        "thank you",
        "ok",
        "okay",
        "alright"
    ]

    q = query.lower().strip()
    return q in small_talk_phrases

