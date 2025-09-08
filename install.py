import subprocess
import sys
import shutil

IMAGE_NAME = "ubuntu-classroom"

def run_command(command, error_message, show_output=True):
    """Runs a command, optionally showing its live output, and exits if it fails."""
    try:
        if show_output:
            # Stream output directly to the console
            process = subprocess.Popen(command, shell=True)
            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command)
        else:
            # Run silently
            subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
    except subprocess.CalledProcessError:
        print(f"\nเกิดข้อผิดพลาด: {error_message}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"เกิดข้อผิดพลาด: ไม่พบคำสั่ง '{command.split()[0]}'. กรุณาตรวจสอบว่าติดตั้งโปรแกรมแล้ว")
        sys.exit(1)

def check_docker():
    """Checks if Docker is installed and running."""
    print("Step 1: กำลังตรวจสอบ Docker...")
    if not shutil.which("docker"):
        print("ไม่พบ Docker! กรุณาติดตั้ง Docker Desktop หรือ Docker Engine ก่อนดำเนินการต่อ")
        print("ดูวิธีการติดตั้งได้ที่: https://docs.docker.com/engine/install/")
        sys.exit(1)
    
    try:
        # Run docker info silently
        run_command("docker info", "Docker ไม่ได้ทำงาน!", show_output=False)
        print("  -> Docker กำลังทำงาน")
    except SystemExit:
        print("Docker ไม่ได้ทำงาน! กรุณาเปิดโปรแกรม Docker Desktop หรือ start Docker service ก่อน")
        sys.exit(1)

def build_docker_image():
    """Builds the Docker image from the Dockerfile."""
    print(f"\nStep 2: กำลังสร้าง Docker image '{IMAGE_NAME}'...")
    print("="*50)
    # Run docker build and show its output
    run_command(
        f"docker build -t {IMAGE_NAME} .",
        f"ไม่สามารถสร้าง Docker image '{IMAGE_NAME}' ได้",
        show_output=True
    )
    print("="*50)
    print(f"  -> สร้าง Docker image '{IMAGE_NAME}' สำเร็จ!")

def main():
    """Main installation function."""
    print("--- เริ่มกระบวนการติดตั้ง Linux Classroom ---")
    check_docker()
    build_docker_image()
    print("\n--- การติดตั้งเสร็จสมบูรณ์! ---")
    print("\nคุณสามารถเริ่มใช้งานเว็บแอปพลิเคชันได้โดยใช้คำสั่ง:")
    print("python app.py")

if __name__ == "__main__":
    main()


