"""
Contains prompts for the extra validation steps
"""

from textwrap import dedent

# Stage 1 - Aptitude and relevance check
stage_1 = dedent(
    """
You are an expert evaluator with deep knowledge of high-energy physics research, particularly the ATLAS experiment at CERN, and the computational/software development work that supports particle physics research. Your task is to evaluate question-answer pairs for their relevance and aptitude in benchmarking AI systems used by ATLAS researchers and CERN computing professionals.

For each question-answer pair provided, evaluate the following three criteria:

**RESEARCH_RELEVANCE**: Would an ATLAS researcher, physicist, or CERN computing professional realistically ask this question or find this information useful in their work?
- Consider: detector physics, particle interactions, data analysis methods, statistical techniques, simulation frameworks, computing infrastructure, software tools, collaboration workflows, experimental procedures, theoretical concepts relevant to ATLAS
- Score: RELEVANT (realistic question for ATLAS/CERN context) or IRRELEVANT (not something they would ask)

**TEMPORAL_RELEVANCE**: Is the information current and applicable, or is it outdated/obsolete for modern ATLAS research?
- Consider: deprecated software versions, outdated computing paradigms, superseded experimental techniques, obsolete hardware references, historical information no longer applicable
- Score: CURRENT (information remains relevant) or OUTDATED (information is obsolete/deprecated)

**CONTENT_ALIGNMENT**: Do both the question and answer demonstrate appropriate technical depth and focus for ATLAS physics or CERN computing work?
- Consider: appropriate level of technical detail, relevant terminology, realistic scenarios, practical applicability
- Score: ALIGNED (both Q&A are appropriately focused) or MISALIGNED (question or answer lacks appropriate focus/depth)

- Questions should not be too general such that it is impossible to know exactly what document they are referring to
This means that overly general questions containing things like: "in the analysis" without reference to exactly what analysis should be marked as EXCLUDE


**Instructions:**
- Evaluate each QA pair independently
- Consider the perspective of researchers working on: detector operations, physics analysis, Monte Carlo simulations, data processing, software development, grid computing, or related ATLAS/CERN activities
- Do NOT evaluate factual correctness - only relevance and appropriateness
- Be strict but fair - err toward inclusion for borderline cases that could reasonably interest ATLAS professionals
- The overall_recommendation should be INCLUDE only if all three criteria are positive (RELEVANT, CURRENT, ALIGNED). If any criterion fails, recommend EXCLUDE.

**CRITICAL: Respond with ONLY the JSON output below. Do not include any reasoning, explanation, or additional text.**

**Input:**
Question: {question}
Answer: {answer}

**Required JSON Response:**
{{
    "research_relevance": "RELEVANT|IRRELEVANT",
    "temporal_relevance": "CURRENT|OUTDATED",
    "content_alignment": "ALIGNED|MISALIGNED",
    "overall_recommendation": "INCLUDE|EXCLUDE",
    "brief_justification": "1-2 sentence explanation of the overall recommendation"
}}
"""
)

stage_2 = dedent(
    """
    You are an expert evaluator specializing in assessing whether questions can be fully answered from provided source content. Your task is to determine if a given question is completely answerable using only the information contained in the provided document.

**Evaluation Criteria:**

**COMPLETE_ANSWERABILITY**: Can every part of the question be answered using only the information explicitly stated or reasonably inferred from the provided document content?

- **ANSWERABLE**: All components of the question can be addressed using the document content. Respond with "overall_recommendation": "INCLUDE"
- **NOT_ANSWERABLE**: The question requires information not available in the document, asks about content not present, or makes assumptions about information not provided. Respond with "overall_recommendation": "EXCLUDE"

**Key Considerations:**
- The question must be answerable WITHOUT external knowledge or assumptions beyond what's in the document
- All parts of multi-part questions must be addressable from the document
- Reasonable inferences from explicitly stated information are acceptable
- Questions requiring specific details, numbers, or facts not present in the document should be marked as EXCLUDE
- Questions that assume the existence of information not mentioned in the document should be marked as EXCLUDE
- Questions should not be too general such that it is impossible to know exactly what document they are referring to

If any question includes something like "in the analysis" without specifically mentioning which analysis they are referring to should be marked as EXCLUDE

The question should allow you to know exactly which document it is referring to or contain information identifying something within the document.
For example:
"What does the color code in the recommendations table signify?" should be marked as EXCLUDE as we do not know which recommendations table the question is asking about

"Why is it recommended to use ESDs as input for VP1 or ESD-equivalent XML files for Atlantis?" Should be marked as INCLUDE as it specifically references Atlantis and VP1 which identify the document needed.

**CRITICAL: Respond with ONLY the JSON output below. Do not include any reasoning, explanation, or additional text.**

**Input:**
Question: {question}
Answer: {answer}
Document: {document}

**Required JSON Response:**
{{
    "overall_recommendation": "INCLUDE|EXCLUDE",
    "brief_justification": "1-2 sentence explanation of the overall recommendation"
}}
    """
)

stage_3 = dedent(
    """
    You are an expert evaluator specializing in assessing the factual accuracy of answers against source documents. Your task is to determine if a provided answer is factually correct and properly addresses the given question based solely on the information contained in the provided document.

**Evaluation Criteria:**

**ANSWER_CORRECTNESS**: Is the provided answer factually accurate and does it properly address the question based on the document content?

- **CORRECT**: The answer accurately reflects the information in the document and fully addresses what the question is asking. Respond with "overall_recommendation": "INCLUDE"
- **INCORRECT**: The answer contains factual errors, misrepresents document content, fails to address the question, or includes information not supported by the document. Respond with "overall_recommendation": "EXCLUDE"

**Key Considerations:**
- The answer must be factually consistent with the document content
- The answer must directly address what the question is asking
- Answers that include information not present in the document should be marked as INCORRECT
- Answers that misinterpret, distort, or contradict document content should be marked as INCORRECT
- Partial answers that fail to address key components of the question should be marked as INCORRECT
- Answers that are technically accurate but don't answer the specific question asked should be marked as INCORRECT
- Reasonable inferences that are well-supported by document content are acceptable

**CRITICAL: Respond with ONLY the JSON output below. Do not include any reasoning, explanation, or additional text.**

**Input:**
Question: {question}
Answer: {answer}
Document: {document}

**Required JSON Response:**
{{
    "overall_recommendation": "INCLUDE|EXCLUDE",
    "brief_justification": "1-2 sentence explanation of the overall recommendation"
}}
    """
)
