from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException
import os

channel_url = "https://www.youtube.com/c/NotSoKoplo/videos"
current_video_url = ""

options = ChromeOptions()
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.headless = True

driver = Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)
driver.get(channel_url)

while True:
    videos_href = driver.execute_script("return "
                                        "[...document.querySelectorAll('ytd-grid-video-renderer ytd-thumbnail a')]"
                                        ".map(e => e.href)")
    videos = driver.find_elements_by_css_selector('ytd-grid-video-renderer ytd-thumbnail a')

    while len(videos_href) == 0:
        videos_href = driver.execute_script("return "
                                            "[...document.querySelectorAll('ytd-grid-video-renderer ytd-thumbnail a')]"
                                            ".map(e => e.href)")
        videos = driver.find_elements_by_css_selector('ytd-grid-video-renderer ytd-thumbnail a')

    try:
        video_index = videos_href.index(current_video_url)
        next_video_index = 0 if video_index == len(videos_href) - 1 else video_index + 1
    except ValueError:
        next_video_index = 0

    current_video_url = videos_href[next_video_index]
    videos[next_video_index].click()
    print(f"Currently Playing: {current_video_url}")

    first_time = True

    while True:
        try:
            if driver.execute_script("return Boolean(document.querySelector('.ytp-time-current'))"):
                is_unstarted = driver.execute_script("return Boolean(document.querySelector('.unstarted-mode'))")
                is_paused = driver.execute_script("return Boolean(document.querySelector('.paused-mode'))")
                is_ads = driver.execute_script("return Boolean(document.querySelector('.ytp-ad-image'))")
                current_time = driver.execute_script("return document.querySelector('.ytp-time-current').innerHTML")
                duration = driver.execute_script("return document.querySelector('.ytp-time-duration').innerHTML")

                if first_time:
                    if is_unstarted or is_paused:
                        driver.find_element_by_css_selector(".ytp-play-button").click()

                    driver.find_element_by_css_selector(".ytp-settings-button").click()
                    first_time = False

                if current_time == duration:
                    if not is_ads:
                        break

                if driver.execute_script("return window.location.href") != current_video_url:
                    break
        except (ElementNotInteractableException, ElementClickInterceptedException):
            pass

    driver.get(channel_url)
