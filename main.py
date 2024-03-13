from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from copy import deepcopy
from states import UserStates, BalanceStates
from requestto import requestto
# from background import keep_alive
from buttons import *
from database import *
from yoomoney import Client
from config import *
import time
import logging


logging.info("An INFO")

yoomoney_client = Client(YOOMONEY_TOKEN)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

DATA2TEXT = {
    "successfulPeople": "Успешные люди",
    "Universities": "ВУЗы",
    "Courses": "Курсы",
    "studentExperience": "Опыт студентов",
    "addMaterials": "Доп. материалы",
    "olympiads": "Олимпиады"
}


async def generate_label(user_id, count):
  t = int(time.time()) % 1000000
  label = f"C{count}ID{user_id}T{t}"
  return label

async def check_payment(label):
  history = yoomoney_client.operation_history()
  print(f"\nLabel: {label}")
  for operation in history.operations:
    if operation.label == label and operation.status == "success":
      print(f"ПЛАТЁЖ {operation.amount} УСПЕШНО ПРОШЁЛ")
      return True
      break
  else:
    print("ПЛАТЁЖ НЕ ОБНАРУЖЕН")
    return False


# @dp.message_handler(commands=['start', 'new_plan'], state="*") # первый вариант
# async def cmd_start(message: types.Message, state):
#     """
#     Отправляем приветственное сообщение и начинаем диалог.
#     """
#     st = await state.get_state()
#     if st in UserStates:
#         if st == "UserStates:result":
#             await message.answer("Создадим новый план. <b>Погнали?</b>", reply_markup=launchMenu, parse_mode="HTML")
#             async with state.proxy() as data:
#                 await bot.edit_message_text("<i>У вас новый план</i>", chat_id=message.from_user.id, message_id=data["result_message_id"], parse_mode="HTML")
#             await state.set_data()
#             await UserStates.launch.set()
#         else:
#             await message.answer("<i>Закончите заполнять текущую анкету</i>", parse_mode="HTML")
#     else:
#         await message.answer("Привет, смотрю ты тут впервые. Я <b>чат-бот Max</b>. Я <b>создаю планы</b> достижения карьерных целей.\n\
# Чтобы я <i>мог создать</i> план твоих целей, тебе нужно ответить на <i>несколько вопросов</i>.\n<b>Погнали?</b>", reply_markup=launchMenu, parse_mode="HTML")
#         await UserStates.launch.set()


@dp.message_handler(commands=['start', 'new_plan'], state="*")  # второй вариант, скорее его оставить
async def cmd_start(message: types.Message, state):
  user_id = message.from_user.id
  if await check_id(user_id):
    st = await state.get_state()
    if st in UserStates:
      if st == "UserStates:result":
        await message.answer(
            "Вы хотите создать новый план?\n\n<b>Если да, то жмите кнопку ниже</b>👇",
            reply_markup=main_menu,
            parse_mode="HTML")
      else:
        await message.answer("<i>Закончите заполнять текущую анкету</i>", parse_mode="HTML")
    else:
      await message.answer("🏠<b>Главное меню</b>", parse_mode="HTML", reply_markup=main_menu)
  else:
    await message.answer(
        f"Привет, смотрю ты тут впервые.\nПоэтому ты получаешь <b>2 {CURRENCY_NAME}</b>",
        parse_mode="HTML")
    await message.answer(f"Коротко обо мне👇\n\nЯ <b>чат-бот Max</b>.\nЯ <b>создаю планы</b> достижения карьерных целей.\n\
Чтобы я мог создать план твоих целей, тебе нужно ответить на <b>несколько вопросов</b>.\n\nЕсли готов, то жми кнопку <b>Новый план</b>",
        reply_markup=main_menu,
        parse_mode="HTML")
    await add_new_user(user_id)


@dp.message_handler(Text("Баланс💰"), state="*")
async def balance(message: types.Message, state):
  user_id = message.from_user.id
  await message.answer(f"<b>Ваш баланс {await get_coins(user_id)} {CURRENCY_NAME}</b>",
                       reply_markup=balanceMenu,
                       parse_mode="HTML")
  await BalanceStates.balance.set()


