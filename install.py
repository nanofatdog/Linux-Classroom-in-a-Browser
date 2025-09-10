import subprocess
import sys
import shutil

IMAGE_NAME = "ubuntu-classroom"
NETWORK_NAME = "classroom-net"

def run_command(command, error_message, show_output=True, capture_output=False):
    """Runs a command, optionally showing its live output, and exits if it fails."""
    try:
        # Determine the appropriate arguments for subprocess.run
        kwargs = {
            "shell": True,
            "check": True
        }
        if not show_output or capture_output:
            kwargs["stdout"] = subprocess.PIPE
            kwargs["stderr"] = subprocess.PIPE
            kwargs["text"] = True

        # Run the command
        process = subprocess.run(command, **kwargs)

        if capture_output:
            return process.stdout.strip()
            
    except subprocess.CalledProcessError as e:
        print(f"\nเกิดข้อผิดพลาด: {error_message}")
        # Print stderr if it was captured
        if "stderr" in kwargs and e.stderr:
            print(e.stderr)
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
        run_command("docker info", "Docker ไม่ได้ทำงาน!", show_output=False)
        print("  -> Docker กำลังทำงาน")
    except SystemExit:
        print("Docker ไม่ได้ทำงาน! กรุณาเปิดโปรแกรม Docker Desktop หรือ start Docker service ก่อน")
        sys.exit(1)

def create_docker_network():
    """Creates a custom bridge network for the containers."""
    print(f"\nStep 2: กำลังตรวจสอบ Docker network '{NETWORK_NAME}'...")
    
    # Check if the network already exists
    existing_network = run_command(
        f"docker network ls --filter name=^{NETWORK_NAME}$ -q", 
        "ไม่สามารถตรวจสอบ network ได้",
        capture_output=True
    )

    if not existing_network:
        print(f"  -> ไม่พบ Network, กำลังสร้าง '{NETWORK_NAME}'...")
        run_command(
            f"docker network create --subnet=172.20.0.0/16 {NETWORK_NAME}",
            f"ไม่สามารถสร้าง Docker network '{NETWORK_NAME}' ได้",
            show_output=False
        )
        print(f"  -> สร้าง Network '{NETWORK_NAME}' สำเร็จ")
    else:
        print(f"  -> Network '{NETWORK_NAME}' มีอยู่แล้ว")

def build_docker_image():
    """Builds the Docker image from the Dockerfile."""
    print(f"\nStep 3: กำลังสร้าง Docker image '{IMAGE_NAME}'...")
    print("="*50)
    run_command(
        f"docker build -t {IMAGE_NAME} .",
        f"ไม่สามารถสร้าง Docker image '{IMAGE_NAME}' ได้"
    )
    print("="*50)
    print(f"  -> สร้าง Docker image '{IMAGE_NAME}' สำเร็จ!")

def main():
    """Main installation function."""
    print("--- เริ่มกระบวนการติดตั้ง Linux Classroom ---")
    check_docker()
    create_docker_network()
    build_docker_image()
    print("\n--- การติดตั้งเสร็จสมบูรณ์! ---")
    print("\nคุณสามารถเริ่มใช้งานเว็บแอปพลิเคชันได้โดยใช้คำสั่ง:")
    print("python app.py")

if __name__ == "__main__":
    main()

