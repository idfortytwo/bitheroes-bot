import time, cv2, selenium, pyautogui, traceback, zope, queue
import numpy as np

from threading import Thread, Lock
from PIL import Image
from io import BytesIO

import tools


class Pipeline(queue.Queue):
    def __init__(self):
        super().__init__(maxsize=1)

    def set_frame(self, frame):
        self.put(frame)

    def get_frame(self):
        frame = self.get()
        return frame


class Bot(Thread):
    def __init__(self, driver):
        Thread.__init__(self)
        self.driver = driver
        self.game_window_location = None
        self.pipeline = Pipeline()


    def run(self):
        print('running bot')
        self.open_cinematic()

        while True:
            try:
                self.game_window_location = self.get_game_window_location()
                # print('game window location acquired')
                break
            except Exception:
                traceback.print_exc()
                time.sleep(1)
                continue

        scenario_manager = ScenarioManager(self.game_window_location, self.driver, self.pipeline)
        scenario_manager.start()

        while True:
            current_frame = self.get_current_frame()
            self.pipeline.set_frame(current_frame)
            # print('frame put into queue')
            time.sleep(0.3)


    def get_game_window_location(self):
        game_window = self.driver.find_element_by_xpath('//*[@id="gameiframe"]')
        game_window_location = {
            'x': game_window.location.get('x') + 30,
            'y': game_window.location.get('y') + 145
        }
        return game_window_location


    def get_current_frame(self):
        region = (self.game_window_location.get('x'), self.game_window_location.get('y'), 800, 520)
        frame = pyautogui.screenshot('current_frame.png', region)
        frame_to_np_array = np.array(frame)
        frame_to_np_array = cv2.cvtColor(frame_to_np_array, cv2.COLOR_RGB2BGR)
        return frame_to_np_array


    def open_cinematic(self):
        time.sleep(0.5)
        open_cinematic_button = self.driver.find_elements_by_xpath('//*[@id="cinematic_mode_link"]')
        for o in open_cinematic_button:
            o.click()


class ScenarioManager(Thread):
    def __init__(self, game_window_location, driver, pipeline):
        Thread.__init__(self)
        self.game_window_location = game_window_location
        self.driver = driver
        self.pipeline = pipeline
        self.lock = Lock()
        self.location = None
        self.MIN_GREEN_COEF = 13.5


    def run(self):
        while True:
            input('Press any key to start')
            break

        while True:
            current_frame = self.pipeline.get_frame()
            if not self.lock.locked():
                # energy_coef = self.get_energy_coef(current_frame)
                # if energy_coef is None:
                #     # print('energy_coef is NONE')
                #     pass
                # else:
                #     if energy_coef > self.MIN_GREEN_COEF:
                #         print('enough energy')
                #         # go_do_quests()
                #         break
                #     else:
                #         print('not enough energy')
                #         continue
                #
                # print('afterrrrrr enddddddddd')

                # base_scenario = BaseScenario(self.game_window_location, self.driver, self.pipeline, self.lock)
                # base_scenario.start()

                battle_scenario = BattleScenario(self.game_window_location, self.driver, self.pipeline, self.lock)
                battle_scenario.start()

                time.sleep(1)

            # else:
            #     # print('locked')
            #     # time.sleep(1)
            #     pass


    def get_energy_coef(self, frame):
        green_pixel = np.array([44, 197, 136])
        dark_green_pixel = np.array([21, 133, 87])
        black_pixel = np.array([51, 50, 49])
        black, green = 0, 0

        energy_bar = frame[12:40, 439:518]
        for pixel in energy_bar[0]:
            if np.all(pixel == green_pixel) or np.all(pixel == dark_green_pixel):
                green += 1
            elif np.all(pixel == black_pixel):
                black += 1

        try:
            green_coef = green / (green + black) * 100
            return green_coef
        except ZeroDivisionError:
            # cv2.imshow(None, energy_bar)
            # cv2.waitKey(0)
            return None



    def open_raid(self, frame):
        self.click_game(37, 328)

    def purple_pixel_in_shard_bar(self, frame):
        shard_bar = frame[53:80, 356:444]
        shard_pixel = np.array([130, 49, 162])
        if np.any(shard_bar == purple_pixel):
            return True
        else:
            return False


    def click_game(self, x, y, **kwargs):
        x = x + self.game_window_location.get('x')
        y = y + self.game_window_location.get('y')
        clicks = kwargs.get('clicks', 1)
        pyautogui.click(x, y, clicks=clicks)
        time.sleep(0.5)


