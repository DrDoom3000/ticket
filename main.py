import json
import os
from collections import defaultdict, deque

DATA_FILE = "user_data.json"
LOG_FILE = "log_history.txt"

admin_usr = []
admin_passw = []
usr = []
usr_passw = []
usr_perms = []
channels = {}
usr_flag = None
username = None
cmd = None
logging = False
log_history = []
user_msgs = defaultdict(deque)
user_replies = defaultdict(deque) 
ticket_owners = {} 
assigned_tickets = defaultdict(list) 
last_assigned_index = defaultdict(int) 

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "admin_usr": admin_usr,
            "admin_passw": admin_passw,
            "usr": usr,
            "usr_passw": usr_passw,
            "usr_perms": usr_perms,
            "channels": {name: {"counter": ch.counter, "tickets": ch.tickets, "status": ch.status} for name, ch in channels.items()},
            "ticket_owners": list(ticket_owners.items()),
            "user_msgs": {u: list(d) for u, d in user_msgs.items()},
            "user_replies": {u: list(d) for u, d in user_replies.items()},
            "assigned_tickets": {u: list(tks) for u, tks in assigned_tickets.items()},
            "last_assigned_index": dict(last_assigned_index)
        }, f)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            admin_usr[:] = data["admin_usr"]
            admin_passw[:] = data["admin_passw"]
            usr[:] = data["usr"]
            usr_passw[:] = data["usr_passw"]
            usr_perms[:] = data["usr_perms"]
            channels.clear()
            for name, ch_data in data["channels"].items():
                ch = TicketChannel(name)
                ch.counter = ch_data["counter"]
                ch.tickets = ch_data["tickets"]
                ch.status = ch_data["status"]
                channels[name] = ch
            ticket_owners.update({tuple(k): v for k, v in data.get("ticket_owners", [])})
            user_msgs.update({k: deque(v) for k, v in data.get("user_msgs", {}).items()})
            user_replies.update({k: deque(v) for k, v in data.get("user_replies", {}).items()})
            assigned_tickets.update({k: [tuple(t) for t in v] for k, v in data.get("assigned_tickets", {}).items()})
            last_assigned_index.update(data.get("last_assigned_index", {}))

class TicketChannel:
    def __init__(self, name):
        self.name = name
        self.counter = 0
        self.tickets = []
        self.status = "Open"

    def create_ticket(self, content=None, full_open=False):
        if full_open:
            self.status = "Full open"
        if content is None:
            content = input("Enter ticket contents: ")
        ticket = f"{self.counter}: {content} [{self.status}]"
        self.tickets.append(ticket)
        self.counter += 1
        ticket_owners[(self.name, self.counter)] = username
        print(f"Ticket created in channel '{self.name}' with ID {self.counter - 1}")

    def get_ticket(self):
        try:
            ticket_id = int(input("Enter ticket ID to find: "))
            if 0 <= ticket_id < len(self.tickets):
                print(self.tickets[ticket_id])
            else:
                print("Invalid ticket ID")
        except ValueError:
            print("Ticket ID must be a number")

    def print_tickets(self):
        amount = input("Amount of tickets to show: ")
        try:
            start = max(0, len(self.tickets) - int(amount))
            for i in range(start, len(self.tickets)):
                print(self.tickets[i])
        except ValueError:
            if amount == "all":
                for i in range(0, len(self.tickets)):
                    print(self.tickets[i])
            else:
                print("Amount must be a number")

load_data()

def Login():
    global username, usr_flag
    username = input("Please enter your username: ")
    passw = input("Please enter your password: ")

    for i in range(len(admin_usr)):
        if username == admin_usr[i] and passw == admin_passw[i]:
            usr_flag = "admin"
            print("Admin login successful.")
            return True
    for i in range(len(usr)):
        if username == usr[i] and passw == usr_passw[i]:
            usr_flag = usr_perms[i] if i < len(usr_perms) else "usr"
            print(f"User login successful. Permission level: {usr_flag}")
            return True

    print(f"No match for user {username}.")
    usr_flag = None
    return False

def log_command(cmd):
    if logging:
        log_history.append(f"User: {username} Command: {cmd}")
        with open(LOG_FILE, "a") as f:
            f.write(log_history[-1] + "\n")

def CommandPrompt():
    global cmd
    cmd = input(f"${username} ")
    log_command(cmd)
    return True

