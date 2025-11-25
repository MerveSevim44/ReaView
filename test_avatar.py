#!/usr/bin/env python3
import requests

url = 'http://127.0.0.1:8000/users/4'
response = requests.get(url)
user = response.json()

print('User 4 data:')
print(f'  username: {user.get("username")}')
print(f'  email: {user.get("email")}')
print(f'  bio: {user.get("bio")}')
print(f'  avatar_url: {user.get("avatar_url")}')
print()
print('Full user object:')
for key, value in user.items():
    print(f'  {key}: {value}')
