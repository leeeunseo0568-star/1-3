import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="달달한 연애 상담소", page_icon="💖", layout="centered")
st.title("💖 달달하고 명쾌한 연애 상담소")
st.write("연애에 대한 고민이 있으신가요? 무엇이든 편하게 이야기해보세요!")

# 2. Streamlit Secrets에서 API 키 가져오기 및 설정
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except KeyError:
    st.error("🔑 Streamlit Secrets에 'GOOGLE_API_KEY'가 설정되지 않았습니다. 설정 후 다시 시도해주세요.")
    st.stop()

# 3. 세션 상태(Session State)를 이용한 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요! 당신의 연애 고민을 들어드릴 AI 상담사입니다. 어떤 고민이 있으신가요? 😊"
        }
    ]

# 4. 이전 채팅 기록 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 5. 사용자 입력 받기
if user_input := st.chat_input("고민을 입력하세요... (예: 썸남이 선톡을 안 해요😭)"):
    
    # 사용자의 메시지를 화면에 출력 및 세션에 저장
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 6. Gemini 모델 호출 및 답변 생성
    with st.chat_message("assistant"):
        with st.spinner("당신의 고민을 신중하게 생각하는 중... 🤔"):
            try:
                # 최신 gemini-2.5-flash-lite 모델 로드
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash-lite",
                    system_instruction=(
                        "당신은 따뜻하고 공감 능력이 뛰어나면서도, 때로는 객관적이고 명쾌한 조언을 해주는 연애 상담 전문가입니다. "
                        "상담 신청자에게 친근한 말투(반말과 존댓말 중 적절히 친근한 어조, 혹은 부드러운 해요체)를 사용하여 위로와 실질적인 팁을 건네세요."
                    )
                )
                
                # 대화 맥락을 유지하기 위해 전체 대화 기록을 프롬프트 형태로 재구성
                # (단순 단발성 호출 대신 대화 흐름 전달)
                chat_history = []
                for msg in st.session_state.messages[:-1]: # 현재 입력 제외한 이전 기록
                    role_label = "user" if msg["role"] == "user" else "model"
                    chat_history.append({"role": role_label, "parts": [msg["content"]]})
                
                # 멀티턴 대화 시작
                chat = model.start_chat(history=chat_history)
                response = chat.send_message(user_input)
                
                # 답변 출력 및 세션 저장
                assistant_response = response.text
                st.write(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                
            except Exception as e:
                # 에러 발생 시 사용자에게 친절하게 안내
                st.error("⚠️ 답변을 생성하는 중에 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
                st.caption(f"Error 이력: {str(e)}") # 개발자 디버깅용 소형 문구
