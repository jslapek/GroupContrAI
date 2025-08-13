from pathlib import Path
from structures import Evidence
import json
from llm import classify

file_types = {
    "text": lambda x: x.suffix.lower() in {
        ".txt", ".text", ".md", ".tex"
    },
    "code": lambda x: x.suffix.lower() in {
        ".py", ".java", ".c", ".cpp", ".cs",
        ".js", ".ts", ".rb", ".swift", ".go",
        ".ipynb", ".m", ".html", ".css", ".rs",
        ".hs", ".htm", ".sh", ".bash", ".bat", 
        ".mk", ".php", 
    },
    "image": lambda x: x.suffix.lower() in {
        ".jpg", ".jpeg", ".png"
    },
    "video": lambda x: x.suffix.lower() in {
        ".mp4", ".wmv", ".m4v"
    },
    "json": lambda x: x.suffix.lower() == ".json", 
    "git": lambda x: x.name.lower() == ".git" 
}

def categorise_file_type(file):
    for f_type, test in file_types.items():
        if test(file):
            return f_type
    return "UNKNOWN"

def categorise_file_type_ai(file):
    # TODO: add classifier
    return "UKNOWN"

def get_evidence():
    evidence = Path("evidence")
    evidence_arr = []
    for file in evidence.iterdir():
        f_type = categorise_file_type(file)
        if f_type == "UNKNOWN":
            f_type = categorise_file_type_ai(file)
        elif f_type == "json":
            f_type = categorise_json(file)
        evidence_arr.append(Evidence(f_type, file))

    return evidence_arr

def categorise_json(file):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    desc = {
        ("messages", "channel") : "chat",
        ("from", "subject", "body", "payload") : "email"
    }

    for k in desc.keys():
        if any(x in data for x in k):
            return desc[k]
    return "UNKNOWN"


    # with open(file, "r") as f:
    #     data = f.read()

    # labels = {
    #     "task description for a group project/assignment (deadline, learning outcome)"
    #     : "task description",
    #     "an email message (with From, To, Subject and a body, greeting, sign-off, cc)"
    #     : "email",
    #     "chat transcript (list of short messages with usernames/timestamps, channels, discussion)"
    #     : "chat"
    # }

    # label = classify(data, list(labels.keys()))
    # return label if label=="UNKNOWN" else labels[label]
