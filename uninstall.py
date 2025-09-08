import subprocess
import sys

IMAGE_NAME = "ubuntu-classroom"

def run_command(command, capture_output=False):
    """Runs a command, returns its output if needed, and handles errors."""
    try:
        if capture_output:
            result = subprocess.run(
                command, 
                shell=True, 
                check=True, 
                capture_output=True, 
                text=True
            )
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=True)
            return ""
    except subprocess.CalledProcessError as e:
        print(f"  -> เกิดข้อผิดพลาดขณะรันคำสั่ง: {e.stderr}")
        return None
    except FileNotFoundError:
        print(f"  -> ไม่พบคำสั่ง '{command.split()[0]}'. กรุณาตรวจสอบว่า Docker ติดตั้งถูกต้อง")
        return None

def main():
    """Main uninstallation function with user confirmation."""
    print(f"--- เริ่มกระบวนการถอนการติดตั้งสำหรับ '{IMAGE_NAME}' ---")

    # Step 1: Find and stop running containers from the image
    print("\nStep 1: กำลังค้นหาและหยุด containers ที่ทำงานอยู่...")
    container_ids = run_command(f"docker ps -q --filter ancestor={IMAGE_NAME}", capture_output=True)

    if container_ids:
        num_containers = len(container_ids.split())
        print(f"  -> พบ containers ที่ทำงานอยู่ {num_containers} ตัว:")
        print(container_ids)
        
        confirm = input("  -> คุณต้องการหยุด containers เหล่านี้หรือไม่? (y/n): ").lower()
        if confirm == 'y':
            ids_to_stop = container_ids.replace('\n', ' ')
            print("  -> กำลังสั่งหยุด containers...")
            run_command(f"docker stop {ids_to_stop}")
            print("  -> หยุด containers สำเร็จ")
        else:
            print("  -> ยกเลิกการหยุด containers")
    elif container_ids is not None:
        print("  -> ไม่พบ containers ที่ทำงานจาก image นี้")

    # Step 2: Remove the Docker image
    print(f"\nStep 2: กำลังลบ Docker image '{IMAGE_NAME}'...")
    image_id = run_command(f"docker images -q {IMAGE_NAME}", capture_output=True)

    if image_id:
        print(f"  -> พบ Docker image '{IMAGE_NAME}' (ID: {image_id[:12]})")
        confirm = input("  -> คุณต้องการลบ image นี้หรือไม่? (การกระทำนี้ไม่สามารถย้อนกลับได้) (y/n): ").lower()
        if confirm == 'y':
            print("  -> กำลังลบ image...")
            run_command(f"docker rmi -f {IMAGE_NAME}")
            print(f"  -> ลบ Docker image '{IMAGE_NAME}' เรียบร้อยแล้ว")
        else:
            print("  -> ยกเลิกการลบ image")
    elif image_id is not None:
        print(f"  -> ไม่พบ Docker image '{IMAGE_NAME}' ในระบบ")

    print("\n--- การถอนการติดตั้งเสร็จสมบูรณ์! ---")

if __name__ == "__main__":
    main()
