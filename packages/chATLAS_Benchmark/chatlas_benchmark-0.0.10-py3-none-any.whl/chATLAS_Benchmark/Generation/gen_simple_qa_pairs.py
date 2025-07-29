# gen_simple_qa_pairs.py
import argparse
import json
import os
import random
import signal
import time
from datetime import datetime

from openai import OpenAI

file_path = os.path.dirname(__file__)

# Global flag for graceful shutdown
should_exit = False

qa_pair_path = "../data/evaluation_simple_qa_pairs.json"
doc_dir = ""


def signal_handler(signum, frame):
    global should_exit
    print("\nGraceful shutdown initiated. Waiting for current document to finish...")
    should_exit = True


signal.signal(signal.SIGINT, signal_handler)


def read_document(file_path):
    with open(file_path) as f:
        return "".join(f.readlines())


def get_documents(twiki_path=None, local_path=None):
    """Get documents from either TWiki or local file storage.

    Args:
        twiki_path (str, optional): Path to TWiki documents directory
        local_path (str, optional): Path to local documents directory

    Returns:
        dict: Dictionary of document names and empty strings (page_content loaded later)
    """
    documents = {}

    if twiki_path is None and local_path is None:
        twiki_path = os.getenv("TWIKI_PATH")  # Fallback to env variable

    paths_to_check = []
    if twiki_path:
        paths_to_check.append(twiki_path)
    if local_path:
        paths_to_check.append(local_path)

    for base_path in paths_to_check:
        for root, _dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    # Remove base path from the file path
                    relative_path = file_path.replace(f"{base_path}/", "")
                    documents[relative_path] = ""

    return documents


def evaluate_document_content(document_content):
    """Check if document has enough meaningful page_content.

    Args:
        document_content (str): The document text to evaluate

    Returns:
        bool: True if document has sufficient page_content, False otherwise
    """
    # Remove common metadata sections
    content = document_content.lower()

    # Common TWiki metadata patterns to remove
    metadata_patterns = [
        r"-----url-----.*?(?=-----|\Z)",
        r"-----last modification----.*?(?=-----|\Z)",
        r"-----parent structure----.*?(?=-----|\Z)",
        r"-----headers-----.*?(?=-----|\Z)",
        r"-----text-----\s*",
        r"https?://[^\s<>]+",  # Remove URLs
    ]

    import re

    for pattern in metadata_patterns:
        content = re.sub(pattern, "", content, flags=re.DOTALL | re.IGNORECASE)

    # Remove extra whitespace and get clean page_content
    clean_content = " ".join(content.split())

    # Check page_content length (after cleaning)
    if len(clean_content) < 1000:
        return False

    # Check for meaningful page_content indicators
    empty_indicators = [
        "page not found",
        "no page_content",
        "empty page",
        "under construction",
        "[empty]",
        "access denied",
        "permission denied",
        "restricted access",
        "page does not exist",
        "this topic does not exist",
        "this page intentionally left blank",
    ]

    # Check for pages that are just navigation/structure
    structure_indicators = [
        all(line.startswith(("*", "-", ">", "•")) for line in content.split("\n") if line.strip()),
        content.count("http") > len(content) / 100,  # Too many URLs relative to page_content
        content.count("/") > len(content) / 50,  # Too many path separators
    ]

    # Check if page_content is mostly metadata/navigation
    if any(structure_indicators):
        return False

    # Check for empty page_content indicators
    if any(indicator in clean_content for indicator in empty_indicators):
        return False

    # Check if page_content has enough unique words
    unique_words = set(clean_content.split())
    if len(unique_words) < 100:  # Require at least 100 unique words
        return False

    return True


def validate_qa_response(response_text):
    """Validate and clean the model's response."""
    try:
        # Try to find JSON page_content if model included other text
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}") + 1
        if start_idx == -1 or end_idx == 0:
            return None

        json_str = response_text[start_idx:end_idx]
        data = json.loads(json_str)

        # Validate structure
        if "qa_pairs" not in data or not isinstance(data["qa_pairs"], list):
            return None

        valid_pairs = []
        for pair in data["qa_pairs"]:
            # Validate each required field exists and is non-empty
            if not all(
                k in pair and isinstance(pair[k], str) and pair[k].strip() for k in ["question", "answer", "type"]
            ):
                continue

            # Basic quality checks
            if len(pair["question"].split()) < 3 or len(pair["answer"].split()) < 3:
                continue

            valid_pairs.append(pair)

        if not valid_pairs:
            return None

        return {"qa_pairs": valid_pairs}

    except json.JSONDecodeError:
        return None


def generate_qa_pair(
    document,
    prompt,
    system_prompt,
    seed=42,
    temperature=0.1,
    model="gpt-3.5-turbo-0125",
):
    client = OpenAI(max_retries=0, api_key=os.getenv("OPENAI_API_KEY"))
    if isinstance(document, str):
        try:
            document_content = read_document("database/" + document)
        except Exception:
            # Using local file store so document not in database/
            document_content = read_document(document)
    else:
        document_content = document[1]
    # Check if document has enough page_content
    if not evaluate_document_content(document_content):
        return None

    full_prompt = f"{prompt}{document}\n```{document_content}```\n"

    # Add explicit instructions about empty documents
    system_prompt += (
        '\nIf the document contains insufficient information or is empty, respond with exactly: {"qa_pairs": []}'
    )

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt},
            ],
            seed=seed,
            temperature=temperature,
        )

        response = completion.choices[0].message.content
        return validate_qa_response(response)
    except Exception:
        return None


