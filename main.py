
import telebot, os, re
from telebot.types import *
from pytube import YouTube, Search

bot = telebot.TeleBot(os.getenv("token"))

user_is_search_youtube = "" # لا تقوم بتعديلهم
search_word = "" # لا تقوم بتعديلهم

@bot.message_handler(content_types=['text'])
def Yout(message: Message):
    global user_is_search_youtube, search_word
    chat_id = message.chat.id
    user_ = message.from_user
    msg_text = message.text
    if (
        (msg_text.startswith("بحث") or msg_text.startswith("يوت") or msg_text.startswith("يوتيوب"))
        and len(message.text.split(" ")) > 1
    ):
        bot.send_chat_action(chat_id, "typing")
        user_is_search_youtube = user_.id
        search_word = " ".join(message.text.split(" ")[1:])
        bot.send_message(message.chat.id, text="هذه العمليات نتيجة للبحث. انقر على الفيديو الذي ترغب في تحميله!",
                         reply_markup=MrkSr(search_word), reply_to_message_id=message.id)
    else:
        bot.send_message(message.chat.id, text="للبحث عن فيديو، اكتب إما (بحث) أو (يوت) أو (يوتيوب) ثم كلمة عنوان البحث.", reply_to_message_id=message.id)

def extract_video_id(text):
    pattern = r'https://www\.youtube\.com/watch\?v=([^\s&]+)'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    else:
        return None



def SendOpSr(srWod:str):
    yt = Search(srWod)

    ur = yt.results
    urls = []
    a = 0
    for i in ur:
        if a == 5:
            break
        i = str(i)
        urs = i[i.find("videoId"): i.find(">")].replace("videoId=", "")
        urls.append("https://www.youtube.com/watch?v=" +urs)
        a += 1
    return urls

def MrkSr(word):
    mrk = InlineKeyboardMarkup(row_width=1)
    btns = []
    for url in SendOpSr(word):
        title_video = YouTube(url).title
        btn = InlineKeyboardButton(text=title_video, callback_data=url)
        btns.append(btn)
    mrk.add(*btns)
    return mrk

@bot.callback_query_handler(func= lambda call:True)
def QueryYoutube(call:CallbackQuery):
    chid = call.message.chat.id
    data = call.data
    message = call.message
    user = call.from_user
    v_id = extract_video_id(data)
    if v_id:
        main_url = "https://www.youtube.com/watch?v=" + str(v_id)
        if user_is_search_youtube == user.id:
            bot.send_chat_action(message.chat.id, "upload_video")
            yt = YouTube(data)
            bot.delete_message(message.chat.id, message.id)
            yt.streams.get_highest_resolution().download(filename=search_word + '.mp4')
 
            bot.send_video(message.chat.id, open(search_word + '.mp4', 'rb'), caption=yt.title, parse_mode="HTML")
            os.remove(search_word + '.mp4')

bot.infinity_polling(skip_pending=True)
