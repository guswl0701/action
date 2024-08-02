from locust import HttpUser, task, between, events
import random
import re
import time
from locust.runners import MasterRunner

# 사용자 계정 정보
user_accounts = [
    "kimhj@gmail.com", "leehj@gmail.com", "wangjh@gmail.com", "kimjs@gmail.com", "parkhb@gmail.com",
    "leesy@gmail.com", "chojh@gmail.com", "kimms@gmail.com", "parkjy@gmail.com", "choisj@gmail.com",
    "kimdk@gmail.com", "hanyh@gmail.com", "leejj@gmail.com", "parksh@gmail.com", "kangej@gmail.com",
    "jungmh@gmail.com", "kimys@gmail.com", "leejy@gmail.com", "kimch@gmail.com", "seojh@gmail.com",
    "choims@gmail.com", "leeej@gmail.com", "kangsh@gmail.com", "parkjy2@gmail.com", "kimhs@gmail.com",
    "leesj@gmail.com", "ahnjh@gmail.com", "kimyh@gmail.com", "choimj@gmail.com", "leesh@gmail.com",
    "kimjy@gmail.com", "kimds@gmail.com", "parkej@gmail.com", "shinjh@gmail.com", "kimsy@gmail.com",
    "leemh@gmail.com", "choijs@gmail.com", "parkhy@gmail.com", "kimjh@gmail.com", "leeej2@gmail.com",
    "kangsh2@gmail.com", "kimms2@gmail.com", "chojy@gmail.com", "leesh2@gmail.com", "kimej@gmail.com",
    "parkjh@gmail.com", "leesy2@gmail.com", "kimmh@gmail.com", "choijs2@gmail.com", "leehy@gmail.com",
    "seojh2@gmail.com", "parkej2@gmail.com", "kimms3@gmail.com", "kimsh@gmail.com", "leejy2@gmail.com",
    "parkdk@gmail.com", "kimyh2@gmail.com", "leemj@gmail.com", "choish@gmail.com", "kangej2@gmail.com",
    "kimjh2@gmail.com", "parksy@gmail.com", "leemh2@gmail.com", "choijs3@gmail.com", "seohy@gmail.com",
    "kimej2@gmail.com", "kangsh3@gmail.com", "leems@gmail.com", "parkjy3@gmail.com", "kimsh2@gmail.com",
    "leeej3@gmail.com"
]

user_names = [
    "김현지", "이현지", "왕지호", "김정수", "박한비", "이서연", "조재현", "김민서", "박지연", "최수진", "김도경", "한윤호", "이재준", "박성훈",
    "강은지", "정민형", "김유신", "이지연", "김철호", "서지현", "최민석", "이은정", "강수현", "박준영", "김현수", "이수진", "안재호", "김영훈",
    "최민주", "이상현", "김지영", "김동석", "박은지", "신재현", "김서연", "이민혁", "최진서", "박효연", "김재현", "이은주", "강성훈", "김민수",
    "조지연", "이상호", "김은지", "박재현", "이서영", "김민호", "최지선", "이현영", "서재훈", "박은정", "김민서", "김성현", "이지영", "박도경",
    "김윤호", "이민재", "최서현", "강은주", "김재호", "박서연", "이민형", "최진수", "서현영", "김은정", "강성호", "이민서", "박지영", "김상현",
    "이은지"
]

