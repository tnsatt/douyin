# douyin
Download Douyin video or get details from video link

# Requirement:
pip install requests

# How to use:

import douyin

url = "https://www.douyin.com/video/7096447262678650148?previous_page=recommend&tab_name=recommend"

data = douyin.get_data(url)

#or

download_link = douyin.get_link(url)
