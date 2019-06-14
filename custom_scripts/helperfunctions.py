# -*- coding: utf-8 -*-
"""This module contains the common helper functions for the MindMeld HR assistant blueprint application.
These functions are used across multiple domains and intents.
"""


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


def _agg_function(qa_out, func='avg', num_col='money'):
# Function Helper that does Sum, Average and Percent Calculations
# param qa_out (list) List of Json Objects Representing Users
# param func (str) - Function Type: 'avg','sum', 'ct', 'pct'
# param num_col (str) - Numerical Column Type : 'money', or 'age'
# returns result (float) - Resulting Value from function operation

    if(func=='avg'): return np.mean([emp[num_col] for emp in qa_out])
    elif(func=='sum'): return np.sum([emp[num_col] for emp in qa_out])
    elif(func=='ct'): return len(qa_out)
    elif(func=='pct'): return len(qa_out)/3


def _get_names(qa_out):
# Get a List of Names from a QA Result
# param qa_out (list) Output of QA from a query

	names = [str(out['first_name']) + ' ' + str(out['last_name']) for out in qa_out]
	names = ', '.join(names)
	return names


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
	app.question_answerer.load_kb('hr_assistant', 'user_data', './hr_assistant/data/user_data.json')
	employee = app.question_answerer.get(index='user_data', emp_name=name)
	entity_option = employee[0][entity_type]

	responder.slots['name'] = name
	responder.slots[entity_type] = entity_option
	return responder