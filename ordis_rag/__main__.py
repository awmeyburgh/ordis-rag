from dotenv import load_dotenv
load_dotenv()

from pprint import pprint
from ordis_rag.ordis import Ordis

ordis = Ordis()
graph = ordis.compile()

while True:
    state = ordis.init_state(input('User: '))
    state = graph.invoke(state)
    print('AI:', state['answer'])