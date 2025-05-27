import requests


def get_friends(user_id, token):
    response = requests.get(f"https://api.vk.com/method/friends.get?user_id={user_id}&fields=first_name,last_name&access_token={token}&v=5.131")
    data = response.json()

    if 'response' in data:
        # print(data)
        return data['response']['items']
    else:
        return []


def get_user_id(usr, token):
    if usr.isdigit():
        return usr
    else:
        username = usr.split('/')[-1]
        response = requests.get(f"https://api.vk.com/method/users.get?user_ids={username}&access_token={token}&v=5.131")
        data = response.json()
        if 'response' in data and len(data['response']) > 0:
            return str(data['response'][0]['id'])
        else:
            return None



def get_groups(user_id, token):
    response = requests.get(
        f"https://api.vk.com/method/groups.get?user_id={user_id}&extended=1&access_token={token}&v=5.131")
    data = response.json()
    if 'response' in data:
        return data['response']['items']
    else:
        return []

def main():
    token = "8369dfaa8369dfaa8369dfaa22805bbefc883698369dfaaeb5c6a85e72441b8cb639708"
    user_inp = input("введите айди юзера или ссылку на него (например, https://vk.com/saitaiu_x or 535465562) : ")
    user_id = get_user_id(user_inp, token)
    if not user_id:
        print("закрытый профиль или пользователь не найден")
        return


    friends = get_friends(user_id, token)
    if friends:
        print(f"Список друзей пользователя")
        for friend in friends:
            print(f"{friend['first_name']} {friend['last_name']}")
    else:
        print("У пользователя нет друзей или произошла ошибка.")

    print("-------------------------")
    groups = get_groups(user_id, token)
    if groups:
        print(f"Список групп пользователя")
        for group in groups:
            print(f"{group['name']}")
    else:
        print("У пользователя нет групп или произошла ошибка.")

if __name__ == "__main__":
    main()