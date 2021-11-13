'''
Vk сводка последних писем на e-mail адресс
by ArtAnichkin
2021
Реализовано: получение по рассписанию данных e-mail сообщений по протоколу IMAP.
Вытягивание адресов отправителей.
Отправка сформированного сообщения по Vk API через бота на личную страницу.
'''

import imaplib
import email
import time
import vk_api
from random import randint

login = 'mymail@mail.ru'  #логин пароль просматриваемой почты  
password = 'password'  
imap_serv = 'imap.mail.ru'  #imap сервер почты  
token = 'my_vk_group_token'  #token группы вк, которая будет отправлять сообщение  
vk_user_id = 'my_vk_id'  #id vk куда будет отправляться сообщение  

alarm_list = ('13:44:00','18:00:00')  #список времен проверки сообщений  

vk = vk_api.VkApi(token = token)

def write_vk_msg(vk_user_id, message):
    vk.method('messages.send', {
        'user_id' : vk_user_id,
        'message'  : message,
        'random_id': randint(0, 10**8)
        })


def main():
    try:
        box = imaplib.IMAP4_SSL(imap_serv)
        box.login(login, password)
        while True:
            if (lambda alarm_list: time.asctime().split()[3] in alarm_list)(alarm_list):
                #Захват списка id непрочитанных сообщений.
                box.list()
                box.select("inbox")
                letters = box.search(None, "UNSEEN")[1] 
                id_list = letters[0].split()

                vk_message = str()
                #Развертка списка начиная с нового сообщения, извлечение адреса и его запись.
                for i in range(len(id_list) - 1, -1, -1):
                    letter = id_list[i]
                    data = box.fetch(letter, "(RFC822)")[1]
                    raw_email = data[0][1]
                    raw_email_string = raw_email.decode('utf-8')
                    email_data = email.message_from_string(raw_email_string)
                    vk_message += email.utils.parseaddr(email_data['From'])[1] 

                if vk_message != '':
                    vk_message = 'Новые сообщения от:\n\n' + vk_message + '\n'
                    write_vk_msg(vk_user_id, vk_message)
    finally:
        box.logout()

if __name__ == "__main__":
	main()