from abc import ABC, abstractmethod
import inspect
import random
import string
import time
import yaml
import os

from pywebwizard import SeleniumManager
# from .email_manager import get_link_from_email, delete_emails
from exceptions import SpellDoesNotExist, PlatformDoesNotExist, SpellOutsideSpellBook, SpellFileDoesNotExist, \
    ConfigFormatError


class Spell:

    def __init__(self, filename: str):
        self.filename = filename
        self.name = self.filename.split('.yaml')[0]
        self.spellbook = None

    def __is_valid_platform__(self):
        if not os.path.isfile(self.get_path()):
            raise SpellFileDoesNotExist(f"Error spell {self.get_path()} file does not exist.")
        with open(self.get_path(), 'r') as config:
            try:
                _data = yaml.safe_load(config)
                self.name = _data.get('spell', {}).get('name', None) or self.name
                return self.spellbook.platform in _data.get('spell', {}).get('platforms', [])
            except Exception as e:
                raise ConfigFormatError(f"Error loading config from file {self.get_path()}: {str(e)}")

    def set_spellbook(self, spellbook):
        self.spellbook = spellbook
        self.__is_valid_platform__()

    def get_path(self):
        if not self.spellbook:
            raise SpellOutsideSpellBook(f"Can't get path for {self.filename} as spell has no SpellBook associated.")
        return os.path.join(self.spellbook.path, self.filename)

    def __repr__(self):
        return self.name

class SpellBook:

    def __init__(self, platform, spellbook_path: str = None):
        self.spells = list()
        self.platform = platform
        self.path = spellbook_path or os.path.join('spellbooks', self.platform)
        self.__load_spells__()

    def __load_spells__(self):
        for _spell in os.listdir(self.path):
            if _spell.endswith('.yaml'):
                _new_spell = Spell(_spell)
                self.add_spell(_new_spell)

    def add_spell(self, spell: Spell):
        if spell not in self.spells:
            self.spells.append(spell)
            spell.set_spellbook(self)

    def get_spell(self, spell_name: str) -> Spell:
        for spell in self.spells:
            if spell.name == spell_name:
                return spell
        raise SpellDoesNotExist(f"Spell {spell_name} does not exist in {self.platform} SpellBook.({self.spells})")


class Platforms:

    HISPALOTO = "hispaloto"
    TELEGRAM = "telegram"

    @classmethod
    def enumerate(cls):
        return [getattr(cls, attr) for attr in dir(cls) if not attr.startswith('__') and not callable(getattr(cls, attr))]


class Wizard(ABC):

    def __init__(self, platform, spellbook_path: str = None, *args, **kwargs):
        if platform not in Platforms.enumerate():
            raise PlatformDoesNotExist(f"Plataform '{platform}' is not valid.")
        self.platform = platform
        self.functions = dict()
        self.accounts = list()
        self.manager = None
        self.spellbook = SpellBook(self.platform, spellbook_path)
        self.args = args
        self.kwargs = kwargs

    def __invoke__(self, spell: str, environment: dict = None):
        _spell = self.spellbook.get_spell(spell)
        if not self.manager:
            self.functions = {
                func_name: func
                for func_name, func in inspect.getmembers(self, predicate=inspect.isfunction)
            }
            self.manager = SeleniumManager(_spell.get_path(), external_functions_mapping=self.functions)
            if environment:
                self.manager.environment |= environment
            return
        self.manager.actions, self.manager.config, self.manager.environment = self.manager.load_config(_spell.get_path())
        if environment:
            self.manager.environment |= environment
    def run(self, spell: str, environment: dict = None, **kwargs):
        self.__invoke__(spell, environment)
        self.manager.actions[0]["times"] = kwargs.get("times", 1)
        for action in self.manager.run_actions():
            print(f"[SPELL] Action: {action}")


# class HispalotoWizard(Wizard):
#
#     def __init__(self, email: str, password: str, spellbook_path: str = None, **kwargs):
#         super().__init__(Platforms.MEGAUPLOAD, spellbook_path, **kwargs)
#         if not email or not password:
#             raise ValueError("Email and password are mandatory")
#         self.email = email
#         self.password = password
#         # TODO Remove if works __invoke__ logic
#         # self.functions = {
#         #     "wait_for_link": self.wait_for_link,
#         #     "create_account": self.create_account,
#         #     "save_account": self.save_account
#         # }
#
#     def wait_for_link(self, delete_account_email=True, max_tries=10, target_email=None):
#         verification_link = None
#         counter = 0
#         while not verification_link and counter < max_tries:
#             print(f"({counter}/{max_tries}) Esperando el email con el link de verificación")
#             time.sleep(1)
#             counter += 1
#             verification_link = get_link_from_email(self.email, self.password, delete=delete_account_email)
#         delete_emails(self.email, self.password, target_email)
#         print(f"Link de verificación recibido:\n{verification_link}")
#         return verification_link
#
#     def create_account(self, length: int = 12):
#         symbols = ''.join(["+" * random.randint(4, 6), "-" * random.randint(3, 4), "_" * random.randint(3, 4)])
#         chars = ''.join([string.ascii_letters, string.digits])
#         name = ''.join([random.choice(chars) for _ in range(length - len(symbols))])
#         data = list(chars + name + symbols)
#         random.shuffle(data)
#         final_name = ''.join(data)
#         new_email = self.email.split("@")
#         email = f"{new_email[0]}+{final_name}@{new_email[1]}"
#         self.accounts.append(email)
#         return email
#
#     def save_account(self):
#         email = self.accounts[-1]
#         with open('accounts_created.txt', 'a+') as f:
#             f.write(email + "\n")
#         print(f"Account saved {email} (Total emails: {len(self.accounts)}): {self.accounts}")
#

# class TelegramWizard(Wizard):
#
#     def __init__(self, chat_id: str, token: str, spellbook_path: str = None, **kwargs):
#         super().__init__(Platforms.TELEGRAM, spellbook_path, **kwargs)
#         if not chat_id or not token:
#             raise ValueError("Chat ID and token are mandatory")
#         self.chat_id = chat_id
#         self.token = token
#         self.functions = {}
#         self.platform = "telegram"


if __name__ == '__main__':
    hispaloto_dni = "asdsa"
    hispaloto_password = "sadsadsad"
    spellbook = r"C:\Users\acer\Nextcloud\020_Informatica\00_Python\lotterymaster\spellbooks\hispaloto"
    mega = MegaWizard(hispaloto_dni, hispaloto_password, spellbook)
    for spell in mega.spellbook.spells:
        print(spell.name, spell.get_path())
    mega.run("create_account")
