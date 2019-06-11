# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'date' domain in 
the MindMeld HR assistant blueprint application
"""
import os

import requests

from .root import app
from hr_assistant_categories.general import _apply_age_filter
from hr_assistant_categories.general import _agg_function
from hr_assistant_categories.general import _categ_filter


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
	
	

@app.handle(intent='get_date_aggregate', has_entity='date_time')
def get_date_aggregate(request, responder):

	func_entities = [e for e in request.entities if e['type'] == 'function']
	money_entities = [e for e in request.entities if e['type'] == 'money']
	time_entities = [e for e in request.entities if e['type'] == 'sys_time']

	date_type_map = {'date of hire':'doh', 'date of termination':'dot', 'dob':'dob'}
	date_entity = date_type_map[[e['value'][0]['cname'] for e in request.entities if e['type'] == 'date_time'][0]]

	if func_entities:

		func_entity = func_entities[0]
		func_dic = {'percent':'pct', 'sum':'sum', 'average':'avg', 'count':'ct'}

		## mapping text entry's canonical entity form using the function dictionary
		key = func_entity['value'][0]['cname']
		print(key)
		# function = func_dic.get(key, default='avg') 
		function = func_dic[key]
		responder.slots['function'] = func_entity['value'][0]['cname']

		qa = app.question_answerer.build_search(index='user_data')

		
		categorical_entities = [e for e in request.entities if e['type'] in ('state', 'sex', 'maritaldesc','citizendesc',
			'racedesc','performance_score','employment_status','employee_source','position','department')]

		if categorical_entities:
			for categorical_entity in categorical_entities:
				key = categorical_entity[0]['type']
				val = categorical_entity[0]['value'][0]['cname']
				kw = {key : val}
				qa = qa.query(**kw)

		# if age_entities:
		# 	qa, size = _apply_age_filter(qa, age_entities, request, responder)
		# 	qa_out = qa.execute(size=size)

		if time_entities:
			qa = qa_out.execute(size=300)

		# if age_entities:	
		# 	responder.slots['value'] = _agg_function(qa_out, func=function, num_col='age')
		# 	responder.reply('The {function} age is {value}')

		if func_entity not in ('avg','sum'):
			qa_out = qa.execute()
			responder.slots['value'] = _agg_function(qa_out, func=function)
			responder.reply('The {function} is {value}')

		else:
			responder.reply('What would you like to know the {function} of?')
			responder.listen()

	else:
		responder.reply('What salary statistic would you like to know?')
		responder.listen()




# Helper functions


def _filter_by_d_custom(d_type, qa_out, gt, gte, lt, lte):
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
	return datetime.strptime(date_str, '%Y-%m-%d')