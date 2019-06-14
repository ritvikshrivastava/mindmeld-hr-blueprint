# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'date' domain in
the MindMeld HR assistant blueprint application
"""
import os
import requests
from .root import app
from hr_assistant.general import _resolve_categorical_entities, _resolve_function_entity, _resolve_extremes, _agg_function, _get_names, _get_person_info, _fetch_from_kb
from dateutil.relativedelta import relativedelta
import datetime
import re



@app.handle(intent='get_date')
def get_date(request, responder):
	"""
	If a user asks for a date related information of any person, this function returns 
	the required date. In case of a termination date related query, it also informs the user 
	of the reason for termination. For non-terminated employees, it informs the user about 
	the active current state of the employee in question.
	"""

	name_ent = [e for e in request.entities if e['type'] == 'name']
	name = name_ent[0]['value'][0]['cname']
	responder.slots['name'] = name

	employee = app.question_answerer.get(index='user_data', emp_name=name)[0]

	action_entity = [e['value'][0]['cname'] for e in request.entities if e['type'] == 'employment_action']
	dob_entity = [e for e in request.entities if e['type'] == 'dob']

	if action_entity:
		action_entity = action_entity[0]

		if action_entity=='hired':
			date = employee['doh']
			responder.slots['date'] = date
			responder.reply("{name}'s date of hire was {date}")

		elif action_entity=='fired':
			date = employee['dot']
			responder.slots['date'] = date
			responder.slots['reason'] = employee['rft']
			if responder.slots['reason'] == 'N/A - still employed':
				responder.reply("{name} is still employed.")
			else:
				responder.reply("{name}'s date of termination was {date}. The reason for termination was: {reason}.")

	elif dob_entity:
		date = employee['dob']
		responder.reply("{name}'s date of birth is {date}")

	else:
		responder.reply('What would you like to know about {name}? You can ask about date of hire, date of termination or date of birth.')
		responder.listen()



@app.handle(intent='get_date_range_aggregate')
def get_date_range_aggregate(request, responder):
	"""
	When a user asks for a statistic, such as average, sum, count or percentage,
	in addition to a date range filter such as date of hire, termination or birth (required), 
	and categorical filters (if any), this function captures all the relevant entities, 
	calculates the desired statistic function and returns it.
	"""

	# Checks for existing function entity from previous turn
	func_entity = request.frame.get('function')

	# If the user provides a new function entity, it replaces the one in context from previous turns
	func_entities = [e for e in request.entities if e['type'] == 'function']

	if func_entities:
		func_entity = func_entities[0]

	if func_entity:
		function, responder = _resolve_function_entity(responder, func_entity)

		function, responder = _resolve_function_entity(responder, func_entities[0])

		qa, size = _resolve_categorical_entities(request, responder)

		qa_out = _resolve_time(request, responder, qa, size)

		responder.slots['value'] = _agg_function(qa_out, func=function)
		responder.reply('The {function} is {value}')

	else:
		responder.reply('What time-filtered statistic would you like to know?')
		responder.listen()



@app.handle(intent='get_date_range_employees')
def get_date_range_employees(request, responder):
	"""
	When a user asks for a list of employees that satisfy certain criteria in addition
	to satisfying a specified date range criterion (date of hire/termination/birth), 
	this dialogue state filters the knowledge base on those criteria and returns the 
	shortlisted list of names.
	"""

	qa, size = _resolve_categorical_entities(request, responder)

	qa_out = _resolve_time(request, responder, qa, size)

	responder.slots['emp_list'] = _get_names(qa_out)
	responder.reply("Here's some employees: {emp_list}")



### Helper functions ###

def _check_time_ent(time_ent, date_compare_ent):
	"""
	Helper function for resolving non numeric time entities, time entities with
	incompatible date formats, and intervals into the format of time that is 
	accepted by the dialogue states defined in this file.
	"""

	time_dict = {}
	time_dict.update(dict.fromkeys(['last year', 'this year', 'past year'], 'years'))
	time_dict.update(dict.fromkeys(['last month', 'this month', 'past month'], 'months'))
	time_dict.update(dict.fromkeys(['last week', 'this week', 'past week'], 'weeks'))

	for i in range(len(time_ent)):
		if time_ent[i] in ('last year', 'last month', 'last week', 'past year', 'past week', 'past month', 'this year', 'this week', 'this month'):
			d = datetime.datetime.today()
			kw = {time_dict[time_ent[i]] : 1}
			old_d = d-relativedelta(**kw)
			d = d.strftime('%Y-%m-%d')
			old_d = old_d.strftime('%Y-%m-%d')
			time_ent[i] = old_d
			time_ent.append(d)

		elif len(time_ent[i].split('-'))==3:
			continue

		elif len(re.split('-|\\|/', time_ent[i]))==1:
			try:
				if date_compare_ent:
					time_ent[i] = str(time_ent[i])+'-01-01'
				else:
					time_old = str(time_ent[i])
					time_ent[i] = time_old+'-01-01'
					time_ent.append(time_old+'-12-31')
			except:
				return None
				break
		else:
			return None
			break

	return time_ent


def _resolve_time(request, responder, qa, size):
	"""
	This helper function is useful to resolve any time related entities in the database, including
	both system entities and custom entities. It captures the type of date entity being talked about by
	the user (say employment related -- hired/fired, or birth). It in-turn determines the time period
	being talked about and filters the knowledge to narrow it down to only the datapoints satisfying
	the duration. The returned value is this shortlisted set of employees.
	"""

	time_ent = [e['text'] for e in request.entities if e['type'] == 'sys_time']
	dur_ent = [e['text'] for e in request.entities if e['type'] == 'sys_duration']
	date_compare_ent = [e for e in request.entities if e['type'] == 'date_compare']
	time_interval = [e for e in request.entities if e['type'] == 'time_interval']
	action_entity = [e['value'][0]['cname'] for e in request.entities if e['type'] == 'employment_action']
	dob_entity = [e for e in request.entities if e['type'] == 'dob']

	if action_entity:
		action_entity = action_entity[0]
		if action_entity=='hired':
			field = 'doh'
		elif action_entity=='fired':
			field = 'dot'
	elif dob_entity:
		field = 'dob'
	else:
		responder.reply("What date would you like to know the statistic about? Hire, termination or birth?")
		responder.listen()
		return

	# One way to process date aggregate questions can be to filter it on defined time periods
	if time_ent:

		# Check if time entities are in an acceptable format
		time_ent = _check_time_ent(time_ent, date_compare_ent)

		if time_ent == None:
			responder.reply('Please repeat your query with a valid date format (YYYY-MM-DD)')
			responder.listen()
			return

		# Two time entities specify an exact time period to filter
		if len(time_ent)==2:
			qa = qa.filter(field=field, gte=time_ent[0], lte=time_ent[1])


		# If there is only one time entity specified, then it could be either
		# the beginning or end of an infinite time period from that date
		elif len(time_ent)==1:
			if date_compare_ent:
				date_compare_canonical = date_compare_ent[0]['value'][0]['cname']

				if date_compare_canonical=='prev':
					qa = qa.filter(field=field, lte=time_ent[0])

				elif date_compare_canonical=='post':
					qa = qa.filter(field=field, gte=time_ent[0])

			else:
				qa = qa.filter(field=field, gte=time_ent[0], lte=time_ent[0])

		qa_out = qa.execute(size=size)

	else:
		responder.reply('Please repeat your query with a valid date format (YYYY-MM-DD)')
		responder.listen()
		return

	return qa_out
