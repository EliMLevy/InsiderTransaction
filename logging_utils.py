# Taken from https://gist.github.com/nguyenkims/e92df0f8bd49973f0c94bddf36ed7fd0
import logging
import sys
from logging import FileHandler

FORMATTER = logging.Formatter("%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s")

def get_console_handler():
	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setFormatter(FORMATTER)
	return console_handler

def get_file_handler(filename):
	file_handler = FileHandler(filename,  mode='w')
	file_handler.setFormatter(FORMATTER)
	return file_handler

def get_logger(logger_name, filename):
	logger = logging.getLogger(logger_name)

	logger.setLevel(logging.DEBUG) # better to have too much log than not enough

	logger.addHandler(get_console_handler())
	logger.addHandler(get_file_handler("logs/" + filename))

	# with this pattern, it's rarely necessary to propagate the error up to parent
	logger.propagate = False

	return logger