#!/usr/bin/env python3

import ruckus
import pprint

host="https://192.168.1.2"

username="root"
password="changeme"

clients = ruckus.getClients(host, username, password)
for client in clients:
    print(client)
print("len:", len(clients))

