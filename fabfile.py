#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from fabfile_common import *

try:
	from fabfile_hosts import *
except ImportError:
	pass


env.supervisor_conf_path = '/etc/supervisord.conf.d/'
env.supervisor_uid = 'winvoice'
env.supervisor_pwd = 'winvoice'


def compile(path, name):
	with cd(path):
		run('pyinstaller %s.spec' % name)


def compile_all():
	stop_all()
	compile('/chat_server', 'chat_server')
	compile('/wx_server', 'upload_server')
	compile('/wx_server', 'wx_server')
	start_all()


def download(path, name, dst_path):
	with cd(path):
		src = '%s/dist/%s' % (path, name)
		dst = '%s/%s' % (dst_path, name)
		get(src, dst)


def download_all():
	download('/chat_server', 'chat_server', 'r:/dist')
	download('/wx_server', 'upload_server', 'r:/dist')
	download('/wx_server', 'wx_server', 'r:/dist')


def deploy_cdrmonitor(jar_file):
	name = 'cdrmonitor'
	abs_jarfile = os.path.abspath(jar_file)
	jar_path, jar_file = os.path.split(abs_jarfile)
	supervisor_conf_file = '%s.supervisor.conf' % name
	if not exists(env.supervisor_conf_path + supervisor_conf_file):
		put(supervisor_conf_file, env.supervisor_conf_path)
	deploy_path = '/home/%s' % name
	if not exists(deploy_path):
		run('mkdir %s' % deploy_path)
	with cd(deploy_path):
		put(abs_jarfile, jar_file)
		run('ln -sf %s %s.jar' % (jar_file, name))
		supervisor_restart(name)


def deploy_chat_server():
	deploy_server('chat_server')


def deploy_upload_server():
	deploy_server('upload_server')


def deploy_wx_server():
	deploy_server('wx_server')


def deploy_server(name):
	deploy_path = '/home/%s' % name
	if not exists(deploy_path):
		run('mkdir %s' % deploy_path)
	with lcd(name):
		supervisor_conf_file = '%s.supervisor.conf' % name
		if not exists(env.supervisor_conf_path + supervisor_conf_file):
			put(supervisor_conf_file, env.supervisor_conf_path)
		with cd(deploy_path):
			put('*', '.')
			run('chmod +x %s' % name)


def supervisor_reload():
# 	run('''python -c "import os
# pid = os.popen('pgrep supervisord').read()
# print 'pid=%s' % pid
# os.popen('kill -HUP %s' % pid)"''')
	run('supervisorctl reload')


def supervisor_start(name):
	run('supervisorctl -u%s -p%s start %s' % (env.supervisor_uid, env.supervisor_pwd, name))


def supervisor_stop(name):
	run('supervisorctl -u%s -p%s stop %s' % (env.supervisor_uid, env.supervisor_pwd, name))


def supervisor_restart(name):
	run('supervisorctl -u%s -p%s restart %s' % (env.supervisor_uid, env.supervisor_pwd, name))


def start_all():
	run('supervisorctl start all')


def stop_all():
	run('supervisorctl stop all')



'''
def front_deploy():
	"""前端代码部署"""
	env.host_string = config.HOST_STRING
	with cd('/var/www/tuomeng'):
		run('git reset --hard HEAD')
		run('git pull -f')


def back_deploy():
	"""前后端代码部署"""
	env.host_string = config.HOST_STRING
	with cd('/var/www/tuomeng'):
		run('git reset --hard HEAD')
		run('git pull -f')
		with prefix('source venv/bin/activate'):
			run('pip install -r requirements.txt')
		run('supervisorctl restart tuomeng')


def restart():
	"""重启服务器"""
	env.host_string = config.HOST_STRING
	run('supervisorctl restart tuomeng')
'''
