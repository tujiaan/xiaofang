from flask_restplus.reqparse import RequestParser
from werkzeug.datastructures import FileStorage

knowledge_parser=RequestParser()
knowledge_parser.add_argument('type',type=str,help='知识类型',required=True,location='form')
knowledge_parser.add_argument('content',type=str,help='指示类容',required=True,location='form')
knowledge_parser.add_argument('title',type=str,help='知识标题',required=True,location='form')
knowledge_parser.add_argument('publish_from',type=str,help='来源',required=True,location='form')

knowledge_parser1=RequestParser()
knowledge_parser1.add_argument('type',type=str,help='知识类型',required=False,location='form')
knowledge_parser1.add_argument('content',type=str,help='指示类容',required=False,location='form')
knowledge_parser1.add_argument('title',type=str,help='知识标题',required=False,location='form')
knowledge_parser.add_argument('publish_from',type=str,help='来源',required=False,location='form')

upload_parser = RequestParser()
upload_parser.add_argument('file',
                           type=FileStorage,
                           help="上传文件",
                           required=True,
                           location='files')

allow_ext = ['png', 'jpg', 'jpeg', 'gif']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allow_ext