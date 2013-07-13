from optparse import OptionParser

parser = OptionParser()
parser.add_option('-p',
                  '--path',
                  dest='path',
                  help="your app local path",
                  default=5)
(option, args) = parser.parse_args()

queue = Queue()
creater = Creater('creater_school', queue, int(option.counts))#每次从数据库获取数据数量
creater.setDaemon(True)
creater.start()