from typing import Dict


def load_facts() -> Dict[str, str]:
    """
    File format: from data/car_facts.txt.
    Each topic starts with "Topic|Explanation".
    """
    facts: Dict[str, str] = {}
    current_topic = None
    current_text = []

    try:
        with open("data/car_facts.txt", "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.rstrip("\n")
                if not line.strip():
                    continue

                # Start of new topic
                if "|" in line:
                    # Save previous topic if exists
                    if current_topic is not None:
                        facts[current_topic] = "\n".join(current_text).strip()
                        current_text = []

                    topic, explanation = line.split("|", 1)
                    current_topic = topic.strip()
                    current_text.append(explanation.strip())

                else:
                    current_text.append(line.strip())

            # Save last topic
            if current_topic is not None:
                facts[current_topic] = "\n".join(current_text).strip()

    except FileNotFoundError:
        facts = { "Error": "car_facts.txt file not found." }

    return facts