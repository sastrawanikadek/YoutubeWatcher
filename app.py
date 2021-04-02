from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException
import os
import time

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

    prev_time = ""
    prev_time_retry = 0
    prev_time_max_retry = 5

    while True:
        time.sleep(1)
        try:
            if driver.execute_script("return Boolean(document.querySelector('video'))"):
                is_ads = driver.execute_script("return Boolean(document.querySelector('.ytp-ad-image'))")
                current_time = driver.execute_script("return document.querySelector('.ytp-time-current').innerHTML")
                duration = driver.execute_script("return document.querySelector('.ytp-time-duration').innerHTML")

                if current_time == prev_time:
                    if prev_time_retry == prev_time_max_retry:
                        driver.find_element_by_css_selector(".ytp-play-button").click()
                        prev_time_retry = 0
                    else:
                        prev_time_retry += 1

                if driver.execute_script("return document.querySelector('.ytp-settings-menu').style.display") == "none":
                    driver.find_element_by_css_selector(".ytp-settings-button").click()

                print(f"Time -> {current_time}/{duration}")

                if current_time == duration:
                    if not is_ads:
                        break

                if driver.execute_script("return window.location.href") != current_video_url:
                    break

                prev_time = current_time
        except (ElementNotInteractableException, ElementClickInterceptedException) as e:
            print(f"Exception ${e}")
            pass

    driver.get(channel_url)
