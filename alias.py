from pathlib import Path
import json

def fetch_alias():
    p = Path("alias.json")
    if p.exists():
        with p.open("r") as f:
            alias = json.load(f)
        print(f"Existing alias file found. Use alias with identifiers: \n{list(alias['identifiers'].values())}\n[Y]/[N]")
        if input() == "y":
            return alias

    print("Creating new alias...")
    alias = {}
    i_dict = {}
    size = int(input("What is the team size: "))
    for x in range(1, size+1):
        identifier = input(f"What should be the identifier for student {x}: ")
        i_dict[x] = identifier

        print(f"Please enter all emails for {identifier} followed by 'enter':")
        e_dict = {}
        while (e:=input()) != "":
            e_dict[e] = x
        alias["emails"] = e_dict

        print(f"Please enter all names/usernames for {identifier} followed by 'enter':")
        n_dict = {}
        while (n:=input()) != "":
            n_dict[n] = x
        alias["names"] = n_dict
    alias["identifiers"] = i_dict

    with open("alias.json", "w") as f:
        json.dump(alias, f)

    return alias

def check_alias(e, n, alias):
    if e in alias["emails"]:
        val = alias["emails"][e]
    elif n in alias["names"]:
        val = alias["names"][n]
    else:
        print(f"\nUnknown email={e} and username={n}. Who is this?")
        for x, i in alias["identifiers"].items():
            print(f"{x}) {i}")
        print("-1) Don't know (discard).")

        val = int(input())

    if val != -1:
        if n != None:
            alias["names"][n] = val
        if e != None:
            alias["emails"][e] = val

    return val