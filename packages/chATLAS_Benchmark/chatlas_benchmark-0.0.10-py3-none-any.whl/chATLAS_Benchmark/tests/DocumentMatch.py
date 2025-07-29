"""A test to see whether the returned documents from the RAG match the document
the question was generated on Has a base score which just determines whether
the correct document was returned at all as well as a weighted score which
weights earlier returned documents as better."""

import os

import numpy as np
import pandas as pd

score_metric = pd.DataFrame(
    columns=[
        "MeanDocumentMatch",  # Mean score of whether test document names are in retrieved documents
        "WeightedDocumentMatch",  # Weighted score emphasizing earlier document matches
    ]
)


def DocumentMatchScore(data: dict):
    """Calculate the DocumentMatch scores for the given data.

    Parameters:
    data (dict): A dictionary containing the following keys:
        - "questions": List of original questions
        - "answers": List of generated answers
        - "documents": List of lists of retrieved documents for each question
        - "test_answers": List of test/truth answers
        - "test_documents": List of lists of test documents for each question

    Returns:
    pd.DataFrame: A dataframe containing the mean DocumentMatch scores for the two metrics:
        - "MeanDocumentMatch": Mean score of whether test document names are in retrieved documents
        - "WeightedDocumentMatch": Weighted score emphasizing earlier document matches
    """

    # Normalise test document names to match "name" metadata format
    def normalize_name(path):
        # Get the base name from any file path and remove the extension
        return os.path.splitext(os.path.basename(path))[0]

    # Extract metadata names from retrieved documents
    document_names = [
        [
            (doc.metadata.get("name") if hasattr(doc, "metadata") and "name" in doc.metadata else None)
            for doc in doc_list
        ]
        for doc_list in data["documents"]
    ]

    # Filter out documents with None values and print a warning
    invalid_documents = sum([1 for doc_list in document_names for name in doc_list if name is None])
    document_names = [[normalize_name(name) for name in doc_list if name is not None] for doc_list in document_names]

    if invalid_documents > 0:
        print(
            f"Warning: {invalid_documents} documents had missing or invalid 'metadata' and were excluded from the "
            f"evaluation."
        )

    test_document_names = [[normalize_name(doc) for doc in doc_list] for doc_list in data["test_documents"]]

    # Metric 1: Mean Document Match
    mean_match_scores = []
    for retrieved, test in zip(document_names, test_document_names, strict=False):
        match_score = int(any(test_name in retrieved for test_name in test))
        mean_match_scores.append(match_score)
    mean_document_match = np.mean(mean_match_scores)

    # Metric 2: Weighted Document Match
    weighted_scores = []
    for retrieved, test in zip(document_names, test_document_names, strict=False):
        weights = np.linspace(1, 0, num=len(retrieved), endpoint=False)
        match_score = max((weights[i] for i, name in enumerate(retrieved) if name in test), default=0)
        weighted_scores.append(match_score)
    weighted_document_match = np.mean(weighted_scores)

    # Create a DataFrame for results
    results = pd.DataFrame(
        {
            "MeanDocumentMatch": [mean_document_match],
            "WeightedDocumentMatch": [weighted_document_match],
        }
    )

    return results
