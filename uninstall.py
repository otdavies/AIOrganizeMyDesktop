import ctypes
import sys
import winreg


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1)


def remove_context_menu():
    if not is_admin():
        print("The script is not running with admin rights. Trying to get admin rights...")
        run_as_admin()
    else:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, 'Directory\\Background\\shell', 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                winreg.DeleteKey(key, 'Organize Files\\command')
                winreg.DeleteKey(key, 'Organize Files')
                print("Successfully removed the context menu entry.")
            except FileNotFoundError:
                print("The context menu entry was not found.")
            except PermissionError:
                print(
                    "Failed to remove the context menu entry. Try running the script as an administrator.")


if __name__ == "__main__":
    remove_context_menu()
