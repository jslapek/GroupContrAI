from structures import GitData, ChatData, EmailData, StudentData, TeamData
from numbers import Number
import matplotlib.pyplot as plt

def print_table(arr, width):
    for r in range(len(arr[0])):
      print("   " if r==0 else f"{r}) ", end="")
      for c in range(len(arr)):
        if isinstance(arr[c][r], Number):
          arr[c][r] = f"{arr[c][r]:.2f}"
        out = str(arr[c][r])[:width-1]
        print(out, end=" "*(width-len(out)))
      print("")

def display_menu(team, alias):
    # team_avg, user_1, ..., user_z
    width = 12
    contribution, interaction = team.calc_summary(exclude=-1)

    print("\n" + "-"*20 + " TEAM DATA " + "-"*20)
    print("-- CONTRIBUTION --")
    c_cols = [["x"*(width-1)] + list(contribution.keys())]
    c_cols.append(["Team Avg."] + list(contribution.values()))
    for x in range(1, team.size+1):
      s = team.students[x]
      c_cols.append([alias["identifiers"][str(x)]] + list(s.contribution.values()))
    print_table(c_cols, width)

    width = 20
    print("\n-- INTERACTION --")
    i_cols = [["x"*(width-1)] + list(interaction.keys())]
    i_cols.append(["Team Avg."] + list(interaction.values()))
    for x in range(1, team.size+1):
      s = team.students[x]
      i_cols.append([alias["identifiers"][str(x)]] + list(s.interaction.values()))
    print_table(i_cols, width)

    while True:
      print("\nSelect an option:")
      print("1) View a specific metric")
      print("2) View a specific user")
      inp = input()
      if inp == "1":
        print("\nSelect the category:")
        print("1) Contribution")
        print("2) Interaction")
        cat = input()
        print("\nEnter the number of the metric:")
        metric = int(input())
        x_label = "Subjects"
        if cat == "1":
          y_label = c_cols[0][metric]
          values = [float(c_cols[x][metric]) for x in range(1, len(c_cols))]
          labels = [c_cols[x][0] for x in range(1, len(c_cols))]
          title = y_label + " Team Scores"
        elif cat == "2":
          y_label = i_cols[0][metric]
          values = [float(i_cols[x][metric]) for x in range(1, len(i_cols))]
          labels = [i_cols[x][0] for x in range(1, len(i_cols))]
          title = y_label + " Team Scores"
        visualise_bar(labels, values, x_label, y_label, title)
      elif inp == "2":
        display_indiv_menu(team, alias, c_cols, i_cols)

def display_indiv_menu(team, alias, c_cols, i_cols):
    print("\n" + "-"*20 + " USER DATA " + "-"*20)
    print("--- USER SELECTION")
    print("Choose which student's data you would like to look at:")
    for i in range(1, team.size + 1):
        print(f"{i}) {alias['identifiers'][str(i)]}")
    inp = int(input())
    s = team.students[inp]    
    contribution, interaction = team.calc_summary(exclude=inp)

    width = 20
    print("\n-- CONTRIBUTION --")
    c_cols = c_cols[:2]
    c_cols.append(["Team Avg. w/ " + alias["identifiers"][str(inp)]] + list(contribution.values()))
    c_cols.append([alias["identifiers"][str(inp)]] + list(team.students[inp].contribution.values()))
    print_table(c_cols, width)

    width = 25
    print("\n-- INTERACTION --")
    i_cols = i_cols[:2]
    i_cols.append(["Team Avg. w/ " + alias["identifiers"][str(inp)]] + list(interaction.values()))
    i_cols.append([alias["identifiers"][str(inp)]] + list(team.students[inp].interaction.values()))
    print_table(i_cols, width)

    while True:
      print("\nSelect an option:")
      print("1) Return to team data")
      print("2) Display a metric")
      print("3) View contribution over time")
      
      inp = input()
      if inp == "1":
        display_menu(team, alias)
      if inp == "2":
        print("\nSelect the category:")
        print("1) Contribution")
        print("2) Interaction")
        cat = input()
        print("\nEnter the number of the metric:")
        metric = int(input())
        x_label = "Subjects"
        if cat == "1":
          y_label = c_cols[0][metric]
          values = [c_cols[x][metric] for x in range(1, len(c_cols))]
          labels = [c_cols[x][0] for x in range(1, len(c_cols))]
          title = y_label + " Indiv. Score"
        elif cat == "2":
          y_label = i_cols[0][metric]
          values = [i_cols[x][metric] for x in range(1, len(i_cols))]
          labels = [i_cols[x][0] for x in range(1, len(i_cols))]
          title = y_label + " Indiv. Score"
        visualise_bar(labels, values, x_label, y_label, title)
      if inp == "3":
        s.git.display_cumulative()

def visualise_bar(labels, values, x_label, y_label, title):
    values = [float(x) for x in values]

    fig, ax = plt.subplots()
    bars = ax.bar(labels, values)

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    for b in bars:
      h = b.get_height()
      ax.annotate(f"{h}", (b.get_x()+b.get_width()/2, h),
                  ha="center", va="bottom", textcoords="offset points", xytext=(0,3))

    plt.tight_layout()
    plt.show()
