import firebase_admin
from firebase_admin import credentials, firestore

# 初始化 Firebase
cred = credentials.Certificate("/Users/yue/Desktop/AIstock/stockgpt-150d0-firebase-adminsdk-fbsvc-9ea0d3c5ec.json")  # 替換為你的密鑰檔案路徑
firebase_admin.initialize_app(cred)
db = firestore.client()

# 函數：讀取使用者輸入並存入 Firestore
def save_user_input():
    # 讀取使用者輸入
    user_id = input("請輸入使用者 ID（例如 user1）：")
    name = input("請輸入使用者名稱：")
    age = input("請輸入使用者年齡：")
    email = input("請輸入使用者電子郵件：")

    # 確認輸入是否完整
    if not (user_id and name and age and email):
        print("輸入不完整，請重新執行程式！")
        return

    # 儲存到 Firestore
    doc_ref = db.collection("users").document(user_id)
    doc_ref.set({
        "name": name,
        "age": int(age),  # 將年齡轉換為整數
        "email": email
    })

    print(f"使用者 {name} 的資料已成功存入 Firestore！")

# 主程式
if __name__ == "__main__":
    save_user_input()
