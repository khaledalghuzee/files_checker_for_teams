import flet as ft
from os.path import join
from output import output_as_csv
from scanner import FilesChecker

def main_gui(page: ft.Page):
    # إعدادات الصفحة
    page.title = "أداة فحص الملفات"
    page.window_icon = "icon.png" 
    page.window_width = 750
    page.window_height = 720 # زيادة بسيطة لاحتواء العناصر الجديدة
    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.START

    header = ft.Text(
        value="نظام التحقق من الملفات",
        size=25,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_800 
    )

    pattern_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.INFO, color=ft.Colors.CYAN_200),
                ft.Text("نمط التسمية: YYYY-MM-DD_AnyText_AnyText.ext", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ]),
            ft.Text("example: 2024-01-09_Files_Report.pdf", color=ft.Colors.GREY_400, size=12),
        ]),
        bgcolor=ft.Colors.BLUE_GREY_900,
        padding=10,
        border_radius=10,
        border=ft.border.all(1, ft.Colors.BLUE_GREY_600)
    )

    txt_path = ft.TextField(
        label="مسار المجلد",
        hint_text="الرجاء اختيار مجلد...",
        read_only=True,
        expand=True,
        border_color=ft.Colors.BLUE_200,
        text_align=ft.TextAlign.LEFT
    )

    logs_list = ft.ListView(
        expand=True,
        spacing=2,
        padding=10,
        auto_scroll=True,
    )

    logs_container = ft.Container(
        content=logs_list,
        bgcolor=ft.Colors.BLACK87, 
        border_radius=10,
        padding=10,
        expand=True,
        visible=False,
        border=ft.border.all(1, ft.Colors.GREY_500)
    )

    stats_container = ft.Container(visible=False)

    def add_log_ui(message: str, color: str = ft.Colors.WHITE):
        """إضافة نص ملون لشاشة السجلات"""
        logs_list.controls.append(
            ft.Text(value=f">> {message}", color=color, font_family="Consolas", size=14)
        )
        page.update()

    def run_check_process(folder_path):
        logs_container.visible = True
        stats_container.visible = False 
        btn_run.disabled = True
        btn_select.disabled = True
        logs_list.controls.clear()
        page.update()

        try:
            add_log_ui("=== بدأت العملية ===", ft.Colors.CYAN_ACCENT)
            
            checker = FilesChecker(folder_path)

            checker.not_on_pattern = 0
            checker.empty = 0
            checker.duplicated = 0
            checker.valid = 0
            
            if not checker.is_valid_path():
                add_log_ui("خطأ: المسار غير موجود!", ft.Colors.RED_ACCENT)
                return
            
            if not checker.isdir():
                add_log_ui("خطأ: المسار ليس مجلداً!", ft.Colors.RED_ACCENT)
                return

            checker.folder_content = checker.list_folder_contenent()
            checker.load_files()

            if checker.is_no_files():
                add_log_ui("تنبيه: المجلد فارغ.", ft.Colors.YELLOW)
                checker.log.warning('المجلد فارغ')
            else:
                add_log_ui(f"تم العثور على {len(checker.files)} ملفات. جارِ الفحص...", ft.Colors.GREEN)

            for i in checker.files:
                full_path = join(checker.path, i)
                
                file_record = {
                    'Name': i,
                    'Stutas': 'Valid',
                    'hash': None,
                    'Notes': ''
                }

                add_log_ui(f"فحص الملف: {i}...", ft.Colors.GREY_400)

                file_record['hash'] = checker.get_file_hash(full_path)

                if not checker.is_follow_pattren(i):
                    file_record['Stutas'] = "False"
                    file_record['Notes'] = 'wrong name'
                    checker.log.warning(f'اسم مخالف للنمط: {i}')
                    add_log_ui(f"  [X] اسم مخالف: {i}", ft.Colors.ORANGE)
                    checker.not_on_pattern+=1

                if checker.is_empty_file(full_path):
                    checker.empty+=1
                    note = 'empty file'
                    if file_record['Notes']:
                        file_record['Notes'] += ' + ' + note
                    else:
                        file_record['Notes'] = note
                    checker.log.warning(f'ملف فارغ: {i}')
                    add_log_ui(f"  [!] ملف فارغ: {i}", ft.Colors.ORANGE)

                if file_record['hash'] and file_record['hash'] in checker.unique_hashes:
                    checker.duplicated+=1
                    for j in checker.checked_files:
                        if j['hash'] == file_record['hash']:
                            if 'Duplicated' not in j['Notes']:
                                if j['Notes']: j['Notes'] += ', Duplicated'
                                else: j['Notes'] = 'Duplicated'
                    
                    if file_record['Notes']: file_record['Notes'] += ', Duplicated'
                    else: file_record['Notes'] = 'Duplicated'
                    
                    file_record['Stutas'] = "False"
                    checker.log.warning(f'ملف مكرر: {i}')
                    add_log_ui(f"  [XX] ملف مكرر: {i}", ft.Colors.RED_ACCENT)
                else:
                    if file_record['hash']:
                        checker.unique_hashes.append(file_record['hash'])
                
                if file_record['Stutas'] != 'False':
                    checker.valid+=1

                checker.checked_files.append(file_record)

            add_log_ui("--------------------------------", ft.Colors.GREY)
            add_log_ui("انتهى الفحص. جاري إنشاء ملف CSV...", ft.Colors.CYAN)
            
            result_msg = output_as_csv(checker.checked_files, checker.path)
            
            checker.log.info('تم تصدير التقرير')
            add_log_ui(result_msg, ft.Colors.GREEN_ACCENT)
            add_log_ui("=== تمت العملية بنجاح ===", ft.Colors.WHITE)

            stats_container.content = ft.Row([
                ft.Column([ft.Text(str(checker.valid), size=20, weight="bold", color="green"), ft.Text("سليم")], alignment="center"),
                ft.Column([ft.Text(str(checker.duplicated), size=20, weight="bold", color="red"), ft.Text("مكرر")], alignment="center"),
                ft.Column([ft.Text(str(checker.not_on_pattern), size=20, weight="bold", color="orange"), ft.Text("نمط خطأ")], alignment="center"),
                ft.Column([ft.Text(str(checker.empty), size=20, weight="bold", color="grey"), ft.Text("فارغ")], alignment="center"),
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
            stats_container.visible = True
            stats_container.update()

            page.snack_bar = ft.SnackBar(
                content=ft.Text("تم الانتهاء بنجاح!"),
                bgcolor=ft.Colors.GREEN
            )
            page.snack_bar.open = True

        except Exception as ex:
            add_log_ui(f"حدث خطأ غير متوقع: {ex}", ft.Colors.RED)
            checker.log.error(f"Main Loop Error: {ex}")
        
        finally:
            btn_run.disabled = False
            btn_select.disabled = False
            page.update()

    def on_dialog_result(e: ft.FilePickerResultEvent):
        if e.path:
            txt_path.value = e.path
            btn_run.disabled = False
            page.update()

    def on_run_click(e):
        if txt_path.value:
            run_check_process(txt_path.value)

    directory_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(directory_picker)

    btn_select = ft.ElevatedButton(
        text="اختر المجلد",
        icon=ft.Icons.FOLDER_OPEN,
        on_click=lambda _: directory_picker.get_directory_path(),
        height=50,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
    )

    btn_run = ft.ElevatedButton(
        text="بدء الفحص والتحليل",
        icon=ft.Icons.PLAY_ARROW,
        on_click=on_run_click,
        disabled=True,
        height=50,
        width=200,
        bgcolor=ft.Colors.GREEN_700,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
    )

    page.add(
        ft.Column(
            controls=[
                header,
                pattern_card, 
                ft.Divider(height=20, thickness=2),
                ft.Row([txt_path, btn_select], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=10),
                ft.Row([btn_run], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=10),
                stats_container, 
                ft.Text("سجل العمليات (Logs):", weight=ft.FontWeight.BOLD),
                logs_container
            ],
            expand=True
        )
    )