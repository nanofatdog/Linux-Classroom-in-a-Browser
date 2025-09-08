import subprocess
import sys

IMAGE_NAME = "ubuntu-classroom"

def run_command(command, capture_output=False):
    """Runs a command, returns its output if needed."""
    try:
        result = subprocess.run(command, check=True, shell=True, text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"คำสั่ง '{command}' ล้มเหลว: {e.stderr}")
        return None
    except FileNotFoundError:
        print(f"เกิดข้อผิดพลาด: ไม่พบคำสั่ง '{command.split()[0]}'.")
        return None

def main():
    """Main uninstallation function."""
    print("--- เริ่มกระบวนการถอนการติดตั้ง Linux Classroom ---")

    # Step 1: Find and stop containers using the image
    print(f"\nStep 1: ค้นหาและหยุด containers ที่ใช้ image '{IMAGE_NAME}'...")
    container_ids = run_command(f"docker ps -q --filter ancestor={IMAGE_NAME}")
    
    if container_ids:
        print(f"  -> พบ containers ที่กำลังทำงาน: {len(container_ids.split())} ตัว")
        run_command(f"docker stop {container_ids.replace('\n', ' ')}")
        print("  -> หยุดการทำงานของ containers ทั้งหมดแล้ว")
    else:
        print("  -> ไม่พบ containers ที่กำลังทำงาน")

    # Step 2: Prune any stopped containers (optional but good practice)
    print("\nStep 2: กำลังลบ stopped containers...")
    run_command("docker container prune -f")
    print("  -> ลบ stopped containers เรียบร้อย")

    # Step 3: Remove the Docker image
    print(f"\nStep 3: กำลังลบ Docker image '{IMAGE_NAME}'...")
    result = run_command(f"docker rmi {IMAGE_NAME}")
    if result:
        print(f"  -> ลบ Docker image '{IMAGE_NAME}' สำเร็จ!")
    else:
        print(f"  -> ไม่พบ Docker image '{IMAGE_NAME}' หรือไม่สามารถลบได้")

    print("\n--- การถอนการติดตั้งเสร็จสมบูรณ์ ---")

if __name__ == "__main__":
    main()
