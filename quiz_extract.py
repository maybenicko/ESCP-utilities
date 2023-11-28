import requests
from bs4 import BeautifulSoup
import threading
import csv
from time import sleep

class QuizExtractor:
    def __init__(self):
        self.user = ''
        self.password = ''
        self.session = requests.Session()
        self.subject_to_get = 'https://escpeurope.blackboard.com/webapps/bb-mygrades-BB5ea86ce51c1ef/myGrades?course_id=_41587_1&stream_name=mygrades&is_stream=false'
        self.quiz_link_intermediate = []
        self.quiz_link = []

    def login(self):
        r = self.session.get('https://escpeurope.blackboard.com/webapps/login/')
        soup = BeautifulSoup(r.text, 'lxml')

        token = soup.find('input', {'name': 'blackboard.platform.security.NonceUtil.nonce.ajax'})['value']

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "it-IT,it;q=0.9",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-ua": "\"Google Chrome\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        }
        body = f"user_id={self.user}&password={self.password}&login=Sign+In&action=login&new_loc=&blackboard.platform.security.NonceUtil.nonce.ajax={token}"
        r = self.session.post("https://escpeurope.blackboard.com/webapps/login/", headers=headers, data=body)

        if str(r.text).split('"batchUid":"')[1].split('"')[0] == self.user:
            print('logged in')
            return

    def get_quiz(self):
        r = self.session.get(self.subject_to_get)
        soup = BeautifulSoup(r.text, 'lxml')
        list_to_filter = soup.find_all('div', {'class': 'cell gradable'})

        for i in list_to_filter:
            if 'onclick' in str(i):
                try:
                    url_quiz = 'https://escpeurope.blackboard.com' + str(i).split("mygrades.loadContentFrame('")[1].split("'")[0].replace('amp;', '')
                    self.quiz_link_intermediate.append(url_quiz)
                except:
                    pass
        print('got quiz links')

    def retrieve_quiz_link(self):
        for i in self.quiz_link_intermediate:
            try:
                r = self.session.get(i)
                link_final = 'https://escpeurope.blackboard.com/webapps/assessment' + str(r.text).split('webapps/assessment')[1].split('"')[0]
                self.quiz_link.append(link_final)
            except:
                pass

    def get_answers(self): # this good just finish getting title - questions - answers
        self.quiz_link.pop(0)
        for i in self.quiz_link:
            r = self.session.get(i)

            soup = BeautifulSoup(r.text, 'lxml')
            title = soup.find('title').text.strip()
            list_questions = soup.find_all('div', {'class': 'details'})
            print(title + '\n')
            for i in list_questions:
                try:
                    data = i.find_all('div', {'class': 'vtbegenerated inlineVtbegenerated'})

                    question = data[0].text.strip()
                    correct_answer = data[1].text.strip()
                    answer_1 = data[2].text.strip()
                    answer_2 = data[3].text.strip()
                    answer_3 = data[4].text.strip()
                    answer_4 = data[5].text.strip()

                    print(question)
                    print('Correct: ' + correct_answer)
                    print('1. ' + answer_1)
                    print('2. ' + answer_2)
                    print('3. ' + answer_3)
                    print('4. ' + answer_4 + '\n')
                except:
                    pass

    def main(self):
        self.login()
        self.get_quiz()
        self.retrieve_quiz_link()
        self.get_answers()

    def start(self):
        with open('data.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            i = 0
            for row in csv_reader:
                i += 1
                if line_count == 0:
                    line_count += 1
                else:
                    sleep(0.03)
                    try:
                        self.user = row[0]
                        self.password = row[1]
                        thread = threading.Thread(target=self.main)
                        thread.start()
                    except Exception as e:
                        pass


bot = QuizExtractor()
bot.start()
