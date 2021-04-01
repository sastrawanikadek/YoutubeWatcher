from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException

channel_url = "https://www.youtube.com/c/NotSoKoplo/videos"
current_video_url = ""

options = ChromeOptions()
options.headless = True

driver = Chrome(executable_path="./drivers/chromedriver.exe", options=options)
driver.get(channel_url)

while True:
    videos = driver.execute_script("return [...document.querySelectorAll('ytd-grid-video-renderer ytd-thumbnail a')]"
                                   ".map(e => e.href)")

    while len(videos) == 0:
        videos = driver.execute_script("return "
                                       "[...document.querySelectorAll('ytd-grid-video-renderer ytd-thumbnail a')]"
                                       ".map(e => e.href)")

    try:
        video_index = videos.index(current_video_url)
        next_video_index = 0 if video_index == len(videos) - 1 else video_index + 1
    except ValueError:
        next_video_index = 0

    current_video_url = videos[next_video_index]
    driver.get(current_video_url)

    while True:
        try:
            if driver.execute_script('return document.readyState') == "complete":
                is_unstarted = driver.execute_script("return Boolean(document.querySelector('.unstarted-mode'))")
                is_paused = driver.execute_script("return Boolean(document.querySelector('.paused-mode'))")
                is_ads = driver.execute_script("return Boolean(document.querySelector('.ytp-ad-image'))")
                current_time = driver.execute_script("return document.querySelector('.ytp-time-current').innerHTML")
                duration = driver.execute_script("return document.querySelector('.ytp-time-duration').innerHTML")

                if is_unstarted or is_paused:
                    driver.find_element_by_css_selector(".ytp-play-button").click()

                if current_time == duration:
                    if not is_ads:
                        break

                driver.find_element_by_css_selector(".ytp-settings-button").click()
        except (ElementNotInteractableException, ElementClickInterceptedException):
            pass

    driver.get(channel_url)
