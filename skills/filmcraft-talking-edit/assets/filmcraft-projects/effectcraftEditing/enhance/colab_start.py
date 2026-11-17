# Starts run_all.sh on the Colab VM as a detached background process (survives the CLI disconnecting) and returns.
import subprocess
subprocess.run("pkill -f run_reuse.py; sed -i 's/\\r$//' /content/run_all.sh; rm -f /content/out/progress.log; mkdir -p /content/out",
               shell=True)
subprocess.Popen(["nohup", "bash", "/content/run_all.sh"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                 start_new_session=True)
print("started RE-USE in the background; log: /content/out/progress.log")
