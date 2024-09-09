import random
import os
import dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message


dotenv.load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Создаем объекты бота и диспетчера
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Количество попыток, доступных пользователю в игре
ATTEMPTS = 8


users = {}

def get_user(message: Message):
    if message.from_user.id not in users:
        users[message.from_user.id] = {
            'in_game': False,
            'secret_number': 0,
            'attempts': 0,
            'total_games': 0,
            'wins': 0
        }
    return users[message.from_user.id]



# Функция возвращающая случайное целое число от 1 до 100
def get_random_number() -> int:
    return random.randint(1, 100)


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message):
    get_user(message)
    await message.answer(
        'Привет!\nДавайте сыграем в игру "Угадай число"?\n\n'
        'Чтобы получить правила игры и список доступных '
        'команд - отправьте команду /help'
    )


# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    get_user(message)
    await message.answer(
        f'Правила игры:\n\nЯ загадываю число от 1 до 100, '
        f'а вам нужно его угадать\nУ вас есть {ATTEMPTS} '
        f'попыток\n\nДоступные команды:\n/help - правила '
        f'игры и список команд\n/cancel - выйти из игры\n'
        f'/stat - посмотреть статистику\n\nДавай сыграем?'
    )


# Этот хэндлер будет срабатывать на команду "/stat"
@dp.message(Command(commands='stat'))
async def process_stat_command(message: Message):
    get_user(message)
    await message.answer(
        f'Всего игр сыграно: {get_user(message)["total_games"]}\n'
        f'Игр выиграно: {get_user(message)["wins"]}'
    )

@dp.message(F.text.lower().in_(['статистика', 'стат', 'игры', 'игр', 'побед',
                                'сколько']))
async def process_stat_command(message: Message):
    get_user(message)
    await message.answer(
        f'Всего игр сыграно: {get_user(message)["total_games"]}\n'
        f'Игр выиграно: {get_user(message)["wins"]}'
    )


# Этот хэндлер будет срабатывать на команду "/cancel"
@dp.message(Command(commands='cancel'))
async def process_cancel_command(message: Message):
    
    if get_user(message)['in_game']:
        get_user(message)['in_game'] = False
        await message.answer(
            'Вы вышли из игры. Если захотите сыграть '
            'снова - напишите об этом'
        )
    else:
        await message.answer(
            'А мы и так с вами не играем. '
            'Может, сыграем разок?'
        )


# Этот хэндлер будет срабатывать на согласие пользователя сыграть в игру
@dp.message(F.text.lower().in_(['да', 'давай', 'сыграем', 'согласен', 'игра',
                                'играть', 'хочу играть']))
async def process_positive_answer(message: Message):
    if not get_user(message)['in_game']:
        get_user(message)['in_game'] = True
        get_user(message)['secret_number'] = get_random_number()
        get_user(message)['attempts'] = ATTEMPTS
        await message.answer(
            'Ура!\n\nЯ загадал число от 1 до 100, '
            'попробуй угадать!'
        )
    else:
        await message.answer(
            'Пока мы играем в игру я могу '
            'реагировать только на числа от 1 до 100 '
            'и команды /cancel и /stat'
        )


# Этот хэндлер будет срабатывать на отказ пользователя сыграть в игру
@dp.message(F.text.lower().in_(['нет', 'не', 'не хочу', 'не буду']))
async def process_negative_answer(message: Message):
    if not get_user(message)['in_game']:
        await message.answer(
            'Жаль :(\n\nЕсли захотите поиграть - просто '
            'напишите об этом'
        )
    else:
        await message.answer(
            'Мы же сейчас с вами играем. Присылайте, '
            'пожалуйста, числа от 1 до 100'
        )


# Этот хэндлер будет срабатывать на отправку пользователем чисел от 1 до 100
@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def process_numbers_answer(message: Message):
    if get_user(message)['in_game']:
        if int(message.text) == get_user(message)['secret_number']:
            get_user(message)['in_game'] = False
            get_user(message)['total_games'] += 1
            get_user(message)['wins'] += 1
            await message.answer(
                'Ура!!! Вы угадали число!\n\n'
                'Может, сыграем еще?'
            )
        elif int(message.text) > get_user(message)['secret_number'] and (int(message.text) - get_user(message)['secret_number']) >= 5:
            get_user(message)['attempts'] -= 1
            await message.answer('Мое число сильно меньше')

        elif int(message.text) > get_user(message)['secret_number'] and (int(message.text) - get_user(message)['secret_number']) < 5:
            get_user(message)['attempts'] -= 1
            await message.answer('Мое число немного меньше')

        elif int(message.text) < get_user(message)['secret_number'] and abs(int(message.text) - get_user(message)['secret_number']) >= 5:
            get_user(message)['attempts'] -= 1
            await message.answer('Мое число сильно больше')

        elif int(message.text) < get_user(message)['secret_number'] and abs(int(message.text) - get_user(message)['secret_number']) < 5:
            get_user(message)['attempts'] -= 1
            await message.answer('Мое немного больше')

        if get_user(message)['attempts'] == 0:
            get_user(message)['in_game'] = False
            get_user(message)['total_games'] += 1
            await message.answer(
                f'К сожалению, у вас больше не осталось '
                f'попыток. Вы проиграли :(\n\nМое число '
                f'было {get_user(message)["secret_number"]}\n\nДавайте '
                f'сыграем еще?'
            )
    else:
        await message.answer('Мы еще не играем. Хотите сыграть?')


# Этот хэндлер будет срабатывать на остальные любые сообщения
@dp.message()
async def process_other_answers(message: Message):
    if get_user(message)['in_game']:
        await message.answer(
            'Мы же сейчас с вами играем. '
            'Присылайте, пожалуйста, числа от 1 до 100'
        )
    else:
        await message.answer(
            'Я довольно ограниченный бот, давайте '
            'просто сыграем в игру?'
        )


if __name__ == '__main__':
    dp.run_polling(bot)