def check_cmd():
    global usr, usr_passw, usr_perms, usr_flag, admin_passw, admin_usr, channels, logging
    ls_cmd = cmd.strip().split()

    if not ls_cmd:
        return False

    if ls_cmd[0] == "passw" and len(ls_cmd) == 3:
        old_pw, new_pw = ls_cmd[1], ls_cmd[2]
        if username in admin_usr:
            idx = admin_usr.index(username)
            if admin_passw[idx] == old_pw:
                admin_passw[idx] = new_pw
                print("Password updated.")
            else:
                print("Incorrect old password.")
        elif username in usr:
            idx = usr.index(username)
            if usr_passw[idx] == old_pw:
                usr_passw[idx] = new_pw
                print("Password updated.")
            else:
                print("Incorrect old password.")
        save_data()

    if not ls_cmd:
        return False

    if ls_cmd[0] == "new" and usr_flag == "admin":
        if len(ls_cmd) > 2 and ls_cmd[1] == "usr":
            new_user = ls_cmd[2]
            new_pass = input(f"Enter password for new user '{new_user}': ")
            usr.append(new_user)
            usr_passw.append(new_pass)
            usr_perms.append("usr")
            print(f"User '{new_user}' added.")
            save_data()
        elif len(ls_cmd) > 2 and ls_cmd[1] == "ticket":
            chan_name = ls_cmd[2]
            if chan_name not in channels:
                channels[chan_name] = TicketChannel(chan_name)
                print(f"New ticket channel '{chan_name}' created.")
                save_data()
            else:
                print("Channel already exists.")
        else:
            print("Invalid 'new' command usage.")

    elif ls_cmd[0] == "create":
        if len(ls_cmd) > 1:
            chan_name = ls_cmd[1]
            if chan_name in channels:
                if channels[chan_name].status in ["Open", "Full open"] or usr_flag == "admin":
                    full_open = usr_flag == "strict"
                    channels[chan_name].create_ticket(full_open=full_open)
                    save_data()
                else:
                    print("Channel closed or insufficient permission.")
            else:
                print("Channel does not exist.")
        else:
            print("Usage: create [channel]")

    elif ls_cmd[0] == "get":
        if len(ls_cmd) > 1 and ls_cmd[1] in channels:
            channels[ls_cmd[1]].get_ticket()
        else:
            print("Specify valid channel to get ticket from.")

    elif ls_cmd[0] == "show":
        if len(ls_cmd) > 1 and ls_cmd[1] in channels:
            channels[ls_cmd[1]].print_tickets()
        else:
            print("Specify valid channel to show tickets from.")

    elif ls_cmd[0] == "perm" and usr_flag == "admin":
        if len(ls_cmd) > 2:
            target_user, perm = ls_cmd[1], ls_cmd[2]
            if perm in ["admin", "usr", "strict", "proc1", "proc2", "proc3"]:
                if target_user in usr:
                    idx = usr.index(target_user)
                    usr_perms[idx] = perm
                    if perm == "admin" and target_user not in admin_usr:
                        admin_usr.append(target_user)
                        admin_passw.append(usr_passw[idx])
                    print(f"Permission of '{target_user}' set to {perm}.")
                    save_data()
                else:
                    print("User not found.")
            else:
                print("Invalid permission type.")
        else:
            print("Usage: perm [username] [admin|usr|strict|proc1|proc2|proc3]")

    elif ls_cmd[0] == "del" and usr_flag == "admin":
        if len(ls_cmd) > 1:
            target = ls_cmd[1]
            if username == "Root" and target in admin_usr:
                idx = admin_usr.index(target)
                admin_usr.pop(idx)
                admin_passw.pop(idx)
                print(f"Admin '{target}' deleted.")
                save_data()
            elif target in usr:
                idx = usr.index(target)
                usr.pop(idx)
                usr_passw.pop(idx)
                usr_perms.pop(idx)
                print(f"User '{target}' deleted.")
                save_data()
            else:
                print("User not found or insufficient permissions.")

    elif ls_cmd[0] == "status" and len(ls_cmd) == 3:
        chan, mode = ls_cmd[1], ls_cmd[2]
        if chan in channels and usr_flag == "admin":
            if mode in ["open", "full", "pause", "close"]:
                channels[chan].status = {
                    "open": "Open",
                    "full": "Full open",
                    "pause": "Paused",
                    "close": "Closed"
                }[mode]
                print(f"Channel '{chan}' status set to {channels[chan].status}.")
                save_data()
            else:
                print("Invalid mode.")

    elif ls_cmd[0] == "log" and username == "Root":
        logging = True
        print("Logging started.")

    elif ls_cmd[0] == "-log" and username == "Root":
        logging = False
        print("Logging stopped. History:")
        for entry in log_history:
            print(entry)
        log_history.clear()

    elif ls_cmd[0] == "logout":
        return True

    elif ls_cmd[0] == "quit":
        exit()

    elif ls_cmd[0] == "root" and username == "Root":
        if ls_cmd[1] == "usr":
            target = ls_cmd[2]
            if target in usr:
                idx = usr.index(target)
                print(f"User: {usr[idx]} \nPassword: {usr_passw[idx]}")
            elif target in admin_usr:
                idx = admin_usr.index(target)
                print(f"Admin: {admin_usr[idx]} \nPassword: {admin_passw[idx]}")
        elif ls_cmd[1] == "ls":
            if ls_cmd[2] == "usr":
                for i in usr:
                    print(f"User: {i}")
            elif ls_cmd[2] == "admin":
                for i in admin_usr:
                    print(f"Admin User: {i}")
            elif ls_cmd[2] == "all":
                for i in usr:
                    print(f"User: {i}")
                for i in admin_usr:
                    print(f"Admin User: {i}")
          
        elif ls_cmd[1] == "reb":
            confirm = input("Reset everything? This cannot be undone (y/n): ")
            if confirm.lower() == "y":
                usr.clear()
                usr_passw.clear()
                usr_perms.clear()
                user_replies.clear()
                user_msgs.clear()
                admin_usr.clear()
                admin_passw.clear()
                admin_usr = ["Admin", "Root"]
                admin_passw = ["123", "abc"]
                usr_perms = ["admin", "admin"]
                channels.clear()
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                if os.path.exists(LOG_FILE):
                    os.remove(LOG_FILE)
                print("System reset complete.")
                save_data()

    elif ls_cmd[0] == "red" and usr_flag == "admin":
        if len(ls_cmd) == 4:
            chan, ticket_id_str, level = ls_cmd[1], ls_cmd[2], ls_cmd[3]
            if chan not in channels:
                print("Channel not found.")
            elif level not in ["1", "2", "3"]:
                print("Invalid complexity level. Use 1, 2, or 3.")
            else:
                try:
                    ticket_id = int(ticket_id_str)
                    ticket = channels[chan].tickets[ticket_id]
                except (ValueError, IndexError):
                    print("Invalid ticket ID.")
                    return False
                perm_target = f"proc{level}"
                matching_users = [usr[i] for i in range(len(usr)) if usr_perms[i] == perm_target]
                if matching_users:
                    print(f"Redirecting ticket {ticket_id} from '{chan}' to users with permission '{perm_target}':")
                    print(f"Ticket: {ticket}")
                    for user in matching_users:
                        print(f"> Sent to: {user}")
                        user_msgs[(user)].append(f"Ticket {ticket_id} from {chan} was redirected to you")
                else:
                    print(f"No users found with permission '{perm_target}'.")
        else:
            print("Usage: red [channel] [ticket_id] [complexity-level]")
    
    elif ls_cmd[0] == "msg" and usr_flag in ["proc1", "proc2", "proc3"]:
        msg(ls_cmd[1] if len(ls_cmd) > 1 else None)

    elif ls_cmd[0] == "reply" and usr_flag in ["proc1", "proc2", "proc3", "admin"]:
        if len(ls_cmd) > 1:
            reply(ls_cmd[1])
        else:
            print("Usage: reply [username]")

    elif ls_cmd[0] == "showmsg" and not usr_flag == "usr":
        if len(ls_cmd) == 1:
            showmsg()
        else:
            print("Usage: showmsg")

    elif ls_cmd[0] == "stat" and not usr_flag == "usr":
        stat(ls_cmd[1], ls_cmd[2], ls_cmd[3])

    elif ls_cmd[0] == "deny" and usr_flag != "usr":
        if len(ls_cmd) > 2:
            deny(ls_cmd[1], ls_cmd[2])
        else:
            print("Usage: deny [channel] [ticket_id]")

    elif ls_cmd[0] == "myt":
        try:
            if not ls_cmd[1] == "ls":
                myt(ls_cmd[1], ls_cmd[2])
            else:
                myt_ls()
        except:
            print("Usage: myt [channel] [id]")
