import aiosqlite, asyncio

async def create_database():
    async with aiosqlite.connect('user_database.db') as db:
        cursor = await db.cursor()
        await cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            ID INTEGER UNIQUE,
            COINS INTEGER,
        )
        ''')
        await db.commit()

async def check_id(user_id):
    # Открываем соединение с базой данных
    async with aiosqlite.connect('user_database.db') as db:
        # Создаем курсор
        async with db.cursor() as cursor:
            # Выполняем SQL-запрос для проверки наличия ID в первом столбце таблицы
            await cursor.execute(f"SELECT 1 FROM users WHERE ID = {user_id}")
            
            # Получаем результат запроса
            result = await cursor.fetchone()

            # Если результат не пустой, значит, ID существует в таблице
            if result:
                return True
            else:
                return False
            
async def add_new_user(new_id):
    # Открываем соединение с базой данных
    async with aiosqlite.connect('user_database.db') as db:
        # Создаем курсор
        async with db.cursor() as cursor:
            # Выполняем SQL-запрос для добавления новой записи с указанным ID и COINS=2
            await cursor.execute(f"INSERT INTO users (ID, COINS) VALUES ({new_id}, 2)")
            
            # Фиксируем изменения в базе данных
            await db.commit()


async def add_coins(user_id, coins_to_add):
    # Открываем соединение с базой данных
    async with aiosqlite.connect('user_database.db') as db:
        # Создаем курсор
        async with db.cursor() as cursor:
            # Выполняем SQL-запрос для обновления значения COINS
            await cursor.execute(f"UPDATE users SET COINS = COINS + {coins_to_add} WHERE ID = {user_id}")
            
            # Фиксируем изменения в базе данных
            await db.commit()

async def remove_coins(user_id, coins_to_remove):
    # Открываем соединение с базой данных
    async with aiosqlite.connect('user_database.db') as db:
        # Создаем курсор
        async with db.cursor() as cursor:
            # Выполняем SQL-запрос для обновления значения COINS
            await cursor.execute(f"UPDATE users SET COINS = COINS - {coins_to_remove} WHERE ID = {user_id}")
            
            # Фиксируем изменения в базе данных
            await db.commit()

async def get_coins(user_id):
    async with aiosqlite.connect('user_database.db') as db:
        # Создаем курсор
        async with db.cursor() as cursor:
            # Выполняем SQL-запрос для получения значения COINS по заданному ID
            await cursor.execute(f"SELECT COINS FROM users WHERE ID = {user_id}")
            
            # Получаем результат запроса
            result = tuple(await cursor.fetchone())[0]
            return result

async def check_coins_positive(user_id):
    result = await get_coins(user_id)

    # Если результат не пустой и значение COINS больше нуля, возвращаем True
    if result > 0:
        return True
    else:
        return False

# asyncio.run(remove_coins(123623, 4))
# print(asyncio.run(get_coins(123)))
