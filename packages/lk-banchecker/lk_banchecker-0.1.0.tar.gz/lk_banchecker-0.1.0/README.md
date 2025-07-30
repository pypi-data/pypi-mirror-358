# LK Ban Checker

A simple Python package to check a user's ban status using the lkteam-bancheck API.

## Installation

Install the package using pip:

```py
pip install lk-banchecker```

```py
from lk_banchecker import check_ban

uid_to_check = "12345678"
result = check_ban(uid_to_check)

if "error" in result:
    print(f"An error occurred: {result['error']}")
else:
    is_banned = result.get('banned', False)
    nickname = result.get('nickname', 'N/A')
    print(f"Nickname: {nickname}")
    print(f"Is Banned: {is_banned}")
    if is_banned:
        print(f"Ban Message: {result.get('ban_message')}")

# Example of a non-existent UID or error
error_result = check_ban("9999999999999999999")
print(error_result)```