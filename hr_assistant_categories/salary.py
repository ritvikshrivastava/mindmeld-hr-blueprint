# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'salary' domain in 
the MindMeld HR assistant blueprint application
"""
import os

import requests

from .root import app
from .exceptions import UnitNotFound


@app.handle(intent='get_salary')
def get_salary(request, responder):

	name_ent = [e for e in request.entities if e['type'] == 'name']
	name = name_ent[0]['value'][0]['cname']

	employee = app.question_answerer.get(index='user_data', emp_name=name)[0]
	money = employee['money']

	responder.slots['name'] = name
	responder.slots['money'] = money
	
	responder.reply("{name}'s hourly salary is {money}")


@app.handle(intent='get_salary', entity='time_recur')
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


	if func_entities:

		func_entity = func_entity[0]
		func_dic = {'percent':'pct', 'sum':'sum', 'average':'avg', 'count':'ct'}

		## mapping text entry's canonical entity form using the function dictionary
		function = func_dic.get(func_entity['value'][0]['cname'], default='avg') 

		categorical_entity = [e for e in request.entities if e['type'] in ('state', 'age', 'sex', 'maritaldesc','citizendesc',
			'racedesc','performance_score','employment_status','employee_source','position','department')][0]

		qa = app.question_answerer.build_search(index='user_data')
		qa = qa.query(categorical_entity['type']=categorical_entity['text'])
		responder.slots['function'] = func_entity['value'][0]['cname']

		if money_entities:
			qa, size = _apply_money_filter(qa, money_entities, request, responder)
			qa_out = qa.execute(size=size)
			responder.slots['value'] = _agg_function(qa_out, func=function, num_col='money')

		elif func_entity not in ('avg','sum'):
			qa_out = qa.execute()
			responder.slots['value'] = _agg_function(qa_out, func=function)

		else:
			responder.reply('What would you like to know the {function} of?')
			responder.listen()

	else:
		responder.reply('What salary statistic would you like to know?')
		responder.listen()