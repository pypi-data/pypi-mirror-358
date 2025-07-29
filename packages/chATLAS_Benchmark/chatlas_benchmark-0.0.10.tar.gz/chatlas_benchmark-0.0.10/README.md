<div align="center">
<h1 align="center" style="font-family: Arial, sans-serif; font-size: 36px; font-weight: bold; color: #600c0c; padding: 10px; display: inline-block; border: 3px solid #46ad9e; border-radius: 10px; background-color: rgba(255,255,255,0.8);">
  <span style="color: #0b7fbf;">chAT</span>LAS Benchmark
</h1>
</div>



<div align="center">
<img src="https://atlas.cern/sites/atlas-public.web.cern.ch/files/inline-images/ATLAS%20logo%20blue%20on%20white%20RGBHEX%20300ppi.png" alt="ATLAS" width="200"/>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Sql_data_base_with_logo.png/800px-Sql_data_base_with_logo.png?20210130181641" alt="SQL" height="30"/>



*A Python package for LLM and RAG benchmarking and testing built for the ATLAS experiment as part of the chATLAS project*

</div>

## 📚 Overview
<span style="font-family: Arial, sans-serif; font-size: 11px; font-weight: bold; color: #600c0c; padding: 3px; display: inline-block; border: 2px solid #46ad9e; border-radius: 10px; background-color: rgba(255,255,255,0.8);">
  <span style="color: #0b7fbf;">chAT</span>LAS_Benchmark
</span>
 provides a flexible framework for testing and benchmarking LLMs and RAG models with robust storage
and retrieval of past runs for comparison using SQL.



### 🌟 Key Features

- Set of benchmarking tests for RAG comparison
  - *Semantic Similarity Score*
  - *F-1 Testing*
  - *ROUGE 1, 2 and l testing*
  - *Document Match scores*
  - *Answer Correct Score*
- SQL storage of results for robust database operations

## 🚀 Quick Start

### 📥 Installation

```bash
pip install chATLAS-Benchmark
```

For Lexical Metrics test (should be downloaded automatically):
```python
import nltk
nltk.download('punkt_tab')
```

For new QA pair Generation:

```shell
export OPENAI_API_KEY="<Your OpenAI Api Key>"
```




### 💡 Basic Usage

```python
# Import the benchmarking module
from chATLAS_Benchmark import BenchmarkTest, fetch_metrics_results

# Initialize the test set
test = BenchmarkTest("/path/to/test.json")

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


# See at all previous scored results in the db
df = fetch_metrics_results()
```

---

## Contents

