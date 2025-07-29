""" embedding """
from enum import Enum
import os
from typing import Any
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("BIANXIE_API_KEY")
api_base = os.getenv("BIANXIE_BASE")


class EmbeddingType(Enum):
    """enum
    """
    DEFAULT_EMBEDDING = "DefaultEmbedding"
    OPENAI_EMBEDDING = 'OpenAIEmbedding'
    SIMILARITY_TEXT_3S_EMBEDDING = "Similaritytext3sEmbedding"
    SIMILARITY_TEXT_3L_EMBEDDING = "Similaritytext3lEmbedding"
    SEARCH_TEXT_3S_EMBEDDING = "Searchtext3sEmbedding"
    SEARCH_TEXT_3L_EMBEDDING = "Searchtext3lEmbedding"

    # 添加更多选项

class Embedding:
    """embedding 方案
    index._embed_model.get_agg_embedding_from_queries(['朱彦青','cc'])   对一组（或多个）相关的查询字符串生成一个聚合的嵌入向量
    index._embed_model.get_text_embedding('朱彦青')    对一个字符串进行词向量嵌入

    """
    def __new__(cls, emb_type: EmbeddingType | str) -> Any:
        if isinstance(emb_type,EmbeddingType):
            assert emb_type.value in [i.value for i in EmbeddingType]
            key_name = emb_type.value
        else:
            assert emb_type in [i.value for i in EmbeddingType]
            key_name = emb_type

        instance = None

        if key_name == 'DefaultEmbedding':
            instance = Settings.embed_model

        elif key_name == 'Similaritytext3sEmbedding':
            instance = OpenAIEmbedding(
                 mode='similarity', #text_search
                 model='text-embedding-3-small',
                 api_base=api_base,
                 api_key=api_key)

        elif key_name == 'Similaritytext3lEmbedding':
            instance = OpenAIEmbedding(
                 mode='similarity', #text_search
                 model='text-embedding-3-large',
                 api_base=api_base,
                 api_key=api_key)

        elif key_name == 'Searchtext3sEmbedding':
            instance = OpenAIEmbedding(
                 mode='text_search',
                 model='text-embedding-3-small',
                 api_base=api_base,
                 api_key=api_key)

        elif key_name == 'Searchtext3lEmbedding':
            instance = OpenAIEmbedding(
                 mode='text_search',
                 model='text-embedding-3-large',
                 api_base=api_base,
                 api_key=api_key)


        elif key_name == 'OpenAIEmbedding':
            instance = OpenAIEmbedding(api_base=api_base,
                                       api_key=api_key)

        else:
            raise TypeError('Unknown type')

        return instance
