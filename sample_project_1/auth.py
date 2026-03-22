def register(username, password):
    users_db[username] = password
    return True

def login(username, password):
    return users_db.get(username) == password