@dp.message_handler(Text("Пополнить💸"), state=BalanceStates.balance)
async def input_amount(message: types.Message, state):
  await message.answer(f"<b>1 {CURRENCY_NAME} = {PRICE_FOR_COIN} рублей</b>\n\nВведите количество {CURRENCY_NAME}, которое хотите приобрести.", reply_markup=cancelMenu, parse_mode="HTML")
  await BalanceStates.next()

@dp.message_handler(lambda message: not message.text.isdigit(), state=BalanceStates.pay)
async def invalid_input_digit(message: types.Message):
  await message.answer("<i>Пожалуйста, введите натуральное число.</i>", parse_mode="HTML")

@dp.message_handler(state=BalanceStates.pay)
async def process_amount(message: types.Message, state):
  user_id = message.from_user.id
  amount = int(message.text)
  label = await generate_label(user_id, amount)
  print(label)
  await message.answer(f"Вы хотите приобрести <b>{amount} {CURRENCY_NAME}</b>\n\nЦена: <b>{amount * PRICE_FOR_COIN} руб.</b>", reply_markup = await GetPaymentsMenu(label), parse_mode="HTML")
  await BalanceStates.next()

@dp.callback_query_handler(lambda c: "C" == str(c.data)[0], state="*")
async def CheckPayment(call, state=FSMContext):
    user_id = call.from_user.id
    label = call.data
    count = int(label[1:label.index("ID")])
    if await check_payment(label):
      await call.answer("Оплата прошла успешно")
      await bot.edit_message_text(f"<b>Вы приобрели {count} {CURRENCY_NAME}</b>\n\nНа них Вы можете создать новый карьерный план!", 
                                  chat_id=user_id, 
                                  message_id=call.message.message_id, 
                                  parse_mode="HTML")
      await add_coins(user_id, count)
      print(f"{user_id} покупка {count} {CURRENCY_NAME}\n")
    else:
        await call.answer("Оплата не получена")
    
@dp.message_handler(Text("Новый план📋"), state="*")
async def prelaunch_new(message: types.Message, state):
  st = await state.get_state()
  if st in UserStates:
    if st == "UserStates:result":
      await message.answer(
          "<b>ПРЕДУПРЕЖДЕНИЕ\n\nПри создании нового плана, предыдущие данные будут стёрты</b>",
          parse_mode="HTML",
          reply_markup=createOrCancelMenu)
    else:
      await message.answer("<i>Закончите заполнять текущую анкету</i>",
                           parse_mode="HTML")
      return
  await message.answer(f"Цена одного плана - <b>1 {CURRENCY_NAME}</b>",
                       parse_mode="HTML",
                       reply_markup=createOrCancelMenu)
  await UserStates.launch.set()


@dp.message_handler(Text("Отмена❌"), state=UserStates.launch)
async def launch_cancel(message: types.Message, state):
  await message.answer("Вы вернулись в <b>главное меню</b>",
                       reply_markup=main_menu,
                       parse_mode="HTML")
  await state.finish()


@dp.message_handler(Text("Создать✅"), state=UserStates.launch)
async def launch(message: types.Message, state):
  """
    Отправляем приветственное сообщение и начинаем диалог.
    """
  async with state.proxy() as data:
    if "result_message_id" in data:
      await bot.edit_message_text("<i>У вас новый план</i>",
                                  chat_id=message.from_user.id,
                                  message_id=data["result_message_id"],
                                  parse_mode="HTML")
  await state.set_data()
  await message.answer("Начали! Давай познакомимся. Как тебя зовут?",
                       reply_markup=removeButton)
  await UserStates.name.set()


@dp.message_handler(lambda message: message.text.isdigit(),
                    state=UserStates.name)
async def process_name_invalid(message: types.Message):
  """
    Имя не должно содержать цифры. (обработчик для состояния "name")
    """
  await message.answer(
      "<i>Пожалуйста, введите ваше имя текстом, без цифр.</i>",
      parse_mode="HTML")


@dp.message_handler(state=UserStates.name)
async def process_name(message: types.Message, state: FSMContext):
  async with state.proxy() as data:
    data['name'] = message.text

    # Спрашиваем возраст
    await message.answer(f"Отлично, {data['name']}! Сколько тебе лет?")
    # Переключаемся на состояние "age"
    await UserStates.age.set()


@dp.message_handler(lambda message: not message.text.isdigit(),
                    state=UserStates.age)
