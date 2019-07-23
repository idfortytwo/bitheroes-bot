from page_manager import PageManager

if __name__ == '__main__':
    pm = PageManager(game_url='https://www.kongregate.com/games/juppiomenz/bit-heroes',
                     path_to_extension='E:\Coding\chromedriver\Adblock-Plus_v1.12.4.crx',
                     executable_path='E:\Coding\chromedriver\chromedriver.exe')

    pm.start_selenium()
    pm.login(email='artem.bugera@gmail.com', password='Qwerty101112')
    pm.start_bot()
