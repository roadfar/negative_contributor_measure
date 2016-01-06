import os
import subprocess
import logging
import csv
import re

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='sonar.log',
                filemode='w')

logging.debug("this is the message !")

//测试时间
#put commits logs
log_indexs=[]
#put the commitors logs
email_list=[]
#put the lines of code made by contributors
contributor_efforts={}
#commits need tobe scaned
commits_need_scaned=[]

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
    log_indexs.reverse
    return log_indexs

def run():
    #get_indexs()
    length = len(log_indexs)
    print "the count of all commits is" + str(len(log_indexs))
    for index,item in list(enumerate(commits_need_scaned)):
        print str(index) +"the limit is "+str(length)
        flag = reset_history(item)
        if flag == 0:
            sonar_measure()

#get the effort of every commitors
def commit_effort_count():
    #git log --pretty='%aN' | sort | uniq -c | sort -k1 -n -r
    state  = os.popen("git log --pretty='%aE' | sort | uniq -c | sort -k1 -n -r").read()
    writer=csv.writer(file('code_effort.csv','wb'))
    writer.writerow(['contributor','commit_count','add','removed','total'])
    tmp_arr = state.split("\n")
    for line in tmp_arr:
        csv_line=[]
        line = line.strip()
        arr = line.split(" ")
        if len(arr) == 2:
            email = line.split(" ")[1]
            csv_line.append(email)
            commit_count = line.split(" ")[0]
            csv_line.append(commit_count)
            code_efforts = os.popen("git log --author="+email+" --pretty=tformat: --numstat | awk '{ add += $1 ; subs += $2 ; loc += $1 - $2 } END { printf \"added lines: \%s removed lines : \%s total lines: \%s\\n\",add,subs,loc }' - ").read()
            add_remove_total = re.findall(r"\d+\.?\d*",code_efforts)
            print add_remove_total
            for num in add_remove_total:
                csv_line.append(num)
            writer.writerow(csv_line)


def get_need_scan_commits():
    get_indexs()
    commits_and_changed_files = {}
    #get index to do the git command
    for line in log_indexs:
        state = os.popen("git show "+line+" --stat").read()
       # print state
        tmp_arr =[]
        for item in state.split("\n"):
            if "|" in item:
                change_files = item.split("|")[0].strip()
                logging.info(change_files)
                tmp_arr.append(change_files)
        commits_and_changed_files[line] = tmp_arr
    pre_change_files=[]

    for index,log in list(enumerate(log_indexs)):
        if index == len(log_indexs)-1:
            commits_need_scaned.append(log)
        elif index == 0:
            pre_change_files.append(commits_and_changed_files[log])
            pre_commit = log
            continue
        change_files = commits_and_changed_files[log]
        if interlist(change_files,pre_change_files)==[]:
            pre_change_files.append(change_files)
            pre_commit = log
        else:
            commits_need_scaned.append(pre_commit)
            pre_commit = log
            pre_change_files=change_files
    print commits_need_scaned
    print len(commits_need_scaned)
    print len(log_indexs)

def interlist(a,b):
    ret=[]
    for i in a:
        if i not in b:
            ret.append(i)
    return ret

if __name__ == '__main__':
    #get the code efforts of every contributor
    commit_effort_count()
    #first get the commits which we need to measure
    get_need_scan_commits()
    #reset to one version and measure
    run()

