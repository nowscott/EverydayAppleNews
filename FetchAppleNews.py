import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 设置存储数据的文件路径
archive_dir = 'archive'
if not os.path.exists(archive_dir):
    os.makedirs(archive_dir)

# 配置Selenium
options = Options()
# options.add_argument('--headless')  # 设置为无头模式
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scroll_down(driver, scroll_time):
    """滚动页面指定的时间"""
    start_time = time.time()
    while time.time() - start_time < scroll_time:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 等待页面加载

def extract_date_from_url(url):
    """从URL中提取日期"""
    try:
        parts = url.split('/')
        date_str = f"{parts[3]}-{parts[4]}-{parts[5]}"
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
    except Exception as e:
        print(f"从URL解析日期时出错: {e}")
        return 'Unknown'

def fetch_news(scroll_time=10):
    url = 'https://9to5mac.com/'
    driver.get(url)
    
    news_data = []
    scroll_down(driver, scroll_time)

    # 获取所有新闻部分的文章
    sections = driver.find_elements(By.CLASS_NAME, 'river__posts')
    for section in sections:
        articles = section.find_elements(By.CLASS_NAME, 'article')
        for article in articles:
            try:
                title_tag = article.find_element(By.CLASS_NAME, 'article__title-link')
                title = title_tag.text
                link = title_tag.get_attribute('href')
                
                date = extract_date_from_url(link)
                
                tags = []
                tags_list = article.find_elements(By.CLASS_NAME, 'meta__guide')
                for tag in tags_list:
                    tags.append(tag.text)
            
                news_data.append({
                    'title': title,
                    'link': link,
                    'date': date,
                    'tags': tags
                })
            except Exception as e:
                print(f"处理文章时出错: {e}")

    return news_data

def save_news(news_data):
    grouped_news = {}
    
    # 按日期分组新闻
    for news in news_data:
        date = news['date']
        if date not in grouped_news:
            grouped_news[date] = []
        grouped_news[date].append(news)
    
    # 保存到不同的文件
    for date, articles in grouped_news.items():
        archive_file = os.path.join(archive_dir, f'{date}.json')
        
        if os.path.exists(archive_file):
            with open(archive_file, 'r') as file:
                existing_data = json.load(file)
        else:
            existing_data = []

        # 去重
        new_data = [news for news in articles if news not in existing_data]
        if new_data:
            existing_data.extend(new_data)
        
        with open(archive_file, 'w') as file:
            json.dump(existing_data, file, indent=4)

if __name__ == "__main__":
    start_time = time.time()
    print("开始爬取新闻...")
    
    news_data = fetch_news(scroll_time=10)  # 滚动10秒
    if news_data:
        save_news(news_data)
        print(f"共抓取并保存了 {len(news_data)} 篇文章。")
    else:
        print("没有抓取到任何新闻数据。")
    
    driver.quit()
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"脚本执行时间为 {duration:.2f} 秒。")