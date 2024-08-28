import os
from datetime import date


class Token:
    def __init__(self) -> None:
        self.__token = None
        self.__script_dir = os.path.dirname(__file__)
        self.remove_token()

    def save_token(self, token):
        with open(f"{self.__script_dir}/token/{date.today()}.txt", "w") as file:
            file.write(token)

    def get_token(self):
        try:
            with open(f"{self.__script_dir}/token/{date.today()}.txt", "r") as file:
                self.__token = file.read()
            return self.__token;
        except Exception as exe:
            print(f"{date.today()}.txt not found")
            return None;

    def remove_token(self):
        print("---Removing all previous day file----")
        token_folder = f"{self.__script_dir}/token"
        for filename in os.listdir(token_folder):
            if filename != f"{date.today()}.txt" and os.path.isfile(os.path.join(token_folder, filename)):
                os.remove(os.path.join(token_folder, filename))
