"""
Performs an extra validation step on all generated qa's to ensure they are of a reasonable quality
"""

import json
import os
import random
import re
import time
import traceback
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

from . import extra_validation_prompts


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
                    documents[os.path.basename(relative_path)] = relative_path

    return documents


def send_request(base_url, API_key, model_name, prompt, max_tokens, max_prompt_len) -> dict:
    """
    Send a request to LLM with improved error handling and rate limiting

    Args:
        base_url (str): Base URL for the API
        API_key (str): API key for authentication
        model_name (str): Name of the model to use
        prompt (str): Input prompt
        max_tokens (int): Maximum tokens for response
        max_prompt_len (int): Maximum length of prompt in bytes

    Returns:
        dict: JSON response from the API

    Raises:
        Exception: If max retries exceeded or other critical errors occur
    """
    # Constants for retry logic
    MAX_RETRIES = 5
    BASE_DELAY = 0.1
    MAX_DELAY = 16
    retries = 0

    while retries < MAX_RETRIES:
        try:
            # Add jitter to base delay (between 75% and 100% of calculated delay)
            jitter = random.uniform(0.75, 1.0)
            delay = min(BASE_DELAY * (2**retries) * jitter, MAX_DELAY)
            time.sleep(delay)

            # Sanitize and truncate prompt
            sanitized_prompt = prompt.encode("utf-8", errors="replace")[:max_prompt_len].decode(
                "utf-8", errors="replace"
            )

            chat_payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": sanitized_prompt,
                    }
                ],
                "max_tokens": max_tokens,
                "model": model_name,
                "temperature": 0.1,
                "n": 1,
            }

            # Add timeout to request
            chat_response = requests.post(
                base_url,
                json=chat_payload,
                headers={"X-API-Key": API_key, "Content-Type": "application/json"},
                timeout=30,  # 30 second timeout
            )

            # Handle different status codes
            if chat_response.status_code == 200:
                return chat_response.json()

            elif chat_response.status_code == 429:  # Too Many Requests
                retry_after = int(chat_response.headers.get("Retry-After", delay))
                time.sleep(min(retry_after, MAX_DELAY))
                retries += 1
                continue

            elif chat_response.status_code >= 500:  # Server errors
                retries += 1
                continue

            else:  # Other errors (400, 401, 403, etc.)
                error_msg = f"API Error (Status {chat_response.status_code}): {chat_response.text}"
                print(error_msg)
                return {"error": error_msg}

        except requests.exceptions.Timeout:
            retries += 1
            if retries == MAX_RETRIES:
                return {"error": "Request timeout after maximum retries"}
            continue

        except requests.exceptions.RequestException as e:
            retries += 1
            if retries == MAX_RETRIES:
                return {"error": f"Request failed after maximum retries: {e!s}"}
            continue

        except Exception as e:
            return {"error": f"Unexpected error: {e!s}"}

    return {"error": "Maximum retries exceeded"}


def find_json_objects(text: str) -> list:
    """
    Find potential JSON objects in text by matching curly braces.
    Returns a list of strings that might be valid JSON.
    """
    json_candidates = []

    # Find all opening braces
    for i, char in enumerate(text):
        if char == "{":
            # Try to find the matching closing brace
            brace_count = 1
            j = i + 1

            while j < len(text) and brace_count > 0:
                if text[j] == "{":
                    brace_count += 1
                elif text[j] == "}":
                    brace_count -= 1
                j += 1

            # If we found a complete object
            if brace_count == 0:
                candidate = text[i:j]
                json_candidates.append(candidate)

    # Sort by length (prefer longer, more complete objects)
    json_candidates.sort(key=len, reverse=True)

    return json_candidates


