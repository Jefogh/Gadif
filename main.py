import base64
import cv2
import numpy as np
import httpx
import random
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView

class CaptchaApp(App):
    def build(self):
        self.accounts = {}
        self.background_images = []

        self.main_layout = BoxLayout(orientation='vertical')
        self.scrollview = ScrollView(size_hint=(1, None), size=(800, 600))
        self.inner_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.inner_layout.bind(minimum_height=self.inner_layout.setter('height'))

        self.scrollview.add_widget(self.inner_layout)
        self.main_layout.add_widget(self.scrollview)

        add_account_button = Button(text="Add Account", size_hint_y=None, height=40)
        add_account_button.bind(on_release=self.add_account)
        self.inner_layout.add_widget(add_account_button)

        upload_background_button = Button(text="Upload Backgrounds", size_hint_y=None, height=40)
        upload_background_button.bind(on_release=self.upload_backgrounds)
        self.inner_layout.add_widget(upload_background_button)

        return self.main_layout

    def upload_backgrounds(self, instance):
        filechooser = FileChooserListView(filters=['*.jpg', '*.png', '*.jpeg'], path='./')
        popup = Popup(title='Select Background Images', content=filechooser, size_hint=(0.9, 0.9))
        filechooser.bind(on_submit=self.on_background_selected)
        popup.open()

    def on_background_selected(self, instance, selection, touch):
        if selection:
            self.background_images = [cv2.imread(path) for path in selection]
            popup = Popup(title='Success', content=Label(text=f'{len(self.background_images)} background images uploaded successfully!'), size_hint=(0.8, 0.4))
            popup.open()

    def add_account(self, instance):
        self.username_input = TextInput(hint_text="Enter Username")
        self.password_input = TextInput(hint_text="Enter Password", password=True)
        popup_layout = BoxLayout(orientation='vertical')
        popup_layout.add_widget(self.username_input)
        popup_layout.add_widget(self.password_input)
        submit_button = Button(text="Submit", size_hint_y=None, height=40)
        submit_button.bind(on_release=self.on_account_submit)
        popup_layout.add_widget(submit_button)
        self.account_popup = Popup(title="Add Account", content=popup_layout, size_hint=(0.8, 0.4))
        self.account_popup.open()

    def on_account_submit(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        if username and password:
            user_agent = self.generate_user_agent()
            session = self.create_session(user_agent)
            login_success = self.login(username, password, user_agent, session)
            if login_success:
                self.accounts[username] = {
                    'password': password,
                    'user_agent': user_agent,
                    'session': session,
                    'captcha_id1': None,
                    'captcha_id2': None
                }
                self.create_account_ui(username)
                self.account_popup.dismiss()

    def create_account_ui(self, username):
        account_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        account_label = Label(text=f"Account: {username}")
        account_box.add_widget(account_label)

        captcha_id1_input = TextInput(hint_text="Enter Captcha ID 1", size_hint_x=None, width=150)
        captcha_id2_input = TextInput(hint_text="Enter Captcha ID 2", size_hint_x=None, width=150)

        self.accounts[username]['captcha_id1'] = captcha_id1_input.text
        self.accounts[username]['captcha_id2'] = captcha_id2_input.text

        request_all_button = Button(text="Request All")
        request_all_button.bind(on_release=lambda x: self.request_all_captchas(username))
        account_box.add_widget(captcha_id1_input)
        account_box.add_widget(captcha_id2_input)
        account_box.add_widget(request_all_button)

        self.inner_layout.add_widget(account_box)

    def request_all_captchas(self, username):
        self.request_captcha(username, self.accounts[username]['captcha_id1'])
        self.request_captcha(username, self.accounts[username]['captcha_id2'])

    def create_session(self, user_agent):
        session = httpx.Client(headers=self.generate_headers(user_agent))
        return session

    def login(self, username, password, user_agent, session, retry_count=3):
        login_url = 'https://api.ecsc.gov.sy:8080/secure/auth/login'
        login_data = {
            'username': username,
            'password': password
        }

        for attempt in range(retry_count):
            try:
                response = session.post(login_url, json=login_data)
                if response.status_code == 200:
                    return True
                elif response.status_code in {401, 402, 403}:
                    print(f"Error {response.status_code}. Retrying...")
                else:
                    return False
            except httpx.RequestError as e:
                print(f"Request error: {e}. Retrying...")
                time.sleep(2)
            except httpx.HTTPStatusError as e:
                print(f"HTTP status error: {e}. Retrying...")
                time.sleep(2)
            except Exception as e:
                print(f"Unexpected error: {e}. Retrying...")
                time.sleep(2)

        return False

    def request_captcha(self, username, captcha_id):
        session = self.accounts[username].get('session')

        if not session:
            popup = Popup(title='Error', content=Label(text=f'No session found for user {username}'), size_hint=(0.8, 0.4))
            popup.open()
            return

        captcha_data = self.get_captcha(session, captcha_id)
        if captcha_data:
            self.show_captcha(captcha_data, username, captcha_id)
        else:
            popup = Popup(title='Error', content=Label(text=f'Failed to get captcha.'), size_hint=(0.8, 0.4))
            popup.open()

    def get_captcha(self, session, captcha_id):
        try:
            options_url = f"https://api.ecsc.gov.sy:8080/rs/reserve?id={captcha_id}&captcha=0"
            options_response = session.options(options_url)

            captcha_url = f"https://api.ecsc.gov.sy:8080/files/fs/captcha/{captcha_id}"
            response = session.get(captcha_url)

            if response.status_code == 200:
                response_data = response.json()
                if 'file' in response_data:
                    return response_data['file']
                else:
                    return None
            return None
        except Exception as e:
            print(f"Failed to get captcha: {e}")
            return None

    def show_captcha(self, captcha_data, username, captcha_id):
        try:
            captcha_base64 = captcha_data.split(",")[1] if ',' in captcha_data else captcha_data
            captcha_image_data = base64.b64decode(captcha_base64)

            with open("captcha.jpg", "wb") as f:
                f.write(captcha_image_data)

            captcha_image = cv2.imread("captcha.jpg")
            processed_image = self.process_captcha(captcha_image)

            image = Image(source="captcha.jpg", size_hint_y=None, height=300)
            self.inner_layout.add_widget(image)

            captcha_input = TextInput(hint_text="Enter Captcha", size_hint_y=None, height=40)
            captcha_input.bind(on_text_validate=lambda instance: self.submit_captcha(username, captcha_id, captcha_input.text))
            self.inner_layout.add_widget(captcha_input)

        except Exception as e:
            popup = Popup(title='Error', content=Label(text=f'Error processing captcha data: {e}'), size_hint=(0.8, 0.4))
            popup.open()

    def process_captcha(self, captcha_image):
        if not self.background_images:
            return captcha_image

        best_background = None
        min_diff = float('inf')

        for background in self.background_images:
            if background.shape != captcha_image.shape:
                background = cv2.resize(background, (captcha_image.shape[1], captcha_image.shape[0]))

            diff = cv2.absdiff(captcha_image, background)
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            score = np.sum(gray_diff)

            if score < min_diff:
                min_diff = score
                best_background = background

        if best_background is not None:
            diff = cv2.absdiff(captcha_image, best_background)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)

            kernel = np.ones((3, 3), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

            return cleaned
        else:
            return captcha_image

    def submit_captcha(self, username, captcha_id, captcha_solution):
        session = self.accounts[username].get('session')

        get_url = f"https://api.ecsc.gov.sy:8080/rs/reserve?id={captcha_id}&captcha={captcha_solution}"
        get_response = session.get(get_url)

        if get_response.status_code == 200:
            popup = Popup(title='Success', content=Label(text="Captcha solved successfully!"), size_hint=(0.8, 0.4))
            popup.open()
        else:
            popup = Popup(title='Error', content=Label(text=f'Failed to solve captcha.'), size_hint=(0.8, 0.4))
            popup.open()

    def generate_headers(self, user_agent):
        headers = {
            'User-Agent': user_agent,
            'Content-Type': 'application/json',
            'Source': 'WEB',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://ecsc.gov.sy/',
            'Origin': 'https://ecsc.gov.sy',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }
        return headers

    def generate_user_agent(self):
        user_agent_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
        ]
        return random.choice(user_agent_list)

if __name__ == "__main__":
    CaptchaApp().run()
