# suddylangchain
本人学习langchain 的代码及测试
模型使用的ollama + qwen2

# 使用方法
1. 新建.env 文件，
填入如下内容
```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2
```
2. 安装依赖
```
pip install -r requirements.txt
```
3. 测试
```
python 1_单节点单工具.py
```
    

避坑：

1。 工具只支持传入单一的string类型，如需传入多个参数，需要自行拼接或json化

