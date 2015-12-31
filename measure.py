import os
import subprocess
import logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='sonar.log',
                filemode='w')

logging.debug("this is the message !")

log_indexs=[]
email_list=[]
contributor_efforts={}


def commit_logs():
    cmd_log = ["git",
               "log",
               "--pretty=oneline"]
    proc = subprocess.Popen(cmd_log,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout,stderr = proc.communicate()

    #commit_log = os.system("git log --pretty=oneline ")
    return stdout

def reset_history(log_index):
    #reset one version
    flag = os.system("git reset --hard "+ log_index)
    return flag

def sonar_measure():
    #sonar=os.system("sonar-runner")
    #use the sonar to measure one version of the project
    proc = subprocess.Popen("sonar-runner",
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout , stderr  = proc.communicate()

def get_indexs():
    logs=commit_logs()
    log_arr = logs.split("\n")
    for line in log_arr:
        if line != " ":
            strs = line.split(" ")
            log_indexs.append(strs[0])
    return log_indexs

def run():
    get_indexs()
    length = len(log_indexs)
    print "the count of all commits is" + str(len(log_indexs))
    log_indexs.reverse()
    for index,item in list(enumerate(log_indexs)):
        print str(index) +"the limit is "+str(length)
        flag = reset_history(item)
        if flag == 0:
            sonar_measure()

#get the effort of every commitors
def commit_effort_count():
    #git log --pretty='%aN' | sort | uniq -c | sort -k1 -n -r
    state  = os.popen("git log --pretty='%aE' | sort | uniq -c | sort -k1 -n -r").read()

    print state
    tmp_arr = state.split("\n")
    for line in tmp_arr:
        line = line.strip()
        arr = line.split(" ")
        if len(arr) == 2:
            email = line.split(" ")[1]
            commit_count = line.split(" ")[0]
            print os.popen("git log --author="+email+" --pretty=tformat: --numstat | awk '{ add += $1 ; subs += $2 ; loc += $1 - $2 } END { printf \"added lines: \%s removed lines : \%s total lines: \%s\\n\",add,subs,loc }' - ").read()



if __name__ == '__main__':
    run()
    commit_effort_count()