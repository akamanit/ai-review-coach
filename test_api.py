from openai import OpenAI
import json
API_KEY = "请输入你的API_KEY"

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

print("正在呼叫AI...")
with open("note.txt","r",encoding="utf-8") as f:
        note = f.read()
print("笔记读取成功，准备发送给AI...")
response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
                {"role": "system", "content":"你是一个严谨的学习助手，必须直接输出合法的JSON格式数据，禁止包含任何解释和Markdown代码块标记（如```json）。"},
                {"role": "user", "content": f"请对以下笔记进行总结、提取关键词，并生成3道自测题。严格按此JSON格式返回：{{\"summary\": \"三句话总结\", \"keywords\": [\"关键词\"], \"questions\": [{{\"q\": \"题目\", \"answer\": \"参考答案\"}}]}}。\n\n笔记内容：\n{note}"}
        ],
        response_format={"type": "json_object"}
)

data = json.loads(response.choices[0].message.content)

print("=== AI 解析成功 ===")
print("总结：", data["summary"])
print("关键词：", data["keywords"])
print("=== 开始答题 ===")

# 遍历所有题目，一一作答
for i, q in enumerate(data["questions"]):
    print(f"\n第 {i+1} 题：{q['q']}")
    
    # 1. 程序暂停，等待你输入答案
    user_answer = input("你的答案：")
    
    # 2. 打包批改请求，发给 AI
    print("正在批改，请稍候...")
    grade_response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个耐心的老师。请根据题目和参考答案，判断学生的答案是否正确。如果正确，请给予肯定；如果错误或不够完整，请指出错误并详细解释。请直接输出批改结果，不要输出JSON。"},
            {"role": "user", "content": f"题目：{q['q']}\n参考答案：{q['answer']}\n学生的答案：{user_answer}\n\n请批改："}
        ]
    )
    
    # 3. 打印 AI 的批改意见
    print("【批改结果】")
    print(grade_response.choices[0].message.content)
    print("-" * 30)

print("\n🎉 今日答题结束，你太棒了！")