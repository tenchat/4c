"""
知识库服务
"""
import os

from sqlalchemy.testing.suite.test_reflection import metadata

import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 递归文本分割器
from datetime import datetime

def check_md5(md5_str: str):
    """
    检查传入的md5字符是否已经被处理过了
    return False（md5没处理过）  True（md5处理过了）
    """
    if not os.path.exists(config.md5_path):
        # 连文件都还没创建，肯定没有处理过
        open(config.md5_path, 'w', encoding='utf-8').close()
        return False
    else:
        for line in open(config.md5_path, 'r', encoding='utf-8').readlines():
            line=line.strip()
            if line == md5_str:
                return True
        return False

def save_md5(md5_str: str):
    """
    将传入的md5字符，记录到文件内保存
    """
    with open(config.md5_path, 'a', encoding='utf-8') as f:
        f.write(md5_str+'\n')

def get_string_md5(input_str: str,encoding='utf-8'):
    """
    获取传入的字符串的md5
    """
    # 价格字符串还原为二进制，转换为bytes字节数组
    str_bytes = input_str.encode(encoding= encoding)

    md5_obj = hashlib.md5()          # 创建md5对象
    md5_obj.update(str_bytes)        # 更新内容（传入即将要转化的字节数组）
    md5_hex = md5_obj.hexdigest()    # 得到md5的十六进制字符串

    return md5_hex

class KnowledgeBaseService(object):
    def __init__(self):
        # 如果文件夹存在就跳过，不存在就创建
        os.makedirs(config.persist_directory, exist_ok=True)
        self.chroma = Chroma(
            collection_name=config.collection_name,      # 向量数据库的名称
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"), # 嵌入模型
            persist_directory=config.persist_directory   # 向量数据库的存储目录
        )   # 向量存储的实例：chroma数据库
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,          # 分割后的文本段最大长度
            chunk_overlap=config.chunk_overlap,    # 分割后的文本段之间的重叠长度
            separators=config.separators,          # 自然段落分割的符号
            length_function=len                    # 文本长度的计算函数
        )  # 文本分割器的对象

    def upload_by_str(self,data : str,filename):
        """
        将传入的字符串进行向量化，存入向量知识库中
        """
        # 先得到传入字符串的md5值
        md5_hex = get_string_md5(data)
        if check_md5(md5_hex):
            return "【跳过】内容已经存在数据库中"
        if len(data)>config.max_spplit_char_num:
            konwledge_chunks: list[str] = self.spliter.split_text(data)
        else:
            konwledge_chunks = [data]

        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operater": "me",
        }
        self.chroma.add_texts(     # 内容就加载到向量库中了
            texts=konwledge_chunks,
            metadatas=[metadata for _ in konwledge_chunks]
        )
        #保存md5，证明已经处理过了
        save_md5(md5_hex)

        return "【成功】向量数据库中添加了{}条数据".format(len(konwledge_chunks))


if __name__ == '__main__':
    service = KnowledgeBaseService()
    r = service.upload_by_str("周杰伦","testfile")
    print(r)