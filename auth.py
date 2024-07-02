import pandas as pd
import hashlib

USER_FILE = "users.csv"

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to load users
def load_users():
    try:
        return pd.read_csv(USER_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["username", "password"])

# Function to save users
def save_users(users):
    users.to_csv(USER_FILE, index=False)

# Function to register a new user
def register_user(username, password):
    users = load_users()
    if username in users['username'].values:
        return False, "Username already exists"
    hashed_password = hash_password(password)
    new_user = pd.DataFrame({"username": [username], "password": [hashed_password]})
    users = pd.concat([users, new_user], ignore_index=True)
    save_users(users)
    return True, "Registration successful"

# Function to login a user
def login_user(username, password):
    users = load_users()
    hashed_password = hash_password(password)
    if username in users['username'].values:
        if users.loc[users['username'] == username, 'password'].values[0] == hashed_password:
            return True, "Login successful"
        else:
            return False, "Incorrect password"
    return False, "Username not found"
