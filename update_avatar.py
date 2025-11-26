import requests

headers = {'Authorization': 'Bearer test_4'}
data = {'avatar_url': 'http://127.0.0.1:8000/avatars/merve123.jpg'}
response = requests.put('http://127.0.0.1:8000/users/4', json=data, headers=headers)
print('Avatar URL updated to:', response.json()['avatar_url'])
