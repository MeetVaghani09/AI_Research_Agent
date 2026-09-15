EVALUATION_DATASET = [
    {
        "question": "How many years of experience does Omniscient have?",
        "expected_answer": "Omniscient has 19+ years of experience.",
        "retrieval_keywords": [
            "19+ years",
            "Treasury",
            "Cash Management",
        ],
        "should_find_document": True,
    },
    {
        "question": "What type of company is Omniscient?",
        "expected_answer": "Omniscient is a fintech company.",
        "retrieval_keywords": [
            "Fintech Company",
        ],
        "should_find_document": True,
    },
    {
        "question": "What domain does Omniscient have experience in?",
        "expected_answer": "Treasury and Cash Management.",
        "retrieval_keywords": [
            "Treasury",
            "Cash Management",
        ],
        "should_find_document": True,
    },
    {
        "question": (
            "What product helps banking and financial service providers "
            "connect with corporate customers?"
        ),
        "expected_answer": "Firestart.",
        "retrieval_keywords": [
            "Firestart",
        ],
        "should_find_document": True,
    },
    {
        "question": "Who is the CEO of Omniscient?",
        "expected_answer": (
            "The uploaded document does not provide this information."
        ),
        "retrieval_keywords": [],
        "should_find_document": False,
    },
    {
        "question": "What is the headquarters location of Omniscient?",
        "expected_answer": (
            "The uploaded document does not provide this information."
        ),
        "retrieval_keywords": [],
        "should_find_document": False,
    },
    {
        "question": "When was Omniscient founded?",
        "expected_answer": (
            "The uploaded document does not provide this information."
        ),
        "retrieval_keywords": [],
        "should_find_document": False,
    },
]