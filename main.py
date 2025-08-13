from evidence_type import get_evidence
from llm import query_llm
from structures import TeamData
from alias import fetch_alias
from menu import display_menu
import json
    
if __name__ == "__main__":
    print("Fetching alias...")
    alias = fetch_alias()
    print("Alias fetched.")

    print("Fetching and categorising evidence...")
    evidence_arr = get_evidence()

    print("Calculating team data...")
    team = TeamData(evidence_arr, alias)

    display_menu(team, alias)

    print("Updating alias...")
    with open("alias.json", "w", encoding="utf-8") as f:
        json.dump(alias, f)
