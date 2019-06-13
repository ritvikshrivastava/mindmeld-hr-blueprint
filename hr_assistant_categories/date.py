# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'date' domain in 
the MindMeld HR assistant blueprint application
"""
import os

import requests

from .root import app
from hr_assistant_categories.general import _apply_age_filter
from hr_assistant_categories.general import _agg_function
from hr_assistant_categories.general import _resolve_categorical_entities
from hr_assistant_categories.general import _resolve_function_entity
from hr_assistant_categories.general import _get_names
from dateutil.relativedelta import relativedelta
import datetime
from word2number import w2n
import re

@app.handle(intent='get_date')
def get_date(request, responder):

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

	# Fetch the different types of entities

	func_entities = [e for e in request.entities if e['type'] == 'function']
	
	if func_entities:

		function, responder = _resolve_function_entity(responder, func_entities[0])

		qa, size = _resolve_categorical_entities(request, responder)

		_resolve_time(request, responder, qa, size, func_type='agg', function=function)

	else:
		responder.reply('What time-filtered statistic would you like to know?')
		responder.listen()



@app.handle(intent='get_date_range_employees')
def get_date_range_employees(request, responder):
	# money_entities = [e for e in request.entities if e['type'] == 'money']

	qa, size = _resolve_categorical_entities(request, responder)

	_resolve_time(request, responder, qa, size, func_type='emp')



# Helper functions

def _check_time_ent(time_ent, date_compare_ent):

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


def _filter_by_d_custom(d_type, qa_out, gt=None, gte=None, lt=None, lte=None):
# 
# Filter the output of the Question Answerer by Date
# param d_type (str) Date Type to Filter On: 'doh', 'dob', 'dot'
# param qa_out (list) List of Json Objects Representing Users
# param gt (str) Greater than Start Date in the format 'YYYY-MM-DD'
# param gte (str) Greater than or equal to Start Date in the format 'YYYY-MM-DD'
# param lt (str) Greater than Start Date in the format 'YYYY-MM-DD'
# param lte (str) Greater than or equal to Start Date in the format 'YYYY-MM-DD'
# Return qa_out_filtered (list) List if JSON Objects filtered by Date Type

    # Less than (or equal to)
    if lt is not None:
        lt = _ymd_to_d(lt)
        qa_out = [x for x in qa_out if _ymd_to_d(x[d_type]) < lt]
    elif lte is not None:
        lte = _ymd_to_d(lte)
        qa_out = [x for x in qa_out if _ymd_to_d(x[d_type]) <= lte]
    # Greater than (or equal to)
    if gt is not None:
        gt = _ymd_to_d(gt)
        qa_out = [x for x in qa_out if _ymd_to_d(x[d_type]) > gt]
    elif gte is not None:
        gte = _ymd_to_d(gte)
        qa_out = [x for x in qa_out if _ymd_to_d(x[d_type]) >= gte]
    # Remove "Null" values in DOT that were replaced with "1800-01-01"
    if d_type == 'dot': qa_out = [x for x in qa_out if _ymd_to_d(x[d_type]) > _ymd_to_d("1800-01-01")] 
    return qa_out


def _ymd_to_d(date_str): 
	# Str Date Format Converted to Date object
	# param date_str (str) - String in the Format 'YYYY-MM-DD'
	return datetime.datetime.strptime(date_str, '%Y-%m-%d')


def _resolve_time(request, responder, qa, size, func_type, function='avg'):
	# money_entities = [e for e in request.entities if e['type'] == 'money']
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
		# responder.params.allowed_intents = ['date.get_date_aggregate']
		responder.listen()
		return

	qa_out = qa.execute(size=size)

	# One way to process date aggregate questions can be to filter it on defined time periods
	if time_ent:
		print(time_ent)

		# Check if time entities are in an acceptable format
		time_ent = _check_time_ent(time_ent, date_compare_ent)

		if time_ent == None:
			responder.reply('Please repeat your query with a valid date format (YYYY-MM-DD)')
			responder.listen()
			return

		# Two time entities specify an exact time period to filter
		if len(time_ent)==2:
			# qa = qa.filter(field=field, gte=time_ent[0], lte=time_ent[1])
			qa_out = _filter_by_d_custom(d_type=field, qa_out=qa_out, gte=time_ent[0], lte=time_ent[1])


		# If there is only one time entity specified, then it could be either 
		# the beginning or end of an infinite time period from that date
		elif len(time_ent)==1:
			if date_compare_ent:
				date_compare_canonical = date_compare_ent[0]['value'][0]['cname']
				if date_compare_canonical=='prev':
					# qa = qa.filter(field=field, lte=time_ent[0])
					qa_out = _filter_by_d_custom(d_type=field, qa_out=qa_out, lte=time_ent[0])

				elif date_compare_canonical=='post':
					# qa = qa.filter(field=field, gte=time_ent[0])
					qa_out = _filter_by_d_custom(d_type=field, qa_out=qa_out, gte=time_ent[0])

			else:
				# qa = qa.filter(field=field, gte=time_ent[0], lte=time_ent[0])
				qa_out = _filter_by_d_custom(d_type=field, qa_out=qa_out, lte=time_ent[0], gte=time_ent[0])

	else:
		responder.reply('Please repeat your query with a valid date format (YYYY-MM-DD)')
		responder.listen()
		return


# if function not in ('avg','sum'):
# 	# qa_out = qa.execute(size=size)
# 	responder.slots['value'] = _agg_function(qa_out, func=function)
# 	responder.reply('The {function} is {value}')
# else:
# 	responder.reply('What would you like to know the {function} of?')
# 	responder.listen()


	if func_type=='agg':	
		responder.slots['value'] = _agg_function(qa_out, func=function)
		responder.reply('The {function} is {value}')

	else:
		responder.slots['emp_list'] = _get_names(qa_out)
		responder.reply('Here\'s some employees: {emp_list}')