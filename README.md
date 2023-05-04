# Mememaker 

This Python program automatically downloads short videos from specified subreddits, merges them into a single video, and uploads it to the user's YouTube account. 

## Main Features

- Downloads videos from Reddit using the PRAW library
- Merges video clips and adds titles and descriptions
- Uploads the final output to YouTube using Selenium

## Dependencies

- praw
- random
- undetected_chromedriver
- time
- logging
- json
- re
- moviepy.editor

## Installation

1. Install Python 3.x if you haven't already.
2. Install the required libraries with:
   ```
   pip install praw random undetected_chromedriver moviepy.editor
   ```
3. Clone or download the repository and fill in the `secrets.json` file with your API keys and login information for Reddit, Google, and Telegram.

## Usage

1. Run the script:

   ```python
   python MemeMaker.py
   ```

2. The script will download the videos from the specified subreddits and create a merged video in the "videos" directory.
3. After the merged video is created, the script will upload the video to your YouTube account.
4. Progress messages will be sent to your specified Telegram account. 

## Example

If there are three subreddits listed in the `secrets.json` file (e.g., 'funny', 'memes', and 'dankmemes'), the script will download videos from all three, merge them with titles, and upload them to your YouTube account. Progress information will be sent to your Telegram account, as specified in your `secrets.json` file.

## Notes

- Make sure to enter your Google ID and password, Reddit API keys, and Telegram token and chat_id in the `secrets.json` file.
- This script uses the Reddit and YouTube APIs; make sure to adhere to their terms of use and API limitations.
- The uploading process uses Selenium and ChromeDriver. Make sure to install an appropriate version of ChromeDriver and add it to your PATH.
- You might need to adjust the `time.sleep()` values in the script based on your internet speed and system performance to prevent errors due to slow page loading.
a fully automated video creating and uploading python program.

https://www.youtube.com/@cookiememes
