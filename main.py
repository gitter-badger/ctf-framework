#!/usr/bin/python2

import os
import sys
import time
import hints
import loader
import config
import logging
import BaseHTTPServer

import sqlite3 as sql

from snippets import *
from urlparse import urlparse, parse_qs

ttypes = loader.load_task_types()

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def tasks(self):
        if (not config.tasks_enabled):
            return 'ARGHHHHHH..... Tasks are closed.'

        document = ''

        document += self.fhead('TASKS') + self.fhints()

        for ttype in range(len(ttypes)):
            document += (task_row_h % task_types[i])
            for subdir in loader.task_types:
                dp = '/'.join(['tasks', task_types[i], subdir, 'desc'])
                if (os.path.isfile(dp)):
                    with open (dp, 'r') as f:
                        f.readline()
                        document += (task_div % (
                                        task_types[i],
                                        subdir,
                                        'btn-primary',
                                        subdir,
                                        f.readline().strip('\n')
                                        )
                                    )
                document += task_row_f
        return document + div_row_e + footer

    def ftitle(self, var_title):
        return {
            'HOME': ('active', '', ''),
            'TASKS': ('', 'active', ''),
            'SCOREBOARD': ('', '', 'active'),
        }[var_title]

    def fhead(self, var_title):
        return '\n'.join([head, (menu % self.ftitle(var_title)), (title % var_title)])

    def not_base_mod(self, module):
        if (module in config.base_modules):
            return False
        return True

    def fhints(self):
        if (not config.hints_enabled):
            return hints_disabled

        rhint = hint_top

        if (config.hints_enabled) :
            reload(hints)
            for var_hint in filter(self.not_base_mod,  dir(hints)):  
                rhint += snipp_hint % hints.rglobals()[var_hint]
        return rhint + hint_bottom


    def index(self, q, args):

        if ((q.path.strip('/') == "") and
                (args.has_key('t')) and 
                (args.has_key('c')) and 
                os.path.isdir( '/'.join(['tasks', args['t'][0],  args['c'][0]]))):
                    return self.taskHandler()

        return self.fhead('HOME') + home + footer

    def taskHandler (self):
        with open ( '/'.join( ['tasks', args['t'][0], args['c'][0], 'desc' ] ), 'r') as f:
                return '\n'.join( [head,    submit_bar,
                                    menu % ('', 'active', ''), (title % args['t'][0]), 
                                    task_description.format( f.readline().strip('\n'),
                                        f.readline().strip('\n'),
                                        f.readline().strip('\n'),
                                        host_ip,
                                        tasks_port,
                                        '/'.join([args['t'][0], args['c'][0]]))]
                                    )
    def scoreboard (self):
        if (not config.scoreboard_enabled):
            return 'Karim says: \'Stop fapping on the scoreboard !\' '

        connection = sql.connect('score.db')
        q = 'select team_name, sum(cost) from score group by team_name order by sum(cost) DESC, date;'
        res = connection.execute(q)

        document = self.fhead('SCOREBOARD') + scoreboard_head
        j = 0
        for row in res:
            j += 1
            document += scoreboard_cell % (j, row[0], row[1])
            
        connection.close()
        return document +scoreboard_footer
        

    
    def do_POST(self):
        if (config.tasks_enabled):
            q = urlparse(self.path)
            args = parse_qs(q.query)

            length = int(self.headers.getheader('content-length'))
            postvars = parse_qs(self.rfile.read(length))

            if (postvars.has_key('team_name') and postvars.has_key('flag')):
                with open ('/'. join(['tasks/', args['t'][0],args['c'][0], 'desc']), 'r') as f:
                    o = f.readlines()
                    self.send_response(301)

                    connection = sql.connect('score.db')
                    q = "select team_name from score where flag = \'%s\' and team_name = \'%s\';"
                    res = connection.execute(q % (postvars['flag'][0], postvars['team_name'][0]))
                    for row in res:
                        if (row):
                            self.send_header('Location', 'index?r=already_added')
                            break
                    else:
                        if(o[3].strip('\n') == postvars['flag'][0]):
                            q = 'insert into score values (\'%s\', \'%s\', %s, \'%s\');'
                            connection.execute(q % (postvars['team_name'][0],
                                postvars['flag'][0],
                                args['c'][0],
                                time.strftime('%Y-%m-%d %H:%M:%S'))
                                                )
                            connection.commit()
                            
                            self.send_header('Location', 'index?r=success')
                        else:
                            self.send_header('Location', 'index?r=fail')

                    connection.close()

                self.end_headers()

            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
        else:
            document = 'You are trying to submit flag after CTF is over. The incedent will be reported!'
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(document)

    notice = ""

    def do_GET(self):
        reload(config)

        q = urlparse(self.path)
        args = parse_qs(q.query)

        try:
            document = {
                'tasks': self.tasks(),
                '': self.index(q, args),
                'index': self.index(q, args),
                'scoreboard': self.scoreboard()
            }[q.path.strip('/')]
        except:
            document = '404'
            print q.path.strip('/')

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