1. [Installation](#installation)
2. [Requirements](#requirements)
3. [Extending chATLAS_Benchmark](#extending-chatlasbenchmark)
   - [Adding New Tests](#adding-new-tests)
4. [Current Metrics Overview](#chatlasbenchmark-metrics-overview)
5. [Project Structure and Imports](#project-structure-and-imports)

---

## Installation

To install the package:

```bash
pip install chATLAS_Benchmark
```

---

## Requirements

### Python Dependencies

Dependencies should be installed automatically when installing the package, but a full list of requirements is given in `requirements.txt` in module root for reference.


### Document Format

For `DocumentMatch` scoring it expects documents to be in `Document`format:
```python
from chATLAS_Benchmark import Document
```

But any document with:
```python
name_of_document = document.metadata["name"]
```
Would work (so langchain document format also compatible as long as the documents have their name in metadata).

---


## Extending chATLAS_Benchmark


## Adding New Tests

Currently, new tests can be added functionally but could(/should) be updated to use class inheritance.

Each testing method is implemented as a separate script in the `/tests` directory. To add a new test:


#### 1. Write new test metric scoring method - return pandas DF

```python
import pandas as pd


def myNewTestMetric(data:dict):
  """
  :param data: (dict) -
  {
    "questions": List[str],       # Original questions
    "answers": List[str],         # Generated answers
    "documents": List[List[str]], # Retrieved documents
    "test_answers": List[str],    # Expected answers
    "test_documents": List[List[str]] # Documents that generated the expected answers
    }
  """
  return pd.DataFrame()
```

#### 2. Add the test name and function to the BaseBenchmark.implemented_tests dict

```python
from chATLAS_Benchmark import BenchmarkTest

myTest = BenchmarkTest("testSet.json")

myTest.implemented_tests["MyNewTest"] = myNewTestMetric
```

#### 3. Run The Testing

```python
gen_answers = []
gen_docs = []
for q in myTest.questions:
    answer, docs = RAG.run(q)
    gen_answers.append(answer)
    gen_docs.append(docs)

# Set generated answers and documents on the test instance
myTest.set_generated_data(gen_answers, gen_docs)

# Run the scoring with any metrics you want
scores = myTest.score_test_set("MyNewTest")

```

#### 4. Storing New Test to DB

Now the package was not built in the most scalable way, so this cannot be done without explicitly editing the source code
for the `chATLAS_Benchmark.test_utils.database_utils.py` script.

You can follow the setup for the other tables in this script to add your own to it.

---


## chATLAS_Benchmark Metrics Overview

The **chATLAS_Benchmark** package provides several evaluation metrics to assess the performance of Retrieval-Augmented Generation (RAG) systems. These metrics help analyze the quality of retrieved documents and generated answers against a ground truth. The defined metrics fall into three main categories:

### 1. DocumentMatch

- **Purpose:**
  Evaluates whether the RAG system successfully retrieves the correct document that was originally used to generate the test question.
- **How it works:**
  The metric checks if the correct document is present within the set of documents retrieved by the system.

### 2. LexicalMetrics

These metrics assess the generated answer's textual similarity to the reference answer using lexical comparison techniques.

- **Exact Match:**
  - Compares the RAG/LLM-generated answer to the ground truth after stemming words to account for variations.
  - Returns `True` if the answers are identical post-stemming, otherwise `False`.

- **F1 Score:**
  - Measures the overlap between the true and generated answers using precision and recall.
  - The F1 score is the harmonic mean of precision and recall, capturing both false positives and false negatives.

- **ROUGE Scores:**
  The package computes the following ROUGE scores to evaluate overlap between the generated and true answers:
  - **ROUGE-1:** Measures overlap of unigrams (single words).
  - **ROUGE-2:** Measures overlap of bigrams (two consecutive words).
  - **ROUGE-L:** Measures the longest common subsequence (LCS) between the true and generated answers.

### 3. SemanticSimilarity

- **Purpose:**
  Evaluates the semantic similarity between the generated and true answers using embedding-based methods.
- **How it works:**
  - Both the generated and ground-truth answers are converted into vector embeddings using a pre-trained model.
  - The **cosine similarity** is computed between these embeddings, providing a score between `0` (completely dissimilar) and `1` (identical), with higher values indicating closer semantic meaning.

### 4. AnswerCorrect
- **Purpose:**
  Evaluates whether the generated answer is correct for the question relative to the generated answer
- **How it works:**
  - Takes original question, true answer and generated answer and sends them to GPT-4o-mini
  - 4o-mini evaluates *yes* it answers the question or *no* it does not answer the question correctly
  - If yes gets assigned a score of 1 for that question if no gets assigned a score of 0 for that question


---

These metrics provide a comprehensive evaluation framework to analyze both lexical accuracy and semantic understanding of RAG-generated responses, ensuring robust performance assessment.



### Project Structure and imports

**Project Structure**:
```text
chATLAS_Benchmark/
│   _version.py
│   __init__.py
│
├───Generation
│   │   gen_qa_pairs.py
│   │   gen_simple_qa_pairs.py
│   │   __init__.py
├───tests
│   │   DocumentMatch.py
│   │   LexicalMetrics.py
│   │   README.md
│   │   semanticSimilarity.py
│   │   test_benchmark_metrics.py
│   │   __init__.py
├───test_utils
│   │   database_utils.py
│   │   __init__.py
```

**Module Imports**:

```python

# Standard Imports
from chATLAS_Benchmark import (
    BenchmarkTest,
    Document,
    fetch_metrics_results
)

# Sub Imports
from chATLAS_Benchmark.Generation import (
    generate_qa,
    generate_qa_from_named_files
)
```





## 🔧 Development Status


Current development priorities:

- [ ] More modular design
- [ ] Integration of *answer correctness* test
- [ ] Additional testing

## CHANGELOG

#### 0.0.9

New extra validation stages for QAs: relevance, answerable and correct

Fix relative paths for benchmark package

Fix jupyter notebook running benchmark causing errors.


#### 0.0.8

Made lexical metrics automatically download required punkt model if using lexical metrics test


#### 0.0.7

Fixes to `fetch_metric_results` so that we can return data even when we don't have all tests run for a particular model.

#### 0.0.6

Minor update to package requirements.

#### 0.0.5

Adding a print to scoring to show average number of documents returned per question.

#### 0.0.4

New AnswerCorrect test for using an LLM to test if answer is correct.

#### 0.0.3

Added ability to create a benchmark test on a dict instead of just Json files.

Added custom keys to benchmark test to load data with different keys to expected.

Added ability to load a set number of questions in the benchmark instance

Added AnswerCorrect score - simple LLM evaluation of is generated answer correct or not

#### 0.0.2

Fixing loading file encoding for json

Fixing docstring for what type of file `BenchmarkTest` accepts

#### 0.0.1

Initial Release

---
## 📄 License

chATLAS_Benchmark is released under Apache v2.0 license.

---

<div align="center">

**Made with ❤️ by the ATLAS Collaboration**

*For questions and support, please [contact](mailto:Ben.Elliot27@outlook.com)*

</div>

