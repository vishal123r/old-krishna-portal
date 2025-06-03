import os

def create_startup_bat():
    # ✅ Startup folder path (for RAM user)
    startup_path = r"C:\Users\RAM\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"

    # ✅ Project path where app.py is located
    project_path = r"E:\khc\VIKAS CRM"

    # ✅ Path where the .bat file will be created
    bat_file_path = os.path.join(startup_path, "start_app.bat")

    # ✅ Write content to .bat file
    with open(bat_file_path, "w") as file:
        file.write("@echo off\n")
        file.write("E:\n")  # Switch to E: drive
        file.write(f'cd "{project_path}"\n')
        file.write("python app.py\n")

    print("✅ start_app.bat created in Windows Startup folder.")
    print(f"📂 Location: {bat_file_path}")
    print("🚀 app.py will now auto-run on system startup!")

if __name__ == "__main__":
    create_startup_bat()
