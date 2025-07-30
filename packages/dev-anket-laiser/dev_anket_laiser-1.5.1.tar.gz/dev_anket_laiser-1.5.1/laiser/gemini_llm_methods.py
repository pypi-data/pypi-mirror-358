"""
Module Description:
-------------------
Class to extract skills from text and align them to existing taxonomy

Ownership:
----------
Project: Leveraging Artificial intelligence for Skills Extraction and Research (LAiSER)
Owner:  George Washington University Institute of Public Policy
        Program on Skills, Credentials and Workforce Policy
        Media and Public Affairs Building
        805 21st Street NW
        Washington, DC 20052
        PSCWP@gwu.edu
        https://gwipp.gwu.edu/program-skills-credentials-workforce-policy-pscwp

License:
--------
Copyright 2024 George Washington University Institute of Public Policy

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Input Requirements:
-------------------
- All the libraries in the requirements.txt should be installed

Output/Return Format:
----------------------------
- List of extracted skills from text

"""
"""
Revision History:
-----------------
Rev No.     Date            Author              Description
[1.0.0]     6/12/2025      Anket Patil  Define llm methods using gemini for MacOS development


TODO:
-----

"""

import re
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import json
import google.generativeai as genai        
genai.configure(api_key="AIzaSyDtNQcGj5mInL3jeuPvMYl_yIm4Sl_pAcQ")   

from laiser.llm_methods import parse_output_vllm
from laiser.utils import get_top_esco_skills
torch.cuda.empty_cache()

def get_completion_vllm_gemini(input_text, text_columns, id_column, input_type, batch_size) -> list:
    """
    Gemini-based replacement for get_completion_vllm.
    """
    # 1) generate raw outputs via Gemini
    raw_outputs = gemini_generate(input_text, input_type)

    # 2) parse each raw text into KSA dicts
    parsed_output = []
    for idx, raw in enumerate(raw_outputs):
        if not raw:
            continue
        try:
            items = parse_output_vllm(raw)
            for item in items:
                item[id_column] = input_text.iloc[idx][id_column]
                item['description'] = input_text.iloc[idx]['description']
                if 'learning_outcomes' in input_text.columns:
                    item['learning_outcomes'] = input_text.iloc[idx]['learning_outcomes']
                parsed_output.append(item)
        except Exception as e:
            print(f"[Gemini parse error] index={idx}: {e}")
    return parsed_output


def gemini_generate(prompt: str) -> str:
    """
    Send `prompt` to Gemini and return the generated text.
    """
    try:
        model = genai.get_model("gemini-1.5-pro")           # pick your Gemini variant
        response = model.generate(prompt=prompt)
        return response.candidates[0].content
    except Exception as e:
        print(f"[Gemini] Error: {e}")
        return ""

def get_ksa_details_gemini(skill: str, description: str, llm, num_key_kr: int = 3, num_key_tas: int = 3):
    """
    Generate Knowledge Required and Task Abilities for a given skill in the context of the supplied description.

    Parameters
    ----------
    skill : str
        The skill name for which to generate KSAs.
    description : str
        The textual description (job description, syllabus, etc.) providing context.
    llm : vllm.LLM
        The LLM instance already initialised by the caller.
    num_key_kr : int, optional
        Maximum length of the Knowledge Required list (default 3).
    num_key_tas : int, optional
        Maximum length of the Task Abilities list (default 3).

    Returns
    -------
    Tuple[list, list]
        knowledge_required, task_abilities – both are lists of strings.  Empty lists are
        returned if generation/parsing fails.
    """

    import json
    import re

    # Guard clause – if llm is None we simply return empty lists.
    if llm is None:
        return [], []

    prompt = (
        "user\n"
        f"Given the following context, provide concise lists for the specified skill.\n\n"
        f"Skill: {skill}\n\n"
        "Context:\n"
        f"{description}\n\n"
        f"For the skill above produce:\n"
        f"- Knowledge Required: {num_key_kr} bullet items, each ≤ 3 words.\n"
        f"- Task Abilities: {num_key_tas} bullet items, each ≤ 3 words.\n\n"
        "Respond strictly in valid JSON with the exact keys 'Knowledge Required' and 'Task Abilities'.\n"
        "model"
    )


    try:
        result = gemini_generate(prompt)        
        raw_text = result[0].outputs[0].text.strip()

        # Attempt to locate JSON object within the text
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not json_match:
            return [], []

        parsed = json.loads(json_match.group())
        knowledge = parsed.get("Knowledge Required", [])
        task_abilities = parsed.get("Task Abilities", [])

        # Ensure they are lists
        if not isinstance(knowledge, list):
            knowledge = [str(knowledge)]
        if not isinstance(task_abilities, list):
            task_abilities = [str(task_abilities)]

        return knowledge, task_abilities
    except Exception as e:
        print(f"[get_ksa_details] Generation/parsing error for skill '{skill}': {e}")
        return [], []