async def process_age_invalid(message: types.Message):
  """
    Возраст должен быть числом. (обработчик для состояния "age")
    """
  await message.answer(
      "<i>Пожалуйста, введите ваш возраст числом. Например, 15.</i>",
      parse_mode="HTML")


@dp.message_handler(state=UserStates.age)
async def process_age(message: types.Message, state: FSMContext):
  async with state.proxy() as data:
    data['age'] = message.text

    # Спрашиваем класс обучения
    await message.answer("В каком классе ты учишься?")
    # Переключаемся на состояние "grade"
    await UserStates.grade.set()


@dp.message_handler(lambda message: not message.text.isdigit(),
                    state=UserStates.grade)
async def process_grade_invalid_numb(message: types.Message):
  """
    Класс должен быть числом. (обработчик для состояния "grade")
    """
  await message.answer(
      "<i>Пожалуйста, введите ваш возраст числом. Например, 9.</i>",
      parse_mode="HTML")


@dp.message_handler(
    lambda message: int(message.text) < 1 or int(message.text) > 11,
    state=UserStates.grade)
async def process_grade_invalid_interv(message: types.Message):
  """
    Класс должен быть между 1 и 11. (обработчик для состояния "grade")
    """
  await message.answer("<i>Номер класса должен быть от 1 до 11.</i>",
                       parse_mode="HTML")


@dp.message_handler(state=UserStates.grade)
async def process_grade(message: types.Message, state: FSMContext):
  async with state.proxy() as data:
    data['grade'] = message.text

    # Спрашиваем, в какой школе учишься
    await message.answer("Какой профиль у твоего класса?",
                         reply_markup=profileMenu)
    # Переключаемся на состояние "school"
    await UserStates.profile.set()


@dp.message_handler(lambda message: message.text not in [
    "Технический", "Гуманитарный", "Естественнонаучный",
    "Социально-экономический", "Общеобразовательный"
],
                    state=UserStates.profile)
async def process_profile_invalid(message: types.Message):
  """
    Выберите один из вариантов ответа. (обработчик для состояния "profile")
    """
  await message.answer("Пожалуйста, выбери один из вариантов ответа⬇️")


@dp.message_handler(state=UserStates.profile)
async def process_profile(message: types.Message, state: FSMContext):
  async with state.proxy() as data:
    data['profile'] = message.text

    # Спрашиваем, в каком городе живешь
    await message.answer("В каком городе ты живешь?",
                         reply_markup=removeButton)
    # Переключаемся на состояние "city"
    await UserStates.city.set()


@dp.message_handler(state=UserStates.city)
async def process_city(message: types.Message, state: FSMContext):
  async with state.proxy() as data:
    data['city'] = message.text

    # Спрашиваем, готов ли сменить город для поступления в университет
    await message.answer(
        "Готовы ли вы сменить город для достижения своей цели?",
        reply_markup=changeCityMenu)
    # Переключаемся на состояние "change_city"
    await UserStates.change_city.set()

@dp.message_handler(lambda message: message.text not in ("Да, готов переехать в любой город", "Хочу переехать в столицу", "Готов переехать в соседний регион", \
                    "Готов переехать в город в своём регионе", "Нет, останусь в своём городе"), state=UserStates.change_city)
async def process_change_city_invalid(message: types.Message):
  """
    Выберите один из вариантов ответа. (обработчик для состояния "change_city")
    """
  await message.answer("Пожалуйста, выбери один из вариантов ответа⬇️")


@dp.message_handler(state=UserStates.change_city)
async def process_change_city(message: types.Message, state: FSMContext):
  async with state.proxy() as data:
    data['change_city'] = message.text

    # Спрашиваем Soft Skills
    await message.answer(
        "Какие <b>Soft Skills</b> у тебя развиты? <i>(Выбери ниже и нажми Продолжить)</i>",
        parse_mode="HTML",
        reply_markup=softSkillsMenu)
    data['tmp_soft_skills'] = list()
    data["user_soft_skills_menu"] = deepcopy(softSkillsMenu)
    # Переключаемся на состояние "soft_skills"
    await UserStates.soft_skills.set()


@dp.callback_query_handler(lambda c: c.data == "continue",
                           state=UserStates.soft_skills)
