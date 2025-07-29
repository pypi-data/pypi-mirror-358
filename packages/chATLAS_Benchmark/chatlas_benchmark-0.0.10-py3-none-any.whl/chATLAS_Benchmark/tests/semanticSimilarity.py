"""A script to perform a semantic similarity test on the RAGs answer compared
to the benchmark answer.

Currently just tests the semantic similarity between generated answer and test answer, could also run for similarity
between returned docs and test answer

Performs a cosine similarity between the generated vectors made using a sentence transformer model.

NOTE: This test does not check factual accuracy so need to use a different metric to check facts and figures of the
question.
"""

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

score_metric = pd.DataFrame(
    columns=[
        "answerSimilarity_score",  # Mean semantic similarity score across all generated answers
        "answerSimilarity_score_by_question",  # List Mean answerSimilarity score for each answer
    ]
)


def calculate_semantic_similarity_score(data: dict) -> pd.DataFrame:
    """Calculate semantic similarity scores between generated answers, test
    answers, and retrieved documents.

    Inputs:
    data (dict): A dictionary containing the following keys:
        - "questions": List of original questions
        - "answers": List of generated answers
        - "documents": List of lists of retrieved documents for each question
        - "test_answers": List of test/truth answers
        - "test_documents": List of document paths (not used for similarity)

    Returns:
    pd.DataFrame: A dataframe containing semantic similarity scores
    """
    # Validate input data
    required_keys = [
        "questions",
        "answers",
        "documents",
        "test_answers",
        "test_documents",
    ]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")

    # Ensure equal length of input lists
    n = len(data["answers"])

    # Initialize embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Calculate semantic similarity scores
    answer_similarity_scores = []

    for i in range(n):
        # Truncate test answer and generated answer
        test_answer = data["test_answers"][i]
        generated_answer = data["answers"][i]

        # Embed test answer and generated answer
        test_answer_embed = model.encode(test_answer, convert_to_tensor=True)
        generated_answer_embed = model.encode(generated_answer, convert_to_tensor=True)

        # Calculate answer similarity using dot product of normalized embeddings
        answer_sim = torch.dot(
            F.normalize(test_answer_embed, p=2, dim=0),
            F.normalize(generated_answer_embed, p=2, dim=0),
        ).item()
        answer_similarity_scores.append(answer_sim)

    # Calculate overall similarity scores
    answer_similarity_overall = np.mean(answer_similarity_scores)

    # Create results DataFrame
    results = pd.DataFrame(
        {
            "answerSimilarity_score": [answer_similarity_overall],
            "answerSimilarity_score_by_question": [answer_similarity_scores],
        }
    )

    return results
