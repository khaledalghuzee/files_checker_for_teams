import csv
from os.path import join, dirname, abspath
def output_as_csv(data, output_path):
    output_path=join(output_path,'Files_Report.csv')
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8-sig') as csv_file:
            fields = ["Name", "Status", "Notes"]
            writer = csv.DictWriter(csv_file, fieldnames=fields,extrasaction='ignore')
            writer.writeheader() 
            writer.writerows(data) 
    
        return (f"تم إنشاء التقرير بنجاح في \n{output_path}")

    except Exception as e:
        try:
            app_path = dirname(abspath(__file__))
            with open(app_path, mode='w', newline='', encoding='utf-8-sig') as csv_file:
                fields = ["Name", "Status", "Notes"]
                writer = csv.DictWriter(csv_file, fieldnames=fields,extrasaction='ignore')
                writer.writeheader() 
                writer.writerows(data) 
        
            return (f"تم إنشاء التقرير بنجاح في \n{app_path}")
        except:
            return(f"حدث خطأ أثناء الكتابة: {e}")