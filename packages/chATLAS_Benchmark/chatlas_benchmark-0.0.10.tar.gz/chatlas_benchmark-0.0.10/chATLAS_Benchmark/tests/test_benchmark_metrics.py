"""Contains main Benchmark Test."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from ..test_utils.database_utils import save_benchmark_results
from .AnswerCorrect import calculate_answer_correct_score
from .DocumentMatch import DocumentMatchScore
from .LexicalMetrics import evaluate_exact_f1_rouge
from .semanticSimilarity import calculate_semantic_similarity_score


@dataclass
class Document:
    """
    Represents a base document with its page_content and metadata.

    Attributes:
        page_content (str): Content of the page.
        metadata (dict[str, Any]): Metadata for the document.
        id (str): ID for the document.
        parent_id (Optional[str]): Parent ID if this document has a parent in a hierarchical vector store.
    """

    page_content: str
    metadata: dict[str, Any]
    id: str
    parent_id: str | None = None


class BenchmarkTest:
    """Class for testing LLM and RAGs.

    :param question_set: Path to json file containing generated questions and answers
    :param keys: Specify what keys loads the data from input dict or json path

    Expects either JSON file with entries like:

    .. code-block:: json

        [
            {
                "document": "docName1.txt",
                "question": "What is the ATLAS experiment at CERN?",
                "answer": "The ATLAS experiment (short for \"A Toroidal LHC Apparatus\") detects subatomic particles"
                # Any other keys are okay, it just won't use them
            },
            {
                "document": "docName2.txt",
                "question": "What is CERN?",
                "answer": "An organization that operates the largest particle physics laboratory in the world."
                # Any other keys are okay, it just won't use them
            }
        ]

    Or a list of dictionary inputs, with test question keys also input.

    **USAGE:**

    .. code-block:: python

        # Import the benchmarking module
        from chATLAS_Benchmark import BenchmarkTest

        # Initialize the test set
        test = BenchmarkTest(question_set_path)
        # OR
        test = BenchmarkTest(test_dictionary, keys={"test_questions": "question", "test_documents":"documents", "test_answer": "answer"}

        # --- Run the RAG on the questions ---
        # Assuming RAG.run() returns an answer and list of docs for each question
        gen_answers = []
        gen_docs = []
        for q in test.questions:
            answer, docs = RAG.run(q)
            gen_answers.append(answer)
            gen_docs.append(docs)

        # Set generated answers and documents on the test instance
        test.set_generated_data(gen_answers, gen_docs)

        # Run the scoring with any metrics you want
        scores = test.score_test_set("LexicalMetrics", "SemanticSimilarity", "DocumentMatch")

        # Save the results to the db
        test.store_results(scores, db_name="database.db", name="NameOfRAG")

    **ADDITIONAL NOTES**

    For DocumentMatch test, RAG needs to return documents with attribute `metadata` (dict) with key ("name")
    i.e. it finds document names via `document.metadata["name"]`
    """

    def __init__(
        self,
        question_set: Path | str | list[dict],
        keys: dict | None = None,
        num_q: int | float | None = 1,
    ):
        """
        :param question_set: Path to json file containing test questions and answers or a dict of qas
        :type Path | str | List[dict]:
        :param keys: Specify what keys loads the data from input dict or json path
        :type Optional[dict]:
        :param Optional[int|float num_q]: Number of questions to use from the test set.
        If float between 0 and 1 - load that fraction of the dataset, if int or > 1 load that number of questions

        Expects a JSON file or list of dicts with entries like:

        ..code-block:: json

            [
                {
                    "document": "docName1.txt",
                    "question": "What is the ATLAS experiment at CERN?",
                    "answer": "The ATLAS experiment (short for "A Toroidal LHC Apparatus") detects subatomic particles"
                    # Any other keys are okay, it just won't use them
                },
                {
                    "document": "docName2.txt",
                    "question": "What is CERN?",
                    "answer": "An organization that operates the largest particle physics laboratory in the world."
                    # Any other keys are okay, it just won't use them
                }
            ]


        If passing in a dict or json with different keys to these also need to pass in keys dict.
        Default is:

        ..code-block:: python

             keys = {
                    "test_name": "Unknown dict",  # Name of the test set for saving results
                    "test_questions": "question",  # Key to use for test questions from the dict
                    "test_documents": "document",  # Key to use for the test documents
                    "test_answers": "answer",  # Key to use for the test answers
                }
        """

        # UPDATE WHENEVER NEW TEST ADDED WITH NAME AND FUNCTION TO BE CALLED
        # Define implemented tests
        self.implemented_tests = {
            "LexicalMetrics": evaluate_exact_f1_rouge,
            "SemanticSimilarity": calculate_semantic_similarity_score,
            "DocumentMatch": DocumentMatchScore,
            "AnswerCorrect": calculate_answer_correct_score,
        }
        self.num_q = num_q

        self.questions: list[list[str]] = [[]]  # Placeholder for test questions
        self.answers = []  # Placeholder for generated answers
        self.documents: list[list[Document]] | list[list[str]] = [[]]  # Placeholder for retrieved document contexts

        self.test_answers = []  # Placeholder for test answers
        self.test_documents: list[list[str]] = [[]]  # Placeholder for test document contexts

        if not keys:
            keys = {
                "test_name": "Unknown dict",
                "test_questions": "question",
                "test_documents": "document",
                "test_answers": "answer",
            }
        elif not all(k in keys for k in ["test_questions", "test_documents", "test_answers"]):
            raise ValueError("Keys dictionary must contain keys 'test_questions', 'test_documents', and 'test_answers'")

        if isinstance(question_set, list):
            self.question_set_path = keys.get("test_name", "Unknown dict")
            self.set_test_data(question_set, keys)

        else:
            self.question_set_path = question_set  # Storing path of qa pairs for results saving

            # Load questions if a path is provided
            if question_set:
                question_set = self.load_question_set(question_set)
                self.set_test_data(question_set, keys)

    @staticmethod
    def load_question_set(json_path: Path | str) -> list[dict[str, str]]:
        """Load a set of questions from a JSON file.

        Args:
            json_path (Path | str): Path to the JSON file containing question-answer pairs.
                Can be absolute or relative to the current working directory.

        Returns:
            List[Dict[str, str]]: List of questions with associated metadata.

        Raises:
            FileNotFoundError: If the JSON file doesn't exist
            json.JSONDecodeError: If the JSON file is invalid
            UnicodeDecodeError: If the file encoding cannot be determined
        """
        # Convert to Path object if string is provided
        path = Path(json_path)

        # Make path absolute if it's relative
        if not path.is_absolute():
            path = Path.cwd() / path

        # Try UTF-8 first, then try to detect encoding if that fails
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except UnicodeDecodeError:
            # If UTF-8 fails, try to detect the encoding
            import chardet

            # Read the raw bytes
            raw_data = path.read_bytes()

            # Detect the encoding
            result = chardet.detect(raw_data)
            encoding = result["encoding"]

            # Try again with detected encoding
            with path.open("r", encoding=encoding) as file:
                data = json.load(file)

        return data

    def set_test_data(self, question_set: list[dict[str, str]], keys: dict | None = None):
        """Sets the questions, answers, and documents variables based on
        provided question set.

        :param question_set: (List[Dict[str, str]]): List of questions and their answers and document contexts.
        :param keys: Dict of keys to use
        """
        if isinstance(self.num_q, int):
            num_keep = len(question_set) if self.num_q == 1 else self.num_q
        elif isinstance(self.num_q, float):
            if 0 < self.num_q <= 1:
                num_keep = int(self.num_q * len(question_set))
            elif self.num_q > 1:
                num_keep = int(self.num_q)
            else:
                raise ValueError("num_q - Number of questions to use must be a positive number")
        else:
            raise TypeError("num_q - Number of questions to use must be either a float or an int")

        try:
            self.questions = [item[keys["test_questions"]] for item in question_set[:num_keep]]
            self.test_answers = [item[keys["test_answers"]] for item in question_set[:num_keep]]
            self.test_documents = [[item[keys["test_documents"]]] for item in question_set[:num_keep]]
        except KeyError:
            print(
                "ERROR: Keys in data not correct, set variable `keys` correctly with the correct keys for your data "
                "when creating the benchmark test!"
            )
            raise

    def set_generated_data(self, answers: list[str], documents: list[list[Document]] | list[list[str]]):
        """Sets the generated answers and documents from an external model for
        evaluation.

        Args:
            answers (List[str]): List of generated answers.
            documents (List[List[Document]]): List of retrieved document contexts, with each sub list containing each
            document for the corresponding question. NOTE: This should be passed in as standard document form from Embed
            with attributes .page_content, .metadata and .similarity
        """
        if len(answers) != len(documents):
            raise ValueError(
                "Length of answers and documents do not match! If no documents are returned by RAG make "
                "sure it returns an empty list instead."
            )
        self.answers = answers
        self.documents = documents

    def store_results(self, scores, db_name="benchmark.db", name="Unknown_RAG", connection_string: str = None):
        """Stores the results from the various tests run to a SQL database for
        later retrieval. Also stores the question path used to generate the
        results.

        :param pd.Dataframe scores: Scores generated from this test
        :param str db_name: name of the database to store results in -> currently stores in current working directory
        :param str name: name of the model to store in the db
        :param str connection_string: Give as value if you want to connect to an extrnal server eg PG server
        """

        save_benchmark_results(
            model_name=name,
            db_name=db_name,
            question_path=self.question_set_path,
            scores=scores,
            connection_string=connection_string,
        )

    def score_test_set(self, *args: str) -> dict[str, pd.DataFrame]:
        """Evaluates answer relevancy on the current test set using stored
        answers and documents.

        Args:
            *args (str): Names of the tests to run. Possible options are:
                "LexicalMetrics",
                "SemanticSimilarity",
                "DocumentMatch",
                "AnswerCorrect"
        Returns:
            Dict[str, pd.DataFrame]: Dictionary where keys are test names and values are DataFrames of scoring results.
        """

        # Data for testing functions
        data = {
            "questions": self.questions,
            "answers": self.answers,
            "documents": self.documents,
            "test_answers": self.test_answers,
            "test_documents": self.test_documents,
        }

        # Collect scores for each requested test
        scores = {}
        for test_name in args:
            if test_name in self.implemented_tests:
                print(f"Running {test_name} test...")
                scores[test_name] = self.implemented_tests[test_name](data)
            else:
                raise ValueError(
                    f"""'{test_name}' test is not implemented.

                Possible options are:
                {self.implemented_tests.keys()}"""
                )

        print(f"AVERAGE NUM DOCUMENTS per QUESTION: {sum([len(doc) for doc in self.documents]) / len(self.documents)}")

        return scores
