import requests
from bs4 import BeautifulSoup
import urllib.parse
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings
import json
from datetime import datetime
from dhooks import *


def main():
    username = 'e213810'
    password = 'Adele1921.'
    disable_warnings(InsecureRequestWarning)
    s = requests.Session()
    login(username, password, s)
    choice = gui()
    url_list = questionnaire(s)
    submit_quest(s, url_list, choice, username)


def gui():
    print('[0] Full auto')
    print('[1] Semi-auto (you will have to select the satisfactory level for each subject)')
    print('[2] Open-manual (Semi-auto and you will have to answer to open questions)')
    choice = int(input('Chioce: '))
    return choice


def login(username, password, s):
    r = s.get('https://cas.escpeurope.eu/cas/login')
    if r.status_code != 200:
        print('|#### Error getting login page ####|')
        return s
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
    data = f"username={username}&password={password}&execution={token}&_eventId=submit&geolocation="
    r = s.post("https://cas.escpeurope.eu/cas/login", headers=headers, data=data)

    if r.status_code == 200 and 'Login eseguito correttamente' in str(r.text):
        print(']---- Logged in ----[')
        return s
    else:
        print('|#### Error posting login ####|')
        return s


def questionnaire(s):
    r = s.get('https://ent.escpeurope.eu/en/StudentDashboard/Grades/index?_dc=168363656383'
              '7&page=1&start=0&limit=25', verify=False)
    if r.status_code != 200:
        print('|#### Error getting grades ####|')
        return
    data = json.loads(r.text)['result']

    url_list = []
    for i in data:
        try:
            quest_list = i['Quest']
            for a in quest_list:
                url = 'https://ent.escpeurope.eu' + a['url'].split('href=\"')[1].split('\">')[0]
                url_list.append(url)
        except:
            pass
    return url_list


def submit_quest(s, url_list, choice, username):
    sat = ''
    if choice == 0:
        sat = gui2('Overall selection.')
    for i in url_list:
        r = s.get(i)
        soup = BeautifulSoup(r.text, 'lxml')
        title = soup.find('div', {'class': 'panel-body'}).text.strip().split('feedback')[1]
        token = soup.find('input', {'name': 'csrf'})['value'].strip()
        q1 = soup.find('label', {'for': 'q742'}).text.split('?')[0].strip()
        q2 = soup.find('label', {'for': 'q743'}).text.split('?')[0].strip()

        if choice == 1 or choice == 2:
            sat = gui2(title)

        if choice == 2:
            q742_raw = str(input(q1 + ': '))
            q743_raw = str(input(q2 + ': '))
            q742 = urllib.parse.quote_plus(q742_raw)
            q743 = urllib.parse.quote_plus(q743_raw)
        else:
            q742_raw = 'The subject areas.'
            q743_raw = 'None, the course is very well done.'
            q742 = urllib.parse.quote_plus(q742_raw)
            q743 = urllib.parse.quote_plus(q743_raw)

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
        data = f"q742={q742}&q743={q743}&q752={sat}&q744={sat}&q745={sat}&q746=&q747={sat}&q748={sat}&q" \
               f"749={sat}&q750={sat}&q751={sat}&csrf={token}&send=Submit"
        r = s.post(i, headers=headers, data=data)
        if 'The form submitted did not originate from the expected site' not in str(r.text):
            print(']---- Form sent ----[')
            send_hook(title, choice, i, username)
        else:
            print('|#### Error submitting form ####|')
            return


def gui2(title):
    print('\n' + title)
    print('[0] Very bad')
    print('[1] Bad')
    print('[2] Good')
    print('[3] Very good')
    print('[4] Neutral')
    choice = int(input('Choose the degree of satisfaction of the overall course: '))
    return choice+1


def send_hook(title, mode, url, username):
    if mode == 0:
        mode = 'Full auto'
    elif mode == 1:
        mode = 'Semi-auto'
    else:
        mode = 'Open-manual'
    now = str(datetime.utcnow().strftime('%d-%m-%Y'))
    hook = Webhook(
        'https://discord.com/api/webhooks/801844941781073940/8sYwB54PmyK7dp6YA'
        'g-YHvz3V1pG887gyKHu35wHGbK29MI4gx7g4tP1AWMgGnQV4WsI')
    embed = Embed(
        color=0x202020
    )
    embed.set_title(title=title)
    embed.set_author(name=f"PiedeAIO - {username}",
                     icon_url="https://cdn.discordapp.com/attachments/799962707377127444"
                              "/990984201664888912/bartFoto.PNG")
    embed.add_field(name="University", value="ESCP")
    embed.add_field(name="Mode", value=mode)
    embed.add_field(name="Feedback", value=f"[Here]({url})")
    embed.set_footer(text=f"{now} • Powered by @PiedeAIO",
                     icon_url="https://cdn.discordapp.com/attachments/799962707377127444"
                              "/990984201664888912/bartFoto.PNG")
    hook.send(embed=embed)


main()
