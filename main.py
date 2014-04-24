#!/usr/bin/python2

import os
import imp
import time
import hints
import config
import BaseHTTPServer

import sqlite3 as sql

from snippets import *
from urlparse import urlparse, parse_qs

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	notice = ""
	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

	def do_POST(self):
		if ( config.tasks_enabled ):
			q = urlparse(self.path)
			args = parse_qs(q.query)

			length = int(self.headers.getheader('content-length'))
			postvars = parse_qs(self.rfile.read(length))
			if (postvars.has_key('team_name') and postvars.has_key('flag')):
				f = open ('tasks/' + args['t'][0] + '/' + args['c'][0] + '/desc', 'r')
				o = f.readlines()
				self.send_response(301)


				connection = sql.connect('score.db')
				q = "select team_name from score where flag = '%s' and team_name = '%s';"
				res = connection.execute(q % (postvars['flag'][0], postvars['team_name'][0]))
				for row in res:
					if (row):
						self.send_header("Location", "index?r=already_added")
						break
				else:
					if(o[3].strip("\n") == postvars['flag'][0]):
						q = "insert into score values ('%s', '%s', %s, '%s');"
						connection.execute(q % (postvars['team_name'][0], postvars['flag'][0], args['c'][0], time.strftime('%Y-%m-%d %H:%M:%S')))
						connection.commit()
						print 'posted?'
						self.send_header("Location", "index?r=success")
					else:
						self.send_header("Location", "index?r=fail")

				connection.close()
				f.close()
				self.end_headers()

			else:
				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()
		else:
			document = "You are trying to submit flag after CTF is over. The incedent will be reported!"
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write(document)


	def do_GET(self):

		reload(config)

		q = urlparse(self.path)
		args = parse_qs(q.query)

		if((q.path.strip("/") == "tasks")):
			document = ""

			if (config.tasks_enabled):
				task_types = os.listdir("./tasks/")
				document += head + (menu % ("", "active", "")) + (title % "TASKS") + hint_top


				if (config.hints_enabled) :
					reload(hints)
					for var_hint in dir(hints):
						if not(var_hint in config.default_modules):
							document += hint % hints.rglobals()[var_hint]
				else:
					document += hints_disabled

				document += hint_bottom
				for i in range(0, len(task_types)):
					document += (task_row_h % task_types[i])
                                        for subdir in filter(lambda x: not '.vdi' in x, os.listdir("./tasks/" + task_types[i])):
						if not (subdir == "index.html"):
							dp = "tasks/" + task_types[i] + '/' + subdir + '/'
							if (os.path.isfile(dp + 'desc')):
								f = open (dp + 'desc', 'r')

								# Select from database. If task is already submitted the mark it with yellow.
								f.readline()
								document += (task_div % ( task_types[i] , subdir,
									"btn-primary", subdir, f.readline().strip('\n')))
								f.close()
					document += task_row_f
				document += div_row_e + footer

			else:
				document += " ARGHHHHHH..... Tasks are closed. "

		elif ((q.path.strip('/') == "") and (args.has_key('t')) and (args.has_key('c')) and os.path.isdir('tasks/' + args['t'][0] + '/' + args['c'][0])):
			f = open ('tasks/' + args['t'][0] + '/' + args['c'][0] + '/desc', 'r')
			o = f.readlines()
			document = head + submit_bar + menu % ("", "active", "") + (title % args['t'][0]) + task_description % ( o[1].strip('\n'),
				o[2].strip('\n'),
				args['t'][0] + '/' + args['c'][0] + '/' + o[0].strip('\n'),
				o[0].strip('\n')
			)

			f.close()

		elif (q.path.strip("/") == "" or q.path.strip("/") == "index" ):
			if (args.has_key('r')):

				if (args['r'][0] == 'success'):
					notice = flag_added
				elif (args['r'][0] == 'fail'):
					notice = flag_declined
				elif (args['r'][0] == 'already_added'):
					notice = flag_already_been_added
				else:
					notice = ""
			else:
				notice = ""

			document = head + notice + (menu % ("active", "", "")) + (title % "HOME")

			document += home
			document += footer

		elif (q.path.strip('/') == "scoreboard"):
			if (config.scoreboard_enabled):

				connection = sql.connect('score.db')
				q = "select team_name, sum(cost) from score group by team_name order by sum(cost) DESC, date;"
				res = connection.execute(q)

				document = head + (menu % ("", "", "active")) + title % "SCOREBOARD" + scoreboard_head
				j = 0
				for row in res:
					j += 1
					document += scoreboard_cell % (j, row[0], row[1])
				document += scoreboard_footer
				# Select from database. Then sum the result for each team
				# time.strftime('%Y-%m-%d %H:%M:%S')
				connection.close()
			else:
				document = "Karim says: \"Stop fapping on the scoreboard !\" "

		else:
			document = head + self.path + footer

		notice = ""

		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(document)

if __name__ == '__main__':
	server_class = BaseHTTPServer.HTTPServer
	httpd = server_class((config.host, config.port), MyHandler)
	print time.asctime(), "Server Starts - %s:%s" % (config.host, config.port)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
	print time.asctime(), "Server Stops - %s:%s" % (config.host, config.port)
