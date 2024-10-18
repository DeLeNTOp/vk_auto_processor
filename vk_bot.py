import time
import datetime
import vk_api
import random
import os

# Конфигурация
config = {
    'token': os.environ.get('VK_TOKEN'),  # Используем переменную окружения
    'group_id': '-227708791',
    'cooldown_like': 5,
    'cooldown_comment': 20,
    'user_id': 425597417  # Замените на свой ID
}

vk_session = vk_api.VkApi(token=config['token'])
vk = vk_session.get_api()

# Предзаданные комментарии
default_comments = [
    "Хахвахвха",
    "Имбаа",
    "имба",
    "крутой пост",
    "Пуджик тута",
    "Пуджик тут",
    "Лайк подписка"
]

def get_time():
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")

def check_wall_access(owner_id):
    try:
        vk.wall.get(owner_id=owner_id, count=1)
        return True
    except vk_api.exceptions.ApiError as e:
        if e.code == 15:
            print(f"{get_time()} Ошибка: доступ к стене отключен для owner_id {owner_id}")
        else:
            print(f"{get_time()} Ошибка API при проверке доступа: {e}")
        return False

def collect_comments(owner_id, post_id):
    try:
        comments = vk.wall.getComments(owner_id=owner_id, post_id=post_id)
        return [comment['text'] for comment in comments['items']]
    except vk_api.exceptions.ApiError:
        return []  # Возвращаем пустой список, если ошибка доступа к комментариям

def generate_comment(comment):
    synonyms = {
        'хороший': ['отличный', 'замечательный', 'прекрасный'],
        'плохой': ['ужасный', 'негодный', 'плохой'],
        'интересный': ['захватывающий', 'увлекательный'],
        'легкий': ['простой', 'несложный'],
        'грустный': ['печальный']
    }
    
    words = comment.split()
    new_words = [random.choice(synonyms.get(word, [word])) for word in words]
    
    return ' '.join(new_words)

def leave_comment(owner_id, post_id, message):
    try:
        vk.wall.createComment(owner_id=owner_id, post_id=post_id, message=message)
        print(f"{get_time()} Оставлен комментарий: {message}")
        time.sleep(config['cooldown_comment'])
    except vk_api.exceptions.ApiError as e:
        print(f"{get_time()} Ошибка API при оставлении комментария: {e}")

def find_user_comment(owner_id, post_id):
    comments = vk.wall.getComments(owner_id=owner_id, post_id=post_id)
    for comment in comments['items']:
        if comment['from_id'] == config['user_id']:
            return True
    return False

def process_new_posts(auto_like=1):
    last_post_id = None
    last_check_time = time.time()

    while True:
        response = vk.wall.get(owner_id=config['group_id'], count=2)
        if response['items']:
            new_post = response['items'][1] if len(response['items']) > 1 else None

            if new_post:
                post_id = new_post['id']
                owner_id = new_post['owner_id']

                if check_wall_access(owner_id):
                    if last_post_id is None or post_id != last_post_id:
                        if auto_like == 1:
                            try:
                                vk.likes.add(type='post', owner_id=owner_id, item_id=post_id)
                                print(f"{get_time()} Лайкнут пост: {post_id}")
                                time.sleep(config['cooldown_like'])
                            except vk_api.exceptions.ApiError as e:
                                print(f"{get_time()} Ошибка API при лайке: {e}")

                        if not find_user_comment(owner_id, post_id):
                            comments = collect_comments(owner_id, post_id)

                            if comments and len(comments) >= 2:
                                combined_comment = " ".join(random.sample(comments, 2))
                                new_comment = generate_comment(combined_comment)
                                leave_comment(owner_id, post_id, new_comment)
                            else:
                                random_comment = random.choice(default_comments)
                                leave_comment(owner_id, post_id, random_comment)

                        last_post_id = post_id
                        last_check_time = time.time()
            else:
                if time.time() - last_check_time > 120 and last_post_id is not None:
                    random_comment = random.choice(default_comments)
                    leave_comment(config['group_id'], last_post_id, random_comment)
                    last_check_time = time.time()

        time.sleep(5)

if __name__ == "__main__":
    print("Запуск скрипта для автолайка и автокомментирования...")
    auto_like = 1  # Автоматический лайк включен по умолчанию
    process_new_posts(auto_like)