def batch_evaluate_qa_pairs(
    qa_pairs_last: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Evaluate and rank the most recent QA pairs, selecting the top 60% for
    further analysis.

    :param qa_pairs_last: List of dictionaries containing question and
        answer pairs
    :return: Filtered list of top-ranked QA pairs
    """
    # Prepare input for the LLM
    print("Evaluating Batch")
    formatted_pairs = []
    for i, pair in enumerate(qa_pairs_last, 1):
        formatted_pairs.append(f"QA Pair {i}:\nQuestion: {pair['question']}\nAnswer: {pair['answer']}")

    # Combine all pairs into a single input
    combined_input = "\n\n".join(formatted_pairs)

    try:
        openai = OpenAI(max_retries=0, api_key=os.getenv("OPENAI_API_KEY"))
        # Send to GPT-4o mini for evaluation
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise evaluator of question-answer pairs for a Retrieval-Augmented Generation (RAG) model assessment.",
                },
                {
                    "role": "user",
                    "content": f"""Carefully evaluate and rank the following question-answer pairs for their suitability in testing a RAG model.

        EVALUATION CRITERIA:
        1. Question Clarity: Is the question well-formed and unambiguous?
        2. Answer Comprehensiveness: Does the answer provide a substantive response?
        3. Generalizability: Can the question be answered without relying on a specific document?
        4. Complexity: Does the QA pair test meaningful retrieval and generation capabilities, such as synthesizing nuanced information?

        RANKING INSTRUCTIONS:
        - Provide a JSON-formatted ranking of the QA pairs.
        - Include a score from 1-10 for each pair, where 10 is highest.
        - Sort the pairs from highest to lowest score.
        - Focus on pairs that demonstrate the ability to retrieve and synthesize nuanced or highly relevant information.

        IMPORTANT: Respond with **ONLY** a valid JSON array of objects containing the following keys:
        - 'index': Original pair number (based on order in the input).
        - 'score': Numeric score (1-10).

        If the input QA pairs are empty or invalid, return an empty JSON array: `[]`.

        EXAMPLE RESPONSE:
        If the input includes two QA pairs, your response should look like this:

        [
            {{
                "index": 1,
                "score": 9
            }},
            {{
                "index": 0,
                "score": 7
            }}
        ]

        IMPORTANT: Ensure the JSON is correctly formatted and does not include any additional text or explanations outside of the array.

        INPUT QA PAIRS:
        {combined_input}""",
                },
            ],
            temperature=0,
        )

        # Parse the JSON response
        rankings = json.loads(response.choices[0].message.content)

        # Sort rankings by score in descending order
        sorted_rankings = sorted(rankings, key=lambda x: x["score"], reverse=True)

        # Calculate how many pairs to keep (top 60%)
        num_to_keep = max(1, int(len(qa_pairs_last) * 0.6))

        # Select top pairs
        top_pairs = sorted_rankings[:num_to_keep]

        # Map back to original QA pairs
        final_pairs = [qa_pairs_last[rank["index"] - 1] for rank in top_pairs]

        return final_pairs

    except Exception as e:
        print(f"Error in evaluating QA pairs: {e}")
        # Fallback to returning original pairs if evaluation fails
        return qa_pairs_last


def generate_evaluation_qa_pairs(
    twiki_path=None,
    local_path=None,
    seed=42,
    temperature=0.7,
    documents=None,
    system_prompt=None,
    user_prompt=None,
    model="gpt-3.5-turbo-0125",
):
    global should_exit

    if not documents:
        documents = get_documents(twiki_path=twiki_path, local_path=local_path)
        preset_content = False
    else:
        preset_content = True
    qa_pairs = []

    if not system_prompt:
        system_prompt = """
        You are an expert at creating clear, unambiguous question-answer pairs for evaluating AI models. For the given document, a single document in a large database of related documents, generate 3 types of questions ONLY IF the document contains sufficient meaningful information:
        1. Factual: Questions directly about explicit, specific facts or details in the text.
        2. Interpretative: Questions that require understanding or inferring relationships between pieces of information in the text.
        3. Contextual: Questions that explore the broader context, implications, or significance of the page_content in the text, as derived solely from the information provided.

        Each question must:
        - Be focused on the page_content and avoid mentioning or referencing "this document" explicitly.
        - Be answerable without requiring knowledge of the specific document it was based on. Avoid questions that rely on document-specific references (e.g., "What does plot 13 show?" or "What is mentioned in section 2.1?").
        - Have a single, clear, unambiguous answer that is answerable from the page_content provided.
        - Be concise (question should be 1-2 sentences).
        - Have an answer that is 1-3 sentences.

        If the document lacks sufficient page_content, return an empty array.

        Format your response as valid JSON with this structure:
        {
            "qa_pairs": [
                {
                    "question": "...",
                    "answer": "...",
                    "type": "factual|interpretative|contextual"
                },
                ...
            ]
        }
        """

    if not user_prompt:
        user_prompt = (
            "Generate 3 question-answer pairs (one of each type) for evaluation based on the information provided "
            "below. Avoid referencing 'this document' and instead focus on crafting questions about the page_content "
            "itself. If the document lacks sufficient meaningful information, return an empty array:\n"
        )

    # Process existing QA pairs to avoid duplicates
    existing_pairs = set()
    if os.path.exists(os.path.join(file_path, qa_pair_path)):
        with open(os.path.join(file_path, qa_pair_path)) as f:
            data = json.load(f)
            for item in data:
                existing_pairs.add(os.path.basename(item["document"]))

    # Remove documents that match on file name
    documents = {key: value for key, value in documents.items() if os.path.basename(key) not in existing_pairs}

    # Process remaining documents
    if not preset_content:
        document_names = list(documents.keys())
        random.shuffle(document_names)
    else:
        document_names = list(documents.items())

    start_time = time.time()
    processed_count = 0

    for idx, document in enumerate(document_names):
        if should_exit:
            print("\nSaving progress and exiting...")
            should_exit = False
            break

        print(f"Processing {idx + 1}/{len(documents)}: {document if isinstance(document, str) else document[0]}")

        # Estimate time remaining
        if processed_count > 0:
            elapsed_time = time.time() - start_time
            avg_time_per_doc = elapsed_time / processed_count
            docs_remaining = len(documents) - idx
            estimated_time = avg_time_per_doc * docs_remaining
            print(f"Estimated time remaining: {estimated_time / 3600:.1f} hours")

        try:
            # Generate QA pairs
            qa_data = generate_qa_pair(
                document,
                user_prompt,
                system_prompt,
                seed=seed,
                temperature=temperature,
                model=model,
            )

            if qa_data is None or not qa_data["qa_pairs"]:
                print(
                    f"Skipping document {document if isinstance(document, str) else document[0]} - insufficient page_content or invalid response"
                )
                continue

            # Add metadata to each QA pair
            for qa_pair in qa_data["qa_pairs"]:
                pair_data = {
                    "document": document if isinstance(document, str) else document[0],
                    "question": qa_pair["question"],
                    "answer": qa_pair["answer"],
                    "type": qa_pair["type"],
                    "created_at": datetime.now().isoformat(),
                }
                qa_pairs.append(pair_data)

            time.sleep(2)

            if idx % 5 == 0:
                last_qa_pairs = qa_pairs[-5 * 3 :]
                culled_qa = batch_evaluate_qa_pairs(last_qa_pairs)
                qa_pairs = qa_pairs[: -5 * 3]
                qa_pairs.extend(culled_qa)

            # Save progress periodically (every 10 documents)
            if idx % 10 == 0:
                save_progress(qa_pairs)

            processed_count += 1

        except TypeError as e:  # Exception
            print(f"Error processing document {document if isinstance(document, str) else document[0]}: {e!s}")
            # Save progress on error
            save_progress(qa_pairs)
            continue

    # Final save
    save_progress(qa_pairs)
    return qa_pairs


def save_progress(qa_pairs):
    """Save current progress to file."""
    file_full_path = os.path.join(file_path, qa_pair_path)

    # Load existing data if the file exists
    if os.path.exists(file_full_path):
        with open(file_full_path) as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    # Create sets of existing questions and answers for deduplication
    existing_questions = {item["question"] for item in existing_data}
    existing_answers = {item["answer"] for item in existing_data}

    # Filter new QA pairs to exclude duplicates
    filtered_qa_pairs = [
        item
        for item in qa_pairs
        if item["question"] not in existing_questions and item["answer"] not in existing_answers
    ]

    # Combine existing data with filtered new data
    save_data = existing_data + filtered_qa_pairs

    # Save the deduplicated data back to the file
    with open(file_full_path, "w") as f:
        json.dump(save_data, f, indent=4)

    print(f"Progress saved - {len(save_data)} total QA pairs")


if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description="Generate QA pairs from documents for AI model evaluation.")

    # Add arguments
    parser.add_argument("-local_path", type=str, default=None, help="Path to local documents directory")

    parser.add_argument("-twiki_path", type=str, default=None, help="Path to TWiki documents directory")

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Temperature for model generation (default: 0.7)",
    )

    # Parse arguments
    args = parser.parse_args()

    print("Starting QA pair generation. Press Ctrl+C to gracefully stop and save progress.")
    print(f"Local path: {args.local_path}")
    print(f"TWiki path: {args.twiki_path}")
    print(f"Seed: {args.seed}")
    print(f"Temperature: {args.temperature}")

    # Generate QA pairs with provided arguments
    qa_pairs = generate_evaluation_qa_pairs(
        twiki_path=args.twiki_path,
        local_path=args.local_path,
        seed=args.seed,
        temperature=args.temperature,
    )
