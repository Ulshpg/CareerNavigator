from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from yoomoney import Quickpay
from config import PRICE_FOR_COIN

main_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
main_menu.add(KeyboardButton("Новый план📋"), KeyboardButton("Баланс💰"))
newPlanOrStayMenu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    KeyboardButton("Новый план📋"), KeyboardButton("Вернуться↩"))
createOrCancelMenu = ReplyKeyboardMarkup(resize_keyboard=True,
                                         row_width=1).add(
                                             KeyboardButton("Создать✅"),
                                             KeyboardButton("Отмена❌"))
balanceMenu = ReplyKeyboardMarkup(resize_keyboard=True,
                                  row_width=1).add(KeyboardButton("Пополнить💸"),
                                                   KeyboardButton("Назад↩"))
softSkillsMenu = InlineKeyboardMarkup(resize_keyboard=True)
cancelMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Назад↩"))
for i, skill in enumerate(("Эффективное общение", "Эмпатия", "Управление конфликтами", "Навыки работы в команде", "Стресс-менеджмент",\
            "Решение проблем", "Продуктивность", "Критическое мышление", "Внимание к деталям", "Адаптируемость")):
  softSkillsMenu.add(InlineKeyboardButton(skill, callback_data=f"{i},{skill}"))
del skill
softSkillsMenu.add(
    InlineKeyboardButton("Продолжить➡️", callback_data="continue"))

profileMenu = ReplyKeyboardMarkup(resize_keyboard=True)

profileMenu.add(KeyboardButton('Технический')).add(
    KeyboardButton('Гуманитарный')).add(
        KeyboardButton('Естественнонаучный')).add(
            KeyboardButton('Социально-экономический')).add(
                KeyboardButton("Общеобразовательный"))

genderMenu = ReplyKeyboardMarkup(resize_keyboard=True)
genderMenu.row(KeyboardButton('Мужской'), KeyboardButton('Женский'))
launchMenu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
launchMenu.add(KeyboardButton('Погнали'))

resultMenu = InlineKeyboardMarkup(1).add(
    InlineKeyboardButton('Успешные люди', callback_data='0,successfulPeople'),
    InlineKeyboardButton('ВУЗы', callback_data='1,Universities'),
    InlineKeyboardButton('Курсы', callback_data='2,Courses'),
    InlineKeyboardButton('Опыт студентов',
                         callback_data='3,studentExperience'),
    InlineKeyboardButton('Доп. материалы', callback_data='4,addMaterials'),
    InlineKeyboardButton('Олимпиады', callback_data='5,olympiads'))

changeCityMenu = ReplyKeyboardMarkup(resize_keyboard=True,
                                     one_time_keyboard=True,
                                     row_width=1)
changeCityMenu.add(KeyboardButton("Да, готов переехать в любой город"), KeyboardButton("Хочу переехать в столицу"), KeyboardButton("Готов переехать в соседний регион"), \
                   KeyboardButton("Готов переехать в город в своём регионе"), KeyboardButton("Нет, останусь в своём городе"))
removeButton = ReplyKeyboardRemove()


async def GetPaymentsMenu(label):
    price = int(label[1:label.index("ID")]) * PRICE_FOR_COIN
    print(price)
    quickpay = Quickpay(receiver="4100118271372368",
                      quickpay_form="shop",
                      targets="Sponsor this project",
                      paymentType="SB",
                      sum=price,
                      label=label)
    PaymentsMenu = InlineKeyboardMarkup(1).add(
        InlineKeyboardButton('Оплатить', url=quickpay.redirected_url),
        InlineKeyboardButton('Проверить оплату', callback_data=label))
    return PaymentsMenu
