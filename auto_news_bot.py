import feedparser
import requests
import json
import urllib.parse
from google import genai

# --- CẤU HÌNH ---
PAGE_ACCESS_TOKEN = "EAAXdtQv3Cw8BSv5NxG4eDxIuZBdYwJqQY2f9vJWX9lZCLFQGX0DG9euL3qodhM6Tddsay4O8bZBYvmPBFGeWEbgc77cAEjj4ZBPjqI7X38ZCgn4wGVp4NWkd9cSpgrnZCxS4eRNixubwrXne9Nnj8QZAYSZAZBZAfklVSg9OeSBXhcImJxdXeDzoyEOhQTABbf5v8RF2AYiaZCAED7Bp9Cj2s3By9xbnGfcTsOKkSgHsFfHBkD7BmvKOahKHupzDDNNpbaZCTZCGMra51FTDAp96oNjti"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Thay bằng API key của bạn

# 1. QUÉT TIN TỨC TỪ GOOGLE NEWS
def fetch_top_google_news(topic="Bóng đá"):
    print(f"📡 Đang quét tin mới từ Google News chủ đề: '{topic}'...")
    encoded_topic = urllib.parse.quote(topic)
    rss_url = f"https://news.google.com/rss/search?q={encoded_topic}&hl=vi&gl=VN&ceid=VN:vi"
    
    feed = feedparser.parse(rss_url)
    if not feed.entries:
        print("❌ Không tìm thấy bài viết nào.")
        return None
    
    # Lấy bài viết mới nhất
    latest_news = feed.entries[0]
    print(f"👉 Chọn tin: {latest_news.title}")
    return {
        "title": latest_news.title,
        "link": latest_news.link,
        "published": latest_news.get("published", "")
    }

# 2. XỬ LÝ VIẾT BÀI BẰNG AI
def generate_post_content(news_item):
    print("🤖 Bắt đầu kết nối AI để tạo nội dung...")
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"""
        Bạn là một biên tập viên Fanpage chuyên nghiệp. Hãy viết lại một bài đăng Facebook hấp dẫn, cuốn hút, chuẩn SEO Fanpage dựa trên tin tức sau:
        - Tiêu đề tin gốc: {news_item['title']}
        - Link nguồn tham khảo: {news_item['link']}

        Yêu cầu:
        1. Tiêu đề giật gân, cuốn hút kèm icon phù hợp.
        2. Tóm tắt nội dung chính ngắn gọn (3-4 đoạn ngắn), dễ đọc trên điện thoại.
        3. Thêm lời kêu gọi hành động (Call to action - thảo luận dưới bình luận).
        4. Thêm 4-6 hashtag liên quan.
        Không thêm bất kỳ lời dẫn nào ngoài nội dung bài viết.
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        print("✅ AI đã hoàn thành bài viết!")
        return response.text
    except Exception as e:
        print(f"❌ Lỗi khi gọi AI: {e}")
        # Fallback nội dung nếu AI lỗi
        return f"🔥 TIN MỚI: {news_item['title']}\n\nXem chi tiết tại: {news_item['link']}\n\n#TinTuc #HotNews"

# 3. ĐĂNG BÀI LÊN FANPAGE
def post_to_fanpage(content, link_url):
    print("🚀 Đang tiến hành đăng bài lên Fanpage...")
    # Lấy Page ID
    info_res = requests.get(
        "https://graph.facebook.com/v20.0/me", 
        params={"access_token": PAGE_ACCESS_TOKEN, "fields": "id,name"}
    )
    if info_res.status_code != 200:
        print(f"❌ Token không hợp lệ hoặc lỗi API: {info_res.text}")
        return False

    page_data = info_res.json()
    page_id = page_data["id"]
    print(f"👉 Đang đăng bài lên: {page_data.get('name')} (ID: {page_id})")

    post_url = f"https://graph.facebook.com/v20.0/{page_id}/feed"
    payload = {
        "message": content,
        "link": link_url,
        "access_token": PAGE_ACCESS_TOKEN
    }

    res = requests.post(post_url, data=payload)
    result = res.json()

    if res.status_code == 200 and "id" in result:
        print(f"🎉 Đã đăng thành công lên Fanpage! Post ID: {result['id']}")
        return True
    else:
        print(f"❌ Lỗi phản hồi từ Facebook: {json.dumps(result, ensure_ascii=False)}")
        return False

# --- CHẠY TOÀN BỘ QUY TRÌNH ---
def run_pipeline():
    print("🔔 Bắt đầu quá trình thực thi")
    news = fetch_top_google_news("Ngoại hạng Anh")
    if not news:
        return
    
    post_text = generate_post_content(news)
    post_to_fanpage(content=post_text, link_url=news["link"])
    print("🏁 Hoàn tất quá trình thực thi")

if __name__ == "__main__":
    run_pipeline()
