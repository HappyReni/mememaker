import os
import telegram
import datetime
import praw
import random
import undetected_chromedriver as uc
import time
import logging
import json
import re

from RedDownloader import RedDownloader
from moviepy.editor import *
from selenium import webdriver
from selenium.webdriver.common.by import By


def remove_invalid_chars(input_str):
    """
    Removes invalid characters for Windows folder name from input_str.
    """
    invalid_chars = r'[<>:"/\\|?*]'
    if bool(re.search(invalid_chars, input_str)):
        output_str = re.sub(invalid_chars, '', input_str)
        return output_str
    
    return input_str

class MemeMaker:
    def __init__(self) -> None:
        ### import secret data ###
        with open('secrets.json', 'r') as f:
            secrets = json.load(f)

        # reddit api
        self.reddit_para = {
            "client_id" : secrets["reddit"]["client_id"],
            "client_secret" : secrets["reddit"]["client_secret"],
            "user_agent" : secrets["reddit"]["user_agent"]
            }
        self.reddit_url = 'https://www.reddit.com'
        
        # google info
        self.google_id = secrets["google"]["ID"]
        self.google_pw = secrets["google"]["PW"]

        # telegram config
        self.bot = telegram.Bot(token=secrets["telegram"]["token"])
        self.chat_id = secrets["telegram"]["chat_id"]

        # date
        today = datetime.datetime.now()
        self.time_withSeconds = today.strftime('%Y%m%d_%H%M%S')
        self.date = today.strftime("%Y%m%d")

        # video sources
        self.subreddits = secrets["subreddits"]

        # video info
        self.video_file = ""
        self.video_address = ""

        #making videos folder
        self.abs_path = os.path.abspath(__file__)
        dir_path = os.path.dirname(self.abs_path)
        video_dir_path = os.path.join(dir_path, "videos")
        if not os.path.exists(video_dir_path):
            os.makedirs(video_dir_path)

        #init log
        self._init_log()

        self.isFinished = False
    def _init_log(self):
        # 현재 파일이 있는 디렉토리 경로
        dir_path = os.path.dirname(self.abs_path)
        # log 폴더 경로
        log_dir_path = os.path.join(dir_path, "logs")
        # log 폴더가 없으면 생성
        if not os.path.exists(log_dir_path):
            os.makedirs(log_dir_path)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)
        log_file = self.time_withSeconds
        file_handler = logging.FileHandler(f'logs\\{log_file}.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.info("program initiated")
    def __del__(self):
        pass

    def _getVideos(self,
                    download_count = 30,
                    video_duration = 25):
        
        self.bot.sendMessage(chat_id=self.chat_id, text=f"===== {self.date} started making video =====")
        self.logger.info("started getting videos")
        reddit = praw.Reddit(
            client_id= self.reddit_para["client_id"],
            client_secret=self.reddit_para["client_secret"],
            user_agent=self.reddit_para["user_agent"],
        )

        titles = []

        # 오늘 날짜로 폴더 생성
        folder_name = "videos\\" + self.date
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
            self.video_address = folder_name
            self.logger.info(f"Successfully created folder: {folder_name}")
        else:
            self.logger.warning(f"Folder : {folder_name} already exists.")
        ##

        for subreddit in self.subreddits:
            submissions = list(reddit.subreddit(subreddit).hot(limit=download_count))
            self.logger.info(f"* ===== subreddit : {subreddit} ===== *\n")
            for submission in submissions:
                title = submission.title
                selftext= submission.selftext.replace("\n","").replace("\\","").replace("\r","")
                url = self.reddit_url + submission.permalink

                if submission.is_video:
                    duration = submission.media["reddit_video"]["duration"]
                    width = submission.media["reddit_video"]["width"]

                    if duration < video_duration and width > 600:
                        title = remove_invalid_chars(title)
                        self.logger.info(f"title : {title}")
                        self.logger.info(f"url : {url}")
                        self.logger.info(f"duration : {duration}")
                        self.logger.info(f"width : {width}")

                        titles.append(title)
                        try:
                            file = RedDownloader.Download(url = url , output=f"{title}", destination=f"{folder_name}\\",quality = 1080)
                            self.logger.info(f"Downloading . . .")
                        except:
                            self.logger.warning(f"download failed")
                    else:
                        self.logger.warning(f"this video is skipped due to duration or width")
                        continue

        self.bot.sendMessage(chat_id=self.chat_id, text=f"* video download finished : total {len(titles)} videos")
        self.logger.info(f"video download finished")

    def _mergeVideos(self,
                    video_count = 25,
                    video_length = 180,
                    font_size = 45,
                    ):
        self.logger.info("started merging videos")
        self.bot.sendMessage(chat_id=self.chat_id, text=f"== video merge started == \n")

        path = self.video_address
        self.logger.info(f"video path : {path}")
        file_list = os.listdir(path)

        try:
            videos = random.sample(file_list,video_count)
        except:
            videos = random.sample(file_list,video_count-5)

        duration = 0
        texted_clips =[]

        self.logger.info("selected video : ")
        self.bot.sendMessage(chat_id=self.chat_id, text=f"selected video : \n")
        selected_videos = ""
        for i,video in enumerate(videos):
            self.logger.info(" * " + video)
            selected_videos = selected_videos + "* " + video + "\n"
            try:
                clip = VideoFileClip(path+f"\\{video}")
                clip = clip.set_position(("center"))
            except:
                pass

            # text config
            text = TextClip(f"{video[:-4]}",
                        fontsize = font_size, 
                        color = 'white',
                        font="Malgun-Gothic-Bold")
            text = text.set_position(("right","top"))
            tx_width,tx_height = text.size
            color = ColorClip(size=(tx_width,tx_height),color=(50,50,50))
            color = color.set_position(("right","top"))
            color = color.set_opacity(.4)
            ##

            background = ImageClip("background.png")
            clip = CompositeVideoClip([background,clip,text,color]).set_duration(clip.duration)

            texted_clips.append(clip)

            duration = duration + int(texted_clips[i].duration)

            if duration > video_length:
                self.logger.info(f"total videos count : {i}")
                self.logger.info(f"video length : {duration} sec")
                self.bot.sendMessage(chat_id=self.chat_id, text=f" * total merged videos : {i}\n * merged video length : {duration} sec ")
                break

        self.bot.sendMessage(chat_id=self.chat_id, text=f"{selected_videos}")
        combined = concatenate_videoclips(texted_clips,method='compose')
        combined.write_videofile(path+f"\\result_{self.time_withSeconds}.mp4")
        self.logger.info(combined)
        try:
            self.video_file = f"result_{self.time_withSeconds}.mp4"
            self.logger.info(f"merged completed : " + f"result_{self.time_withSeconds}.mp4")
        except Exception as e:
            self.logger.warning(e)

        for clip in texted_clips:
            clip.close()
    def _upload(self):
        VIDEO_FILE = self.video_file
        VIDEO_ADDRESS = r"C:\Workplace\python\memevideo" + "\\" + self.video_address

        VIDEO_TITLE = "Today's Cookie Memes : " + self.date
        VIDEO_DESCRIPTION = "Daily cookie for your soul"
        ID = self.google_id
        PW = self.google_pw

        self.logger.info("started uploading videos")
        options = webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")
        driver = uc.Chrome(options=options)
        driver.set_window_position(0,0)
        driver.set_window_size(1920, 1080)

        driver.get("https://www.youtube.com/upload")
        driver.implicitly_wait(1.0)

        try:
            login_email_region = driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/c-wiz/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div/div[1]/div/div[1]/input")
            login_email_region.click()
            login_email_region.send_keys(ID)
            self.logger.info("email typed")
        except:
            self.logger.warning("failed email typed")

        try:
            next_button = driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/c-wiz/div/div[2]/div/div[2]/div/div[1]/div/div/button")
            next_button.click()
            driver.implicitly_wait(10.0)
            self.logger.info("next button clicked")
        except:
            self.logger.warning("failed next button clicked")

        try:
            login_pw_region = driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/c-wiz/div/div[2]/div/div[1]/div/form/span/section[2]/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input")
            login_pw_region.click()
            login_pw_region.send_keys(PW)
            self.logger.info("pw typed")
        except:
            self.logger.warning("failed pw typed")

        try:
            next_button = driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[2]/div/c-wiz/div/div[2]/div/div[2]/div/div[1]/div/div/button")
            next_button.click()
            driver.implicitly_wait(10.0)
            self.logger.info("next button clicked")
        except:
            self.logger.warning("failed next button clicked")

        time.sleep(2.0)
        try:    
            select_button = driver.find_element(By.XPATH, '//*[@id="content"]/input')
            select_button.send_keys(VIDEO_ADDRESS+"\\"+VIDEO_FILE)
            self.logger.info("select button clicked")
        except:
            self.logger.warning("failed select button clicked")
        
        time.sleep(7.0)

        try:
            title_input = driver.find_element(By.XPATH,"/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[1]/ytcp-social-suggestions-textbox/ytcp-form-input-container/div[1]/div[2]/div/ytcp-social-suggestion-input/div")
            title_input.clear()
            title_input.send_keys(VIDEO_TITLE)
            self.logger.info(f"title input : {VIDEO_FILE}")
        except:
            self.logger.warning("failed input video title")
        
        time.sleep(1.0)

        try:
            desc_input = driver.find_element(By.XPATH,"/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[2]/ytcp-social-suggestions-textbox/ytcp-form-input-container/div[1]/div[2]/div/ytcp-social-suggestion-input/div")
            desc_input.send_keys(VIDEO_DESCRIPTION)
            self.logger.info(f"description input : {VIDEO_DESCRIPTION}")
        except:
            self.logger.warning("failed input video description")
        
        time.sleep(1.0)

        try:
            radio_button = driver.find_element(By.XPATH,"/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[5]/ytkc-made-for-kids-select/div[4]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[2]/div[1]/div[1]")
            radio_button.click()
            self.logger.info(f"radio button clicked")
        except:
            self.logger.warning("failed radio button clicked")
        
        time.sleep(1.0)

        url = ""
        try:
            link = driver.find_element(By.CSS_SELECTOR,"#details > ytcp-video-metadata-editor-sidepanel > ytcp-video-info > div > div.row.style-scope.ytcp-video-info > div.left.style-scope.ytcp-video-info > div.value.style-scope.ytcp-video-info > span > a")
            url = link.get_attribute("href")
            self.logger.info(f"url : {url}")
        except Exception as e:
            self.logger.warning(e)
        
        time.sleep(1.0)

        for i in range(3):
            try:
                next_button = driver.find_element(By.XPATH,"/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[2]")
                next_button.click()
                self.logger.info(f"next button clicked")
            except:
                self.logger.warning("failed next button clicked")

            time.sleep(1.0)

        try:
            radio_button = driver.find_element(By.XPATH,"/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[2]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[3]/div[1]/div[1]")
            radio_button.click()
            self.logger.info(f"radio button clicked")
        except:
            self.logger.warning("failed radio button clicked")
        
        time.sleep(1.0)

        try:
            save_button = driver.find_element(By.XPATH,"/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[3]")
            save_button.click()
            self.logger.info(f"save button clicked")
        except:
            self.logger.warning("failed save button clicked")

        time.sleep(3.0)
        try:
            close_button = driver.find_element(By.XPATH,"/html/body/ytcp-uploads-still-processing-dialog/ytcp-dialog/tp-yt-paper-dialog/div[3]/ytcp-button/div")
            close_button.click()
        except:
            self.logger.warning("failed close button clicked")

        try:
            self.bot.sendMessage(chat_id=self.chat_id, text=f"===== Video upload finished ===== \n * video url : {url}")
        except:
            self.logger.warning("failed to send telegram message")

        print("upload finished.")
        driver.quit()
        self.isFinished = True

    def begin(self):
        ## begin
        start = time.time()
        self._getVideos()
        self._mergeVideos()
        self._upload()
        end = time.time()
        meme.logger.info(f"Execution time: {end - start} seconds")
        ##

meme = MemeMaker()
meme.begin()



