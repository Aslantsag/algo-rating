import json
import requests
from bs4 import BeautifulSoup

LOGIN = 'YOUR LOGIN'
PASSWORD = 'YOUR PASSWORD'
USER_AGENT = 'RANDOM USER AGENT'

class Export:
    url_main = 'https://backoffice.algoritmika.org'
    url_schedule = 'https://backoffice.algoritmika.org/group/default/schedule'
    url_login = 'https://backoffice.algoritmika.org/s/auth/api/e/user/auth'
    url_group = 'https://backoffice.algoritmika.org/api/v2/group/index'
    url_group_students = 'https://backoffice.algoritmika.org/api/v2/group/student/index?expand=lastGroup&groupId='

    def __init__(self):
        self.client = requests.session()
        response = self.auth()
        if response == 200:
            print("Auth success!")
        else:
            print("Auth error!", response)

    def auth(self):
        print("Auth process...")
        data = {
            'login': LOGIN,
            'password': PASSWORD,
        }

        headers = {
            'User-Agent': USER_AGENT,
            'Referer': self.url_main,
        }

        request = self.client.post(self.url_login, data=data, headers=headers)
        return request.status_code

    def get_group_keys(self):
        request = self.client.get(self.url_group)
        response = json.loads(request.text)
        keys = []
        for group in response['data']['items']:
            if group['status'] == 'active' and group['title'].find('МК') == -1:
                keys.append((group['id'], group['title']))
        return keys

    def get_group_weekday(self, key):
        request = self.client.get(self.url_schedule)
        soup = BeautifulSoup(request.text, 'html.parser')
        days_list = []
        rows = soup.find_all('tr', attrs={'data-key': key})
        for tr in rows:
            days_list.append(tr.find('td', attrs={'data-col-seq': 'weekday'}).text.upper())
        return days_list

    def get_group_data(self):
        print("Trying to get group data...")
        keys = self.get_group_keys()
        data = {}
        for i in range(len(keys)):
            students = []
            request = self.client.get(self.url_group_students + str(keys[i][0]))
            response = json.loads(request.text)
            for student in response['data']['items']:
                if keys[i][0] == student['lastGroup']['id'] and student['lastGroup']['status'] == 0:
                    students.append(student['fullName'])
            group_days = " ".join(self.get_group_weekday(keys[i][0]))
            data[group_days + " " + keys[i][1]] = students
        return data


if __name__ == '__main__':
    exp = Export()
    try:
        with open('data.json', 'w') as file:
            json.dump(exp.get_group_data(), file, ensure_ascii=False, indent=4)
            print("Success!)) The result - 'data.json' file.")
    except requests.exceptions.HTTPError as err:
        print("HTTP Error:", err)
    except requests.exceptions.ConnectionError as err:
        print("Error Connecting:", err)
    except requests.exceptions.Timeout as err:
        print("Timeout Error:", err)
    except requests.exceptions.RequestException as err:
        print("Error!", err)