password = "1234"
login_index = 0
logged_in_users = []

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        if len(logged_in_users) < len(user_accounts):
            self.login()
        else:
            self.perform_random_task()

    def login(self):
        global login_index
        if login_index < len(user_accounts):
            user = user_accounts[login_index]
            user_name = user_names[login_index]
            login_index += 1

            # CSRF 토큰 가져오기 시도 횟수
            max_attempts = 3
            csrf_token = None
            for attempt in range(max_attempts):
                response = self.client.get("/login/")
                csrf_token = self.extract_csrf_token(response.text)
                if csrf_token:
                    break
                time.sleep(1)  # 잠시 대기 후 재시도

            if csrf_token:
                response = self.client.post("/login/", data={"uid": user, "password": password, "csrfmiddlewaretoken": csrf_token}, headers={"Referer": "/login/"})
                if response.status_code == 200:
                    try:
                        json_response = response.json()
                        if json_response.get('success'):
                            print(f"Logged in successfully as {user}")
                            logged_in_users.append(user)
                            self.check_existing_reservation(user_name)  # 로그인 후 바로 예매 여부 확인
                        else:
                            print(f"Failed to log in as {user}: {json_response.get('message')}")
                    except ValueError:
                        print(f"Login response is not JSON for user {user}")
                else:
                    print(f"Failed to log in as {user}: HTTP {response.status_code}")
            else:
                print("Failed to retrieve CSRF token after multiple attempts.")
        else:
            self.perform_random_task()

    def extract_csrf_token(self, text):
        match = re.search(r'name="csrfmiddlewaretoken" value="(.+?)"', text)
        if match:
            return match.group(1)
        return None

    @task
    def perform_random_task(self):
        tasks = [
            self.view_notice,
            self.view_reservation_log
        ]
        task = random.choice(tasks)
        task()

    def view_notice(self):
        with self.client.get("/notice", catch_response=True) as response:
            if response.status_code == 200:
                print("Notice page viewed successfully")
            else:
                print(f"Failed to view notice page: {response.status_code}")
                response.failure("Failed to load notice page")

    def check_existing_reservation(self, user_name):
        # 예매 내역 확인
        with self.client.get("/reservationlog", catch_response=True) as response:
            if response.status_code == 200:
                if "예매 내역이 존재합니다" in response.text:  # 예매 내역이 있으면
                    print(f"{user_name} already has a reservation. Skipping reservation process.")
                else:
                    self.view_reservation(user_name)
            else:
                print(f"Failed to check reservation log: {response.status_code}")
                response.failure("Failed to check reservation log")

    def view_reservation(self, user_name):
        with self.client.get("/reservation", catch_response=True) as response:
            if response.status_code == 200:
                print("Reservation page viewed successfully")
                self.perform_reservation(user_name)
            else:
                print(f"Failed to view reservation page: {response.status_code}")
                response.failure("Failed to load reservation page")

    def perform_reservation(self, user_name):
        # 예매 페이지에서 이름과 가격을 입력하고 예매하기 버튼 클릭
        with self.client.get("/reservation/", catch_response=True) as response:
            if response.status_code == 200:
                csrf_token = self.extract_csrf_token(response.text)
                if csrf_token:
                    with self.client.post("/reservation/", data={
                        "userName": user_name,
                        "price": "백만원",
                        "csrfmiddlewaretoken": csrf_token
                    }, headers={"Referer": "/reservation/"}, catch_response=True) as post_response:
                        if post_response.status_code == 200:
                            print(f"Reservation successful for {user_name}")
                            self.confirm_payment(user_name, csrf_token)
                        else:
                            print(f"Reservation request failed: HTTP {post_response.status_code}")
                            post_response.failure("Failed to make reservation")
                else:
                    print("Failed to retrieve CSRF token for reservation")
                    response.failure("Failed to retrieve CSRF token")
            else:
                print(f"Failed to load reservation page: {response.status_code}")
                response.failure("Failed to load reservation page")

    def confirm_payment(self, user_name, csrf_token):
        # 결제 요청
        with self.client.post("/create-payment/", json={
            "userName": user_name,
            "agree": True,
            "csrfmiddlewaretoken": csrf_token
        }, headers={"X-CSRFToken": csrf_token, "Content-Type": "application/json"}, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    if json_response.get('success'):
                        print("Payment successful")
                        self.view_reservation_log()
                    else:
                        print(f"Payment failed: {json_response.get('error')}")
                        response.failure("Payment failed")
                except ValueError:
                    print("Payment response is not JSON")
                    response.failure("Payment response is not JSON")
            else:
                print(f"Payment request failed: HTTP {response.status_code}")
                response.failure("Payment request failed")

    def view_reservation_log(self):
        with self.client.get("/reservationlog", catch_response=True) as response:
            if response.status_code == 200:
                print("Reservation log page viewed successfully")
            else:
                print(f"Failed to view reservation log page: {response.status_code}")
                response.failure("Failed to load reservation log page")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global login_index
    login_index = 0
    logged_in_users.clear()

    # 15명의 사용자를 30초 간격으로 스폰
    if isinstance(environment.runner, MasterRunner):
        for i in range(0, len(user_accounts), 15):
            for j in range(15):
                if i + j < len(user_accounts):
                    environment.runner.spawn_user(WebsiteUser)
            time.sleep(30)

if __name__ == "__main__":
    import os
    import sys
    from locust.main import main

    sys.argv = [
        "locust",
        "-f", __file__,
        "--headless",
        "--host=https://tickettopia.co"
    ]
    main()
