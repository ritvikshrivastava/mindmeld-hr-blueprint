# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'salary' domain in 
the MindMeld HR assistant blueprint application
"""
import os
import requests
from .root import app
from hr_assistant.general import _resolve_categorical_entities, _resolve_function_entity, _resolve_extremes, _agg_function, _get_names, _get_person_info, _fetch_from_kb
import numpy as np



@app.handle(intent='get_salary')
def get_salary(request, responder):
	"""
	If a user asks for the salary of a specific person, this function returns their
	hourly salary by querying into the knowledge base according to the employee name.
	"""

	responder = _get_person_info(request, responder, 'money')
	responder.reply("{name}'s hourly salary is {money}")


@app.handle(intent='get_salary', has_entity='time_recur')
def get_salary_for_interval(request, responder):
	"""
	If a user asks for the salary of a specific person for a given time interval (say hourly,
	daily, weekly, monthly, yearly; default = hourly), this dialogue state fetches the hourly
	salary from the knowledge base and returns it after converting it to the requested
	time interval.
	"""
	
	recur_ent = [e['value'][0]['cname'] for e in request.entities if e['type'] == 'time_recur'][0]

	responder = _get_person_info(request, responder, 'money')
	money = responder.slots['money']
	total_money = _get_interval_amount(recur_ent, money)
	
	responder.slots['money'] = total_money
	responder.slots['interval'] = recur_ent
	
	responder.reply("{name}'s {interval} salary is {money}")


@app.handle(intent='get_salary_aggregate')
def get_salary_aggregate(request, responder):
	"""
	When a user asks for a statistic, such as average, sum, count or percentage,
	in addition to an income related filter (required) and categorical filters (if any), 
	this function captures all the relevant entities, calculates the desired 
	statistic function and returns it.
	"""

	func_entities = [e for e in request.entities if e['type'] == 'function']
	money_entities = [e for e in request.entities if e['type'] == 'money']
	recur_ent = [e['value'][0]['cname'] for e in request.entities if e['type'] == 'time_recur']

	salary_response = "Hmm, looks like you want a salary statistic. You can ask me about averages, sums, counts and percentages. For eg. what is the average salary for women?" 

	if func_entities:

		function, responder = _resolve_function_entity(responder, func_entities[0])

		qa, size = _resolve_categorical_entities(request, responder)

		if money_entities:
			qa, size = _apply_money_filter(qa, money_entities, request, responder)
			qa_out = qa.execute(size=size)
			if recur_ent and function in ('avg','sum'):
				responder = _calculate_agg_salary(responder, qa_out, function, recur_ent[0])
				if np.isnan(responder.slots['value']):
					responder.reply(salary_response)
					responder.listen()
					return
				responder.reply("Based on your query, the {function} {interval} is {value}")
			else:
				responder = _calculate_agg_salary(responder, qa_out, function)
				if np.isnan(responder.slots['value']):
					responder.reply(salary_response)
					responder.listen()
					return
				responder.reply('The {function} based on your query is {value}')

		elif function not in ('avg','sum'):
			qa_out = qa.execute()
			responder = _calculate_agg_salary(responder, qa_out, function)
			if np.isnan(responder.slots['value']):
					responder.reply(salary_response)
					responder.listen()
					return
			responder.reply("The {function} of employees is {value}")

		else:
			responder.reply("I see you are looking for the {function}, can you be more specific?")
			responder.listen()

	else:
		responder.reply(salary_response)
		responder.listen()



@app.handle(intent='get_salary_employees')
def get_salary_employees(request, responder):
	"""
	When a user asks for a list of employees that satisfy certain criteria in addition
	to satisfying a specified monetary criterion, this dialogue state filters the 
	knowledge base on those criteria and returns the shortlisted list of names.
	"""

	money_entities = [e for e in request.entities if e['type'] == 'money']

	categorical_entities = [e for e in request.entities if e['type'] in ('state', 'sex', 'maritaldesc','citizendesc',
		'racedesc','performance_score','employment_status','employee_source','position','department')]

	qa, size = _resolve_categorical_entities(request, responder)

	if money_entities:
		qa, size = _apply_money_filter(qa, money_entities, request, responder)

	qa_out = qa.execute(size=size)
	responder.slots['emp_list'] = _get_names(qa_out)
	responder.reply("Here's some employees: {emp_list}")




### Helper functions ###


def _apply_money_filter(qa, age_entities, request, responder):
	"""
	This function is used to filter any salary related queries, that may include a 
	comparator, such as, 'what percentage earns less than 20 dollars an hour? ' or an extreme,
	such as, 'highest earning employee'. 
	"""

	num_entity = [e['text'] for e in request.entities if e['type'] == 'sys_number']

	for i in range(len(num_entity)):
		if 'k' in num_entity[i]:
			num_entity[i] = num_entity[i].strip('k')
			num_entity[i] = str(float(num_entity[i])*1000)


	sys_amount_ent =  [e['text'] for e in request.entities if e['type'] == 'sys_amount-of-money']
	for i in range(len(sys_amount_ent)):
		sys_amount_ent[i].strip('$')
		if 'k' in sys_amount_ent[i]:
			sys_amount_ent[i] = sys_amount_ent[i].strip('k')
			sys_amount_ent[i] = str(float(sys_amount_ent[i])*1000)

		num_entity.append(sys_amount_ent[i])

	num_entity = [float(i) for i in num_entity]

	try:
		comparator_entity = [e for e in request.entities if e['type'] == 'comparator'][0]
	except:
		comparator_entity = []


	try:
		extreme_entity = [e for e in request.entities if e['type'] == 'extreme'][0]
	except:
		extreme_entity = []

	# The money entity can have either be accompanied by a comparator, extreme or no entity. 
	# These are mutually exclusive of others and hence can only be queried separately from
	# the knowledge base.

	if comparator_entity:
		comparator_canonical = comparator_entity['value'][0]['cname']

		if comparator_canonical == 'more than' and len(num_entity)==1:
			gte_val = num_entity[0]
			lte_val = 1000 # Default value since it is much above the hourly salary limit

		elif comparator_canonical == 'less than' and len(num_entity)==1:
			lte_val = num_entity[0]
			gte_val = 0

		elif comparator_canonical == 'equals to':
			gte_val = num_entity[0]
			lte_val = num_entity[0]

		elif len(num_entity)>1:
			gte_val = np.min(num_entity)
			lte_val = np.max(num_entity)
		
		qa = qa.filter(field='money', gte=gte_val, lte=lte_val)
		size = 300


	elif extreme_entity:
		qa, size = _resolve_extremes(qa, extreme_entity, 'money', num_entity)

	elif len(num_entity)>=1:
		qa = qa.filter(field='money', gte=np.min(num_entity), lte=np.max(num_entity))
		size = 300

	else:
		size = 300

	return qa, size


def _get_interval_amount(recur_ent, money):
	"""
	Get the Salary Amount Based on a Recurring Period of Time
	param recur_ent (str): 'yearly', 'monthly', 'weely', 'daily', 'hourly'
	param money (float): Hourly Salary of an employee
	"""


    intv_mult = { "yearly": 12*4*5*8, "monthly": 4*5*8, "weekly":5*8, "daily": 8,"hourly": 1}
    return round(intv_mult[recur_ent] * money, 2)         


def _calculate_agg_salary(responder, qa_out, function, recur_ent='hourly'):
	"""
	Calculate Salary by first fetching it from the knowledge base and then
	multiplying by the appropriate time factor that the user is seeking
	"""

	value = _agg_function(qa_out, func=function, num_col='money')

	if recur_ent:
		value = _get_interval_amount(recur_ent, value)
		responder.slots['interval'] = recur_ent
		
	responder.slots['value'] = value

	return responder