class BaseScenario(Thread):
    def __init__(self, game_window_location, driver, pipeline, lock):
        Thread.__init__(self)
        self.game_window_location = game_window_location
        self.driver = driver
        self.pipeline = pipeline
        self.lock = lock
        self.dialogue_lock = Lock()
        self.current_frame = None
        print('base scenario initialized')

        queue_listener_thread = Thread(target=self.update_current_frame)
        queue_listener_thread.start()

        default_filter_thread = Thread(target=self.filter)
        default_filter_thread.start()

    def run(self):
        self.lock.acquire()
        while True:
            if self.current_frame is not None:
                self.main()
                self.lock.release()
                break
            else:
                time.sleep(0.5)


    def main(self):
        print('default main()')
        while True:
            # time.sleep(5)
            # print('main finished')
            # break
            pass

    def update_current_frame(self):
        while True:
            self.current_frame = self.pipeline.get_frame()


    def filter(self):
        while True:
            if self.current_frame is not None:
                self.detect_disconnected()
                self.detect_dialogue()
                time.sleep(1)


    def detect_disconnected(self):
        if tools.template_is_on_screen(self.current_frame, 'reconnect.png'):
            self.click_game(400, 360)
            print('disconnect detected')


    def detect_dialogue(self):
        corner_pixel = np.array([99, 91, 83])
        if (np.any(self.current_frame[207, 478] == corner_pixel) and \
         np.any(self.current_frame[207, 683] == corner_pixel) and \
         np.any(self.current_frame[247, 478] == corner_pixel) and \
         np.any(self.current_frame[247, 683] == corner_pixel)) \
         or (np.any(self.current_frame[207, 116] == corner_pixel) and \
         np.any(self.current_frame[207, 322] == corner_pixel) and \
         np.any(self.current_frame[247, 116] == corner_pixel) and \
         np.any(self.current_frame[247, 322] == corner_pixel)):
            self.click_game(400, 300)
            print('dialogue detected')



    def click_game(self, x, y, **kwargs):
        x = x + self.game_window_location.get('x')
        y = y + self.game_window_location.get('y')
        clicks = kwargs.get('clicks', 1)
        pyautogui.click(x, y, clicks=clicks)
        time.sleep(1)


class SetupScenario(BaseScenario):
    def __init_(self):
        print('beginning to initialize setup scenario')
        super().__init__(self)


    def main(self):
        self.lock.acquire()

        self.detect_loading_into_main_menu()
        time.sleep(0.5)

        print('setting up')
        self.collect_rewards()
        time.sleep(0.5)

        self.wait_for_news_window()
        time.sleep(0.5)

        self.dialogue_lock.acquire()
        self.close_lock.acquire()
        self.set_options()
        print('set up done')
        self.dialogue_lock.release()
        self.close_lock.acquire()

        self.lock.release()


    def collect_rewards(self):
        print('collectiong rewards')
        seconds_passed = 0
        while True:
            if tools.template_is_on_screen(source=self.current_frame, template_filename='rewards.png'):
                time.sleep(0.2)
                self.click_game(400, 455)

                while True:
                    if tools.template_is_on_screen(self.current_frame, 'items.png'):
                        self.click_game(588, 148)
                        break

                break

            else:
                print('no rewards window found')
                close_button_location = tools.get_template_center_point(self.current_frame, 'x.png')
                if close_button_location is not None:
                    print('close button found')
                    if tools.template_is_on_screen(self.current_frame, 'news.png'):
                        print('''...but it's news''')
                    else:
                        self.click_game(close_button_location[0], close_button_location[1])
                        seconds_passed = 0
                        print('close button clicked')
                else:
                    print('no close button found')

            time.sleep(1)
            seconds_passed += 1
            print(f'seconds passed: {seconds_passed}')
            if seconds_passed == 2:
                print('exiting claim_rewards()')
                break


    def wait_for_news_window(self):
        print('waiting for news')
        while True:
            if tools.template_is_on_screen(source=self.current_frame, template_filename='news.png'):
                time.sleep(0.2)
                self.click_game(460, 460)
                print('exiting wait_for_news_window()')
                break

            time.sleep(1)


    def set_options(self):
        print('setting options')
        self.click_game(690, 480) #open options

        time.sleep(1.5)

        self.click_game(360, 200) #disable music
        self.click_game(360, 265) #disable sound

        self.click_game(620, 400, clicks=8) #scroll down
        self.click_game(190, 190) #disable notifications
        self.click_game(190, 360) #disable friend requests
        self.click_game(190, 400) #disable duel requests

        self.click_game(620, 400, clicks=5) #scroll down
        self.click_game(190, 230) #disable world boss requests

        self.click_game(620, 400, clicks=15) #scroll down
        self.click_game(190, 173) #decline duplicate familiars
        self.click_game(210, 250) #deselect rare
        self.click_game(210, 290) #deselect epic
        self.click_game(210, 336) #deselect legendary
        self.click_game(210, 380) #deselect mythic

        self.click_game(620, 400) #scroll_down
        self.click_game(190, 375) #decline merchants

        self.click_game(660, 80) #exit


class BattleScenario(BaseScenario):
    def __init__(self, game_window_location, driver, pipeline, lock):
        super().__init__(game_window_location, driver, pipeline, lock)
        print('battle scenario initialized')


    # def main(self):
    #     print('default main()')
    #     while True:
    #         # time.sleep(5)
    #         # print('main finished')
    #         # break
    #         pass

    def filter(self):
        while True:
            if self.current_frame is not None:
                self.detect_disconnected()
                self.detect_dialogue()
                self.detect_cleared()
                time.sleep(1)


    def detect_cleared(self):
        if np.any(self.current_frame[118, 260] == np.array([114, 173, 152])) and \
         np.any(self.current_frame[118, 535] == np.array([42, 162, 98])) and \
         np.any(self.current_frame[354, 238] == np.array([51, 51, 88])):
            self.click_game(326, 362)
            print('cleared')


class MainMenuScenario(BaseScenario):
    def __init__(self):
        super().__init__()
        print('main menu scenario initialized')


class CampaignScenario(BaseScenario):
    def __init__(self):
        super().__init__()
        print('campaign scenario initialized')
