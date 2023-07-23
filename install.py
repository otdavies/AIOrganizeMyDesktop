import ctypes
import os
import sys
import winreg


class Install():
    description = 'Install a right-click context menu for the file organizer'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Check if the program is running with admin rights
        if not self.is_admin():
            print(
                "The script is not running with admin rights. Trying to get admin rights...")

            # Try to elevate privileges
            self.run_as_admin()

        else:
            # The command that the context menu item will execute
            # Get the current directory
            current_dir = os.path.dirname(os.path.realpath(__file__))

            # The command that the context menu item will execute
            cmd = f'cmd /c "{os.path.join(current_dir, "run.bat")} " "%v"'

            print("Trying to run the following command: " + cmd)

            # Add the context menu item to the registry
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, 'Directory\\Background\\shell', 0, winreg.KEY_SET_VALUE) as key:
                # Add a new key for our command
                with winreg.CreateKey(key, 'Organize Files') as subkey:
                    # Set the default value to the command
                    winreg.SetValue(subkey, 'command', winreg.REG_SZ, cmd)

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_as_admin(self):
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)


app = Install()
app.run()
