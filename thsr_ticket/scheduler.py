import datetime
import subprocess
import time
import sys

def run_at_specific_time(command: list):
    try:
        time_str = input("請輸入目標執行時間 (格式 YYYY-MM-DD HH:MM:SS): ")
        target_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        print(f"設定成功！")
        print(f"  - 目標時間: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  - 執行指令: {' '.join(command)}")
        print("-" * 30)

    except ValueError:
        print("錯誤：時間格式不正確，請確保格式為 YYYY-MM-DD HH:MM:SS")
        return

    while True:
        current_time = datetime.datetime.now()
        if current_time >= target_time:
            print(f"\n時間到！現在執行指令...")
            try:
                result = subprocess.run(
                    command,
                    check=True,          # 如果指令返回非零(錯誤)碼，則引發例外
                    capture_output=True, # 捕獲標準輸出和標準錯誤
                    text=True            # 以文字模式解碼輸出
                )
                print("程式執行成功！")
                print("--- 輸出內容 ---")
                print(result.stdout)
                print("--------------------")

            except FileNotFoundError:
                print(f"錯誤：找不到程式 '{command[1]}'")
            except subprocess.CalledProcessError as e:
                print(f"錯誤：程式執行時發生錯誤")
                print("--- 錯誤訊息 ---")
                print(e.stderr)
                print("------------------")
            break

        else:
            print(f"\r等待中... 目前時間: {current_time.strftime('%H:%M:%S')}", end="")
            time.sleep(1)

if __name__ == "__main__":

    command = [
        sys.executable, 
        'thsr_ticket/main.py', 
        '--config=thsr_ticket/.db/history.json', 
        '--record=1',
        '--OCR'
    ]
    run_at_specific_time(command)