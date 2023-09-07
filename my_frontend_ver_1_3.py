import re
import streamlit as st 
from io import BytesIO # 바이트 데이터를 다뤄야 해서
import requests  # HTTP요청을 보낼 때 사용
import mimetypes # 파일 확장자 검사할때 사용
import time

# 세션 상태 초기화
if 'logged_in' not in st.session_state:   # p_1
    st.session_state['logged_in'] = False

if 'login_message_displayed' not in st.session_state: # p_2
    st.session_state['login_message_displayed'] = False

if 'loading' not in st.session_state: # p_3
    st.session_state['loading'] = False

if 'sign_up' not in st.session_state: # p_4
    st.session_state['sign_up'] = False

if 'output' not in st.session_state: # p_5
    st.session_state['output'] = False

# 로그인이 되지 않은 경우
if not st.session_state['logged_in']: # p_1
    st.session_state['logged_in'] = False

    # 회원가입 세션 활성화 여부에 따라 다른 UI를 보여줌
    if st.session_state['sign_up']:  # p_4
        st.markdown("<h1 style='font-size: 32px;'>회원가입</h1>", unsafe_allow_html=True)

        signup_username = st.text_input("닉네임")
        signup_id = st.text_input("이메일 주소", key='signup_email')
        signup_pw = st.text_input("비밀번호", type="password")
        signup_confirm_pw = st.text_input("비밀번호 확인", type="password")
        signup_gender = st.selectbox("성별", ["남성", "여성"])

        # 이메일 형식 검증
        def validate_email(email):
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
            if re.search(regex, email):
                return True
            else:
                return False
            
        # 비밀번호 형식 검증
        def validate_password(password):
            regex = r'^.{6,}$'
            if re.search(regex, password):
                return True
            else:
                return False
            
        # 회원가입 버튼 클릭 후 세션 이동
        if st.button("회원가입 신청"):  # HJ_01
            if signup_pw == signup_confirm_pw:
                if validate_email(signup_id) and validate_password(signup_pw):  # 이메일 형식 및 비밀번호 형식 검증
                    response = requests.post("http://localhost:5000/sign-up", json={
                        "username": signup_username,
                        "id": signup_id,
                        "pw": signup_pw,
                        "gender": signup_gender
                    })
                    if response.status_code == 200:
                        st.success("회원가입 성공")
                        st.session_state['sign_up'] = False
                        st.session_state['logged_in'] = True
                        st.experimental_rerun()
                    else:
                        st.error("회원가입 실패: " + response.json().get('msg', ''))
                else:
                    st.error("이메일 형식으로 입력해주세요.")
            else:
                st.error("비밀번호가 일치하지 않습니다.")
    else:
        left_column, right_column = st.columns(2)
        # 로그인 폼
        left_column.markdown("<h1 style='font-size: 36px;'>AI패션 추천 서비스</h1>", unsafe_allow_html=True)
    
        email = left_column.text_input("이메일 주소", key='login_email')
        password = left_column.text_input("비밀번호", type="password", key='login_password')  # key로 로그인 폼의 password인지 회원가입 폼의 password인지 구별해줘야함.

        if left_column.button("로그인"):
            response = requests.post("http://localhost:5000/login", data={"email": email, "password": password})
            if response.status_code == 200:
                left_column.success("로그인 성공")
                st.session_state['logged_in'] = True
                st.session_state['login_message_displayed'] = True
                time.sleep(3)
                st.experimental_rerun()
            else:
                left_column.error("로그인 실패")

        elif left_column.button("회원가입"):        
            st.session_state['sign_up'] = True
            st.experimental_rerun()
        
        right_column.image("./front_images/main_image.jpg", use_column_width=True)
   
# 로그인 성공 페이지
elif 'login_message_displayed' not in st.session_state: # p_2
    st.session_state['login_message_displayed'] = False
    st.success("로그인 성공! 이미지 업로드 페이지로 이동합니다..")
    st.session_state['login_message_displayed'] = False  # <-- 상태를 다시 False로 변경
    time.sleep(3)
    st.experimental_rerun()


# 로딩 상태인 경우
elif st.session_state['loading']: # p_3
    st.image("./front_images/loading_image.jpg", use_column_width=True)  # 로딩 이미지
    st.text("분석 중입니다... \n 의류의 종류, 색상을 판단하고 어울릴만한 패션을 선별 중입니다.")
    # 여기서 flask에서 어떤 반응이오면 다음 세션으로 넘어가는 코드가 들어가야할 것 같음.


# 로그인이 되어 있는 경우 (그리고 로딩 상태도 아니며, 로그인 메시지도 표시하지 않는 경우)
else: # p_0
    # 이미지 업로드와 관련된 UI 코드
    left_column, right_column = st.columns(2)
    
    with left_column:
        st.markdown("<h1 style='font-size: 32px;'>AI에게 내 옷 보여주기</h1>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("이미지 업로드", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            # 파일 확장자 검증
            ext = mimetypes.guess_extension(uploaded_file.type)
            if ext not in ['.jpg', '.jpeg', '.png']:
                st.error("업로드 파일을 다시 확인해주시고, 의류 이미지를 업로드 해주세요.")
            else:
                file_stream = BytesIO(uploaded_file.read())
                uploaded_file.seek(0)
                st.image(file_stream, caption="업로드된 이미지", use_column_width=True)

                if st.button('AI에게 사진 보내기'):
                    flask_server_url = "http://localhost:5000/upload"
                    files = {"file": (uploaded_file.name, file_stream)}
                    response = requests.post(flask_server_url, files=files)

                    if response.status_code == 200:
                        st.success("이미지 전송 성공!")
                        st.session_state['loading'] = True  # 로딩 상태를 True로 설정
                        time.sleep(3)  # 3초 대기하거나 원하는 동작 수행
                        st.experimental_rerun()
                    else:
                        st.error("이미지 전송 실패")

    with right_column:
        st.image("./front_images/upload_session_image.jpg", use_column_width=True)

