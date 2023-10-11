import telebot
import requests
import zipfile
import os

bot_token = 'TOKEN'
bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Отправьте мне ссылки на изображения для скачивания.")


@bot.message_handler(func=lambda message: True)
def process_images(message):
    user_id = message.from_user.id
    links = message.text.split()
    image_folder = f"user_{user_id}_images"
    os.makedirs(image_folder, exist_ok=True)

    for link in links:
        try:
            response = requests.get(link)
            if response.status_code == 200:
                image_filename = os.path.join(image_folder, link.split("/")[-1])
                with open(image_filename, 'wb') as f:
                    f.write(response.content)
        except Exception as e:
            print(f"Ошибка при загрузке изображения: {str(e)}")

    if os.listdir(image_folder):
        zip_filename = f"user_{user_id}_images.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for image_file in os.listdir(image_folder):
                zipf.write(os.path.join(image_folder, image_file), os.path.basename(image_file))

        with open(zip_filename, 'rb') as zip_file:
            bot.send_document(user_id, zip_file)

        os.remove(zip_filename)
        for image_file in os.listdir(image_folder):
            os.remove(os.path.join(image_folder, image_file))
        os.rmdir(image_folder)
    else:
        bot.send_message(user_id, "Не удалось скачать изображения по предоставленным ссылкам.")


if __name__ == '__main__':
    bot.polling()