def load_json_validated(json_string: str) -> dict:
    original_string = json_string

    # Remove thinking model tags if present
    if "<think>" in json_string and "</think>" in json_string:
        # Find the position of JSON content after think tags
        json_start = json_string.find("```json\n")
        if json_start != -1:
            json_end = json_string.find("```", json_start + 7)
            if json_end != -1:
                json_string = json_string[json_start + 7 : json_end].strip()

    # Fix potential JSON formatting issues
    if json_string.startswith("{{") and json_string.endswith("}}"):
        json_string = json_string[1:-1]

    try:
        answer = json.loads(json_string)
    except json.JSONDecodeError:
        # Try to find JSON objects using brace matching
        json_candidates = find_json_objects(original_string)

        for candidate in json_candidates:
            try:
                # Handle double curly braces
                if candidate.startswith("{{") and candidate.endswith("}}"):
                    candidate_form = candidate[1:-1]
                else:
                    candidate_form = candidate  # needed for ruff
                return json.loads(candidate_form)
            except json.JSONDecodeError:
                continue

        raise ValueError(f"Invalid JSON response from LLM: \n{json_string}")

    return answer


def extra_evaluation_on_qa(
    qa_path: Path,
    documents_dir: Path,
    new_qa_dir: Path,
    llm_base_url: str,
    model_name: str,
    llm_api_key: str | None = None,
    max_tokens: int = 1024,
    max_prompt_len: int = 25000,
) -> list:
    """
    Performs extra validation steps on generated QAs to ensure high performance

    Note this uses many LLM calls for validation so watch rate limits

    QA pair save format should be of form:
    {
        "document": "xyz.txt",
        "question": "",
        "answer": "",
        "type": "",
        "created_at": "2024-12-13T11:40:13.898081"
    },


    :param qa_path: Path to the previously generated QA Pairs
    :param documents_dir: Directory containing .txt files of base sources
    :param new_qa_dir: Path to directory to save both new qa pairs and csv of excluded qa's and why
    :param llm_base_url: Base URL of llm you want to use
    :param model_name: Model name you want to use
    :param llm_api_key: OPTIONAL - LLM key to use for chosen LLM (if not set will use env: LLM_API_KEY
    :param max_tokens: DEFAULT = 1024 - Max tokens returned by LLM
    :param max_prompt_len: DEFAULT - 25000 - Max prompt len in num bytes (~ num chars)

    :return List of kept QAs
    """

    if not llm_api_key:
        llm_api_key = os.environ["LLM_API_KEY"]

    # Pre-Checks - load info
    base_sources_names = get_documents(local_path=documents_dir)

    # Fix relative paths
    if not qa_path.is_absolute():
        current_dir = Path(os.getcwd())
        qa_path = (current_dir / qa_path).resolve()

    if not new_qa_dir.is_absolute():
        current_dir = Path(os.getcwd())
        new_qa_dir = (current_dir / new_qa_dir).resolve()

    with open(qa_path, encoding="UTF-8") as f:
        qa_pairs = json.load(f)

    kept_questions = []
    discarded_questions = []

    # Stage 1 - Ensure question answer pair is realistic and relevant
    stage_1_prompt = extra_validation_prompts.stage_1

    # Stage 2 - Ensure question is answerable from the source
    stage_2_prompt = extra_validation_prompts.stage_2

    # Stage 3 - Ensure answer is correct
    stage_3_prompt = extra_validation_prompts.stage_3
    pbar = tqdm(qa_pairs)

    for qa in pbar:
        pbar.set_postfix(
            {"PASSED": len(kept_questions), "FAILED": len(discarded_questions)},
            refresh=True,
        )

        # ===== Stage 1 =====
        stage_1_prompt_qa = stage_1_prompt.replace("{question}", qa["question"]).replace(
            "{answer}", qa["answer"]
        )  # This should be .format not replace

        try:
            response = send_request(
                base_url=llm_base_url,
                API_key=llm_api_key,
                model_name=model_name,
                prompt=stage_1_prompt_qa,
                max_tokens=max_tokens,
                max_prompt_len=max_prompt_len,
            )

            answer_str = response["choices"][0]["message"]["content"]

            answer = load_json_validated(answer_str)

            recommendation = answer.get("overall_recommendation")

            if not recommendation:
                recommendation = answer.get("ANSWER_CORRECTNESS", {}).get("overall_recommendation", "INCLUDE")

            if recommendation == "EXCLUDE":
                discarded_questions.append(
                    {
                        "question": qa["question"],
                        "answer": qa["answer"],
                        "document": qa["document"],
                        "stage_failed": "RELEVANCE",
                        "reason_for_exclusion": answer.get("brief_justification", ""),
                    }
                )
                continue

            # ===== Stage 2 =====
            qa_file = base_sources_names.get(qa["document"], "")

            if not qa_file:
                raise Exception(f"Cannot find file - {qa['document']}")

            with open(Path(documents_dir) / qa_file, encoding="utf-8", errors="replace") as f:
                file_contents = "".join(f.readlines())

            stage_2_prompt_qa = stage_2_prompt.format(
                question=qa["question"], answer=qa["answer"], document=file_contents
            )

            response = send_request(
                base_url=llm_base_url,
                API_key=llm_api_key,
                model_name=model_name,
                prompt=stage_2_prompt_qa,
                max_tokens=max_tokens,
                max_prompt_len=max_prompt_len,
            )

            answer_str = response["choices"][0]["message"]["content"]

            answer = load_json_validated(answer_str)

            recommendation = answer.get("overall_recommendation")

            if not recommendation:
                recommendation = answer.get("ANSWER_CORRECTNESS", {}).get("overall_recommendation", "INCLUDE")

            if recommendation == "EXCLUDE":
                discarded_questions.append(
                    {
                        "question": qa["question"],
                        "answer": qa["answer"],
                        "document": qa["document"],
                        "stage_failed": "ANSWERABLE",
                        "reason_for_exclusion": answer.get("brief_justification", ""),
                    }
                )
                continue

            # ===== Stage 3 =====

            stage_3_prompt_qa = stage_3_prompt.format(
                question=qa["question"], answer=qa["answer"], document=file_contents
            )

            response = send_request(
                base_url=llm_base_url,
                API_key=llm_api_key,
                model_name=model_name,
                prompt=stage_3_prompt_qa,
                max_tokens=max_tokens,
                max_prompt_len=max_prompt_len,
            )
            answer_str = response["choices"][0]["message"]["content"]

            answer = load_json_validated(answer_str)

            recommendation = answer.get("overall_recommendation")

            if not recommendation:
                recommendation = answer.get("ANSWER_CORRECTNESS", {}).get("overall_recommendation", "INCLUDE")

            if recommendation == "EXCLUDE":
                discarded_questions.append(
                    {
                        "question": qa["question"],
                        "answer": qa["answer"],
                        "document": qa["document"],
                        "stage_failed": "CORRECT",
                        "reason_for_exclusion": answer.get("brief_justification", ""),
                    }
                )
                continue

        except Exception as e:
            print(
                f"Error processing qa: \n\n {qa} \n ERROR:\n{e}\nStack trace:\n{traceback.format_exc()} \n\n Treating as kept pair."
            )
            kept_questions.append(qa)

        # QAs have now passed all tests, we can keep it!
        kept_questions.append(qa)

    # Finished with all questions - Can now save everything!

    # Ensure the directory exists, create if it doesn't
    qa_dir = Path(new_qa_dir)
    qa_dir.mkdir(parents=True, exist_ok=True)

    # Save good QAs with error handling
    qa_path = qa_dir / "new_validated_qa.json"
    try:
        with open(qa_path, "w", encoding="UTF-8") as f:
            json.dump(kept_questions, f)
    except Exception as e:
        print(f"Error saving validated QA file: {e}")
        raise

    # Save csv of dropped questions with error handling
    try:
        df = pd.DataFrame(discarded_questions)
        csv_path = qa_dir / "discarded_qa.csv"
        df.to_csv(csv_path, index=False)
    except Exception as e:
        print(f"Error saving discarded QA file: {e}")
        raise

    print(f"Successfully saved files to {qa_dir}")
    print(f"- Kept QAs: {qa_path}")
    print(f"- Discarded QAs: {csv_path}")

    return kept_questions
