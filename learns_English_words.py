import time
import random


def add_value():
    s = print('Добавьте в словарь слово в формате: "слово:перевод". Для выхода - "3".')
    while True:
        s = input()
        if s == '3':
            break
        if s.find(':') >= 0:
            with open('DictOfEnglW.txt', 'a+', encoding='utf-8') as f_obj:
                f_obj.write(s + '\n')
        else:
            print('Вы ввели запись в неправильном формате.')


def extraction():
    key = []
    val = []
    with open('DictOfEnglW.txt', 'r', encoding='utf-8') as f_obj:
        for f in f_obj.readlines():
            key.append(f.split(':')[0])
            val.append(f.strip().split(':')[1])
    return key, val


def checker(word):
    with open('DictOfEnglW.txt', 'r', encoding='utf-8') as f_obj:
        for f in f_obj.readlines():
            if f.split(':')[0] == word:
                cor_tran = f.strip().split(':')[1]
    return cor_tran


def option_selection():
    words, translations = extraction()
    word = random.choice(words)
    translation = random.sample(translations, 3)
    cor_tran = checker(word)
    translation.append(cor_tran)
    translation = set(translation)
    while len(translation) != 4:
        with open('DictOfEnglW.txt', 'r', encoding='utf-8') as f_obj:
            for f in f_obj.readlines():
                translation.add(f.strip().split(':')[1])
    return word, translation


def main():
    word, translation = option_selection()
    cor_tran = checker(word)
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
        print(f'Ответ неверный. Верный ответ -{checker(word)}.')


def choice_time():
    tictac = input('Введите время в минутах:\n')
    tictac = float(tictac)*60
    while True:
        time.sleep(tictac)
        main()


if __name__ == '__main__':
    add_value()
    #main()
    choice_time()
