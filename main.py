#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        blogposts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")

        if blogposts:
            self.render("front.html", blogs=blogposts)

class NewPostHandler(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            b = Blog(title = title, body = body)
            b.put()

            self.redirect('/blog/%s' % str(b.key().id()))
            return
        else:
            error = "we need both a title and some blog text"
            self.render("newpost.html", title=title, body=body, error=error)

class ViewPostHandler(Handler):
    def get(self, id):
        b = Blog.get_by_id(int(id))
        self.render("viewpost.html", blog=b)

app = webapp2.WSGIApplication([
    webapp2.Route(r'/', handler=MainPage),
    webapp2.Route(r'/blog', handler=MainPage),
    webapp2.Route(r'/blog/newpost', handler=NewPostHandler),
    webapp2.Route(r'/blog/<id:\d+>', handler=ViewPostHandler)
], debug=True)
