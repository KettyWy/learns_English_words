import time
import random

words = []
weights = []
translations = []
with open('DictOfEnglW.txt', 'r', encoding='utf-8') as f_obj:
    for f in f_obj.readlines():
        words.append(f.split(':')[:2])
        weights.append(int(f.split(':')[0]))
        translations.append(f.strip().split(':')[2])


def add_value(value):
    if value.find(':') >= 0:
        with open('DictOfEnglW.txt', 'a+', encoding='utf-8') as f_obj:
            f_obj.write('100:' + value + '\n')
        return True
    else:
        return False


def del_value(value):
    with open('DictOfEnglW.txt', 'r', encoding='utf-8') as f_obj:
        data = f_obj.readlines()
        data = filter(lambda line: value not in line, data)
    with open('DictOfEnglW.txt', 'w', encoding='utf-8') as f_obj:
        f_obj.write("".join(data))


def find_word(word):
    with open('DictOfEnglW.txt', 'r', encoding='utf-8') as f_obj:
        data = f_obj.readlines()
        try:
            data = list(filter(lambda line: word in line, data))[0]
            return ' - '.join(data.strip().split(':')[1:])
        except IndexError:
            return f'Нет такого слова.'
        # for el in data:
        #     if el.split(':').count(word) > 0:
        #         return ' - '.join(el.strip().split(':')[1:])


def get_translate(user_word):
    for idx, word in enumerate(words):
        if user_word == word:
            cor_tran = translations[idx]
            return cor_tran


def option_selection():
    word = random.choices(words, weights=weights)[0]
    translation = set()
    cor_tran = get_translate(word)
    translation.add(cor_tran)
    while len(translation) != 4:
        translation.add(random.choice(translations))
    return word, translation


def main():
    word, translation = option_selection()
    old_word = f'{word[0]}:{word[1]}'
    cor_tran = get_translate(word)
    print(f'Как переводиться слово "{word[1]}"?')
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
        if int(word[0]) > 0:
            word[0] = int(word[0]) - 1
        new_word = f'{word[0]}:{word[1]}'
        with open('DictOfEnglW.txt', 'r', encoding='utf-8') as f_obj:
            old_text = f_obj.read()
            new_text = old_text.replace(old_word, new_word)
        with open('DictOfEnglW.txt', 'w', encoding='utf-8') as f_obj:
            f_obj.write(new_text)

    else:
        print(f'Ответ неверный. Верный ответ -{cor_tran}.')


def choice_time():
    tictac = input('Введите время в минутах:\n')
    tictac = float(tictac) * 60
    while True:
        main()
        time.sleep(tictac)


if __name__ == '__main__':
    # main()
    # choice_time()
    # add_value()
    # del_value('kb')
    print(find_word('word'))
