
import json
import re
from laiser.llm_models.llm_router import llm_router

def get_ksa_details(skill: str, description: str, model_id, use_gpu, num_key_kr: int = 3, num_key_tas: int = 3):
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
    print("KSA Function test")

    try:
        raw_text = llm_router([prompt],model_id, use_gpu)
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