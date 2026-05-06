# Nova AI - Bug Fix & Optimization Methods

This document outlines strategies to improve the local model's performance on task context retrieval and extraction, based on recent test results.

## 1. Task Context RAG (Fix for Test 2)
**Issue:** The local model blends the "Knowledge Base Context" and the "User Task List," leading to confusion about which tasks are active and which are just retrieved information.

### Recommended Methods:
- **Unified List Structure**: Instead of two separate blocks (KB and Task List), merge them into a single list but tag items with `[DOC]` or `[ACTIVE]`. Smaller models handle one list much better than two.
- **Role Reinforcement**: Explicitly tell the model: "The USER TASK LIST is your current memory. The KNOWLEDGE BASE is extra info. Answer only from the TASK LIST unless the question is about a document."
- **Negative Constraints**: Add: "DO NOT mention tasks from the Knowledge Base if they are not also in the User Task List."

---

## 2. Local Task Extraction (Fix for Test 3)
**Issue:** The model is "hallucinating" values from the RAG context instead of extracting them from the user's input (e.g., extracting "PAY_ELECTRICITY_BILL" when the user said "Finish budget report").

### Recommended Methods:
- **Selective RAG**: Disable RAG context for the `Add Task` mode by default. RAG is useful for chat, but for a fresh task, it often acts as "noise" that distracts a small model.
- **Context Labeling**: If context is kept, rename the header from `CONTEXT` to `POTENTIALLY RELATED PAST TASKS (IGNORE UNLESS RELEVANT)`.
- **Instruction Overhaul**: Add a rule: "IGNORE the context if it does not directly match the new task. Use ONLY the 'Task' string at the top for extraction."
- **Strict Format Enforcement**: Force the model to use the input text verbatim for the `task_name` field unless a cleanup is clearly needed.

---

## 3. General Local Model Stability
**Issue:** 50% accuracy on extraction suggests the model is struggling with the JSON schema.

### Recommended Methods:
- **Smaller Schema**: Remove `date_info` and `time_info` from the JSON for local models and use a separate regex-based extractor (like the `DateTimeExtractor` already in `utils.py`). This reduces the "brain load" on the model.
- **Schema-First Prompting**: Put the JSON structure at the very top of the prompt, then the input, then the instruction. Some models respond better when they see the "shape" of the output first.

---

## 4. Ultra-Small Model Optimization (Specialized for 0.5B Models)
**Issue:** 0.5B models have very limited "reasoning" capacity and are easily overwhelmed by long prompts or complex context.

### Recommended Methods:
- **Zero-Noise Prompts**: For 0.5B models, remove ALL background context (RAG) during task extraction. Every extra line of context reduces the model's ability to focus on the user's input.
- **Extreme Instruction Compression**: Instead of "You are a task extractor...", use "Extract to JSON:".
- **Template Completion**: Instead of "Output JSON", provide the start of the JSON: `{"category": "` and ask the model to complete it. This forces it to follow the structure.
- **No-Explanation Rule**: Explicitly add `NO EXPLANATION. NO CHAT.` to the very end of the prompt.
- **Lower Temperature**: Ensure the sampling temperature is very low (e.g., 0.1) to prevent the model from "wandering" off into the context documents.
- **Regex Post-Processing**: Since 0.5B models often fail JSON syntax, use the Python backend to aggressively "fix" the string (e.g., adding missing quotes or braces) before parsing.

