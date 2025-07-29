"""Tests to carry out exact match, F1 and rouge score on the answers from the
RAG compared to ground truth answers.

**NOTE**: Needs nltk package 'punkt_tab' downloaded, uncomment code at top of script if this test fails from this

Exact Match: Measures whether the generated answer exactly matches the ground truth answer
F1: Measures the overlap of tokens between generated and true answers

ROUGE-1: Measures unigram (single word) overlap
ROUGE-2: Measures bigram (two consecutive words) overlap
ROUGE-L: Measures longest common subsequence (LCS)


This does not account for semantic differences so rephrasing of the answers if they are not specific enough could lead
to low scores


Potential changes/additional metrics:
Running BM25 or IDF to get important keywords from the answers
"""

# DOWNLOAD punkt_tab if test fails
# import nltk
# exitCode = nltk.download('punkt_tab')
# while not exitCode:
#     exitCode = nltk.download('punkt_tab')

import time
from collections import Counter
from urllib.error import URLError

import nltk
import numpy as np
import pandas as pd
from nltk.data import find
from nltk.tokenize import word_tokenize
from nltk.util import ngrams


def ensure_punkt_downloaded(max_retries=5, delay=0.2):
    """Ensures the punkt tokenizer models are downloaded with retry logic.

    Args:
        max_retries: Maximum number of download attempts
        delay: Seconds to wait between retries
    """
    for attempt in range(max_retries):
        try:
            find("tokenizers/punkt")
            return
        except LookupError:
            try:
                success = nltk.download("punkt", quiet=True)
                if success:
                    return
                else:
                    if attempt == max_retries - 1:
                        raise RuntimeError(
                            f"Failed to download NLTK punkt after {max_retries} attempts. "
                            "Please try:\n"
                            "1. Check your internet connection\n"
                            "2. Run 'python -m nltk.downloader punkt' manually\n"
                        )
                    time.sleep(delay)
            except (URLError, ConnectionError, TimeoutError) as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(
                        f"Failed to download NLTK punkt after {max_retries} attempts. "
                        f"Error: {e!s}. "
                        "Please try:\n"
                        "1. Check your internet connection\n"
                        "2. Run 'python -m nltk.downloader punkt' manually\n"
                    ) from e
                time.sleep(delay)


# Returned metric from scoring
score_metric = pd.DataFrame(
    columns=[
        "exact_match_score",  # float - mean value across all qa tested
        "f1_score",  # float - mean value across all qa tested
        "rouge_1_score",  # float - mean ROUGE-1 F1 score
        "rouge_2_score",  # float - mean ROUGE-2 F1 score
        "rouge_l_score",  # float - mean ROUGE-L F1 score
        "exact_match_by_question",  # List - all individual question scores
        "f1_score_by_question",  # List - all individual question scores
        "rouge_1_by_question",  # List - all individual ROUGE-1 scores
        "rouge_2_by_question",  # List - all individual ROUGE-2 scores
        "rouge_l_by_question",  # List - all individual ROUGE-L scores
    ]
)


def evaluate_exact_f1_rouge(data: dict) -> pd.DataFrame:
    """Scores retrieved documents using exact match, F1 scoring, and ROUGE
    metrics.

    Inputs:
    data = {
        "questions": List[str],      # Original question asked
        "answers": List[str],        # Generated answer from RAG
        "documents": List[List[str]],      # Retrieved documents
        "test_answers": List[str],   # Test/truth answers
        "test_documents": List[List[str]]  # Test documents answers were generated from
        }

    Returns:
        DataFrame with all evaluation metrics
    """
    exact_scores = exact_match_score(data)
    f1_scores = f1_score(data)
    rouge_scores = rouge_score(data)

    evaluation_metrics = {
        "exact_match_score": exact_scores["exact_match_score"],
        "f1_score": f1_scores["f1_score"],
        "rouge_1_score": rouge_scores["rouge_1_score"],
        "rouge_2_score": rouge_scores["rouge_2_score"],
        "rouge_l_score": rouge_scores["rouge_l_score"],
        "exact_match_by_question": exact_scores["exact_match_by_question"],
        "f1_score_by_question": f1_scores["f1_score_by_question"],
        "rouge_1_by_question": rouge_scores["rouge_1_by_question"],
        "rouge_2_by_question": rouge_scores["rouge_2_by_question"],
        "rouge_l_by_question": rouge_scores["rouge_l_by_question"],
    }

    return pd.DataFrame([evaluation_metrics])


def exact_match_score(data: dict) -> dict:
    """Scores generated answers based on exact match to true answers.

    Inputs:
    data: dict

    Returns:
    score_returns = {
        "exact_match_score": mean_score,
        "exact_match_by_question": results
    }
    """

    gen_answers = data["answers"]
    true_answers = data["test_answers"]

    results = []
    for gen_answer, true_answer in zip(gen_answers, true_answers, strict=False):
        normalised_generated = normalize_and_tokenize(gen_answer)
        normalised_true = normalize_and_tokenize(true_answer)

        results.append(1 if normalised_generated == normalised_true else 0)

    mean_score = np.mean(results)

    score_returns = {
        "exact_match_score": mean_score,
        "exact_match_by_question": results,
    }
    return score_returns


