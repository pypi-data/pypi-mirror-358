"""
Test for evaluating correctness of the answer as judged by an LLM

By default, uses ChatGPT 40-mini for this - needs environment variable OPENAI_API_KEY set for this
"""

import numpy as np
import pandas as pd
from openai import OpenAI

score_metric = pd.DataFrame(
    columns=[
        "answerCorrect_score",  # Mean semantic similarity score across all generated answers
        "answerCorrect_score_by_question",  # List Mean answerSimilarity score for each answer
    ]
)


def calculate_answer_correct_score(data: dict) -> pd.DataFrame:
    """
    Calculate the answer correctness score using an LLM
    :param data: A dictionary containing the following keys:
        - "questions": List of original questions
        - "answers": List of generated answers
        - "documents": List of lists of retrieved documents for each question
        - "test_answers": List of test/truth answers
        - "test_documents": List of document paths (not used for similarity)
    :type data: dict
    :return: scores
    :rtype: pd.DataFrame
    """
    # Initialize OpenAI client
    client = OpenAI()

    questions = data["questions"]
    gen_answers = data["answers"]
    true_answers = data["test_answers"]

    # Initialize lists to store scores
    correctness_scores = []
    correctness_scores_by_question = []

    # Iterate over each question and its corresponding answers
    for question, gen_answer, true_answer in zip(questions, gen_answers, true_answers, strict=False):
        # Construct the messages for the API call
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that evaluates answer correctness. Respond with only 'yes' or "
                "'no'.",
            },
            {
                "role": "user",
                "content": f"Question: {question}\nTrue Answer: {true_answer}\nGenerated Answer: {gen_answer}\nDoes "
                f"the generated answer correctly answer the question?",
            },
        ]

        # Call the OpenAI API to get the response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=5,
            n=1,
            temperature=0.0,
        )

        # Extract the response text
        response_text = response.choices[0].message.content.strip().lower()

        # Determine the score based on the response
        score = 1 if response_text == "yes" else 0
        correctness_scores.append(score)
        correctness_scores_by_question.append(score)

    # Calculate the mean correctness score
    mean_correctness_score = np.mean(correctness_scores)

    # Create a DataFrame for results
    results = pd.DataFrame(
        {
            "answerCorrect_score": [mean_correctness_score],
            "answerCorrect_score_by_question": [correctness_scores_by_question],
        }
    )

    return results
