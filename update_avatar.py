import requests
import sys

API_BASE = 'http://127.0.0.1:8000'

# User avatar mappings
# Note: If user has no specific avatar, they can use generated ones or upload their own
avatar_mappings = {
    1: None,  # ali - no specific avatar file
    2: None,  # ayse - no specific avatar file
    3: None,  # user12 - no specific avatar file
    4: 'merve123.jpg',  # merve123 - has avatar file
    5: 'images.jpg',  # testuser - can use images.jpg
    6: 'images.jpg',  # zeyco - can use images.jpg
}

# Test tokens for each user (you need to generate these or use a valid token)
test_tokens = {
    1: 'test_1',
    2: 'test_2',
    3: 'test_3',
    4: 'test_4',
    5: 'test_5',
    6: 'test_6',
}

def update_user_avatar(user_id, filename, token):
    """Update user avatar URL in database"""
    if not filename:
        print(f"⏭️  User {user_id}: Skipping (no avatar file)")
        return
    
    avatar_url = f'{API_BASE}/avatars/{filename}'
    headers = {'Authorization': f'Bearer {token}'}
    data = {'avatar_url': avatar_url}
    
    try:
        response = requests.put(
            f'{API_BASE}/users/{user_id}',
            json=data,
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ User {user_id}: Avatar updated to {avatar_url}")
            print(f"   Response: {result.get('avatar_url', 'N/A')}")
        else:
            print(f"❌ User {user_id}: Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ User {user_id}: Error - {e}")

# Update all avatars
print("🔄 Updating user avatars in database...\n")
for user_id, filename in avatar_mappings.items():
    token = test_tokens.get(user_id, 'test_default')
    update_user_avatar(user_id, filename, token)

print("\n✅ Avatar update script completed!")
