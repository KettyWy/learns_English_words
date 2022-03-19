import time
import random


words = []
translations = []
with open('DictOfEnglW.txt', 'r', encoding='utf-8') as f_obj:
    for f in f_obj.readlines():
        words.append(f.split(':')[0])
        translations.append(f.strip().split(':')[1])


def add_value(value):
    if value.find(':') >= 0:
        with open('DictOfEnglW.txt', 'a+', encoding='utf-8') as f_obj:
            f_obj.write(value + '\n')
        return True
    else:
        return False


def get_translate(user_word):
    for idx, word in enumerate(words):
        if user_word == word:
            cor_tran = translations[idx]
            return cor_tran


def option_selection():
    word = random.choice(words)
    translation = set()
    cor_tran = get_translate(word)
    translation.add(cor_tran)
    while len(translation) != 4:
        translation.add(random.choice(translations))
    return word, translation


def main():
    word, translation = option_selection()
    cor_tran = get_translate(word)
    print(f'Как переводиться слово "{word}"?')
    for idx, el in enumerate(translation):
        print(f'{idx + 1}){el}')
        if el == cor_tran:
            ans = idx + 1
    while True:
        try:
            answer = int(input('_'))
            if answer > 4:
                raise ValueError
            break
        except ValueError:
            print('Введите числа от 1 до 4.')
    if answer == ans:
        print('Верный ответ.')
    else:
        print(f'Ответ неверный. Верный ответ -{cor_tran}.')


def choice_time():
    tictac = input('Введите время в минутах:\n')
    tictac = float(tictac) * 60
    while True:
        main()
        time.sleep(tictac)


if __name__ == '__main__':
    # add_value('sun:Солнце')
    # add_value('word:Слово')
    # add_value('kb:клавиатура')
    # add_value('mouse:Мышь')
    #main()
    choice_time()