def msg(channel=None):
    for t in assigned_tickets.get(username, []):
        if channel is None or t[0] == channel:
            print(f"{t[0]} Ticket {t[1]}: {channels[t[0]].tickets[t[1]]}")

def reply(user):
    text = input("Enter reply text: ")
    user_replies[user].appendleft(text)
    print("Reply sent.")

def showmsg():
    for msg in user_msgs.get(username, []):
        print(msg)

def stat(channel, ticket_id, status):
    if status not in ["Open", "In Work", "Solved"]:
        print("Invalid status")
        return
    ticket = channels[channel].tickets[int(ticket_id)]
    content = ":".join(ticket.split(":")[1:]).split("[")[0].strip()
    channels[channel].tickets[int(ticket_id)] = f"{ticket_id}: {content} [{status}]"
    print(f"Ticket {ticket_id} status set to {status}")

def deny(channel, ticket_id):
    stat(channel, ticket_id, "Request Denied")
    owner = ticket_owners.get((channel, int(ticket_id)))
    if owner:
        user_replies[owner].appendleft("Request Denied")
        print("User notified.")

def myt(channel, ticket_id):
    if ticket_owners.get((channel, int(ticket_id))) == username:
        print(channels[channel].tickets[int(ticket_id)])
        for reply in list(user_replies[username])[:5]:
            print(f"Reply: {reply}")
    else:
        print("You didn't create this ticket.")

def myt_ls(limit=None):
    created = [(ch, i) for (ch, i), u in ticket_owners.items() if u == username]
    if limit:
        created = created[-int(limit):]
    for ch, i in created:
        print(f"{ch} Ticket {i}: {channels[ch].tickets[i]}")

#Main
while True:
    while True:
        if not Login():
            break
        save_data()
        while True:
            if not CommandPrompt():
                break
            if check_cmd():
                save_data()
                print("Logged out.")
                break

