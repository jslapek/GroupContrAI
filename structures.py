import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
from dateutil import parser
from git import Repo
from collections import defaultdict
import json
from alias import check_alias
from numbers import Number

class Evidence:
    f_type = ""
    path = None

    def __init__(self, f_type, path):
        self.f_type = f_type
        self.path = path

class ChatData:
    msg_count = 0
    char_count = 0
    msg_char_ratio = 0.0
    longest_silence = 0
    avg_interval = 0
    skew = 0

    def __init__(self, data):
        if data == None:
            return
        self.msg_count = data[1]["msg_count"]
        self.char_count = data[1]["char_count"]
        self.msg_char_ratio = self.char_count / self.msg_count

        intervals = [parser.parse(d) for d in data[1]["timestamps"]]

class EmailData:
    send_count = 0
    rcv_count = 0
    avg_response_time = 0
    diversity = 0

    def __init__(self, data):
        if data == None:
            return
        self.send_count = data[1]["send_count"]
        self.rcv_count = data[1]["rcv_count"]

class GitData:
    timestamps = []
    intervals = []

    commits = 0
    line_count = 0
    avg_interval = 0
    weighted_avg_time = 0
    weighted_skew = 0
    # gini_inequality = 0

    def __init__(self, data):
        if data == None:
            return
        self.identifier = data[0]
        self.commits = data[1]["commits"]
        self.line_count = data[1]["count"]
        self.timestamps = sorted(data[1]["timestamps"], key=lambda x:x[1])

        # get intervals
        for i in np.arange(1, len(self.timestamps)):
            self.intervals.append(self.timestamps[i][1] - self.timestamps[i-1][1])
        self.avg_interval = sum(i.total_seconds() for i in self.intervals) / len(self.intervals)

        self.weighted_skew, self.weighted_avg_time = self.calculate_skew(self.timestamps)

    def calculate_skew(self, timestamps):
        counts, times = map(list, zip(*self.timestamps))
        times = pd.to_datetime(times, utc=True)
        counts = np.abs(counts)

        t0, t1 = times.min(), times.max()
        span = (t1 - t0).total_seconds()
        if span == 0:
            return 0, t0

        x = (times - t0).total_seconds() / span
        c_sum = counts.sum()
        mu = np.sum(x * counts) / c_sum
        xc = x - mu
        m2 = np.sum(counts * xc**2) / c_sum
        m3 = np.sum(counts * xc**3) / c_sum
        skew = 0 if m2 <= 0 else m3 / (m2 ** 1.5)

        weighted_avg_time = t0 + timedelta(seconds=mu*span)
        return skew, weighted_avg_time

    def display_cumulative(self):
        counts, times = map(list, zip(*self.timestamps))
        for i in np.arange(1, len(counts)):
            counts[i] += counts[i-1]
        plt.plot(times, counts)
        plt.gcf().autofmt_xdate()
        plt.xlabel("Time")
        plt.ylabel("Cumulative Lines of Code")
        plt.title(f"LoC over Time")
        plt.show()

class StudentData:
    student_id = 0
    git = GitData(None)
    chat = ChatData(None)
    email = EmailData(None)
    contribution = {} 
    interaction = {}

    def __init__(self, sid):
        self.student_id = sid
        self.contribution = {"Commits":0, "Line Count":0}
        self.interaction = {"Avg. Interval":0, 
                    #    "Weighted Avg. Time":0,
                       "Avg. Weighted Skew":0,
                       "Chat Msg Count":0,
                       "Chat Avg. Msg Length":0,
                       "Chat Avg. Interval":0,
                       "Chat Skew":0,
                       "Email Count":0,
                       "Email Avg. Resp. Time":0,
                       "Email Diversity":0}

    def calculate_data(self):
        # git
        self.contribution["Commits"] = self.git.commits
        self.contribution["Line Count"] = self.git.line_count
        self.interaction["Avg. Interval"] = self.git.avg_interval
        # self.interaction["Weighted Avg. Time"] = self.git.weighted_avg_time
        self.interaction["Avg. Weighted Skew"] = self.git.weighted_skew

        # chat
        self.interaction["Chat Msg Count"] = self.chat.msg_count
        self.interaction["Chat Avg. Msg Length"] = self.chat.msg_char_ratio
        self.interaction["Chat Avg. Interval"] = self.chat.avg_interval
        self.interaction["Chat Skew"] = self.chat.skew

        # email
        self.interaction["Email Count"] = self.email.send_count
        self.interaction["Email Avg. Resp. Time"] = self.email.avg_response_time
        self.interaction["Email Diversity"] = self.email.diversity