def f1_score(data: dict):
    """Scores generated answers based on their f1 score to true answers by
    tokenizing using nltik tokenizer.

    Inputs:
    data: dict

    Returns:
    score_returns = {
        "f1_score": np.mean(results),
        "f1_score_by_question": results
    }
    """
    gen_answers = data["answers"]
    true_answers = data["test_answers"]

    results = []

    for gen_answer, true_answer in zip(gen_answers, true_answers, strict=False):
        # Tokenize both predicted and reference answers
        predicted_tokens = normalize_and_tokenize(gen_answer)
        reference_tokens = normalize_and_tokenize(true_answer)

        # Count token occurrences for each answer
        predicted_counts = Counter(predicted_tokens)
        reference_counts = Counter(reference_tokens)

        # Calculate the number of matching tokens
        common_tokens = predicted_counts & reference_counts  # Intersection of counters
        num_common_tokens = sum(common_tokens.values())

        # Precision and Recall calculations
        if len(predicted_tokens) == 0 or len(reference_tokens) == 0:
            return 0  # Edge case: one of the answers is empty
        precision = num_common_tokens / len(predicted_tokens)
        recall = num_common_tokens / len(reference_tokens)

        # F1 Score calculation (avoid division by zero)
        if precision + recall == 0:
            return 0
        f1 = 2 * (precision * recall) / (precision + recall)

        results.append(f1)

    score_returns = {"f1_score": np.mean(results), "f1_score_by_question": results}

    return score_returns


def rouge_score(data: dict) -> dict:
    """Calculate ROUGE scores for all answer pairs.

    Returns:
        Dictionary containing mean ROUGE scores and scores by question
    """
    gen_answers = data["answers"]
    true_answers = data["test_answers"]

    rouge_1_scores = []
    rouge_2_scores = []
    rouge_l_scores = []

    for gen_answer, true_answer in zip(gen_answers, true_answers, strict=False):
        scores = calculate_rouge_scores(gen_answer, true_answer)
        rouge_1_scores.append(scores["rouge_1"])
        rouge_2_scores.append(scores["rouge_2"])
        rouge_l_scores.append(scores["rouge_l"])

    return {
        "rouge_1_score": np.mean(rouge_1_scores),
        "rouge_2_score": np.mean(rouge_2_scores),
        "rouge_l_score": np.mean(rouge_l_scores),
        "rouge_1_by_question": rouge_1_scores,
        "rouge_2_by_question": rouge_2_scores,
        "rouge_l_by_question": rouge_l_scores,
    }


def normalize_and_tokenize(text):
    # Lowercase and tokenize text using NLTK's word_tokenize
    ensure_punkt_downloaded()
    text = text.lower()
    tokens = word_tokenize(text)
    return tokens


def get_ngrams(tokens: list[str], n: int) -> set[tuple]:
    """Generate n-grams from a list of tokens."""
    return set(ngrams(tokens, n))


def lcs_length(tokens1: list[str], tokens2: list[str]) -> int:
    """Calculate the length of Longest Common Subsequence between two token
    lists."""
    m, n = len(tokens1), len(tokens2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if tokens1[i - 1] == tokens2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]


def calculate_rouge_scores(gen_answer: str, true_answer: str) -> dict:
    """Calculate ROUGE-1, ROUGE-2, and ROUGE-L scores for a pair of answers.

    Returns:
        Dict containing F1 scores for ROUGE-1, ROUGE-2, and ROUGE-L
    """
    # Tokenize both answers
    gen_tokens = normalize_and_tokenize(gen_answer)
    true_tokens = normalize_and_tokenize(true_answer)

    # Calculate ROUGE-1 (unigrams)
    gen_unigrams = get_ngrams(gen_tokens, 1)
    true_unigrams = get_ngrams(true_tokens, 1)
    common_unigrams = len(gen_unigrams & true_unigrams)

    rouge_1_precision = common_unigrams / len(gen_unigrams) if gen_unigrams else 0
    rouge_1_recall = common_unigrams / len(true_unigrams) if true_unigrams else 0
    rouge_1_f1 = (
        2 * (rouge_1_precision * rouge_1_recall) / (rouge_1_precision + rouge_1_recall)
        if (rouge_1_precision + rouge_1_recall) > 0
        else 0
    )

    # Calculate ROUGE-2 (bigrams)
    gen_bigrams = get_ngrams(gen_tokens, 2)
    true_bigrams = get_ngrams(true_tokens, 2)
    common_bigrams = len(gen_bigrams & true_bigrams)

    rouge_2_precision = common_bigrams / len(gen_bigrams) if gen_bigrams else 0
    rouge_2_recall = common_bigrams / len(true_bigrams) if true_bigrams else 0
    rouge_2_f1 = (
        2 * (rouge_2_precision * rouge_2_recall) / (rouge_2_precision + rouge_2_recall)
        if (rouge_2_precision + rouge_2_recall) > 0
        else 0
    )

    # Calculate ROUGE-L (longest common subsequence)
    lcs = lcs_length(gen_tokens, true_tokens)
    rouge_l_precision = lcs / len(gen_tokens) if gen_tokens else 0
    rouge_l_recall = lcs / len(true_tokens) if true_tokens else 0
    rouge_l_f1 = (
        2 * (rouge_l_precision * rouge_l_recall) / (rouge_l_precision + rouge_l_recall)
        if (rouge_l_precision + rouge_l_recall) > 0
        else 0
    )

    return {"rouge_1": rouge_1_f1, "rouge_2": rouge_2_f1, "rouge_l": rouge_l_f1}
