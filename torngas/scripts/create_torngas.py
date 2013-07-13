import os, shutil
import torngas

example = os.path.dirname(torngas.__file__) + '/resource/app'
target_path = ''


def copyfile(source, target):
    if not os.path.exists(target):

        os.makedirs(target)
    for file in os.listdir(source):
        source_file = os.path.join(source, file)
        if os.path.isdir(source_file):
            todir = os.path.join(target, file)
            print 'create dir:', todir
            copyfile(source_file, todir)
        else:

            tofile = os.path.join(target, file)
            # if not tofile.endswith('pyc'):
            print 'create file:', tofile
            shutil.copyfile(source_file, tofile)


if __name__ == "__main__":
    print 'create target app...'
    copyfile(example, os.getcwd())
    print 'finished...'
