import requests
import time
import threading

names = []
available = []

with open('names.txt', 'r') as f:
    for line in f:
        names.append(line.strip().replace("'", '').lower())

# reverse and remove duplicates
names.reverse()
names = list(dict.fromkeys(names))

# sends each double check individually to avoid errors with the order of the operation responses
def doubleCheck(name: str):
    try:
        body = requests.post('https://gql.twitch.tv/gql', json=[{
            'operationName': 'UsernameValidator_User',
            'variables': {
                'username': name
            },
            'extensions': {
                'persistedQuery': {
                    'version': 1,
                    'sha256Hash': 'fd1085cf8350e309b725cf8ca91cd90cac03909a3edeeedbd0872ac912f3d660'
                }
            }
        }], headers={
            'Client-Id': 'kimne78kx3ncx6brgo4mv6wki5h1ko'
        }).json()
        
        if not body[0]['data']['isUsernameAvailable']:
            print(f'[{name}] TAKEN')
            return

        print(f'[{name}] AVAILABLE')
        available.append(name)

        with open('available.txt', 'a') as f:
            for name in available:
                f.write(f'{name}\n')

    except Exception as e:
        print(e)
        doubleCheck(name)


def check():
    operations = []
    checkingNames = []
    while len(operations) < 35 and len(names) > 0:
        name = names.pop()
        if not name:
            break

        checkingNames.append(name)
        operations.append({
            'operationName': 'ChannelShell',
            'variables': {
                'login': name
            },
            'extensions': {
                'persistedQuery': {
                    'version': 1,
                    'sha256Hash': '580ab410bcd0c1ad194224957ae2241e5d252b2c5173d8e0cce9d32d5bb14efe'
                }
            }
        })

    if len(operations) == 0:
        return

    try:
        body = requests.post('https://gql.twitch.tv/gql', json=operations, headers={
            'Client-Id': 'kimne78kx3ncx6brgo4mv6wki5h1ko'
        }).json()

        if not body or len(body) == 0:
            raise Exception('No body')

        for d in body:
            user = d['data']['userOrError']

            if not 'reason' in user:
                continue

            reason = user['reason']
            username = user['userDoesNotExist']

            if reason != 'UNKNOWN':
                continue

            threading.Thread(target=doubleCheck, args=(username,)).start()
    except Exception as e:
        print('ERROR:' + e)
        for name in checkingNames:
            names.append(name)


def main():
    print(f'Loaded {len(names)} names, starting now...')

    while len(names) > 0:
        threading.Thread(target=check).start()
        time.sleep(0.1)

    print(f'Found {len(available)} available names')
    print('Finished checking all names')


if __name__ == '__main__':
    main()
