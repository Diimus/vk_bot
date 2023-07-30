import vk_api
from sqlalchemy import create_engine
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

import bd_bot
from config import access_token as a_token, comunity_token as c_token, db_url_object
from bot_root import VkTools

class BotVkInterface():
    def __init__(self, a_token, c_token, engine):
        self.vk = vk_api.VkApi(token=c_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(a_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send',
                        {
                         'user_id': user_id,
                         'message': message,
                         'attachment': attachment,
                         'random_id': get_random_id(),
                        }
                      )

    def get_user_photo(self, worksheets):
        worksheet = self.worksheets.pop()
        photo_string = ''
        for photo in photos:
            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
        return photo_string

# обработка событий / получение сообщений

    def event_info(self):
        
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Салют, {self.params["name"]}.')

                elif command == 'поиск':
                    self.message_send(event.user_id, 'Секундочку...')

                    if self.params.get('city') is None:
                        self.message_send(event.user_id, 'Где находитесь (город необходимо указать).')
                        continue
                    elif self.params.get('bdate') is None:
                        self.message_send(event.user_id, 'Полных лет (необходимо указать).')
                        continue
                    else:
                        self.message_send(event.user_id)
                                                            
                elif command.startswith('город '):
                    city_name = ' '.join(event.text.lower().split()[1:])
                    city = self.vk_tools.__class__(city_name)
                    
                    if city is None:
                        self.message_send(event.user_id, 'Не удалось найти такой город')
                    else:
                        self.params['city'] = self.vk_tools.__class__(city_name)
                        self.message_send(event.user_id)
                                          
                elif command.startswith('возраст '):
                    age = event.text.lower().split()[1]
                    try:
                        age = int(age)
                    except ValueError:
                        self.message_send(event.user_id, 'Необходимо ввести число')
                        continue

                    self.params['bdate'] = age
                    self.message_send(event.user_id)
                    
                elif command == 'показать фото':
    
                    if self.worksheets:
                        photo_string = get_user_photo(worksheets)
                        
                    else:
                        self.worksheets = self.vk_tools.search_worksheet(self.params, self.offset)
                        photo_string = get_user_photo(worksheets)
                        
                    self.offset += 10
                        
                    self.message_send(event.user_id, f'имя: {worksheet["name"]} ссылка: vk.com/{worksheet["id"]}',
                                      attachment=photo_string)
                    
                    if not bd_bot.check_user(engine, event.user_id, worksheet["id"]):
                        bd_bot.add_user(engine, event.user_id, worksheet["id"])
            
                elif command == 'пока':
                    self.message_send(event.user_id, 'До скорой встречи.\nАривидерчи!')
                else:
                    self.message_send(event.user_id, 'Ошибка ввода...')

if __name__ == '__main__':
    engine = create_engine(db_url_object)
    bot_interface = BotVkInterface(a_token, c_token, engine)
    bot_interface.event_info()
