import os,shutil
import torngas
example=os.path.dirname(torngas.__file__) + '/resource/app'
target_path=''
def copyfile(source,target):

    if not os.path.exists(target):
        print 'create target dir...'
        os.makedirs(target)
    for file in os.listdir(source):
        source_file=os.path.join(source,file)
        if os.path.isdir(source_file):
            print 'create dir:',source_file
            copyfile(source_file,os.path.join(target,file))
        else:
            print 'create file:',file
            shutil.copyfile(source_file,os.path.join(target,file))

if __name__=="__main__":
    copyfile(example,'/Users/mengqingyun/Documents/app')
