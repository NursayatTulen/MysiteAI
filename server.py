from flask import Flask, request, jsonify, render_template
import difflib
from flask_cors import CORS
from langdetect import detect, DetectorFactory
import logging
import datetime  # datetime модулін импорттау

DetectorFactory.seed = 0 

app = Flask(__name__)
CORS(app)

# Журнал файлы
LOG_FILE = "questions.log"

def log_question(question, answer):
    """Пайдаланушы сұрағын лог файлға жазу"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} | Q: {question} | A: {answer}\n")

# Нұрсаят туралы ақпарат үш тілде
my_info = {
    "атың кім": {
        "kk": "Менің атым Нұрсаят.",
        "ru": "Меня зовут Нурсаят.",
        "en": "My name is Nursayat."
    },
    "what is your name": {
        "kk": "Менің атым Нұрсаят.",
        "ru": "Меня зовут Нурсаят.",
        "en": "My name is Nursayat."
    },
    "как тебя зовут": {
        "kk": "Менің атым Нұрсаят.",
        "ru": "Меня зовут Нурсаят",
        "en": "My name is Nursayat."
    },
    "жасың қаншада": {
        "kk": "Менің жасым 21-де.",
        "ru": "Мне 21 год.",
        "en": "I am 21 years old."
    },
    "how old are you": {
        "kk": "Менің жасым 21-де.",
        "ru": "Мне 21 год.",
        "en": "I am 21 years old."
    },
    "сколько тебе лет": {
        "kk": "Менің жасым 21-де.",
        "ru": "Мне 21 год.",
        "en": "I am 21 years old."
    },
    "не істейсің": {
        "kk": "Мен Digital Engineering мамандығында оқимын.",
        "ru": "Я изучаю Digital Engineering.",
        "en": "I study Digital Engineering."
    },
    "what do you do": {
        "kk": "Мен Digital Engineering мамандығында оқимын.",
        "ru": "Я изучаю Digital Engineering.",
        "en": "I study Digital Engineering."
    },
    "чем занимаешься": {
        "kk": "Мен Digital Engineering мамандығында оқимын.",
        "ru": "Я изучаю Digital Engineering.",
        "en": "I study Digital Engineering."
    },
    "қайдансың": {
        "kk": "Мен Жетісай қаласының тумасымын.",
        "ru": "Я родом из города Жетысай.",
        "en": "I am from the city of Zhetysai."
    },
    "where are you from": {
        "kk": "Мен Жетісай қаласының тумасымын.",
        "ru": "Я родом из города Жетысай.",
        "en": "I am from the city of Zhetysai."
    },
    "откуда ты": {
        "kk": "Мен Жетісай қаласының тумасымын.",
        "ru": "Я родом из города Жетысай.",
        "en": "I am from the city of Zhetysai."
    },
    "әскери мәртебең қандай": {
        "kk": "Мен арнайы құпия органда резервтемін.",
        "ru": "Я в резерве специального секретного органа.",
        "en": "I am in the reserve of a special secret organization."
    },
    "what is your military status": {
        "kk": "Мен арнайы құпия органда резервтемін.",
        "ru": "Я в резерве специального секретного органа.",
        "en": "I am in the reserve of a special secret organization."
    },
    "какой у тебя военный статус": {
        "kk": "Мен арнайы құпия органда резервтемін.",
        "ru": "Я в резерве специального секретного органа.",
        "en": "I am in the reserve of a special secret organization."
    },
    "жобаларың қандай": {
        "kk": "Мен Nuralem жүйесі, AR-голограммалар, Wi-Fi жүйесі сияқты жобалармен айналысамын.",
        "ru": "Я работаю над проектами Nuralem, AR-голограммы, Wi-Fi системы.",
        "en": "I work on projects like Nuralem system, AR holograms, and Wi-Fi systems."
    },
    "what projects are you working on": {
        "kk": "Мен Nuralem жүйесі, AR-голограммалар, Wi-Fi жүйесі сияқты жобалармен айналысамын.",
        "ru": "Я работаю над проектами Nuralem, AR-голограммы, Wi-Fi системы.",
        "en": "I work on projects like Nuralem system, AR holograms, and Wi-Fi systems."
    },
    "над какими проектами ты работаешь": {
        "kk": "Мен Nuralem жүйесі, AR-голограммалар, Wi-Fi жүйесі сияқты жобалармен айналысамын.",
        "ru": "Я работаю над проектами Nuralem, AR-голограммы, Wi-Fi системы.",
        "en": "I work on projects like Nuralem system, AR holograms, and Wi-Fi systems."
    },
    "хоббиің қандай": {
        "kk": "Мен AOC3 ойнағанды және кітап оқығанды ұнатамын.",
        "ru": "Я люблю играть в AOC3 и читать книги.",
        "en": "I enjoy playing AOC3 and reading books."
    },
    "what are your hobbies": {
        "kk": "Мен AOC3 ойнағанды және кітап оқығанды ұнатамын.",
        "ru": "Я люблю играть в AOC3 и читать книги.",
        "en": "I enjoy playing AOC3 and reading books."
    },
    "какие у тебя хобби": {
       "kk": "Мен AOC3 ойнағанды және кітап оқығанды ұнатамын.",
        "ru": "Я люблю играть в AOC3 и читать книги.",
        "en": "I enjoy playing AOC3 and reading books."
    },
     "саған қайдан толық ақпарат алуға болады": {
        "kk": "Мен туралы толығырақ ақпаратты Google-дан табуға болады.",
        "ru": "Более подробную информацию обо мне можно найти в Google.",
        "en": "More detailed information about me can be found on Google."
    },
    "где можно узнать о тебе больше": {
        "kk": "Мен туралы толығырақ ақпаратты Google-дан табуға болады.",
        "ru": "Более подробную информацию обо мне можно найти в Google.",
        "en": "More detailed information about me can be found on Google."
    },
    "where can I find more about you": {
        "kk": "Мен туралы толығырақ ақпаратты Google-дан табуға болады.",
        "ru": "Более подробную информацию обо мне можно найти в Google.",
        "en": "More detailed information about me can be found on Google."
    },
    "сәлем": {
        "kk": "Сәлем! Қалайсыз?",
        "ru": "Привет! Как дела?",
        "en": "Hello! How are you?"
    },
     "қалайсың": {
        "kk": "Жақсы, рақмет! Сіз ше?",
        "ru": "Хорошо, спасибо! А у вас?",
        "en": "I'm good, thank you! And you?"
    },
    "амансың ба": {
        "kk": "Иә, аман-есенмін!",
        "ru": "Да, всё в порядке!",
        "en": "Yes, I'm doing fine!"
    },
    "атың кім": {
        "kk": "Менің атым Нұрсаят.",
        "ru": "Меня зовут Нурсаяt.",
        "en": "My name is Nursayat."
    },
    "сен кімсің": {
        "kk": "Мен Нұрсаятпын.",
        "ru": "Я Нурсаяt.",
        "en": "I am Nursayat."
    },
    "қайда оқисың": {
        "kk": "Мен Нархоз университетінде оқимын.",
        "ru": "Я учусь в университете Нархоз.",
        "en": "I study at Narxoz University."
    },
    "сенің мамандығың не": {
        "kk": "Мен Digital Engineering мамандығын оқимын.",
        "ru": "Моя специальность - Digital Engineering.",
        "en": "My major is Digital Engineering."
    },
     "қай жерде туылдың": {
        "kk": "Мен Жетісайда туылдым.",
        "ru": "Я родился в Жетысае.",
        "en": "I was born in Zhetysai."
    },
    "сен қай жақтансың": {
        "kk": "Мен Жетісайданмын.",
        "ru": "Я из Жетысая.",
        "en": "I am from Zhetysai."
    },
     "әскерде қызмет еттің бе": {
        "kk": "Мен арнайы құпия органда резервтемін.",
        "ru": "Я в резерве специального секретного органа.",
        "en": "I am in the reserve of a special secret organization."
    },
    "сен код жазасың ба": {
        "kk": "Иә, мен код жазамын және программист ретінде стажермын.",
        "ru": "Да, я пишу код и работаю стажером-программистом.",
        "en": "Yes, I write code and work as a programming intern."
    },
    "кімді жақсы көресің": {
        "kk": "Бұл жеке мәселе, мен оны бөліскім келмейді.",
        "ru": "Это личный вопрос, я не хочу обсуждать это.",
        "en": "That's a personal question, I'd rather not discuss it."
    },
     "қызын бар ма": {
        "kk": "Бұл менің жеке өміріме қатысты, кешіріңіз.",
        "ru": "Это касается моей личной жизни, извините.",
        "en": "That concerns my personal life, sorry."
    },
    "қандай кітаптар оқисың": {
        "kk": "Мен техникалық, бизнес және мотивациялық кітаптарды оқимын.",
        "ru": "Я читаю технические, бизнес и мотивационные книги.",
        "en": "I read technical, business, and motivational books."
    },
    "қандай фильмдерді көресің": {
        "kk": "Мен ғылыми фантастика және тарихи фильмдерді жақсы көремін.",
        "ru": "Я люблю научную фантастику и исторические фильмы.",
        "en": "I love science fiction and historical movies."
    },
      "қандай музыканы ұнатасың": {
        "kk": "Мен хип-хоп пен классикалық музыканы тыңдағанды ұнатамын.",
        "ru": "Мне нравится слушать хип-хоп и классическую музыку.",
        "en": "I enjoy listening to hip-hop and classical music."
    },
    "қандай бағдарламалау тілдерін білесің": {
        "kk": "Мен Python, JavaScript, C++ және SQL тілдерін білемін.",
        "ru": "Я знаю Python, JavaScript, C++ и SQL.",
        "en": "I know Python, JavaScript, C++, and SQL."
    },
      "қандай технологияларды қолданасың": {
        "kk": "Мен Flask, Django, React, және Docker қолданамын.",
        "ru": "Я использую Flask, Django, React и Docker.",
        "en": "I use Flask, Django, React, and Docker."
    },
     "қай салада жұмыс істегің келеді": {
        "kk": "Маған киберқауіпсіздік пен жасанды интеллект қызықтырады.",
        "ru": "Мен интересуюсь кибербезопасностью и искусственным интеллектом.",
        "en": "I am interested in cybersecurity and artificial intelligence."
    },
     "денсаулыққа пайдалы қандай кеңестерің бар": {
        "kk": "Дұрыс тамақтану, ұйқы режимін сақтау және спортпен айналысу маңызды.",
        "ru": "Важно правильно питаться, соблюдать режим сна и заниматься спортом.",
        "en": "It is important to eat properly, maintain a sleep schedule, and exercise."
    },
     "өнімділікті қалай арттыруға болады": {
        "kk": "Тайм-менеджментті қолдану, мақсат қою және үзіліс жасау тиімді.",
        "ru": "Эффективно использовать тайм-менеджмент, ставить цели и делать перерывы.",
        "en": "Using time management, setting goals, and taking breaks is effective."
    },
     "өзін-өзі дамыту үшін қандай кітаптар оқуға болады": {
        "kk": "Мен 'Атомдық дағдылар' және 'Өмірді өзгертетін сиқыр' кітаптарын ұсынамын.",
        "ru": "Я рекомендую книги 'Атомные привычки' и 'Магия утра'.",
        "en": "I recommend 'Atomic Habits' and 'The Miracle Morning'."
    },
    "мотивацияны қалай сақтайсың": {
        "kk": "Жаңа мақсаттар қою арқылы өзімді ынталандырамын.",
        "ru": "Я мотивирую себя, ставя новые цели.",
        "en": "I motivate myself by setting new goals."
    },
     "қандай фильмдер немесе сериалдар көруге кеңес бересің": {
        "kk": "'Интерстеллар', 'Mr. Robot', 'Black Mirror' фильмдері қызықты.",
        "ru": "'Интерстеллар', 'Mr. Robot', 'Black Mirror' — интересные фильмы.",
        "en": "'Interstellar', 'Mr. Robot', 'Black Mirror' are interesting films."
    },
    "қазақстанда саяхаттауға ең жақсы жерлер қайсы": {
        "kk": "Алматы, Бурабай, Шарын шатқалы мен Көлсай көлдері керемет.",
        "ru": "Алматы, Боровое, Чарынский каньон и Кольсайские озера прекрасны.",
        "en": "Almaty, Burabay, Charyn Canyon, and Kolsai Lakes are amazing."
    },
     "егер уақыт машинасы болса қай ғасырға барушы едің": {
        "kk": "Мен болашаққа барып, технологияның дамуын көрер едім.",
        "ru": "Я бы отправился в будущее, чтобы увидеть развитие технологий.",
        "en": "I would go to the future to see technological advancements."
    },
     "бір күнге суперқаһарман болсаң не істер едің": {
        "kk": "Мен әлемдегі мәселелерді шешуге тырысар едім.",
        "ru": "Я бы попытался решить мировые проблемы.",
        "en": "I would try to solve global problems."
    },
    "егер өз бизнесіңді бастасаң қандай бағытты таңдар едің": {
        "kk": "Мен IT-стартап немесе киберқауіпсіздік компаниясын ашар едім.",
        "ru": "Я бы открыл IT-стартап или компанию по кибербезопасности.",
        "en": "I would start an IT startup or a cybersecurity company."
    },
     "егер бір тілді толық үйрену мүмкіндігің болса қайсысын таңдар едің": {
        "kk": "Мен қытай немесе жапон тілін үйренер едім.",
        "ru": "Я бы выучил китайский или японский язык.",
        "en": "I would learn Chinese or Japanese."
    },
     "hello": {
        "kk": "Сәлем! Қалайсыз?",
        "ru": "Привет! Как дела?",
        "en": "Hello! How are you?"
    },
    "how are you": {
        "kk": "Жақсы, рақмет! Сіз ше?",
        "ru": "Хорошо, спасибо! А у вас?",
        "en": "I'm good, thank you! And you?"
    },
    "are you okay": {
        "kk": "Иә, аман-есенмін!",
        "ru": "Да, всё в порядке!",
        "en": "Yes, I'm doing fine!"
    },
    "what is your name": {
        "kk": "Менің атым Нұрсаят.",
        "ru": "Меня зовут Нурсаяt.",
        "en": "My name is Nursayat."
    },
    "who are you": {
        "kk": "Мен Нұрсаятпын.",
        "ru": "Я Нурсаяt.",
        "en": "I am Nursayat."
    },
    "where do you study": {
        "kk": "Мен Нархоз университетінде оқимын.",
        "ru": "Я учусь в университете Нархоз.",
        "en": "I study at Narxoz University."
    },
    "what is your major": {
        "kk": "Мен Digital Engineering мамандығын оқимын.",
        "ru": "Моя специальность - Digital Engineering.",
        "en": "My major is Digital Engineering."
    },
    "where were you born": {
        "kk": "Мен Жетісайда туылдым.",
        "ru": "Я родился в Жетысае.",
        "en": "I was born in Zhetysai."
    },
    "where are you from": {
        "kk": "Мен Жетісайданмын.",
        "ru": "Я из Жетысая.",
        "en": "I am from Zhetysai."
    },
    "did you serve in the army": {
        "kk": "Мен арнайы құпия органда резервтемін.",
        "ru": "Я в резерве специального секретного органа.",
        "en": "I am in the reserve of a special secret organization."
    },
    "do you code": {
        "kk": "Иә, мен код жазамын және программист ретінде стажермын.",
        "ru": "Да, я пишу код и работаю стажером-программистом.",
        "en": "Yes, I write code and work as a programming intern."
    },
    "who do you love": {
        "kk": "Бұл жеке мәселе, мен оны бөліскім келмейді.",
        "ru": "Это личный вопрос, я не хочу обсуждать это.",
        "en": "That's a personal question, I'd rather not discuss it."
    },
    "do you have a girlfriend": {
        "kk": "Бұл менің жеке өміріме қатысты, кешіріңіз.",
        "ru": "Это касается моей личной жизни, извините.",
        "en": "That concerns my personal life, sorry."
    },
    "what books do you read": {
        "kk": "Мен техникалық, бизнес және мотивациялық кітаптарды оқимын.",
        "ru": "Я читаю технические, бизнес и мотивационные книги.",
        "en": "I read technical, business, and motivational books."
    },
    "what movies do you watch": {
        "kk": "Мен ғылыми фантастика және тарихи фильмдерді жақсы көремін.",
        "ru": "Я люблю научную фантастику и исторические фильмы.",
        "en": "I love science fiction and historical movies."
    },
    "what kind of music do you like": {
        "kk": "Мен хип-хоп пен классикалық музыканы тыңдағанды ұнатамын.",
        "ru": "Мне нравится слушать хип-хоп и классическую музыку.",
        "en": "I enjoy listening to hip-hop and classical music."
    },
    "what programming languages do you know": {
        "kk": "Мен Python, JavaScript, C++ және SQL тілдерін білемін.",
        "ru": "Я знаю Python, JavaScript, C++ и SQL.",
        "en": "I know Python, JavaScript, C++, and SQL."
    },
    "what technologies do you use": {
        "kk": "Мен Flask, Django, React, және Docker қолданамын.",
        "ru": "Я использую Flask, Django, React и Docker.",
        "en": "I use Flask, Django, React, and Docker."
    },
     "what technologies do you use": {
        "kk": "Мен Flask, Django, React, және Docker қолданамын.",
        "ru": "Я использую Flask, Django, React и Docker.",
        "en": "I use Flask, Django, React, and Docker."
    },
    "what field do you want to work in": {
        "kk": "Маған киберқауіпсіздік пен жасанды интеллект қызықтырады.",
        "ru": "Мен интересуюсь кибербезопасностью и искусственным интеллектом.",
        "en": "I am interested in cybersecurity and artificial intelligence."
    },
    "what health tips do you have": {
        "kk": "Дұрыс тамақтану, ұйқы режимін сақтау және спортпен айналысу маңызды.",
        "ru": "Важно правильно питаться, соблюдать режим сна и заниматься спортом.",
        "en": "It is important to eat properly, maintain a sleep schedule, and exercise."
    },
    "how to improve productivity": {
        "kk": "Тайм-менеджментті қолдану, мақсат қою және үзіліс жасау тиімді.",
        "ru": "Эффективно использовать тайм-менеджмент, ставить цели и делать перерывы.",
        "en": "Using time management, setting goals, and taking breaks is effective."
    },
    "what books to read for self-development": {
        "kk": "Мен 'Атомдық дағдылар' және 'Өмірді өзгертетін сиқыр' кітаптарын ұсынамын.",
        "ru": "Я рекомендую книги 'Атомные привычки' и 'Магия утра'.",
        "en": "I recommend 'Atomic Habits' and 'The Miracle Morning'."
    },
    "how do you stay motivated": {
        "kk": "Жаңа мақсаттар қою арқылы өзімді ынталандырамын.",
        "ru": "Я мотивирую себя, ставя новые цели.",
        "en": "I motivate myself by setting new goals."
    },
    "what movies or series do you recommend": {
        "kk": "'Интерстеллар', 'Mr. Robot', 'Black Mirror' фильмдері қызықты.",
        "ru": "'Интерстеллар', 'Mr. Robot', 'Black Mirror' — интересные фильмы.",
        "en": "'Interstellar', 'Mr. Robot', 'Black Mirror' are interesting films."
    },
    "what are the best places to travel in Kazakhstan": {
        "kk": "Алматы, Бурабай, Шарын шатқалы мен Көлсай көлдері керемет.",
        "ru": "Алматы, Боровое, Чарынский каньон и Кольсайские озера прекрасны.",
        "en": "Almaty, Burabay, Charyn Canyon, and Kolsai Lakes are amazing."
    },
    "if you had a time machine, which century would you go to": {
        "kk": "Мен болашаққа барып, технологияның дамуын көрер едім.",
        "ru": "Я бы отправился в будущее, чтобы увидеть развитие технологий.",
        "en": "I would go to the future to see technological advancements."
    },
    "if you were a superhero for a day, what would you do": {
        "kk": "Мен әлемдегі мәселелерді шешуге тырысар едім.",
        "ru": "Я бы попытался решить мировые проблемы.",
        "en": "I would try to solve global problems."
    },
    "if you started your own business, what direction would you choose": {
        "kk": "Мен IT-стартап немесе киберқауіпсіздік компаниясын ашар едім.",
        "ru": "Я бы открыл IT-стартап или компанию по кибербезопасности.",
        "en": "I would start an IT startup or a cybersecurity company."
    },
    "if you could fully learn one language, which one would you choose": {
        "kk": "Мен қытай немесе жапон тілін үйренер едім.",
        "ru": "Я бы выучил китайский или японский язык.",
        "en": "I would learn Chinese or Japanese."
    },
    "жақсы ма?": {
        "kk": "Рақмет! 😊",
        "en": "Thank you! 😊"
    },
    "жаман ба?": {
        "kk": "Өкінішті... 😔",
        "en": "That's unfortunate... 😔"
    },
    "өте жақсы ма?": {
        "kk": "Тамаша! 👍",
        "en": "Great! 👍"
    },
    "өте жаман ба?": {
        "kk": "Қап, сондай болмағанда ғой... 😕",
        "en": "Oh no, I wish it wasn't like that... 😕"
    },
    "нашар ма?": {
        "kk": "Жақсарып кетеді деп үміттенемін! 🤞",
        "en": "I hope it gets better! 🤞"
    },
    "жаман емес пе?": {
        "kk": "Жақсы ғой! 😊",
        "en": "That's good! 😊"
    },
    "жақсы емес пе?": {
        "kk": "Түсінікті... 😐",
        "en": "Got it... 😐"
    },
     "Это хорошо?": {
        "kk": "Рақмет! 😊",
        "ru": "Спасибо! 😊",
        "en": "Thank you! 😊"
    },
    "Это плохо?": {
        "kk": "Өкінішті... 😔",
        "ru": "Жаль... 😔",
        "en": "That's unfortunate... 😔"
    },
    "Это очень хорошо?": {
        "kk": "Тамаша! 👍",
        "ru": "Отлично! 👍",
        "en": "Great! 👍"
    },
    "Это очень плохо?": {
        "kk": "Қап, сондай болмағанда ғой... 😕",
        "ru": "О нет, жаль, что так... 😕",
        "en": "Oh no, I wish it wasn't like that... 😕"
    },
    "Это плохо?": {
        "kk": "Жақсарып кетеді деп үміттенемін! 🤞",
        "ru": "Надеюсь, что всё наладится! 🤞",
        "en": "I hope it gets better! 🤞"
    },
    "Это не плохо?": {
        "kk": "Жақсы ғой! 😊",
        "ru": "Это хорошо! 😊",
        "en": "That's good! 😊"
    },
    "Это не хорошо?": {
        "kk": "Түсінікті... 😐",
        "ru": "Понял... 😐",
        "en": "Got it... 😐"
    },
      "норм?": {
        "kk": "Жақсы! 😉",
        "ru": "Норм! 😉",
        "en": "Fine! 😉"
    },
    "зор?": {
        "kk": "Керемет! 🔥",
        "ru": "Огонь! 🔥",
        "en": "Awesome! 🔥"
    },
     "мен сені жақсы көрем": {
        "kk": "Мен де сені жақсы көрем! ❤️",
        "ru": "Я тоже тебя люблю! ❤️",
        "en": "I love you too! ❤️"
    },
    "мен сені қатты жақсы көрем": {
        "kk": "Мен де сені шексіз жақсы көрем! ❤️🔥",
        "ru": "Я тоже тебя безгранично люблю! ❤️🔥",
        "en": "I love you endlessly too! ❤️🔥"
    },
    "мен сені ұнатам": {
        "kk": "Маған да ұнайсың! 😊",
        "ru": "Ты мне тоже нравишься! 😊",
        "en": "I like you too! 😊"
    },
    "мен сені сағындым": {
        "kk": "Мен де сені сағындым! 🤗",
        "ru": "Я тоже скучаю по тебе! 🤗",
        "en": "I miss you too! 🤗"
    },
     "я тебя люблю": {
        "kk": "Мен де сені жақсы көрем! ❤️",
        "ru": "Я тоже тебя люблю! ❤️",
        "en": "I love you too! ❤️"
    },
    "я тебя очень люблю": {
        "kk": "Мен де сені шексіз жақсы көрем! ❤️🔥",
        "ru": "Я тоже тебя безгранично люблю! ❤️🔥",
        "en": "I love you endlessly too! ❤️🔥"
    },
    "ты мне нравишься": {
        "kk": "Маған да ұнайсың! 😊",
        "ru": "Ты мне тоже нравишься! 😊",
        "en": "I like you too! 😊"
    },
    "я по тебе скучаю": {
        "kk": "Мен де сені сағындым! 🤗",
        "ru": "Я тоже скучаю по тебе! 🤗",
        "en": "I miss you too! 🤗"
    },
    "сен не білесің": {
        "kk": "Мен көп нәрсені білемін, бірақ бәрін емес! 😊",
        "ru": "Я знаю многое, но не всё! 😊",
        "en": "I know a lot, but not everything! 😊"
    },
    "сен не істей аласың": {
        "kk": "Мен сұрақтарға жауап бере аламын, кеңес бере аламын және көмектесе аламын! 🤖",
        "ru": "Я могу отвечать на вопросы, давать советы и помогать! 🤖",
        "en": "I can answer questions, give advice, and help! 🤖"
    },
    "сен қанша білесің": {
        "kk": "Менің білімім шексіз емес, бірақ көмектесуге тырысамын! 📚",
        "ru": "Мои знания не безграничны, но я стараюсь помочь! 📚",
        "en": "My knowledge is not unlimited, but I try to help! 📚"
    },
    "что ты знаешь": {
        "ru": "Я знаю многое, но не всё! 😊",
        "kk": "Мен көп нәрсені білемін, бірақ бәрін емес! 😊",
        "en": "I know a lot, but not everything! 😊"
    },
    "что ты умеешь": {
        "ru": "Я могу отвечать на вопросы, давать советы и помогать! 🤖",
        "kk": "Мен сұрақтарға жауап бере аламын, кеңес бере аламын және көмектесе аламын! 🤖",
        "en": "I can answer questions, give advice, and help! 🤖"
    },
    "сколько ты знаешь": {
        "ru": "Мои знания не безграничны, но я стараюсь помочь! 📚",
        "kk": "Менің білімім шексіз емес, бірақ көмектесуге тырысамын! 📚",
        "en": "My knowledge is not unlimited, but I try to help! 📚"
    },
     "сен қандай кітаптар оқисың": {
        "kk": "Мен 'Атомдық дағдылар' және 'Өмірді өзгертетін сиқыр' кітаптарын ұсынамын.",
        "ru": "Я рекомендую книги 'Атомные привычки' и 'Магия утра'.",
        "en": "I recommend 'Atomic Habits' and 'The Miracle Morning'."
    },
    "сен қандай ойындар ойнайсың": {
        "kk": "Мен стратегия ойындарын ұнатамын, әсіресе 'Hearts of Iron IV'.",
        "ru": "Мне нравятся стратегические игры, особенно 'Hearts of Iron IV'.",
        "en": "I like strategy games, especially 'Hearts of Iron IV'."
    },
    "сен қай тілдерді білесің": {
        "kk": "Мен қазақ, орыс және ағылшын тілдерін білемін.",
        "ru": "Я знаю казахский, русский и английский языки.",
        "en": "I know Kazakh, Russian, and English."
    },
      "сен қай елге барғың келеді": {
        "kk": "Мен Жапония немесе Қытайға барғым келеді.",
        "ru": "Я бы хотел поехать в Японию или Китай.",
        "en": "I would like to visit Japan or China."
    },
    "сен қай салада жұмыс істегің келеді": {
        "kk": "Маған киберқауіпсіздік пен жасанды интеллект қызықтырады.",
        "ru": "Мне интересна кибербезопасность и искусственный интеллект.",
        "en": "I am interested in cybersecurity and artificial intelligence."
    },
    "сенің жасың қанша?": {
        "kk": "Мен 19 жастамын.",
        "ru": "Мне 19 лет.",
        "en": "I am 19 years old."
    },
     "сенің бойың қанша?": {
        "kk": "Менің бойым 186 см.",
        "ru": "Мой рост 186 см.",
        "en": "My height is 186 cm."
    },
    "сенің салмағың қанша?": {
        "kk": "Менің салмағым 75 кг.",
        "ru": "Мой вес 75 кг.",
        "en": "My weight is 75 kg."
    },
     "қай универде оқисың?": {
        "kk": "Мен Нархоз университетінде оқимын.",
        "ru": "Я учусь в университете Нархоз.",
        "en": "I study at Narxoz University."
    },
    "қандай мамандықта оқисың?": {
        "kk": "Менің мамандығым — ДЕ.",
        "ru": "Моя специальность — ДЕ.",
        "en": "My major is DE."
    },
    "қанша курс оқисың?": {
        "kk": "Мен 2-курс студентімін.",
        "ru": "Я студент 2-го курса.",
        "en": "I am a 2nd-year student."
    },
    "сабағың қалай?": {
        "kk": "Сабақтарым жақсы өтуде.",
        "ru": "Мои занятия проходят хорошо.",
        "en": "My studies are going well."
    },
    "оқу қиын ба?": {
        "kk": "Иә, кейде қиын, бірақ қызықты.",
        "ru": "Да, иногда сложно, но интересно.",
        "en": "Yes, sometimes it's hard, but interesting."
    },
    "нені жақсы көресің?": {
        "kk": "Мен спортпен айналысқанды жақсы көремін.",
        "ru": "Я люблю заниматься спортом.",
        "en": "I love doing sports."
    },
    "қалай демаласың?": {
        "kk": "Мен табиғатта серуендеуді жақсы көремін.",
        "ru": "Я люблю гулять на природе.",
        "en": "I love walking in nature."
    },
     "қалай демалуды ұнатасың?": {
        "kk": "Мен өзіме уақыт бөліп, тыныш жерде демалуды ұнатамын.",
        "ru": "Мне нравится отдыхать в тихом месте, уделяя время себе.",
        "en": "I like to relax in a quiet place, taking time for myself."
    },
    "қалай уақытыңды өткізесің?": {
        "kk": "Мен уақытты достарыммен өткізуді жақсы көремін.",
        "ru": "Мне нравится проводить время с друзьями.",
        "en": "I like spending time with my friends."
    },
     "қандай тағамдарды ұнатасың?": {
        "kk": "Мен итальяндық пицца мен суши жегенді жақсы көремін.",
        "ru": "Мне нравится итальянская пицца и суши.",
        "en": "I love Italian pizza and sushi."
    },
    "нені жиі істейсің?": {
        "kk": "Мен спортпен шұғылданамын және достарыммен уақыт өткіземін.",
        "ru": "Я занимаюсь спортом и провожу время с друзьями.",
        "en": "I do sports and spend time with my friends."
    },
    "қалай оқу оқисың?": {
        "kk": "Мен кітаптарды тыныш жерде, бір ыңғайлы орындықта оқығанды жақсы көремін.",
        "ru": "Я люблю читать книги в тихом месте, в удобном кресле.",
        "en": "I enjoy reading books in a quiet place, in a comfortable chair."
    },
    "қандай жерлерде демалуды ұнатасың?": {
        "kk": "Мен теңіз жағалауында немесе тауларда демалғанды ұнатамын.",
        "ru": "Я люблю отдыхать на побережье или в горах.",
        "en": "I like relaxing by the seaside or in the mountains."
    },
    "қандай ойындарды ойнауды ұнатасың?": {
        "kk": "Мен стратегиялық және ақыл-ойды дамытатын ойындарды ұнатамын.",
        "ru": "Мне нравятся стратегические и интеллектуальные игры.",
        "en": "I enjoy strategic and mind-developing games."
    },
    "қалай көңіл күйіңді көтересің?": {
        "kk": "Мен музыка тыңдап, серуендеуді ұнатамын.",
        "ru": "Я слушаю музыку и гуляю, чтобы поднять настроение.",
        "en": "I listen to music and go for walks to lift my mood."
    },
     "қашан көп нәрсені үйренесің?": {
        "kk": "Мен жаңа нәрселерді оқып, тәжірибе жасаған кезде көп нәрсені үйренемін.",
        "ru": "Я учусь многому, когда читаю и получаю опыт.",
        "en": "I learn a lot when I read and gain experience."
    },
    "нені жақсы көріп тыңдайсың?": {
        "kk": "Мен әртүрлі жанрларда музыка тыңдағанды жақсы көремін.",
        "ru": "Мне нравится слушать музыку разных жанров.",
        "en": "I love listening to music of various genres."
    },
    "қалай жиі спортпен айналысасың?": {
        "kk": "Мен аптасына үш рет спортзалға барамын.",
        "ru": "Я хожу в спортзал три раза в неделю.",
        "en": "I go to the gym three times a week."
    },
      "отбасыңызда қанша адам бар?": {
        "kk": "Менің отбасымда 8 адам бар.",
        "ru": "В моей семье 8 человек.",
        "en": "There are 8 people in my family."
    },
    "бақыланатын бауырыңыз қанша?": {
        "kk": "Менде 6 бауырым бар.",
        "ru": "У меня 6 братьев и сестер.",
        "en": "I have 6 siblings."
    },
    "отбасыңызда қанша бала бар?": {
        "kk": "Біздің отбасымызда 5 бала бар.",
        "ru": "В нашей семье 5 детей.",
        "en": "We have 5 children in our family."
    },
    "қыз бауырыңыз бар ма?": {
        "kk": "Менде бір қыз бауырым бар.",
        "ru": "У меня есть одна сестра.",
        "en": "I have one sister."
    },
    "отбасыңыздың тұратын жері қайда?": {
        "kk": "Біздің отбасымыз Жетісайда тұрады.",
        "ru": "Моя семья живет в Джетысай.",
        "en": "My family lives in Zhetysai."
    },
    "сіздің руыңыз қандай?": {
        "kk": "Менің руым – Токболат.",
        "ru": "Мой род — Токболат.",
        "en": "My tribe is Tokbolat."
    },
    "ананың руы қандай?": {
        "kk": "Менің анамның руы – Күлшығаш.",
        "ru": "Род моей мамы — Кульшыгаш.",
        "en": "My mother's tribe is Kulshygash."
    },
    "сіздің отбасыңызда қандай мамандық иелері бар?": {
        "kk": "Менің анам мен әкем мұғалімдер.",
        "ru": "Моя мама и папа — учителя.",
        "en": "My mother and father are teachers."
    },
    "құдайы жатыңыз қандай?": {
        "kk": "Менің үш інішім, бір әпкем, бір ағам бар.",
        "ru": "У меня есть три брата, одна сестра, один брат.",
        "en": "I have three brothers, one sister, and one older brother."
    },
    "әкеңіздің жұмысы қандай?": {
        "kk": "Әкем мұғалім.",
        "ru": "Мой папа — учитель.",
        "en": "My father is a teacher."
    },
    "ананың жұмысы қандай?": {
        "kk": "Анам да мұғалім.",
        "ru": "Моя мама тоже учитель.",
        "en": "My mother is also a teacher."
    },
    "сен отбасында ең үлкен немесе ең кіші болып табыласың?": {
        "kk": "Мен отбасымда ең кіші баламын.",
        "ru": "Я самый младший в семье.",
        "en": "I am the youngest in my family."
    },
    "әкемнің аты қандай?": {
        "kk": "Әкемнің аты — [әкеңіздің аты].",
        "ru": "Имя моего папы — [имя вашего папы].",
        "en": "My father's name is [your father's name]."
    },
    "анаңның аты қандай?": {
        "kk": "Анамның аты — [анаңыздың аты].",
        "ru": "Имя моей мамы — [имя вашей мамы].",
        "en": "My mother's name is [your mother's name]."
    },
    "сен қандай бала болғанды ұнатасың?": {
        "kk": "Мен бала кезімде шаян болып, білім алу мені жақсы көретін едім.",
        "ru": "Я всегда любил учиться и быть послушным ребенком.",
        "en": "I liked to study and be a well-behaved child."
    },
    "отбасыңыздың маңызды дәстүрі қандай?": {
        "kk": "Біздің отбасымызда бірге тамақ ішу мен әр мерекеде бірге болу дәстүрі бар.",
        "ru": "В нашей семье традиция — есть вместе и быть вместе на праздники.",
        "en": "In our family, we have the tradition of eating together and being together on holidays."
    },
    "қандай мерекелерді отбасыңызбен бірге атап өтесіздер?": {
        "kk": "Біз Наурыз, Рамазан айы және Жаңа жылды бірге атап өтеміз.",
        "ru": "Мы отмечаем Наурыз, Рамазан и Новый год вместе.",
        "en": "We celebrate Nowruz, Ramadan, and New Year together."
    },
    "отбасыңызда кім басқаратын адам?": {
        "kk": "Отбасымызда менің анам мен әкем — бізді басқаратын адамдар.",
        "ru": "В нашей семье мои мама и папа — главные.",
        "en": "In our family, my mother and father are the ones who lead."
    },
    "отбасыңызда достық қарым-қатынастар бар ма?": {
        "kk": "Иә, біздің отбасымызда достық қарым-қатынастар өте жақсы.",
        "ru": "Да, в нашей семье очень хорошие отношения.",
        "en": "Yes, we have very good relationships in our family."
    },
    "қалай стажер болдың?": {
        "kk": "Мен стажер болып жұмысқа қабылдандым, бұл мен үшін үлкен мүмкіндік.",
        "ru": "Я был принят стажером на работу, это для меня большая возможность.",
        "en": "I was hired as an intern, which is a great opportunity for me."
    },
    "неге осы жобамен айналысуды таңдадың?": {
        "kk": "Бұл жоба маған көптеген жаңа білімдер мен тәжірибе алуға мүмкіндік береді.",
        "ru": "Этот проект дает мне возможность получить много новых знаний и опыта.",
        "en": "This project provides me with the opportunity to gain a lot of new knowledge and experience."
    },
    "жобада қандай қызмет атқарасың?": {
        "kk": "Мен жобаның техникалық бөлімінде жұмыс істеймін, бағдарламалау мен зерттеу жүргіземін.",
        "ru": "Я работаю в технической части проекта, занимаюсь программированием и исследованиями.",
        "en": "I work in the technical section of the project, doing programming and research."
    },
    "жоба қалай жүріп жатыр?": {
        "kk": "Жоба жақсы жүріп жатыр, көптеген қиындықтар кездеседі, бірақ біз оларды шешіп жатырмыз.",
        "ru": "Проект идет хорошо, есть много сложностей, но мы их решаем.",
        "en": "The project is going well, there are many challenges, but we are solving them."
    },
    "қалай жұмысқа бейімделдің?": {
        "kk": "Мен әріптестерімнің көмегімен тез бейімделіп, өз орнымды таптым.",
        "ru": "Я быстро адаптировался с помощью коллег и нашел свое место.",
        "en": "I quickly adapted with the help of my colleagues and found my place."
    },
    "зарплатаң қанша?": {
        "kk": "Менің айлық жалақым 300 000 теңге.",
        "ru": "Моя зарплата составляет 300 000 тенге.",
        "en": "My monthly salary is 300,000 tenge."
    },
    "жоба үшін қандай дағдылар қажет болды?": {
        "kk": "Жоба үшін бағдарламалау, аналитикалық ойлау және топта жұмыс істеу дағдылары қажет болды.",
        "ru": "Для проекта нужны были навыки программирования, аналитического мышления и работы в команде.",
        "en": "The project required skills in programming, analytical thinking, and teamwork."
    },
    "жобаға қанша уақыт бөлесің?": {
        "kk": "Мен жобамен күніне 6-8 сағат айналысамын.",
        "ru": "Я занимаюсь проектом по 6-8 часов в день.",
        "en": "I spend 6-8 hours a day on the project."
    },
    "жобаның қандай қиындықтары бар?": {
        "kk": "Жоба барысында техникалық қиындықтар мен уақыт жетіспеушілігі кездеседі.",
        "ru": "В процессе проекта возникают технические трудности и нехватка времени.",
        "en": "The project faces technical difficulties and lack of time."
    },
    "қалай жаңа дағдылар үйрендің?": {
        "kk": "Жаңа дағдыларды жұмыс процесі мен әріптестерімнің көмегімен үйрендім.",
        "ru": "Я освоил новые навыки через рабочий процесс и с помощью коллег.",
        "en": "I learned new skills through the work process and with the help of my colleagues."
    },
    "кәсіби даму үшін не істейсіз?": {
        "kk": "Мен жаңа технологиялар мен әдістерді үйреніп, тәжірибе жинақтап, дамуды жалғастырамын.",
        "ru": "Я продолжаю учиться новым технологиям и методам, набираюсь опыта и развиваюсь.",
        "en": "I continue to learn new technologies and methods, gaining experience and developing myself."
    },
    "келешекте қандай мақсаттар бар?": {
        "kk": "Мен болашақта үлкен жобаларды басқаруға және жетекші маман болуға тырысамын.",
        "ru": "В будущем я хочу руководить крупными проектами и стать ведущим специалистом.",
        "en": "In the future, I aim to lead large projects and become a senior specialist."
    },
    "қалай өзіңді мотивируешь?": {
        "kk": "Менің басты мотивациям — өзімді дамыту және табысты болу.",
        "ru": "Моя основная мотивация — развиваться и быть успешным.",
        "en": "My main motivation is to develop myself and be successful."
    },
    "жобада қандай нәтижелерге жетуді жоспарлайсың?": {
        "kk": "Мен жобаның уақытында аяқталуын және барлық мақсаттарымызға жетуді жоспарлаймын.",
        "ru": "Я планирую завершить проект вовремя и достичь всех наших целей.",
        "en": "I plan to complete the project on time and achieve all our goals."
    },
    "топта жұмыс істеу ұнайды ма?": {
        "kk": "Иә, топта жұмыс істеу мен үшін өте қызықты, өйткені әркімнің өз үлесі бар.",
        "ru": "Да, работа в команде мне очень нравится, так как каждый вносит свою лепту.",
        "en": "Yes, I really enjoy working in a team because everyone contributes their part."
    },
    "қалай уақытты дұрыс басқаруға тырысасың?": {
        "kk": "Мен уақытты жоспарлап, маңызды тапсырмаларды бірінші орынға қоямын.",
        "ru": "Я планирую свое время и ставлю важные задачи на первое место.",
        "en": "I plan my time and prioritize important tasks."
    },
    "құқықтарыңызға қатысты қандай мәселелер болды ма?": {
        "kk": "Жоқ, менің жұмысымда құқықтарым бұзылған жоқ.",
        "ru": "Нет, мои права на работе не нарушались.",
        "en": "No, my rights have not been violated at work."
    },
    "өзіңізді болашақта қай салада көресіз?": {
        "kk": "Мен болашақта ақпараттық технологиялар саласында, бағдарламалаушы болып жұмыс істегім келеді.",
        "ru": "В будущем я хочу работать в области информационных технологий, как программист.",
        "en": "In the future, I would like to work in the field of information technology as a programmer."
    },
    "сәйкес келетін кеңестеріңіз бар ма?": {
        "kk": "Ең бастысы — үнемі үйрену, жаңа дағдыларды меңгеру және жақсы коммуникация құру.",
        "ru": "Самое главное — постоянно учиться, осваивать новые навыки и наладить хорошую коммуникацию.",
        "en": "The most important thing is to constantly learn, acquire new skills, and establish good communication."
    },
    "жұмысқа қалай кірдің?": {
        "kk": "Мен стажер ретінде бастадым және көп ұзамай жобадағы негізгі тапсырмаларға кірістім.",
        "ru": "Я начал как стажер и вскоре перешел к основным задачам проекта.",
        "en": "I started as an intern and soon moved on to the main tasks of the project."
    },
    "жұмыстағы ең қызықты нәрсе не?": {
        "kk": "Менің жұмысымда ең қызықты нәрсе — жаңа білімдер алу және үлкен жобаларға қатысу.",
        "ru": "Самое интересное в моей работе — получение новых знаний и участие в крупных проектах.",
        "en": "The most interesting part of my job is acquiring new knowledge and participating in large projects."
    },
    "қазіргі жобада қандай жауапкершіліктеріңіз бар?": {
        "kk": "Мен техникалық тапсырмаларды орындап, жобаның бағдарламалау аспектілеріне жауаптымын.",
        "ru": "Я выполняю технические задачи и отвечаю за программирование проекта.",
        "en": "I perform technical tasks and am responsible for the programming aspect of the project."
    },
    "қазіргі жұмысыңда қандай дағдыларды дамыттың?": {
        "kk": "Мен бағдарламалау дағдыларымды жақсартып, жобаларды басқару мен командамен жұмыс істеуді үйрендім.",
        "ru": "Я улучшил свои навыки программирования и научился управлять проектами и работать в команде.",
        "en": "I have improved my programming skills and learned project management and teamwork."
    },
    "жұмыс ортасында қалай үйлесімді жұмыс істейсің?": {
        "kk": "Мен әріптестеріммен ашық қарым-қатынас орнатып, топ ішінде үйлесімді жұмыс жасауға тырысамын.",
        "ru": "Я стараюсь поддерживать открытое общение с коллегами и работать согласованно в команде.",
        "en": "I try to maintain open communication with colleagues and work harmoniously within the team."
    },
    "жұмыстың қиын тұстары қандай?": {
        "kk": "Жұмыс барысында уақыт тапшылығы мен техникалық қиындықтар кездеседі, бірақ мен оларды шешуге тырысамын.",
        "ru": "На работе часто возникает нехватка времени и технические трудности, но я стараюсь их преодолевать.",
        "en": "At work, there are often time constraints and technical difficulties, but I try to overcome them."
    },
    "жұмыстағы ең үлкен жетістігің қандай?": {
        "kk": "Жобаның маңызды кезеңдерінде табысты жұмыс істеп, командаға қосқан үлесіммен мақтанамын.",
        "ru": "Я горжусь тем, что успешно работал на важных этапах проекта и внес свой вклад в команду.",
        "en": "I am proud of successfully working on important project stages and contributing to the team."
    },
    "жұмысыңды жақсы орындау үшін қандай дағдылар қажет?": {
        "kk": "Бағдарламалау, аналитикалық ойлау, уақытты басқару және командамен жақсы жұмыс істеу дағдылары қажет.",
        "ru": "Необходимы навыки программирования, аналитического мышления, управления временем и командной работы.",
        "en": "Skills in programming, analytical thinking, time management, and teamwork are necessary."
    },
    "жұмыста өзіңді қалай дамытасың?": {
        "kk": "Мен әрдайым жаңа технологияларды үйреніп, кәсіби дағдыларымды жетілдіруге тырысамын.",
        "ru": "Я постоянно учусь новым технологиям и стараюсь улучшать свои профессиональные навыки.",
        "en": "I am always learning new technologies and trying to improve my professional skills."
    },
    "жұмысқа қандай мақсаттар қоясың?": {
        "kk": "Мен болашақта үлкен жобаларда жетекші болуды және өз дағдыларымды дамыту үшін жаңа мүмкіндіктер іздеуді жоспарлаймын.",
        "ru": "Я планирую стать лидером крупных проектов и искать новые возможности для развития своих навыков.",
        "en": "I plan to become a leader in large projects and look for new opportunities to develop my skills."
    },
    "жұмысты қалай тиімді ұйымдастырасың?": {
        "kk": "Мен тапсырмаларды жоспарлап, маңызды міндеттерді бірінші орындауды қамтамасыз етемін.",
        "ru": "Я планирую задачи и ставлю самые важные задачи на первое место.",
        "en": "I plan tasks and make sure to prioritize the most important ones."
    },
    "жұмысты аяқтау үшін қанша уақыт бөлесің?": {
        "kk": "Мен жұмысты жоспар бойынша аяқтаймын және қажетті уақытта барлық тапсырмаларды орындаймын.",
        "ru": "Я завершаю работу по плану и выполняю все задачи вовремя.",
        "en": "I finish work according to plan and complete all tasks on time."
    },
    "жұмысыңды қалай бағалайсың?": {
        "kk": "Мен жұмысымды үнемі жақсарту үшін өзімді бағалаймын және кері байланысты тыңдаймын.",
        "ru": "Я оцениваю свою работу и слушаю обратную связь, чтобы постоянно улучшаться.",
        "en": "I evaluate my work and listen to feedback to continuously improve."
    },
    "қазірдің өзінде қандай жетістіктерге жеттің?": {
        "kk": "Мен жаңа жобаларға қатысып, көптеген тапсырмаларды сәтті орындадым.",
        "ru": "Я участвовал в новых проектах и успешно выполнил много задач.",
        "en": "I participated in new projects and successfully completed many tasks."
    },
    "қалай жұмысқа ынталандырасың?": {
        "kk": "Мен өзіме жаңа мақсаттар қойып, әр тапсырманы жақсы орындауға тырысамын.",
        "ru": "Я ставлю перед собой новые цели и стараюсь выполнять каждую задачу наилучшим образом.",
        "en": "I set new goals for myself and try to perform each task to the best of my ability."
    },
    "жұмыс ортасында жақсы қарым-қатынас орнатуға қалай тырысасың?": {
        "kk": "Мен әріптестеріммен жақсы қарым-қатынас орнату үшін ашық болуға және көмектесуге тырысамын.",
        "ru": "Я стараюсь быть открытым и помогать коллегам, чтобы установить хорошие отношения на работе.",
        "en": "I try to be open and help colleagues to establish good relationships at work."
    },
    "жұмыс барысында қандай мотивация көзі бар?": {
        "kk": "Менің мотивациям — кәсіби дамуды жалғастыру және өз жұмысымды жақсы орындау.",
        "ru": "Моя мотивация — продолжать развиваться профессионально и выполнять свою работу хорошо.",
        "en": "My motivation is to continue developing professionally and perform my job well."
    },
    "қалай жаңа жобаларға қатысуды жоспарлайсың?": {
        "kk": "Мен өз білімімді қолдана отырып, келешекте жаңа жобаларға қатысу үшін мүмкіндіктер іздеймін.",
        "ru": "Я ищу возможности для участия в новых проектах, применяя свои знания.",
        "en": "I look for opportunities to participate in new projects by applying my knowledge."
    },
    "қалай жаңа идеялар ұсынасың?": {
        "kk": "Мен топ ішінде белсенді пікір білдіріп, өз идеяларымды ұсынамын.",
        "ru": "Я активно высказываю мнения в команде и предлагаю свои идеи.",
        "en": "I actively express my opinions in the team and offer my ideas."
    },
      "қандай қызды ұнатасың?": {
        "kk": "Мен әдемі, ақылды, және өмірге оң көзқарасы бар қыздарды ұнатамын.",
        "ru": "Мне нравятся красивые, умные и позитивно настроенные девушки.",
        "en": "I like girls who are beautiful, intelligent, and have a positive outlook on life."
    },
    "сұлулыққа қалай қарайсың?": {
        "kk": "Сұлулық сыртқы түрімен ғана емес, адамның ішкі дүниесімен де байланысты.",
        "ru": "Красота не только во внешности, но и в внутреннем мире человека.",
        "en": "Beauty is not only about appearance, but also about the inner world of a person."
    },
    "қандай қасиеттерді бағалайсың?": {
        "kk": "Мен адалдық, сенімділік және адамгершілік қасиеттерін бағалаймын.",
        "ru": "Я ценю честность, надежность и человечность.",
        "en": "I value honesty, reliability, and humanity."
    },
    "қыздың қандай хоббиі болуын қалайсың?": {
        "kk": "Мен үшін қыздың өз хоббиі мен қызығушылықтары болуы маңызды, бұл оның өмірге деген көзқарасын көрсетеді.",
        "ru": "Для меня важно, чтобы девушка имела свои хобби и увлечения, это показывает ее взгляд на жизнь.",
        "en": "It's important to me that a girl has her own hobbies and interests, as it reflects her outlook on life."
    },
    "қыздың стилі қандай болуын ұнатасың?": {
        "kk": "Мен стильді, бірақ қарапайым киінетін қыздарды ұнатамын, ештеңе асырып немесе артық болмайды.",
        "ru": "Мне нравятся девушки, которые одеваются стильно, но просто, ничего лишнего или чрезмерного.",
        "en": "I like girls who dress stylishly but simply, without anything excessive or over the top."
    },
    "қандай фильмдер мен музыка ұнатасың?": {
        "kk": "Мен драмалар мен комедияларды ұнатамын, ал музыкадан көбіне рок пен поп тыңдаймын.",
        "ru": "Мне нравятся драмы и комедии, а из музыки я предпочитаю рок и поп.",
        "en": "I like dramas and comedies, and in terms of music, I mostly listen to rock and pop."
    },
    "сыйластыққа қалай қарайсың?": {
        "kk": "Сыйластық екі жақты болуы тиіс, және бір-бірімізді түсініп, қолдауға дайын болуымыз керек.",
        "ru": "Уважение должно быть взаимным, и мы должны быть готовы понимать и поддерживать друг друга.",
        "en": "Respect should be mutual, and we should be ready to understand and support each other."
    },
    "қыздың өмірге деген көзқарасы қандай болу керек?": {
        "kk": "Мен өмірге оң көзқарасы бар және әр нәрседен қуаныш табатын қызды ұнатамын.",
        "ru": "Мне нравится девушка с позитивным взглядом на жизнь, которая находит радость в каждой мелочи.",
        "en": "I like a girl who has a positive outlook on life and finds joy in every little thing."
    },
    "қыздың мінезі қандай болуын қалайсың?": {
        "kk": "Мен сабырлы, бірақ өз пікірін ашық айтатын қызды ұнатамын.",
        "ru": "Мне нравится спокойная, но открытая в выражении своего мнения девушка.",
        "en": "I like a girl who is calm but speaks her mind openly."
    },
    "қызбен бірге қалай уақыт өткізуге ұнатасың?": {
        "kk": "Мен табиғатта серуендеп немесе қызықты жерлерді аралап уақыт өткізгенді ұнатамын.",
        "ru": "Мне нравится проводить время, гуляя на природе или посещая интересные места.",
        "en": "I enjoy spending time walking in nature or visiting interesting places."
    },
      "қандай армандарың бар?": {
        "kk": "Менің арманым – өзімнің сүйікті ісіммен айналысып, әлемді жақсы жаққа өзгерту.",
        "ru": "Моя мечта — заниматься любимым делом и менять мир к лучшему.",
        "en": "My dream is to do what I love and make the world a better place."
    },
    "арманды іске асыру үшін не қажет?": {
        "kk": "Арманды іске асыру үшін еңбекқорлық, табандылық және өзіңе сену қажет.",
        "ru": "Для осуществления мечты нужно трудолюбие, настойчивость и вера в себя.",
        "en": "To make a dream come true, you need hard work, persistence, and belief in yourself."
    },
    "келешектен не күтесің?": {
        "kk": "Келешектен мен өзімді дамыту мен жаңа мүмкіндіктерді ашуды күтемін.",
        "ru": "Я ожидаю от будущего развитие себя и открытие новых возможностей.",
        "en": "I expect the future to bring self-development and new opportunities."
    },
    "арманыңа жету үшін қандай қадамдар жасадың?": {
        "kk": "Мен өз арманыма жету үшін білім алып, тәжірибе жинап, әрқашан дамуға тырысамын.",
        "ru": "Я работаю над своим развитием, получая образование и собирая опыт.",
        "en": "I work on my development by gaining education and experience."
    },
    "болашақта қандай мамандықты меңгергің келеді?": {
        "kk": "Мен болашақта технологиялар мен инновациялар саласында маман болуды қалаймын.",
        "ru": "Я хочу стать специалистом в области технологий и инноваций в будущем.",
        "en": "In the future, I want to become a specialist in the field of technology and innovation."
    },
    "арманыңа жеткенде қандай сезімде болар едің?": {
        "kk": "Арманыма жеткенде мен үлкен қуаныш пен қанағат сезінетін болар едім.",
        "ru": "Когда я достигну своей мечты, я буду чувствовать большое счастье и удовлетворение.",
        "en": "When I achieve my dream, I would feel immense happiness and satisfaction."
    },
    "арманыңды жүзеге асыру үшін қандай қиындықтар күтесің?": {
        "kk": "Арманымды жүзеге асыру үшін кейбір қиындықтар мен сәтсіздіктер болуы мүмкін, бірақ мен оларды жеңіп шығуға дайынмын.",
        "ru": "Для осуществления своей мечты будут некоторые трудности и неудачи, но я готов преодолеть их.",
        "en": "There may be some difficulties and setbacks in realizing my dream, but I am ready to overcome them."
    },
    "болашақта қайда тұруды армандайсың?": {
        "kk": "Мен болашақта табиғаты керемет жерде тұрып, жеке тыныштық пен үйлесім табуды армандаймын.",
        "ru": "Я мечтаю жить в месте с прекрасной природой, находя личный покой и гармонию.",
        "en": "I dream of living in a place with beautiful nature, finding personal peace and harmony."
    },
    "арманыңды орындау үшін қандай адам болу керек?": {
        "kk": "Арманымды орындау үшін мен табанды, еңбекқор және өз мақсатыма адал болуым керек.",
        "ru": "Чтобы исполнить свою мечту, я должен быть упорным, трудолюбивым и преданным своей цели.",
        "en": "To achieve my dream, I need to be persistent, hardworking, and loyal to my goal."
    },
    "арманыңды жүзеге асыру үшін кімнен көмек сұрар едің?": {
        "kk": "Мен өз арманыма жету үшін отбасымнан, достарымнан және ұстаздарымнан көмек сұрар едім.",
        "ru": "Для осуществления своей мечты я бы обратился за помощью к своей семье, друзьям и наставникам.",
        "en": "To realize my dream, I would ask for help from my family, friends, and mentors."
    }




}

def detect_language(question):
    """Сұрақтың тілін анықтау."""
    try:
        lang = detect(question)
        return lang if lang in ["kk", "ru", "en"] else "kk"  # Негізгі тіл - қазақша
    except:
        return "kk"  # Егер тіл анықталмаса, қазақша деп алу

def find_best_match(question):
    """Сұрақты ең жақын сәйкес сұрақпен табу."""
    best_match = difflib.get_close_matches(question, my_info.keys(), n=1, cutoff=0.5)
    return best_match[0] if best_match else None

def log_question(question, answer):
    """Сұрақ пен жауапты лог файлға жазу."""
    logging.info(f"Сұрақ: {question} | Жауап: {answer}")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").lower().strip()

    if not question:
        return jsonify({"answer": "Сұрақ бос болмауы керек!"})

    lang = detect_language(question)
    best_match = find_best_match(question)

    if best_match:
        answer = my_info[best_match][lang]
    else:
        answer = {
            "kk": "Менде бұл туралы білмеймін немесе бұл сұраққа жауап бере алмаймын.",
            "ru": "На этот вопрос нет точного ответа.",
            "en": "I don't know about this or I can't answer this question."
        }[lang]

    log_question(question, answer)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)