from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
from deep_translator import GoogleTranslator
import time
import firebase_admin
from firebase_admin import credentials, firestore

# 初始化 Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("/Users/yue/Desktop/AIstock/stockgpt-150d0-firebase-adminsdk-fbsvc-9ea0d3c5ec.json")  # 替換成你的 Firebase 金鑰檔案路徑
    firebase_admin.initialize_app(cred)
    print("Firebase 初始化成功")
else:
    print("Firebase 已初始化")

# 獲取 Firestore 客戶端
db = firestore.client()

# 初始化翻譯器
translator = GoogleTranslator(source="zh-TW", target="en")

# 加載分詞器和模型
tokenizer = BertTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = BertForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
sentiment_analyzer = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# 初始化 Selenium WebDriver
options = Options()
options.chrome_executable_path = "/Users/yue/Downloads/chromedriver-mac-arm64/chromedriver"
driver = webdriver.Chrome(options=options)

for i in range(1, 3):
    url = f"https://money.udn.com/search/result/1001/%E5%8F%B0%E7%A9%8D%E9%9B%BB/{i}"
    driver.get(url)
    time.sleep(3)

    # 滾動視窗直到底部，確保載入所有新聞
    scroll_pause_time = 2
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # 等待標題與時間載入
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "story__headline")))
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "time")))

    # 抓取標題 & 時間
    titles = driver.find_elements(By.CLASS_NAME, "story__headline")
    dates = driver.find_elements(By.TAG_NAME, "time")
    print(f"找到 {len(titles)} 則新聞標題和 {len(dates)} 個日期")


    # 確保數量一致
    for title, date in zip(titles, dates):
        news_date = date.text.replace("/", "-")  # 格式化日期
        news_title = title.text.strip()

        # 翻譯新聞標題
        translated_title = translator.translate(news_title)

        # 進行情緒分析
        sentiment_result = sentiment_analyzer(translated_title)
        sentiment = sentiment_result[0]["label"]

        # 將資料寫入 Firestore
        news_data = {
            "title": news_title,
            "translated_title": translated_title,
            "date": news_date,
            "sentiment": sentiment
        }

        # 使用日期作為文檔 ID，避免重複
        doc_ref = db.collection("news").document(news_date)
        doc_ref.set(news_data)
        print(f"✅ 已存入 Firebase: {news_date} - {news_title} ({sentiment})")

    print("=============================")

driver.quit()