import calendar
import os.path
import time

import flask
from flask import Blueprint
from flask import g

import react.jsx

def JSXBlueprint(app):
	blueprint = Blueprint("jsx", __name__)
	
	@blueprint.route("/js/<path:path>")
	def js(path):
		path = os.path.normpath(path)
		if path.startswith("../"):
			flask.abort(404)
		
		# Unprocessed .js files
		inputPath = app.config["Path"] + "/static/js/" + path
		if os.path.isfile(inputPath):
			return flask.send_file(inputPath, conditional = True)
		
		# Unprocessed .jsx files
		inputPath = app.config["Path"] + "/static/jsx/" + path
		if os.path.isfile(inputPath):
			response = flask.send_file(inputPath, conditional = True)
			response.content_type = "application/javascript"
			return response
		
		# Processed .jsx files
		inputPath = app.config["Path"] + "/static/jsx/" + path + "x"
		outputPath = app.config["Path"] + "/data/js/" + path
		if os.path.isfile(inputPath):
			lastModificationTime = int(os.path.getmtime(inputPath))
			cachedModificationTime = None
			
			# Cached modification time
			if flask.request.if_modified_since is not None:
				cachedModificationTime = int(calendar.timegm(flask.request.if_modified_since.timetuple()))
			
			# HTTP 304
			if lastModificationTime == cachedModificationTime:
				response = flask.make_response()
				response.status_code = 304
				return response
			
			# Regenerate if no processed copy exists
			# or the cached version is out of date
			if not os.path.exists(outputPath) or cachedModificationTime is not None:
				# Delete existing processed copy, so if this fails we don't continue serving
				# an out of date version
				os.remove(outputPath)
				
				# Create output directory
				outputDirectory = os.path.dirname(outputPath)
				if not os.path.exists(outputDirectory):
					os.makedirs(outputDirectory)
				
				# Transform
				react.jsx.transform(inputPath, js_path = outputPath)
			
			# Serve
			response = flask.send_file(outputPath, conditional = True)
			response.last_modified = lastModificationTime
			return response
		
		flask.abort(404)
		
	return blueprint