async def process_soft_skills(call, state: FSMContext):
  async with state.proxy() as data:
    data['soft_skills'] = ", ".join(data['tmp_soft_skills'])
    del data['tmp_soft_skills']
    del data["user_soft_skills_menu"]
    await call.answer("Soft skills выбраны")
    if data['soft_skills']:
      await bot.edit_message_text(
          f"Вы выбрали следующие <b>Soft skills</b>: <i>{data['soft_skills']}</i>",
          chat_id=call.from_user.id,
          message_id=call.message.message_id,
          parse_mode="HTML")
    else:
      await bot.edit_message_text("Вы не выбрали ни одного <b>Soft skills</b>",
                                  chat_id=call.from_user.id,
                                  message_id=call.message.message_id,
                                  parse_mode="HTML")
    # Спрашиваем Hard Skills
    await bot.send_message(
        call.from_user.id,
        "Какие <b>Hard Skills</b> у тебя развиты? <i>(перечисли через запятую)</i>",
        parse_mode="HTML",
        reply_markup=removeButton)
    # Переключаемся на состояние "hard_skills"
    await UserStates.hard_skills.set()


@dp.callback_query_handler(state=UserStates.soft_skills)
async def add_soft_skills(call, state):
  async with state.proxy() as data:
    user_data = call.data.split(",")
    numb = int(user_data[0])
    skill = user_data[1]
    if skill not in data['tmp_soft_skills']:
      data["user_soft_skills_menu"]["inline_keyboard"][numb][0]["text"] += "✅"
      data['tmp_soft_skills'].append(skill)
      await call.answer(f"{skill} добавлен")
    else:
      data["user_soft_skills_menu"]["inline_keyboard"][numb][0]["text"] = softSkillsMenu["inline_keyboard"][numb][0]["text"]
      data['tmp_soft_skills'].remove(skill)
      await call.answer(f"{skill} удалён")
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=data["user_soft_skills_menu"])


@dp.message_handler(state=UserStates.hard_skills)
async def process_hard_skills(message: types.Message, state: FSMContext):
  async with state.proxy() as data:
    data['hard_skills'] = message.text

    # Спрашиваем, какие предметы в школе нравятся
    await message.answer(
        "Какие предметы в школе тебе нравятся? (перечисли через запятую)")
    # Переключаемся на состояние "subjects"
    await UserStates.subjects.set()


@dp.message_handler(state=UserStates.subjects)
async def process_subjects(message: types.Message, state: FSMContext):
  async with state.proxy() as data:
    data['subjects'] = message.text
    await message.answer("<b>Вы ответили на все вопросы!</b>",
                         parse_mode="HTML",
                         reply_markup=main_menu)
    result_text = "Я могу:\n\
1)  Рассказать тебе об историях людей, добившихся успеха в похожих на твою областях\n\
2)  Рассказать тебе о том, в каких университетах классно обучают твоей специальности\n\
3)  Рассказать какие есть открытые курсы от ведущих университетов мира\n\
4)  Рассказать, где ты можешь пообщаться со студентами разных университетов\n\
5)  Дать ссылки на полезные для тебя: Ютуб-каналы, Книги, учебники, сайты\n\
6)  Рассказать и дать ссылки на олимпиады, в которых тебе стоит участвовать."

    await message.answer(result_text, reply_markup=resultMenu)

    # Переключаемся на состояние "result"
    await UserStates.result.set()


@dp.callback_query_handler(state=UserStates.result)
async def answers(call, state):
  user_data = call.data.split(",")
  numb = int(user_data[0])
  option = user_data[1]
  await call.answer(DATA2TEXT[option])
  async with state.proxy() as data:
    data["result_message_id"] = call.message.message_id
    if option not in data:
      await bot.edit_message_text("<i>Немного подождите, готовим ответ</i>🕖",
                                  chat_id=call.from_user.id,
                                  message_id=call.message.message_id,
                                  parse_mode="HTML")
      result = await requestto(option, input_data=dict(data))
      # result = "Недоступно"
      data[option] = f"<b>{DATA2TEXT[option]}</b>\n\n{result}"
    userLookResultMenu = deepcopy(resultMenu)
    userLookResultMenu["inline_keyboard"][numb][0]["text"] += "👀"
    await bot.edit_message_text(data[option],
                                chat_id=call.from_user.id,
                                message_id=data["result_message_id"],
                                parse_mode="HTML",
                                reply_markup=userLookResultMenu,
                                disable_web_page_preview=True)


# keep_alive()
if __name__ == '__main__':
  executor.start_polling(dp, skip_updates=True)
