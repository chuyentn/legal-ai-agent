import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_ID = os.environ.get('LEGAL_FOLDER_ID', '')
OUTPUT_DIR = './data/van_ban_phap_ly/'

def get_drive_service():
    creds_data = json.loads(open('credentials.json').read())
    creds = service_account.Credentials.from_service_account_info(
        creds_data, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def download_folder(service, folder_id, local_path):
    os.makedirs(local_path, exist_ok=True)
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(
        q=query, fields="files(id, name, mimeType)").execute()
    
    for file in results.get('files', []):
        name, fid, mime = file['name'], file['id'], file['mimeType']
        
        if mime == 'application/vnd.google-apps.folder':
            download_folder(service, fid, os.path.join(local_path, name))
        else:
            print(f"📥 Tải: {name}")
            try:
                request = service.files().get_media(fileId=fid)
                fh = BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                with open(os.path.join(local_path, name), 'wb') as f:
                    f.write(fh.getbuffer())
                print(f"✅ Xong: {name}")
            except Exception as e:
                print(f"⚠️ Bỏ qua {name}: {e}")

if __name__ == '__main__':
    if not FOLDER_ID:
        print("❌ LEGAL_FOLDER_ID chưa được set!")
        exit(1)
    
    print(f"🚀 Bắt đầu sync từ folder: {FOLDER_ID}")
    service = get_drive_service()
    download_folder(service, FOLDER_ID, OUTPUT_DIR)
    print("🎉 Sync hoàn tất!")
