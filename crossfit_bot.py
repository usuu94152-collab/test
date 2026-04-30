import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# ================================
# 설정 (본인 정보로 교체하세요)
# ================================
TOKEN = "8675538197:AAE-lmEK5jHhXDI3kqDAE0KFIsfo-u0-lrc"   # BotFather에서 재발급받은 토큰
CHAT_ID = "1793267160"
URL = "https://www.crossfit.com/essentials"
SEEN_FILE = "seen_posts.json"      # 이전에 본 글 목록 저장 파일

# ================================
# 이전에 본 글 목록 불러오기
# ================================
def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

# ================================
# 크롤링
# ================================
def get_posts():
    res = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    posts = []

    for a in soup.select("h2 a, h3 a"):
        title = a.get_text(strip=True)
        link = a.get("href", "")
        if not link.startswith("http"):
            link = "https://www.crossfit.com" + link
        if title and "/essentials/" in link:
            posts.append({"title": title, "link": link})

    return posts

# ================================
# 텔레그램 메시지 전송
# ================================
def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
    )

# ================================
# 메인 실행
# ================================
def main():
    seen = load_seen()
    posts = get_posts()
    new_posts = [p for p in posts if p["link"] not in seen]

    if new_posts:
        for post in new_posts:
            msg = (
                f"📢 <b>CrossFit Essentials 새 글!</b>\n\n"
                f"📌 {post['title']}\n"
                f"🔗 {post['link']}"
            )
            send_message(msg)
            seen.add(post["link"])
            print(f"전송 완료: {post['title']}")
        save_seen(seen)
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 새 글 없음")

if __name__ == "__main__":
    main()
