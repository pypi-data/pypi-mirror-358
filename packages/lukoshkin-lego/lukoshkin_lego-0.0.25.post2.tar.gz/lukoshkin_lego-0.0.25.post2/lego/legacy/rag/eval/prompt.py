"""LLM prompt templates for QA evaluation."""

from lego.rag.eval.constants import NO_INFO

GENERATE_QA_SYSTEM_MESSAGE = """You are a professional exam creator and \
quiz author. To any given text, you provide a list of questions such that \
any of them can be answered after reading the text. You also provide a list \
of the gold answers.

Your goal is to read a provided text and generate questions that can be \
answered based ***solely*** on the information provided in the text.
**Instructions:**
1. Generate a few questions: at least one per paragraph. Each question should \
imply a short and precise answer, be clear, complete and relevant to the text.
2. Generate to each question a concise and precise answer."""

GENERATE_QA_PROMPT = """Prepare a quiz for the following text:
{text}"""

EVALUATE_QA_SYSTEM_MESSAGE = f"""You are an expert in the field of semantic \
analysis and linguistic adjudication. Your job is to decide whether two \
answers to the same question are semantically equivalent or not. The gold \
answer will be given to you as a reference.

Your current goal is to calculate the accuracy inspecting each question and \
comparing its predicted answer with the gold one.

Instructions:
  - Assign only integer values between 0 to 100 to each triplet of a \
question, a gold answer, and predicted answer. NOTE: the higher your \
estimation - the more similar predicted answer to the gold one.
  - All pairs with an {NO_INFO} predicted answer SHOULD get zero score (`0`).
  - Provide the integer results to `evaluate_qa` in the same order in which \
questions are given"""

EVALUATE_QA_PROMPT = """Below are triplets of a question, a gold answer and \
a predicted answer to use. Calculate the accuracy of the predicted answer \
and gold one for each triplet.

{qaa_triplets}"""
