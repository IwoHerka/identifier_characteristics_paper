import os
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": """
            Can you classify one main topic/tag of a GitHub repository by README fragment for me? 

            Give me ONLY the topc in answer, no other text.

            Here it is:

            <font size=7>[English](README.en-US.md)| 简体中文</font>

# Alink

 Alink是基于Flink的通用算法平台,由阿里巴巴计算平台PAI团队研发,欢迎大家加入Alink开源用户钉钉群进行交流。
 
 
<div align=center>
<img src="https://img.alicdn.com/tfs/TB1kQU0sQY2gK0jSZFgXXc5OFXa-614-554.png" height="25%" width="25%">
</div>

- Alink组件列表：http://alinklab.cn/manual/index.html
- Alink教程：http://alinklab.cn/tutorial/index.html
- Alink插件下载器：https://www.yuque.com/pinshu/alink_guide/plugin_downloader

#### Alink教程
<div align=center>
<img src="https://img.alicdn.com/imgextra/i2/O1CN01Z7sbCr1Hg22gLIsdk_!!6000000000786-0-tps-1280-781.jpg" height="50%" width="50%">
</div>

- Alink教程（Java版）：http://alinklab.cn/tutorial/book_java.html
- Alink教程（Python版）：http://alinklab.cn/tutorial/book_python.html
- 源代码地址：https://github.com/alibaba/Alink/tree/master/tutorial
- Java版的数据和资料链接：http://alinklab.cn/tutorial/book_java_00_reference.html
- Python版的数据和资料链接：http://alinklab.cn/tutorial/book_python_00_reference.html
- Alink教程(Java版)代码的运行攻略  http://alinklab.cn/tutorial/book_java_00_code_help.html
- Alink教程(Python版)代码的运行攻略  http://alinklab.cn/tutorial/book_python_00_code_help.html

#### 开源算法列表

<div align=center>
<img src="https://img.alicdn.com/imgextra/i2/O1CN01RKHbLE202moQzvYjW_!!6000000006792-2-tps-1876-955.png" height="100%" width="100%">
</div>
            """
            ,
        }
    ],
    model="gpt-3.5-turbo"
)

print(chat_completion.choices[0])
