"""
基于Streamlit框架完成WEB网页上传服务
Streamlit:当web页面元素发生变化（上传一次文件或刷新页面），则代码重新执行一遍
"""
import time

import streamlit as st
from knowledge_base import KnowledgeBaseService

# 设置页面标题
st.title("知识库更新服务")

# 创建上传文件组件
uploader_file = st.file_uploader(
    "请选择要上传的文件",
     type=['txt'],
     accept_multiple_files=False,    # 是否允许上传多个文件,False表示仅接受一个文件的上传
)


# session_state就是一个字典，在页面元素发生改变时，它不会状态刷新，里面的东西会保留
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()



if uploader_file is not None:
    # 获取上传文件的名称
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024   #KB
    st.subheader(f"文件名：{file_name}")
    st.write(f"格式：{file_type} | 大小：{file_size:.2f}KB")
    # 获取上传文件的内容
    file_content = uploader_file.getvalue().decode("utf-8")

    # # 创建一个文件并写入内容
    # with open(file_name, 'wb') as f:
    #     f.write(file_content)
    # # 显示上传成功信息
    # st.success("上传成功")
    # st.write(file_content)

    with st.spinner("正在处理..."):
        time.sleep(1)
        result = st.session_state["service"].upload_by_str(file_content, file_name)
        st.write(result)