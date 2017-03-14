'''
Created on Nov 30, 2016

@author: julimatt
'''
#this is a test file to check uwsgi and can be deleted without affecting zibawa


def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    return [b"Hello World"] # python3
    #return ["Hello World"] # python2