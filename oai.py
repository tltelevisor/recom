import openai
from openai import OpenAI
from pydantic import BaseModel
from config import API_KEY, OPENAI_MODEL, FILES_DIR, ALL, DATABASE, NUMBER_ALL
import os, logging, sqlite3
# import pandas as pd
from scipy import spatial

logging.basicConfig(level=logging.INFO, filename='latoken.log',
                    format='%(asctime)s %(levelname)s %(message)s')

client = OpenAI(api_key=API_KEY)

def check_openai_api_key(api_key = API_KEY):
    try:
        client.models.list()
    except openai.AuthenticationError as err:
        logging.error(f'err: {err}, api_key: {api_key}')
        return False
    else:
        return True

def set_openai_api_key(user, api_key):
    global client
    client = OpenAI(api_key=api_key)
    logging.info(f'Установлен введенный пользователем {user} API_KEY: {api_key}')
    return

def oai_test_question(user_id, test_all, ctx = ALL):
    logging.info(f'test_all: {test_all}, about: {ctx["about"]}, files: {ctx["files"]}')
    if test_all:
        cnxt = context(ctx['files'])
    else:
        sql = f'SELECT text FROM mess WHERE tlgid="{user_id}";'
        conn = sqlite3.connect(DATABASE)
        text, *rest = conn.cursor().execute(sql).fetchall()
        conn.commit()
        conn.close()
        cnxt = ''
        for et in text:
            cnxt = cnxt + '\n' + et[0]

    class QuestionAnswer(BaseModel):
        question: str
        answer_right: str
        answer_wrong: str

    sys_prompt = (f'Ты эксперт по компании LATOKEN. В тройных кавычках - описание {ctx["about"]} компании: """{cnxt}""". '
                  f'Выбери случайный факт. Задай по нему вопрос. Сформулируй два варианта ответа, один правильный, второй неравильный.')
    messages = [{"role": "system", "content": sys_prompt}]
    response = client.beta.chat.completions.parse(
        messages=messages,
        model=OPENAI_MODEL,
        response_format=QuestionAnswer,
        max_tokens=500,
    )
    logging.info(
        f'user_id: {user_id}, prompt_tokens: {response.usage.prompt_tokens}, completion_tokens: {response.usage.completion_tokens}')
    completion = response.choices[0].message.parsed
    return completion.question, completion.answer_right, completion.answer_wrong

def context(file_list):
    files = os.listdir(FILES_DIR)
    file_content = ''
    for ef in files:
        if ef in file_list or len(file_list) == 0:
            file_path = f'{FILES_DIR}/{ef}'
            logging.info(f'file: {ef}')
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file_content + '\n' + file.read()
    return file_content

def oai_context(user_id, message, ctx = ALL):
    cnxt = context(ctx['files'])
    sys_prompt = f'Ты эксперт по компании LATOKEN. В тройных кавычках - описание {ctx["about"]} компании: """{cnxt}""". Ответь на вопрос.'
    logging.info(f'about: {ctx["about"]}, files: {ctx["files"]}')
    messages = [{'role': 'system', 'content': sys_prompt}]
    messages.append({'role': 'user', 'content': message})

    response = client.chat.completions.create(
        messages=messages,
        model=OPENAI_MODEL
    )
    logging.info(
        f'user_id: {user_id}, prompt_tokens: {response.usage.prompt_tokens}, completion_tokens: {response.usage.completion_tokens}')
    return response.choices[0].message.content.strip()

def oai_fact(user_id, ctx = ALL):
    cnxt = context(ctx['files'])
    sys_prompt = f'Ты эксперт по компании LATOKEN. В тройных кавычках - описание {ctx["about"]} компании: """{cnxt}""". Выбери случайный факт из контекста и расскажи о нем.'
    logging.info(f'about: {ctx["about"]}, files: {ctx["files"]}')
    messages = [{'role': 'system', 'content': sys_prompt}]
    response = client.chat.completions.create(
        messages=messages,
        model=OPENAI_MODEL
    )
    logging.info(
        f'user_id: {user_id}, prompt_tokens: {response.usage.prompt_tokens}, completion_tokens: {response.usage.completion_tokens}')
    return response.choices[0].message.content.strip()

def oai_give_question(user_id, ctx = ALL):
    cnxt = context(ctx['files'])
    sys_prompt = f'Ты эксперт по компании LATOKEN. В тройных кавычках - описание {ctx["about"]} компании: """{cnxt}""". Выбери случайный факт из контекста и задай по нему вопрос.'
    logging.info(f'about: {ctx["about"]}, files: {ctx["files"]}')
    messages = [{"role": "system", "content": sys_prompt}]
    response = client.chat.completions.create(
        messages=messages,
        model=OPENAI_MODEL
    )
    logging.info(
        f'user_id: {user_id}, prompt_tokens: {response.usage.prompt_tokens}, completion_tokens: {response.usage.completion_tokens}')
    return response.choices[0].message.content.strip()

def oai_check_answer(user_id, question, answer, ctx = ALL):
    cnxt = context(ctx['files'])
    sys_prompt = f'Ты эксперт по компании LATOKEN. В тройных кавычках - описание {ctx["about"]} компании: """{cnxt}""". Твоя задача - оценить в баллах от 1 до 5 насколько ответ """{answer}""" соответствует вопросу """{question}""".'
    logging.info(f'about: {ctx["about"]}, files: {ctx["files"]}')
    messages = [{"role": "system", "content": sys_prompt}]
    response = client.chat.completions.create(
        messages=messages,
        model=OPENAI_MODEL
    )
    logging.info(
        f'user_id: {user_id}, prompt_tokens: {response.usage.prompt_tokens}, completion_tokens: {response.usage.completion_tokens}')
    return response.choices[0].message.content.strip()

# не используется
# def strings_ranked_by_relatedness(
#             query: str,
#             df: pd.DataFrame,
#             relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
#             top_n: int = NUMBER_ALL
#     ) -> tuple[list[str], list[float]]:
#     if df.shape[0] > 0:
#         embedding_result = client.embeddings.embeddings_generation(input=query)
#         query_embedding = embedding_result.data[0].embedding
#         strings_and_relatednesses = [
#             (row["id"], row["question"], relatedness_fn(query_embedding, pickle.loads(row["emb_q"])))
#             for i, row in df.iterrows()
#         ]
#         strings_and_relatednesses.sort(key=lambda x: x[2], reverse=True)
#         id, strings, relatednesses = zip(*strings_and_relatednesses)
#         return id[:top_n], strings[:top_n], round(relatednesses[:top_n], 2)
#     else:
#         return [], [], []