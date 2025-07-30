class ManagerMenu:
    @staticmethod
    def switch_to_classic_menu():
        """change to Windows 11 classic right-click menu"""
        import os

        os.system(
            'reg add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /f /ve'
        )
        os.system("taskkill /f /im explorer.exe & start explorer.exe")

    @staticmethod
    def switch_to_new_menu():
        """change to Windows 11 new right-click menu"""
        import os

        os.system(
            'reg delete "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" /f'
        )
        os.system("taskkill /f /im explorer.exe & start explorer.exe")

    @staticmethod
    def add_cursor_context_menu():
        """add Cursor to Windows right-click menu"""
        import os

        username = os.getenv("USERNAME")
        cursor_path = (
            rf"C:\\Users\\{username}\\AppData\\Local\\Programs\\Cursor\\Cursor.exe"
        )

        reg_content = f"""Windows Registry Editor Version 5.00

    [HKEY_CLASSES_ROOT\\*\\shell\\Open with Cursor]
    @="Open with Cursor"
    "Icon"="{cursor_path}"

    [HKEY_CLASSES_ROOT\\*\\shell\\Open with Cursor\\command]
    @="\\"{cursor_path}\\" \\"%1\\""

    [HKEY_CLASSES_ROOT\\Directory\\shell\\Open with Cursor]
    @="Open with Cursor"
    "Icon"="{cursor_path}"

    [HKEY_CLASSES_ROOT\\Directory\\shell\\Open with Cursor\\command]
    @="\\"{cursor_path}\\" \\"%1\\""

    [HKEY_CLASSES_ROOT\\Directory\\Background\\shell\\Open with Cursor]
    @="Open with Cursor current folder"
    "Icon"="{cursor_path}"

    [HKEY_CLASSES_ROOT\\Directory\\Background\\shell\\Open with Cursor\\command]
    @="\\"{cursor_path}\\" \\"%V\\""
    """

        # write registry content to temporary file
        with open("cursor_context_menu.reg", "w") as f:
            f.write(reg_content)

        # execute registry file
        os.system("regedit /s cursor_context_menu.reg")

        # delete temporary file
        os.remove("cursor_context_menu.reg")

    @staticmethod
    def remove_cursor_context_menu():
        """remove Cursor from Windows right-click menu"""
        import os

        reg_content = """Windows Registry Editor Version 5.00

    [-HKEY_CLASSES_ROOT\\*\\shell\\Open with Cursor]
    [-HKEY_CLASSES_ROOT\\Directory\\shell\\Open with Cursor]
    [-HKEY_CLASSES_ROOT\\Directory\\Background\\shell\\Open with Cursor]
    """

        # write registry content to temporary file
        with open("remove_cursor_context_menu.reg", "w") as f:
            f.write(reg_content)

        # execute registry file
        os.system("regedit /s remove_cursor_context_menu.reg")

        # delete temporary file
        os.remove("remove_cursor_context_menu.reg")
