import subprocess
import json


# should use this instead (gittools)
# https://github.com/chuanconggao/extratools/blob/main/extratools/gittools.py
# >_ git status -s -b --porcelain=2

def get_git_state()-> tuple[bool,str]:

    run=lambda cmd:subprocess.run(cmd,shell=True,capture_output=True,text=True).stdout

    status=run("git status")
    cleanState="Your branch is up to date with" in status
    cleanState &="nothing to commit, working tree clean" in status
    


    git_HEAD=run("git rev-parse HEAD").strip()
    print(f"HEAD is {git_HEAD}")

    return cleanState,git_HEAD