import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Konfigurasi Google Sheets
SHEET_NAME = "Kutipan_10_Hari"  # Ganti dengan nama Google Sheets kamu
CREDENTIALS_FILE = "shopeebot.json"  # Path ke credentials JSON

# Setup koneksi ke Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client_gsheet = gspread.authorize(creds)
sheet = client_gsheet.open(SHEET_NAME).sheet1

def get_pending_quote():
    """
    Mengambil kutipan yang berstatus 'Pending' dari Google Sheets.
    """
    try:
        data = sheet.get_all_values()
        if not data:
            print("🚨 Google Sheets kosong!")
            return None

        # Ambil header dan cari kolom yang sesuai
        header = [h.strip().lower() for h in data[0]]
        if "kutipan" not in header or "penulis" not in header or "status" not in header:
            print("🚨 Kolom tidak ditemukan! Pastikan ada 'Kutipan', 'Penulis', dan 'Status'.")
            return None

        index_kutipan = header.index("kutipan")
        index_penulis = header.index("penulis")
        index_status = header.index("status")

        for i, row in enumerate(data[1:], start=2):  # Mulai dari baris kedua (data, bukan header)
            if len(row) > index_status and row[index_status].strip().lower() == "pending":
                kutipan = row[index_kutipan] if len(row) > index_kutipan else ""
                penulis = row[index_penulis] if len(row) > index_penulis else "Anonim"

                if kutipan:
                    return i, kutipan, penulis  # Kembalikan baris, kutipan, dan penulisnya

        print("🚨 Tidak ada kutipan dengan status 'Pending'.")
        return None

    except Exception as e:
        print(f"🚨 Error membaca Google Sheets: {e}")
        return None

def update_status(row_number):
    """
    Mengupdate status kutipan menjadi 'Posted' setelah berhasil diposting.
    """
    try:
        sheet.update_cell(row_number, 3, "Posted")  # Kolom Status ada di indeks 3
        print(f"✅ Status di Google Sheets diperbarui menjadi 'Posted'.")
    except Exception as e:
        print(f"🚨 Error mengupdate status: {e}")
