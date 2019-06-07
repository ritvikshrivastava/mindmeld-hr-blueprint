# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'general' domain in 
the MindMeld HR assistant blueprint application
"""

from .root import app
import numpy as np

@app.handle(intent='get_info')
def get_info(request, responder):
	name_ent = [e for e in request.entities if e['type'] == 'name']
	name = name_ent[0]['value'][0]['cname']
	responder.frame['name'] = name
	responder.slots['name'] = responder.frame['name']
	responder.reply("What information would you like to know about {name}?")
	responder.listen()


@app.handle(intent='get_info', entity='age')
def get_info_age(request, responder):
	responder = _get_person_info(responder, 'age')
	responder.reply("The age of {name} is {age}")

@app.handle(intent='get_info', entity='state')
def get_info_status(request, responder):
	responder = _get_person_info(request, responder, 'state')
	responder.reply("{name} is from {state}")


@app.handle(intent='get_info', entity='maritaldesc')
def get_info_maritaldesc(request, responder):
	responder = _get_person_info(request, responder, 'maritaldesc')
	responder.reply("{name} is {maritaldesc}")


@app.handle(intent='get_info', entity='citizendesc')
def get_info_citizendesc(request, responder):
	responder = _get_person_info(request, responder, 'citizendesc')
	responder.reply("{name} is a {citizendesc}")


@app.handle(intent='get_info', entity='racedesc')
def get_info_racedesc(request, responder):
	responder = _get_person_info(request, responder, 'racedesc')
	responder.reply("{name}'s race is {racedesc}")


@app.handle(intent='get_info', entity='performance_score')
def get_info_performance_score(request, responder):
	responder = _get_person_info(request, responder, 'performance_score')
	responder.reply("{name}'s performance status is: {performance_score}")


@app.handle(intent='get_info', entity='reason_for_termination')
def get_info_rft(request, responder):
	responder = _get_person_info(request, responder, 'reason_for_termination')
	responder.reply("{name}'s reason for termination was: {rft}")


@app.handle(intent='get_info', entity='employee_source')
def get_info_employee_source(request, responder):
	responder = _get_person_info(request, responder, 'employee_source')
	responder.reply("{name}'s discovered the organisation through: {employee_source}")


@app.handle(intent='get_info', entity='position')
def get_info_position(request, responder):
	responder = _get_person_info(request, responder, 'position')
	responder.reply("{name}'s position in the organisation is: {position}")


@app.handle(intent='get_info', entity='employment_status')
def get_info_employment_status(request, responder):
	responder = _get_person_info(request, responder, 'employment_status')
	responder.reply("{name}'s employment status is: {employment_status}")


@app.handle(intent='get_info', entity='department')
def get_info_dept(request, responder):
	responder = _get_person_info(request, responder, 'department')
	responder.reply("{name} was in the {department} department")


@app.handle(intent='get_aggregate')
def get_aggregate(request, responder):

	func_entities = [e for e in request.entities if e['type'] == 'function']
	age_entities = [e for e in request.entities if e['type'] == 'age']

	if func_entities:

		func_entity = func_entity[0]
		func_dic = {'percent':'pct', 'sum':'sum', 'average':'avg', 'count':'ct'}

		## mapping text entry's canonical entity form using the function dictionary
		function = func_dic.get(func_entity['value'][0]['cname'], default='avg') 

		categorical_entity = [e for e in request.entities if e['type'] in ('state', 'sex', 'maritaldesc','citizendesc',
			'racedesc','performance_score','employment_status','employee_source','position','department')][0]

		qa = app.question_answerer.build_search(index='user_data')
		qa = qa.query(categorical_entity['type']=categorical_entity['text'])
		responder.slots['function'] = func_entity['value'][0]['cname']

		if age_entities:
			qa, size = _apply_age_filter(qa, age_entities, request, responder)
			qa_out = qa.execute(size=size)
			responder.slots['value'] = _agg_function(qa_out, func=function, num_col='age')

		elif func_entity not in ('avg','sum'):
			qa_out = qa.execute()
			responder.slots['value'] = _agg_function(qa_out, func=function)

		else:
			responder.reply('What would you like to know the {function} of?')
			responder.listen()

	else:
		responder.reply('What statistic would you like to know?')
		responder.listen()


@app.handle(intent='get_employees')
def get_employees(request, responder):
	age_entities = [e for e in request.entities if e['type'] == 'age']

	categorical_entities = [e for e in request.entities if e['type'] in ('state', 'sex', 'maritaldesc','citizendesc',
		'racedesc','performance_score','employment_status','employee_source','position','department')]

	qa = app.question_answerer.build_search(index='user_data')

	for categorical_entity in categorical_entities:
		qa = qa.query(categorical_entity['type']=categorical_entity['value'][0]['cname'])

	size = 300

	if age_entities:
		qa, size = _apply_age_filter(qa, age_entities,request, responder)
		size = 1

	qa_out = qa.execute(size=size)
	responder.slots['emp_list'] = _get_names(qa_out)
	responder.reply('Here\'s some employees: {emp_list}')


# Helper Functions

def _get_person_info(request, responder, entity_type):
	try:
		name = responder.frame.pop('name')
	except:
		name_ent = [e for e in request.entities if e['type'] == 'name']
		name = name_ent[0]['value'][0]['cname']

	employee = app.question_answerer.get(index='user_data', emp_name=name)
	entity_option = employee[0][entity_type]

	responder.slots['name'] = name
	responder.slots[entity_type] = entity_option
	return responder


# Get a List of Names from a QA Result
# param qa_out (list) Output of QA from a query
def _get_names(qa_out):
	return [out['emp_name'] for out in qa_out]


def _apply_age_filter(qa, age_entities, request, responder):

	## Considering that the only numerical value(s) for this intent will be age
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

	# The age entity can have either be accompanied by a comparator, extreme or no entity. 
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
		
		qa = qa.filter(field='age', gte=gte, lte=lte_val).execute()
		size = 300


	elif extreme_entity:
		extreme_canonical = extreme_entity['value'][0]['cname']

		if extreme_canonical == 'highest':
			qa = qa.sort(field='age', sort_type='desc')
		
		elif extreme_canonical == 'lowest':
			qa = qa.sort(field='age', sort_type='desc')
		
		if num_entity:
			size = num_entity[0]
		else:
			size = 1


	else:
		if len(num_entity)>1:
			qa = qa.filter(filter='age', gte=np.min(num_entity), lte=np.max(num_entity))
		else:
			qa = qa.filter(filter='age', gte=num_entity[0]['text'], lte=num_entity[0]['text'])

		size = 300

	return qa, size



