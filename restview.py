import os, errno

from django.core.management.base import copy_helper, CommandError, LabelCommand
from django.utils.importlib import import_module

class Command(LabelCommand):
	help = "Creates a RESTful view to build upon given app name in the current directory."
	args = "[appname]"
	label = 'application name'

	requires_model_validation = False
	# Can't import settings during this command, because they haven't
	# necessarily been created.
	can_import_settings = False


	def handle_label(self, app_name, directory=None, **options):
		if directory is None:
			directory = os.getcwd()

		# Determine the project_name by using the basename of directory,
		# which should be the full path of the project directory (or the
		# current directory if no directory was passed).
		project_name = os.path.basename(directory)

		# Check that the app_name cannot be imported.
		try:
			import_module(app_name)
		except ImportError:
			raise CommandError("%r doesn't exist. Are you sure you are trying to build a RESTful view for an application that exists?", app_name)            

		f = open(directory + "/" + app_name + "/views.py", 'w')
		f.write('from django.template import Context, loader\nfrom django.shortcuts import render_to_response\nfrom django.http import HttpResponse\n\n')
		templatedir = directory + "/templates/" + app_name
		try:
			os.makedirs(templatedir)
		except OSError, exc:
			if exc.errno == errno.EEXIST:
				pass
			else:
				raise

		actions = ['index','new','create','edit','update','destroy','show']
		for action in actions:
			arg_vars = "request"
			if action=='show' or action=='edit':
				arg_vars += ", id"
			f.write('def ' + action + '(' + arg_vars + '):\n')
			f.write('\tvars = \'\'\n')
			f.write('\treturn render_to_response("' + app_name + '/' + action + '.html", {\'vars\': vars})\n\n')
			templ = open(directory + "/templates/" + app_name + '/' + action + '.html','w')
			templ.write("<h1>" + app_name + ":" + action + " view</h1>")
			templ.close()
		f.close()
		#copy_helper(self.style, 'app', app_name, directory, project_name)

class ProjectCommand(Command):
	help = ("Creates a Django app directory structure for the given app name in this project's directory.")

	def __init__(self, project_directory):
		super(ProjectCommand, self).__init__()
		self.project_directory = project_directory

	def handle_label(self, app_name, **options):
		super(ProjectCommand, self).handle_label(app_name, self.project_directory, **options)