class TeamData:
    students = {}
    size = 0

    # evidence
    git = []
    chat = []
    emails = []
    text = []

    def __init__(self, evidence, alias):
        # create students
        for id_num, name in alias["identifiers"].items():
            self.students[int(id_num)] = StudentData(id_num)
        self.size = len(self.students)

        # compile evidence
        for e in evidence:
            if e.f_type == "git":
                self.git.append(e)
            elif e.f_type == "chat":
                self.chat.append(e)
            elif e.f_type == "email":
                self.emails.append(e)
            elif e.f_type == "text":
                self.text.append(e)
            # TODO: other file types

        # calculate individual evidence-specific stats 
        for stat in self.git_stats(alias):
            self.students[stat[0]].git = GitData(stat)
        for stat in self.chat_stats(alias):
            self.students[stat[0]].chat = ChatData(stat)
        for stat in self.email_stats(alias):
            self.students[stat[0]].email = EmailData(stat)

        # calculate team stats
    
    def calc_summary(self, exclude):
        size = self.size
        
        contributions = []
        interactions = []
        for x in range(1, self.size+1):
            if x == exclude:
                size -= 1
                continue
            s = self.students[x]
            s.calculate_data()
            contributions.append(s.contribution)
            interactions.append(s.interaction)

        return self.mean_dicts(contributions, size), self.mean_dicts(interactions, size)

    def mean_dicts(self, dicts, size):
        sums = defaultdict(float)

        for d in dicts:
            for k, v in d.items():
                if not isinstance(v, Number):
                    v = v.timestamp()
                sums[k] += v

        return {k: (sums[k] / size) for k in sums}

    def chat_stats(self, alias):
        stats = defaultdict(lambda: dict(msg_count=0, char_count=0, timestamps=[]))

        hdrs = {
            "text" : ("body", "content", "message"),
            "date" : ("date", "datetime", "timestamp")
        }

        for c_f in self.chat:
            with open(c_f.path, "r", encoding="utf-8") as f:
                c = json.load(f)["messages"]

            for m in c:
                f = lambda x: x in m
                g = lambda x: m[next(filter(f, hdrs[x]), None)]
                text = g("text")
                date = g("date")
                # TODO: make this compatible for chats other than discord
                name = m["author"]["name"]

                val = check_alias(None, name, alias)
                if val == -1:
                    continue

                stats[val]["msg_count"] += 1
                stats[val]["char_count"] += len(text)
                stats[val]["timestamps"].append(date)
                
        return stats.items()



    def email_stats(self, alias):
        stats = defaultdict(lambda: dict(send_count=0, 
                                         rcv_count=0, 
                                         send_tstamps={i:[] for i in range(1, self.size)},
                                         rcv_tstamps={i:[] for i in range(1, self.size)}))

        hdrs = {
            "send" : ("from", "sender"),
            "rcv" : ("to", "receiver"),
            "text" : ("body", "content", "message"),
            "date" : ("date", "datetime", "timestamp")
        }

        for email_f in self.emails:
            with open(email_f.path, "r", encoding="utf-8") as f:
                email = json.load(f)

            f = lambda x: x in email
            g = lambda x: email[next(filter(f, hdrs[x]), None)]
            sender = g("send")
            rcvs = g("rcv")
            text = g("text")
            date = g("date")

            send_val = check_alias(sender, None, alias)
            rcv_vals = [check_alias(rcv, None, alias) for rcv in rcvs]
            if send_val == -1 or -1 in rcv_vals:
                continue
            
            stats[send_val]["send_count"] += 1
            for rcv_val in rcv_vals:
                stats[rcv_val]["rcv_count"] += 1
                stats[send_val]["send_tstamps"][rcv_val].append(date)
                stats[rcv_val]["rcv_tstamps"][send_val].append(date)

        return stats.items()
    
    def git_stats(self, alias):
        stats = defaultdict(lambda: dict(commits=0, count=0, timestamps=[]))

        for git_file in self.git:
            repo = Repo(git_file.path)
            for c in repo.iter_commits():  
                e = c.author.email.lower()
                n = c.author.name.lower()

                val = check_alias(e, n, alias)
                if val == -1:
                    continue

                st = c.stats
                stats[val]["commits"] += 1
                count = st.total["insertions"] - st.total["deletions"]

                stats[val]["count"] += count
                stats[val]["timestamps"].append((count, c.committed_datetime))

        return stats.items()


