#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fabric.api import run, env, lcd, cd, prefix, settings, get, put
from fabric.contrib.files import exists


def host_type():
	run('uname -s')


def get_python_version():
	ret = run('python -V')	# Python 2.7.11
	return str(ret)


def upgrade_python():
	py_ver = get_python_version().split()[-1][:3]
	print 'remote python version: %s' % py_ver
	if py_ver < "2.7":
		run('yum install openssl* -y')
		run('yum install sqlite-devel -y')
		run('yum install rlwrap readline readline-devel -y')
		run('yum install ncurses-devel -y')
		with cd('/tmp'):
			if not exists('Python-2.7.11'):
				run('wget https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tgz')
				run('tar xzvf Python-2.7.11.tgz')
			with cd('Python-2.7.11'):
				with settings(warn_only=True):
					run('make clean')
					run('make distclean')
				run('./configure --enable-shared')
				run('make')
				run('make install')
				run('make clean')
				run('make distclean')
				run('echo /usr/local/lib >> /etc/ld.so.conf')
				run('ldconfig -v')
			# backup old python
			#run('mv /usr/bin/python /usr/bin/python%s' % py_ver)
			#update_yum_interpreter()

			install_setup_tools()
			install_pip()


def install_setup_tools():
	ver = '20.7.0'
	with cd('/tmp'):
		if not exists('setuptools-%s' % ver):
			run('wget --no-check-certificate https://pypi.python.org/packages/source/s/setuptools/setuptools-%s.zip' % ver)
			run('unzip setuptools-%s.zip' % ver)
		with cd('setuptools-%s' % ver):
			run('python setup.py install')


def install_pip():
	pip_ver = '8.1.1'
	with cd('/tmp'):
		if not exists('pip-%s' % pip_ver):
			run('wget --no-check-certificate https://pypi.python.org/packages/source/p/pip/pip-%s.tar.gz' % pip_ver)
			run('tar xzvf pip-%s.tar.gz' % pip_ver)
		with cd('pip-%s' % pip_ver):
			run('python setup.py install')
		# upgrade
		run('pip install pip --upgrade')


def update_yum_interpreter():
	lines = '''lines = open('/usr/bin/yum').read().split('\\n')
new_interpreter = '#!/usr/bin/python2.4'
print '%s -> %s' % (lines[0], new_interpreter)
lines[0] = new_interpreter
s = '\\n'.join(lines)
open('/usr/bin/yum', 'w').write(s)
'''
	code = ';'.join(lines.split('\n'))
	run('python -c "%s"' % code)


def install_cxOracle():
	src_dir = 'F:\Software\Development\Database\Oracle'
	run('yum install libaio')
	with cd('/tmp'):
		if not exists('oracle-instantclient11.2-basic-11.2.0.4.0-1.x86_64.rpm'):
			put('%s/oracle-instantclient11.2-basic-11.2.0.4.0-1.x86_64.rpm' % src_dir, '.')
		put('%s/oracle-instantclient11.2-devel-11.2.0.4.0-1.x86_64.rpm' % src_dir, '.')
		run('rpm -ivh oracle-instantclient11.2-basic-11.2.0.4.0-1.x86_64.rpm')
		run('rpm -ivh oracle-instantclient11.2-devel-11.2.0.4.0-1.x86_64.rpm')
		run('echo /usr/lib/oracle/11.2/client64/lib/ >> /etc/ld.so.conf')
		run('ldconfig')


def install_git():
	git_ver = '2.8.1'
	run('yum install curl curl-devel zlib-devel openssl-devel perl cpio expat-devel gettext-devel -y')
	with cd('/tmp'):
		if not exists('git-%s' % git_ver):
			run('wget --no-check-certificate https://www.kernel.org/pub/software/scm/git/git-2.8.1.tar.gz')
			run('tar zxvf git-%s.tar.gz' % git_ver)
		with cd('git-%s' % git_ver):
			run('autoconf')
			run('./configure')
			run('make')
			run('make install')


def install_supervisor():
	run('pip install supervisor')
	#run('echo_supervisord_conf > /etc/supervisord.conf')
	if not exists('/logs'):
		run('mkdir /logs')
	put('supervisord.conf', '/etc/supervisord.conf')
