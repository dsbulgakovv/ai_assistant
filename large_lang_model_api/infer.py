import logging
from logging.config import dictConfig

from log_config import LogConfig


dictConfig(LogConfig().dict())
logger = logging.getLogger("large_lang_model")


def infer_llm(inp_text: str) -> str:
    return inp_text


def main():
    inp_text = 'Сколько океанов в мире?'
    text = infer_llm(inp_text)
    print(text)


if __name__ == '__main__':
    main()
