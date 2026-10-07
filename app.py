import streamlit as st
import streamlit as st

# === 密码锁功能 ===
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False

if not st.session_state.password_correct:
    st.title("🔒 AI 课程复习教练")
    pwd = st.text_input("请输入访问密码：", type="password")
    if st.button("进入"):
        # 从秘密文件里读取密码进行比对
        if pwd == st.secrets["PASSWORD"]:
            st.session_state.password_correct = True
            st.rerun() # 密码正确，重新加载页面进入应用
        else:
            st.error("密码错误，请重试。")
    st.stop() # 密码不对，下面的代码全部不执行

# === 下面接你原来 app.py 的代码 ===
# st.set_page_config(...)
# st.title(...)
# ...
from openai import OpenAI
import json

# 设置网页的标题和图标
st.set_page_config(page_title="AI 课程复习教练", page_icon="📚")
st.title("📚 AI 课程复习教练")

# ⚠️ 注意：换成你自己的 API Key
API_KEY = st.secrets["API_KEY"]


client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

# 初始化状态，防止每次点击按钮页面刷新时数据丢失
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None

# === 第一部分：输入区 ===
note = st.text_area("第一步：请粘贴你的笔记/文章", height=200)

if st.button("第二步：生成题目与总结"):
    if not note:
        st.warning("笔记不能为空哦！")
    else:
        with st.spinner("AI 正在努力出题中..."):
            prompt = f"请对以下笔记进行总结、提取关键词，并生成3道自测题。严格按此JSON格式返回：{{\"summary\": \"三句话总结\", \"keywords\": [\"关键词\"], \"questions\": [{{\"q\": \"题目\", \"answer\": \"参考答案\"}}]}}。\n\n笔记内容：\n{note}"
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个严谨的学习助手，必须直接输出合法的JSON格式数据。"},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            st.session_state.quiz_data = json.loads(response.choices[0].message.content)

# === 第二部分：展示与答题区 ===
if st.session_state.quiz_data:
    data = st.session_state.quiz_data
    st.success("题目生成成功！")
    
    st.subheader("📝 总结")
    st.info(data["summary"])
    
    st.subheader("🔑 关键词")
    st.write("、".join(data["keywords"]))
    
    st.markdown("---")
    st.subheader("✍️ 自测题")
    
    for i, q in enumerate(data["questions"]):
        st.markdown(f"**第 {i+1} 题：{q['q']}**")
        user_ans = st.text_input("你的答案：", key=f"user_ans_{i}")
        
        if st.button(f"提交第 {i+1} 题批改", key=f"grade_btn_{i}"):
            if not user_ans:
                st.warning("请先输入答案！")
            else:
                with st.spinner("老师正在批改..."):
                    grade_response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": "你是一个耐心的老师。请根据题目和参考答案，判断学生的答案是否正确并详细解释。"},
                            {"role": "user", "content": f"题目：{q['q']}\n参考答案：{q['answer']}\n学生的答案：{user_ans}\n\n请批改："}
                        ]
                    )
                    st.success("【批改结果】")
                    st.write(grade_response.choices[0].message.content)
        st.markdown("---")