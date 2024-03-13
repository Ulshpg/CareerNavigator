from aiogram.dispatcher.filters.state import State, StatesGroup


class UserStates(StatesGroup):
  prelaunch = State()
  launch = State()
  name = State()
  age = State()
  grade = State()
  profile = State()
  city = State()
  change_city = State()
  soft_skills = State()
  hard_skills = State()
  subjects = State()
  result = State()


class BalanceStates(StatesGroup):
  balance = State()
  pay = State()
  check = State()