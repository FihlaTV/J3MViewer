import os, requests, re
import tornado.ioloop, tornado.web, tornado.httpserver
from operator import itemgetter

class Index(tornado.web.RequestHandler):
	def get(self):
		self.render('index.html', route='main', title="")
		
class Submissions(tornado.web.RequestHandler):
	def get(self):
		self.render('index.html', route='submissions', title=' : Submissions')
		
class Submission(tornado.web.RequestHandler):
	def initialize(self, submission_id):
		self.submission_id = submission_id
		
	def get(self, submission_id):
		self.render('index.html', route='submission', title=' : Submission %s' % submission_id)
		
class Sources(tornado.web.RequestHandler):
	def get(self):
		self.render('index.html', route='sources', title=' : Sources')
		
class Source(tornado.web.RequestHandler):
	def initialize(self, source_id):
		self.source_id = source_id
		
	def get(self, submission_id):
		self.render('index.html', route='source', title=' : Source %s' % source_id)
		
class Media(tornado.web.RequestHandler):
	def initialize(self, route):
		self.route = route
		
	def get(self, route):
		r = requests.get("%s%s" % (media, route))
		self.write(r.content)
		
class Api(tornado.web.RequestHandler):
	def initialize(self, route):
		self.route = route
	
	def get(self, route):
		route_ = route
		
		if route == "recent/":
			route_ = "submissions/"
			
		if re.match("submission/\w{32}/", route):
			route_ = route[:-1]
		
		request = "%s%s" % (api, route_)
		if self.request.query != "":
			request += "?%s" % self.request.query
		
		r = requests.get(request)
		self.write(self.sanitize(r.json(), route))
		
	def sanitize(self, json, route):
		print "sanitizing results for %s" % route
		
		try:
			if route == "recent/" or route == "submissions/":
				# sort by date
				json['data'] = sorted(
					json['data'], 
					key=itemgetter('date_admitted'), 
					reverse=True
				)
				
			if route == "recent/":
				# return top 10
				json['data'] = json['data'][:10]
				
			if re.match("submission/\w{32}/", route):
				# mustache requires a bit of massaging of data here...
				# load up j3m
				
				# load up source
				
				# get location
				
				json['data'] = json['data']
				
		except:
			pass
		
		return json

api = "http://icdev.guardianproject.info/api/"
media = "http://icdev.guardianproject.info/media/"

js_path = os.path.join(os.path.dirname(__file__), "js")
css_path = os.path.join(os.path.dirname(__file__), "css")
images_path = os.path.join(os.path.dirname(__file__), "images")
layout_path = os.path.join(os.path.dirname(__file__), "layout")
	
routes = [
	(r"/", Index),
	(r"/submissions/", Submissions),
	(r"/submission/(.*)/", Submission, dict(submission_id=None)),
	(r"/sources/", Sources),
	(r"/source/(.*)/", Source, dict(source_id=None)),
	(r"/api/(.*)", Api, dict(route=None)),
	(r"/media/(.*)", Media, dict(route=None)),
	(r"/js/(.*)", tornado.web.StaticFileHandler, {'path': js_path}),
	(r"/css/(.*)", tornado.web.StaticFileHandler, {'path': css_path}),
	(r"/images/(.*)", tornado.web.StaticFileHandler, {'path': images_path}),
	(r"/layout/(.*)", tornado.web.StaticFileHandler, {'path': layout_path})
]

app = tornado.web.Application(routes)

if __name__ == "__main__":
	server = tornado.httpserver.HTTPServer(app)
	server.listen(6666)
	
	tornado.ioloop.IOLoop.instance().start()