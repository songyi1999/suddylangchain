
# 安装启动ollama

curl -fsSL https://ollama.com/install.sh | sh

# 添加qwen2
ollama serve &
ollama pull qwen2:1.5b

python -m pip install -r  requirement.txt