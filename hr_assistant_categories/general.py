# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'general' domain in 
the MindMeld HR assistant blueprint application
"""

from .root import app
import numpy as np


@app.handle(intent='get_info', has_entity='age')
def get_info_age(request, responder):
	responder.slots['name'] = request.frame.get('name')
	responder = _get_person_info(request, responder, 'age')
	responder.reply("The age of {name} is {age}")

@app.handle(intent='get_info', has_entity='state')
def get_info_state(request, responder):
	responder.slots['name'] = request.frame.get('name')
	responder = _get_person_info(request, responder, 'state')
	responder.reply("{name} is from {state}")


@app.handle(intent='get_info', has_entity='maritaldesc')
def get_info_maritaldesc(request, responder):
	responder.slots['name'] = request.frame.get('name')
	responder = _get_person_info(request, responder, 'maritaldesc')
	responder.reply("{name} is {maritaldesc}")


@app.handle(intent='get_info', has_entity='citizendesc')
def get_info_citizendesc(request, responder):
	responder.slots['name'] = request.frame.get('name')
	responder = _get_person_info(request, responder, 'citizendesc')
	responder.reply("{name} is a {citizendesc}")


@app.handle(intent='get_info', has_entity='racedesc')
def get_info_racedesc(request, responder):
	responder.slots['name'] = request.frame.get('name')
	responder = _get_person_info(request, responder, 'racedesc')
	responder.reply("{name}'s race is {racedesc}")


@app.handle(intent='get_info', has_entity='performance_score')
def get_info_performance_score(request, responder):
	responder.slots['name'] = request.frame.get('name')
	responder = _get_person_info(request, responder, 'performance_score')
	responder.reply("{name}'s performance status is: {performance_score}")


@app.handle(intent='get_info', has_entity='reason_for_termination')
def get_info_rft(request, responder):
	responder.slots['name'] = request.frame.get('name')
	responder = _get_person_info(request, responder, 'reason_for_termination')
	responder.reply("{name}'s reason for termination was: {rft}")


@app.handle(intent='get_info', has_entity='employee_source')
def get_info_employee_source(request, responder):
	responder.slots['name'] = request.frame.get('name')
	responder = _get_person_info(request, responder, 'employee_source')
	responder.reply("{name}'s discovered the organisation through: {employee_source}")


@app.handle(intent='get_info', has_entity='position')
def get_info_position(request, responder):
	responder.slots['name'] = request.frame.get('name')
	responder = _get_person_info(request, responder, 'position')
	responder.reply("{name}'s position in the organisation is: {position}")


@app.handle(intent='get_info', has_entity='employment_status')
def get_info_employment_status(request, responder):
	responder.slots['name'] = request.frame.get('name')
	responder = _get_person_info(request, responder, 'employment_status')
	responder.reply("{name}'s employment status is: {employment_status}")


@app.handle(intent='get_info', has_entity='department')
def get_info_dept(request, responder):
	responder.slots['name'] = request.frame.get('name')
	responder = _get_person_info(request, responder, 'department')
	responder.reply("{name} was in the {department} department")


@app.handle(intent='get_info', has_entity='name')
def get_info_name(request, responder):

	# find out the name entity
	name_ent = [e for e in request.entities if e['type'] == 'name']
	name = name_ent[0]['value'][0]['cname']

	# store for use in future turns
	responder.frame['name'] = name
	responder.slots['name'] = responder.frame['name']

	responder.reply("What information would you like to know about {name}?")

	# redirect to intents that follow this dialogue flow after hearing user's next turn
	responder.params.allowed_intents = ('general.get_info', 'hierarchy.get_hierarchy')

	# get user's next turn
	responder.listen()


# Default case
@app.handle(intent='get_info')
def get_info_default(request, responder):
	try:
		name_ent = [e for e in request.entities if e['type'] == 'name']
		name = name_ent[0]['value'][0]['cname']
		responder.frame['name'] = name
	except:
		replies = "Hello! What information are you looking for? You can ask for an employee's individual information (eg. Is Ivan married?), \
some statistic about the employees (eg. average salary) \
or get a list of employees according to your criteria (eg. list of male employees)"
		responder.reply(replies)
		responder.listen()	



@app.handle(intent='get_aggregate')
def get_aggregate(request, responder):

	# print(request.frame.get('function'))
	func_entity = request.frame.get('function')


	func_entities = [e for e in request.entities if e['type'] == 'function']
	age_entities = [e for e in request.entities if e['type'] == 'age']

	if func_entities:
		func_entity = func_entities[0]

	if func_entity:
		function, responder = _resolve_function_entity(responder, func_entities[0])

		qa, size = _resolve_categorical_entities(request, responder)

		# Handles Numerical Variables
		if age_entities:
			qa, size = _apply_age_filter(qa, age_entities, request, responder)
			qa_out = qa.execute(size=size)
			responder.slots['value'] = _agg_function(qa_out, func=function, num_col='age')
			responder.reply('The {function} age is {value}')

		elif function not in ('avg','sum'):
			qa_out = qa.execute(size=300)
			responder.slots['value'] = _agg_function(qa_out, func=function)
			responder.reply('The {function} is {value}')

		else:
			responder.reply('What would you like to know the {function} of?')
			responder.params.allowed_intents = ('general.get_aggregate', 'general.get_employees')
			responder.listen()

	else:
		responder.reply('What statistic would you like to know?')
		responder.params.allowed_intents = ('general.get_aggregate', 'general.get_employees')
		responder.listen()



@app.handle(intent='get_employees')
def get_employees(request, responder):
	
	# Finding age entities (indicators), if any
	age_entities = [e for e in request.entities if e['type'] == 'age']

	# Considering that the only numerical value(s) for this intent will be age
	num_entity = [int(e['text']) for e in request.entities if e['type'] == 'sys_number'] 
	num_entity = [float(i) for i in num_entity]

	# Finding extreme entities (indicators), if any
	try:
		extreme_entity = [e for e in request.entities if e['type'] == 'extreme'][0]
	except:
		extreme_entity = []

	qa, size = _resolve_categorical_entities(request, responder)

	if age_entities:
		qa, size = _apply_age_filter(request, responder, qa, age_entities, num_entity)

	if extreme_entity:
		qa, size = _resolve_extremes(qa, extreme_entity, 'age', num_entity)

	qa_out = qa.execute(size=size)
	responder.slots['emp_list'] = _get_names(qa_out)
	responder.reply("Here's some employees: {emp_list}")


# Helper Functions

def _get_person_info(request, responder, entity_type):

	name = responder.frame.get('name')

	# if the user has provided a new name, replace the existing name with it
	try:
		name_ent = [e for e in request.entities if e['type'] == 'name']
		name = name_ent[0]['value'][0]['cname']
		responder.frame['name'] = name
	except:
		pass

	responder = _fetch_from_kb(responder, name, entity_type)
	return responder

def _fetch_from_kb(responder, name, entity_type):
	app.question_answerer.load_kb('hr_assistant_categories', 'user_data', './hr_assistant_categories/data/user_data.json')
	employee = app.question_answerer.get(index='user_data', emp_name=name)
	entity_option = employee[0][entity_type]

	responder.slots['name'] = name
	responder.slots[entity_type] = entity_option
	return responder


# Get a List of Names from a QA Result
# param qa_out (list) Output of QA from a query
def _get_names(qa_out):
	return [out['emp_name'] for out in qa_out]


def _apply_age_filter(request, responder, qa, age_entities, num_entity):
	try:
		comparator_entity = [e for e in request.entities if e['type'] == 'comparator'][0]
	except:
		comparator_entity = []

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
		
		qa = qa.filter(field='age', gte=gte_val, lte=lte_val)
		size = 300

	elif len(num_entity)>=1:
		qa = qa.filter(field='age', gte=np.min(num_entity), lte=np.max(num_entity))

		size = 300

	else:
		size = 300

	return qa, size


def _resolve_categorical_entities(request, responder):
	# Resolving categorical entities
	categorical_entities = [e for e in request.entities if e['type'] in ('state', 'sex', 'maritaldesc','citizendesc',
		'racedesc','performance_score','employment_status','employee_source','position','department')]

		# Building custom search
	qa = app.question_answerer.build_search(index='user_data')

	if categorical_entities:
		for categorical_entity in categorical_entities:
			key = categorical_entity['type']
			val = categorical_entity['value'][0]['cname']
			kw = {key : val}
			qa = qa.filter(**kw)
	
	size = 300

	return qa, size


def _resolve_function_entity(responder, func_entity):

	# A dictionary to convert the canonical form of the function entity to one
	# that is accepted by the '_agg_function' for calculation of the aggregate value
	func_dic = {'percent':'pct', 'sum':'sum', 'average':'avg', 'count':'ct'}

	## mapping text entry's canonical entity form using the function dictionary
	key = func_entity['value'][0]['cname']
	function = func_dic[key]
	responder.slots['function'] = func_entity['value'][0]['cname']
	responder.frame['function'] = func_entity

	return function, responder


def _resolve_extremes(qa, extreme_entity, field, num_entity):
	extreme_canonical = extreme_entity['value'][0]['cname']

	if extreme_canonical == 'highest':
		qa = qa.sort(field=field, sort_type='desc')
	
	elif extreme_canonical == 'lowest':
		qa = qa.sort(field=field, sort_type='asc')
	
	if num_entity:
		size = num_entity[0]
	else:
		size = 1

	return qa, size


# Function Helper that does Sum, Average and Percent Calculations
# param qa_out (list) List of Json Objects Representing Users
# param func (str) - Function Type: 'avg','sum', 'ct', 'pct'
# param num_col (str) - Numerical Column Type : 'money', or 'age'
# returns result (float) - Resulting Value from function operation
def _agg_function(qa_out, func='avg', num_col='money'):
    if(func=='avg'): return np.mean([emp[num_col] for emp in qa_out])
    elif(func=='sum'): return np.sum([emp[num_col] for emp in qa_out])
    elif(func=='ct'): return len(qa_out)
    elif(func=='pct'): return len(qa_out)/3
