import os
import streamlit as st
from google import genai
from google.genai import types

# --- 1. 使用单例模式管理客户端 ---
# 这样可以防止客户端被频繁创建和关闭
@st.cache_resource
def get_stable_client(api_key):
    return genai.Client(api_key=api_key)

# --- 2. 优化后的核心调用函数 ---
def call_divine_ai(api_key, question, nums, model_choice):
    # 获取稳定的客户端
    client = get_stable_client(api_key)
    
    sys_instruction = """你是一位精通梅花易数的赛博占卜师。
    请按以下流程起卦：
    1. 告知卦名（如：地火明夷）。
    2. 给出程序员视角的硬核逻辑解析。
    3. 提供避坑指南。"""
    
    prompt = f"问事：{question}\n数字：{nums}"

    config = types.GenerateContentConfig(
        system_instruction=sys_instruction,
        temperature=0.7,
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )
    
    # 直接返回流对象
    return client.models.generate_content_stream(
        model=model_choice,
        contents=prompt,
        config=config,
    )

# --- 3. UI 逻辑部分 ---
st.title("🔮 赛博易经：数字推演")

# 侧边栏配置
# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 配置")
    user_api_key = st.text_input("Gemini API Key", type="password")
    # 修改为官方支持的模型名称
    model_name = st.selectbox("选择模型", ["models/gemini-2.5-flash", "models/gemini-2.5-pro"]) # 从您列出的可用模型中选择   

# 主界面输入
user_q = st.text_input("咨询事项")
user_n = st.text_input("随机数（如：8, 12, 5）")







if st.button("开始推演"):
    if not user_api_key:
        st.error("请输入 API Key")
    else:
        try:
            # 这里的 res_area 用于动态显示流式文字
            res_area = st.empty()
            full_text = ""
            
            # 关键：调用函数并迭代流
            # 注意：我们将 model_name 也传进去，保证一致性
            response_stream = call_divine_ai(user_api_key, user_q, user_n, model_name)
            
            for chunk in response_stream:
                if chunk.text:
                    full_text += chunk.text
                    res_area.markdown(full_text)
            
            st.balloons()
        except Exception as e:
            # 如果报错，清除缓存重试
            st.cache_resource.clear()
            st.error(f"推演中断：{e}")