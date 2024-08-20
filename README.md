# DrissionPageDemo
DrissionPage库的练手项目自用

## API请求

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
-H "Content-Type: application/json" \
-d '{
  "messages": [
    {
      "role": "system",
      "content": "You are ChatGPT, a large language model trained by OpenAI."
    },
    {
      "role": "user",
      "content": "What is the capital of France?"
    },
    {
      "role": "assistant",
      "content": "The capital of France is Paris."
    },
    {
      "role": "user",
      "content": "And what about the UK?"
    }
  ],
  "stream": true,
  "model": "gpt-3.5-turbo-16k",
  "temperature": 0.5,
  "presence_penalty": 0,
  "frequency_penalty": 0,
  "top_p": 1
}'
```

支持流式和非流式请求，流式请求需要设置`stream`为`true`，非流式请求需要设置`stream`为`false`。

![image](https://github.com/user-attachments/assets/67017db4-afee-49b6-b5c3-3f732dad350a)



![image](https://github.com/user-attachments/assets/c1066680-a102-46a7-ab23-45dee5166bcc)

![image](https://github.com/user-attachments/assets/8dae6a06-6535-4a8e-8ecd-c035f543d372)
