# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'salary' domain in 
the MindMeld HR assistant blueprint application
"""
import os

import requests

from .root import app
# from .exceptions import UnitNotFound
from hr_assistant_categories.general import _apply_age_filter
from hr_assistant_categories.general import _agg_function


@app.handle(intent='get_salary')
def get_salary(request, responder):

	name_ent = [e for e in request.entities if e['type'] == 'name']
	name = name_ent[0]['value'][0]['cname']

	employee = app.question_answerer.get(index='user_data', emp_name=name)[0]
	money = employee['money']

	responder.slots['name'] = name
	responder.slots['money'] = money
	
	responder.reply("{name}'s hourly salary is {money}")


@app.handle(intent='get_salary', has_entity='time_recur')
def get_salary_for_interval(request, responder):

	name_ent = [e for e in request.entities if e['type'] == 'name']
	name = name_ent[0]['value'][0]['cname']

	recur_ent = [e for e in request.entities if e['type'] == 'time_recur'][0]['value'][0]['cname']

	employee = app.question_answerer.get(index='user_data', emp_name=name)[0]
	money = employee['money']

	total_money, interval = _get_interval_amount(recur_ent, money)

	responder.slots['name'] = name
	responder.slots['money'] = total_money
	responder.slots['interval'] = interval
	
	responder.reply("{name}'s {interval} salary is {money}")


# @app.handle(intent='get_salary_aggregate', entity='comparator')
# def get_salary_aggregate_with_age(request, responder):
# 	comparator_entities = [e for e in request.entities if e['type'] == 'comparator']
# 	responder.frame['comparator'] = comparator_entities


@app.handle(intent='get_salary_aggregate')
def get_salary_aggregate(request, responder):

	func_entities = [e for e in request.entities if e['type'] == 'function']
	money_entities = [e for e in request.entities if e['type'] == 'money']
	# age_entities = [e for e in request.entities if e['type'] == 'age']


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

		
		categorical_entities = [e for e in request.entities if e['type'] in ('state', 'sex', 'age', 'maritaldesc','citizendesc',
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
		# 	responder.slots['value'] = _agg_function(qa_out, func=function, num_col='age')
		# 	responder.reply('The {function} age is {value}')

		if money_entities:
			qa, size = _apply_money_filter(qa, money_entities, request, responder)
			qa_out = qa.execute(size=size)
			responder.slots['value'] = _agg_function(qa_out, func=function, num_col='money')
			responder.reply('The {function} salary is {value}')

		elif func_entity not in ('avg','sum'):
			qa_out = qa.execute()
			responder.slots['value'] = _agg_function(qa_out, func=function)
			responder.reply('The {function} salary is {value}')

		else:
			responder.reply('What would you like to know the {function} of?')
			responder.listen()

	else:
		responder.reply('What salary statistic would you like to know?')
		responder.listen()



@app.handle(intent='get_salary_employees')
def get_salary_employees(request, responder):
	money_entities = [e for e in request.entities if e['type'] == 'money']

	categorical_entities = [e for e in request.entities if e['type'] in ('state', 'sex', 'age', 'maritaldesc','citizendesc',
		'racedesc','performance_score','employment_status','employee_source','position','department')]

	qa = app.question_answerer.build_search(index='user_data')

	if categorical_entities:
		for categorical_entity in categorical_entities:
			key = categorical_entity['type']
			val = categorical_entity['value'][0]['cname']
			kw = {key : val}
			qa = qa.query(**kw)
	size = 300

	if age_entities:
		qa, size = _apply_money_filter(qa, money_entities,request, responder)
		# size = 1

	qa_out = qa.execute(size=size)
	responder.slots['emp_list'] = _get_names(qa_out)
	responder.reply('Here\'s some employees: {emp_list}')



# Helper functions

def _apply_money_filter(qa, age_entities, request, responder):

	num_entity = [int(e['text']) for e in request.entities if e['type'] == 'sys_number'] 

	try:
		comparator_entity = [e for e in request.entities if e['type'] == 'comparator'][0]
	except:
		comparator_entity = []


	try:
		extreme_entity = [e for e in request.entities if e['type'] == 'extreme'][0]
	except:
		extreme_entity = []


	filter_set = False

	# The money entity can have either be accompanied by a comparator, extreme or no entity. 
	# These are mutually exclusive of others and hence can only be queried separately from
	# the knowledge base.

	if comparator_entity:
		comparator_canonical = comparator_entity['value'][0]['cname']

		if comparator_canonical == 'more than':
			gte_val = num_entity[0]['text']
			lte_val = 100
			# filter_set = True

		elif comparator_canonical == 'less than':
			lte_val = num_entity[0]['text']
			gte_val = 0
			# filter_set = True

		elif comparator_canonical == 'equals to':
			gte_val = num_entity[0]['text']
			lte_val = num_entity[0]['text']

		elif len(num_entity)>1:
			gte_val = np.min(num_entity)
			lte_val = np.max(num_entity)
		
		qa = qa.filter(field='money', gte=gte, lte=lte_val).execute()
		size = 300


	elif extreme_entity:
		extreme_canonical = extreme_entity['value'][0]['cname']

		if extreme_canonical == 'highest':
			qa = qa.sort(field='money', sort_type='desc')
		
		elif extreme_canonical == 'lowest':
			qa = qa.sort(field='money', sort_type='desc')
		
		if num_entity:
			size = num_entity[0]
		else:
			size = 1


	elif len(num_entity)>=1:
		qa = qa.filter(filter='money', gte=np.min(num_entity), lte=np.max(num_entity))
		size = 300

	else:
		size = 300

	return qa, size