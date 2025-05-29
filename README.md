This is a terminal based ticket system with an integrated CLI. After start, there will be 2 users on default: "Root" and "Admin". You can use the following commands in the terminal:

new usr [username]:  Create a new user

new ticket [name]:  Create a new ticket channel

create [channel]:  Create a new ticket in the ticket channel

perm [user] [permission]:  Grant a user permissions (Admin(admin), Standard(usr), Strict(strict), or ticket-processing(proc1|proc2|proc3))

get [channel]:  Show the contents of a ticket in a channel

show [channel]:  Show a specific amount of tickets in a channel, when entered "all", it shows all

log:  Lets the root user log all actions

-log:  Stop logging

del [user]:  Delete a user

red [channel[ [id] [level]:  Redirect a ticket to a level (1-3 for proc1 to proc3)

logout:  Log out

reply [channel] [id]:  Reply to a ticket

deny [channel] [id]: Automatically deny a ticket

showmsg:  Show all messages

myt [channel] [id]:  Show all info about one of your tickets

myt ls:  Show all of your tickets (may glitch on unstable systems)

root usr [user]:  View username and password of a user (only possible as root user)

root ls usr: Show all users

root reb: Restart the system and clear all stored information

quit:  Stop the process (Information keeps stored)
