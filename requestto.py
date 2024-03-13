from langchain.indexes import VectorstoreIndexCreator
from langchain.document_loaders import DirectoryLoader
from langchain.chat_models import ChatOpenAI
import os


os.environ["OPENAI_API_KEY"] = "я"
loaders = DirectoryLoader("data", "*.txt")
index = VectorstoreIndexCreator().from_loaders([loaders])
user_requests = {
    "successfulPeople": "Меня зовут {input_data[name]}. Мои любимые предметы: {input_data[subjects]}. Мое направление: {input_data[profile]}. \
Мои профессиональные навыки: {input_data[hard_skills]}. Напиши мотивационные истории 3-5 реальных людей, добившихся успеха в моей области. По-желанию можешь вставить немного цитат. \
Ответ должен быть в свободной форме, направленный на школьника",

    "Universities": "Ты профессиональный тьютор. Меня зовут {input_data[name]}. Составь для меня список Российских ВУЗов ориентируясь на вопросы: В каком городе живёшь: {input_data[city]}. \
Готов переехать для поступления: {input_data[change_city]}.\
Любимые предметы: {input_data[subjects]}. Навыки: {input_data[hard_skills]}. Направление: {input_data[profile]}. В ответе напиши 4 ВУЗа (реальных) по возрастанию места по России. \
Ответ должен содержать: навазние ВУЗа, его место по России. Прикрепи ссылки на главную страницу и страница факультеты",

    "Courses": "Ты профессиональный тьютор. Составь мне список курсов и ссылки на них по трём критериям: в области {input_data[profile]}. По следующим предметам: {input_data[subjects]}. \
И связаны с навыками: {input_data[hard_skills]}. Не пиши лишней информации",
    "studentExperience": "Напиши мне опыт 5 студентов в области {input_data[profile]}",
    "addMaterials": "Посоветуй дополнительную литературу, форумы, помогающие в области: {input_data[profile]} или в предметах: {input_data[subjects]}",
    "olympiads": "Ты профессиональный тьютор. Составь мне список олимпиад и ссылки на них по трём критериям: в области {input_data[profile]}. По следующим предметам: {input_data[subjects]}. \
И связаны с навыками: {input_data[hard_skills]}. Не пиши лишней информации"
}

async def requestto(option, input_data):
    query = user_requests[option].format(input_data=input_data)
    return index.query(query, llm=ChatOpenAI(temperature=1, request_timeout=400))