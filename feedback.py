import requests
from bs4 import BeautifulSoup
import urllib.parse
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
import json


class SendFeedback:
    def __init__(self, username, password, satisfaction, comment_1, comment_2):
        self.username = username
        self.password = password
        self.satisfaction = satisfaction
        self.comment_1 = comment_1
        self.comment_2 = comment_2
        disable_warnings(InsecureRequestWarning)
        self.s = requests.Session()
        self.url_list = []
        self.submitted_forms = 0

    def main(self):
        self.login()
        self.questionnaire()
        self.submit_quest()
        return str(self.submitted_forms)

    def login(self):
        r = self.s.get('https://cas.escpeurope.eu/cas/login')
        if r.status_code != 200:
            print('|#### Error getting login page ####|')
            return self.s
        soup = BeautifulSoup(r.text, 'lxml')
        token_raw = soup.find('input', {'name': 'execution'})['value']
        token = urllib.parse.quote(token_raw)

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image"
                      "/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "it-IT,it;q=0.9",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        }
        data = f"username={self.username}&password={self.password}&execution={token}&_eventId=submit&geolocation="
        r = self.s.post("https://cas.escpeurope.eu/cas/login", headers=headers, data=data)

        if r.status_code == 200 and 'Login eseguito correttamente' in str(r.text):
            print(']---- Logged in ----[')
            return self.s
        else:
            print('|#### Error posting login ####|')
            return self.s

    def questionnaire(self):
        r = self.s.get('https://ent.escpeurope.eu/en/StudentDashboard/Grades/index?_dc=168363656383'
                  '7&page=1&start=0&limit=25', verify=False)
        if r.status_code != 200:
            print('|#### Error getting grades ####|')
            return
        data = json.loads(r.text)['result']
        for i in data:
            try:
                quest_list = i['Quest']
                for a in quest_list:
                    url = 'https://ent.escpeurope.eu' + a['url'].split('href=\"')[1].split('\">')[0]
                    self.url_list.append(url)
            except:
                pass
        return

    def submit_quest(self):
        print(self.url_list)
        for i in self.url_list:
            r = self.s.get(i)
            soup = BeautifulSoup(r.text, 'lxml')
            title = soup.find('div', {'class': 'panel-body'}).text.strip().split('feedback')[1]
            token = soup.find('input', {'name': 'csrf'})['value'].strip()

            q742 = urllib.parse.quote_plus(self.comment_1)
            q743 = urllib.parse.quote_plus(self.comment_2)

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,i"
                          "mage/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "it-IT,it;q=0.9",
                "cache-control": "max-age=0",
                "content-type": "application/x-www-form-urlencoded",
                "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1"
            }
            data = f"q742={q742}&q743={q743}&q752={self.satisfaction}&q744={self.satisfaction}&q745={self.satisfaction}&q746=&q747={self.satisfaction}&q748={self.satisfaction}&q" \
                   f"749={self.satisfaction}&q750={self.satisfaction}&q751={self.satisfaction}&csrf={token}&send=Submit"
            r = self.s.post(i, headers=headers, data=data)
            if 'The form submitted did not originate from the expected site' not in str(r.text):
                self.submitted_forms += 1
                print(']---- Form sent ----[')
            else:
                print('|#### Error submitting form ####|')
                return

