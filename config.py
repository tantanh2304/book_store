import os

class Config:
    # Secret key cho session
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'b1c31b83877c9964c56ce123890ad470353ef740a8215211ec52f55f813850ce'
    
    # Cấu hình SQL Server
    SQL_SERVER = 'thanhtruc'  # hoặc địa chỉ server của bạn
    SQL_DATABASE = 'BookstoreDB'
    
    
    # Connection string cho SQL Server
    SQLALCHEMY_DATABASE_URI = f'mssql+pyodbc://{SQL_SERVER}/{SQL_DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder
    UPLOAD_FOLDER = 'static/images'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size