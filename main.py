import json

EVIDENCE_JSON = "evidence.json"

def evidence_json(folder_path):
    # TODO: method to compile evidence from folder_path into json
    
    with open(EVIDENCE_JSON, "r") as evidence:
        return json.load(evidence)
    
if __name__ == "__main__":
    evidence = evidence_json("")
    print(evidence)
