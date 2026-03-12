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
with st.sidebar:
    st.header("⚙️ 配置")
    # 让用户填写的输入框
    user_api_key = st.text_input("Gemini API Key (留空则使用作者默认)", type="password")
    
    # 修改模型名称（确保代号正确，避免404）
    model_name = st.selectbox("选择模型", ["gemini-2.0-flash", "gemini-1.5-flash"]) 

# 主界面输入
user_q = st.text_input("咨询事项")
user_n = st.text_input("随机数（如：8, 12, 5）")

if st.button("开始推演"):
    # --- 核心逻辑：二选一 ---
    # 1. 检查 Secrets 里有没有存 MY_OWN_KEY
    system_default_key = st.secrets.get("MY_OWN_KEY")
    
    # 2. 优先级判断：如果用户填了就用用户的，没填就用系统的
    final_api_key = user_api_key if user_api_key else system_default_key
    
    if not final_api_key:
        st.error("❌ 错误：未检测到 API Key。请在侧边栏输入或联系作者配置后台。")
    elif not user_q or not user_n:
        st.warning("⚠️ 提示：请完整输入事项和数字")
    else:
        try:
            res_area = st.empty()
            full_text = ""
            
            # 使用我们确定的 final_api_key 进行调用
            response_stream = call_divine_ai(final_api_key, user_q, user_n, f"models/{model_name}")
            
            for chunk in response_stream:
                if chunk.text:
                    full_text += chunk.text
                    res_area.markdown(full_text)
            
            st.balloons()
        except Exception as e:
            st.cache_resource.clear()
            st.error(f"推演中断：{e}")