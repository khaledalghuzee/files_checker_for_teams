import os
from logginger import Logging
from re import match
import hashlib
import stat


class FilesChecker:
    def __init__(self,path):
        self.pattern  = r"^\d{4}-\d{2}-\d{2}_[A-Za-z0-9]+_[A-Za-z0-9_]+(\.\d+)?\.[a-zA-Z0-9]+$"
        self.path = path
        self.duplicated = 0
        self.valid = 0
        self.empty = 0
        self.not_on_pattern = 0
        self.files = [] #اسماء الملفات
        self.folder_content = [] 
        self.checked_files = [] # بيانات التقرير
        self.unique_hashes = [] # لكشف التكرار
        # لحفظ ملف log في نفس مجلد الأداه
        self.log = Logging(os.path.dirname(os.path.abspath(__file__)))
 

    def is_valid_path(sefl):
        """التحقق من وجود المسار وصحته"""
        return os.path.exists(sefl.path)
    
    
    def isdir(self):
        """التحقق هل المسار عباره عن مجلد"""
        return os.path.isdir(self.path)
    

    def get_file_hash(self, file_path):
        """أخذ hash للملف ليعمل كبصمه تميزه من التكرار"""
        h = hashlib.sha256()
        try:
            with open(file_path, 'rb') as file:
                while chunk := file.read(65536): # 64kb
                    h.update(chunk)
            return h.hexdigest()
        except Exception as e:
            self.log.warning(f"Hash error {file_path}: {e}")
            return None

    def list_folder_contenent(self):
        """جلب محتويات المجلد"""
        return os.listdir(self.path)

    def list_folder_contenent(self):
        try:
            return os.listdir(self.path)
        except Exception:
            return []

    def load_files(self):
        
        for file in self.folder_content:
            full_path = os.path.join(self.path, file)
            
            #  تأكد أنه ملف وليس مجلداً
            if not os.path.isfile(full_path):
                continue
                # تجاهل ملفات النظام الشهيرة
            if file.lower() in ['thumbs.db', 'desktop.ini']:
                continue
            
            #  تجاهل ملفات  المؤقتة للأوفيس
            if file.startswith('~$'):
                continue

    
            try:
                file_stats = os.stat(full_path)
                
                # تجاهل ملفات نظام
                if file_stats.st_file_attributes & stat.FILE_ATTRIBUTE_SYSTEM:
                    continue
                
                # if file_stats.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN: continue # للملفات المخفية

            except Exception:
                continue # اكيد ملف نظام 

            #  فحص الملفات المفتوحة 
            try:
                with open(full_path, 'rb'):
                    pass
            except PermissionError:
                self.log.warning(f"تم تجاهل الملف لأنه مفتوح في برنامج آخر: {file}")
                continue 
            except Exception as e:
                self.log.warning(f"تم تجاهل ملف غير قابل للقراءة: {file}")
                continue

            self.files.append(file)

    def is_no_files(self):
        return not len(self.files)
    
    def is_empty_file(self,file_path):
        return not os.path.getsize(file_path)
    
    def is_follow_pattren(self,file):
        return match(self.pattern ,file)
    

