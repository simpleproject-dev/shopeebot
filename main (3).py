import os
import tweepy
import time
from sheets import get_pending_quote, update_status  # Import fungsi dari sheets.py

# Setup API Twitter
consumer_key = os.environ.get('API_KEY')
consumer_secret = os.environ.get('API_SECRET')
access_token = os.environ.get('ACCESS_TOKEN')
access_token_secret = os.environ.get('ACCESS_SECRET')
bearer_token = os.environ.get('BEARER_TOKEN')

# Pastikan semua variabel environment sudah terisi
if not all([consumer_key, consumer_secret, access_token, access_token_secret, bearer_token]):
    raise ValueError("🚨 Pastikan semua environment variables API sudah diatur dengan benar!")

# Inisialisasi Tweepy Client
client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

def post_tweet():
    """
    Mengambil kutipan dari Google Sheets dan mempostingnya ke X (Twitter).
    """
    kutipan_data = get_pending_quote()
    if not kutipan_data:
        return  # Jika tidak ada kutipan pending, hentikan program

    row_number, kutipan, penulis = kutipan_data

    tweet_text = f"📜 \"{kutipan}\" - {penulis}"

    # Pastikan panjang tweet <= 280 karakter
    if len(tweet_text) > 280:
        tweet_text = tweet_text[:277] + "..."

    try:
        response = client.create_tweet(text=tweet_text)
        tweet_id = response.data["id"]
        print(f"✅ Tweet berhasil diposting! ID: {tweet_id}")
        print(f"Tweet Text: {tweet_text}")

        # Update status di Google Sheets setelah berhasil diposting
        update_status(row_number)

    except tweepy.TweepyException as e:
        print(f"🚨 Error saat memposting tweet: {e}")


from threading import Thread
import server  # Impor server Flask

# Menjalankan server di thread terpisah agar tidak mengganggu bot utama
# Gunakan port 3000 untuk menghindari konflik
Thread(target=server.app.run, kwargs={"host": "0.0.0.0", "port": 8080}).start()

# Jalankan fungsi untuk posting tweet
while True:
    try:
        post_tweet()  # Memanggil fungsi untuk posting tweet
        print("⏳ Menunggu 3 jam sebelum tweet berikutnya...")
        time.sleep(21600)  # 10800 detik = 3 jam
    except tweepy.TweepyException as e:
        if "429" in str(e):  # Rate limit error
            wait_time = 3600  # Tunggu 1 jam jika terkena rate limit
            print(f"🚫 Rate limit terdeteksi. Tunggu {wait_time//60} menit...")
            time.sleep(wait_time)
        else:
            print(f"🚨 Error tidak dikenal: {e}")
            time.sleep(600)  # Tunggu 10 menit jika ada error lain