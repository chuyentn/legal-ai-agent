import subprocess
import time
import re

def monitor_terminal_log(command, done_pattern=r"✅ Embedding done!", error_pattern=r"(Traceback|Exception|Error|exit code|FAILED)", poll_interval=5):
    """
    Chạy command và tự động theo dõi output, báo done hoặc lỗi.
    """
    print(f"[Monitor] Running: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    done = False
    while True:
        line = process.stdout.readline()
        if not line:
            if process.poll() is not None:
                break
            time.sleep(poll_interval)
            continue
        print(line, end="")
        if re.search(done_pattern, line):
            print("[Monitor] ✅ DONE detected!")
            done = True
            break
        if re.search(error_pattern, line, re.IGNORECASE):
            print("[Monitor] ❌ ERROR detected!")
            break
    process.terminate()
    if done:
        print("[Monitor] Pipeline completed successfully!")
    else:
        print("[Monitor] Pipeline exited with error or was interrupted.")

if __name__ == "__main__":
    # Lệnh chạy pipeline (có thể chỉnh lại cho phù hợp môi trường)
    cmd = "d:/AI-KILLS/legal-ai-agent-main/.venv/Scripts/python.exe scripts/run_all.py"
    monitor_terminal_log(cmd)
