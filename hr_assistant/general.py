# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'general' domain in 
the MindMeld HR assistant blueprint application
"""

from .root import app
import numpy as np


"""
The dialogue states below are entity specific cases of the 'get_info_default'
dialogue state below.
"""
@app.handle(intent='get_info', has_entity='age')
def get_info_age(request, responder):
	responder = _get_person_info(request, responder, 'age')
	try:
		responder.reply("The age of {name} is {age}")
	except:
		responder.reply(_not_an_employee())
		return

@app.handle(intent='get_info', has_entity='sex')
def get_info_sex(request, responder):
	responder = _get_person_info(request, responder, 'sex')
	try:
		responder.reply("{name} is {sex}")
	except:
		responder.reply(_not_an_employee())
		return

@app.handle(intent='get_info', has_entity='state')
def get_info_state(request, responder):
	responder = _get_person_info(request, responder, 'state')
	try:
		responder.reply("{name} is from {state}")
	except:
		responder.reply(_not_an_employee())
		return


@app.handle(intent='get_info', has_entity='maritaldesc')
def get_info_maritaldesc(request, responder):
	responder = _get_person_info(request, responder, 'maritaldesc')
	try:
		responder.reply("{name} is {maritaldesc}")
	except:
		responder.reply(_not_an_employee())
		return


@app.handle(intent='get_info', has_entity='citizendesc')
def get_info_citizendesc(request, responder):
	responder = _get_person_info(request, responder, 'citizendesc')
	try:
		responder.reply("{name} is an {citizendesc}")
	except:
		responder.reply(_not_an_employee())
		return


@app.handle(intent='get_info', has_entity='racedesc')
def get_info_racedesc(request, responder):
	responder = _get_person_info(request, responder, 'racedesc')
	try:
		responder.reply("{name}'s race is {racedesc}")
	except:
		responder.reply(_not_an_employee())
		return


@app.handle(intent='get_info', has_entity='performance_score')
def get_info_performance_score(request, responder):
	responder = _get_person_info(request, responder, 'performance_score')
	try:
		responder.reply("{name}'s performance status is: {performance_score}")
	except:
		responder.reply(_not_an_employee())
		return


@app.handle(intent='get_info', has_entity='reason_for_termination')
def get_info_rft(request, responder):
	responder = _get_person_info(request, responder, 'rft')
	try:
		responder.reply("{name}'s reason for termination was: {rft}")
	except:
		responder.reply(_not_an_employee())
		return


@app.handle(intent='get_info', has_entity='employee_source')
def get_info_employee_source(request, responder):
	responder = _get_person_info(request, responder, 'employee_source')
	try:
		responder.reply("{name}'s discovered the organisation through: {employee_source}")
	except:
		responder.reply(_not_an_employee())
		return


@app.handle(intent='get_info', has_entity='position')
def get_info_position(request, responder):
	responder = _get_person_info(request, responder, 'position')
	try:
		responder.reply("{name}'s position in the organisation is: {position}")
	except:
		responder.reply(_not_an_employee())
		return


@app.handle(intent='get_info', has_entity='employment_status')
def get_info_employment_status(request, responder):
	responder = _get_person_info(request, responder, 'employment_status')
	try:
		responder.reply("{name}'s employment status is: {employment_status}")
	except:
		responder.reply(_not_an_employee())
		return


@app.handle(intent='get_info', has_entity='department')
def get_info_dept(request, responder):
	responder = _get_person_info(request, responder, 'department')
	try:
		responder.reply("{name} was in the {department} department")
	except:
		responder.reply(_not_an_employee())
		return


# Default case
@app.handle(intent='get_info')
def get_info_default(request, responder):
	"""
	When a user asks for any information regarding a single user without speciying a
	categorical, monetary or date related entitiy for the user, or in case of the system
	not being able to recognize that entity, this dialogue state captures the name of the
	person and prompts user to provide one of the abovementioned types of entities in the
	subsequent turn. Once the user does, this dialogue state redirects (along with the 
	contextual information, i.e. name, from the previous turns) to more specific dialogue states
	corresponding to certain domain, intent and entities.
	"""

	try:
		name_ent = [e for e in request.entities if e['type'] == 'name']
		name = name_ent[0]['value'][0]['cname']
		responder.frame['name'] = name
		responder.frame['info_visited'] = True
		responder.slots['name'] = name
		responder.reply("What would you like to know about {name}?")
		responder.params.allowed_intents = ('general.get_info', 'hierarchy.get_hierarchy_up', 'hierarchy.get_hierarchy_down', 'salary.get_salary', 'date.get_date')
		responder.listen()

	except:
		if request.frame.get('info_visited'):
			name = request.frame.get('name')
			responder.slots['name'] = name
			employee = app.question_answerer.get(index='employee_data', emp_name=name)
			if employee:
				details = employee[0]
				expand_dict = {'rft':'Reason for Termination', 'doh':'Date of Hire', 'dot':'Date of Termination', 'dob':'Date of Birth',
				'performance_score':'Performance Score', 'citizendesc': 'Citizenship Status', 'maritaldesc':'Marital Status', 'racedesc':'Race',
				'manage':'Manager', 'sex':'Gender', 'state':'State', 'employment_status':'Employment Status', 'position':'Position', 
				'department':'Department', 'age':'Age', 'money':'Hourly Pay'}
				details = [str(expand_dict[key])+" : "+str(details[key]) for key in details.keys() if key in expand_dict]
				responder.slots['details'] = '; '.join(details)
				responder.reply("I found the following details about {name}: {details}")
				responder.frame = {}
			else:
				responder.reply("Hmmm, looks like this employee did not work here! Would you like to know about someone else?")
				responder.frame = {}
		else:
			responder.reply("I believe that person is not an employee here.")
			responder.frame['info_visited'] = False


@app.handle(intent='get_aggregate')
def get_aggregate(request, responder):
	"""
	When a user asks for a statistic, such as average, sum, count or percentage,
	in addition to categorical filters (if any), this function captures all the 
	relevant entities, calculates the desired statistic function and returns it.
	"""

	# Checks for existing function entity from previous turn
	func_entity = request.frame.get('function')

	# If the user provides a new function entity, it replaces the one in context from previous turns
	func_entities = [e for e in request.entities if e['type'] == 'function']
	age_entities = [e for e in request.entities if e['type'] == 'age']

	if func_entities:
		func_entity = func_entities[0]

	if func_entity:
		function, responder = _resolve_function_entity(responder, func_entity)

		qa, size = _resolve_categorical_entities(request, responder)

		# Handles Numerical Variables
		if age_entities or _find_additional_age_entities(request, responder):
			qa, size = _apply_age_filter(request, responder, qa, age_entities)
			qa_out = qa.execute(size=size)

			responder.slots['value'] = _agg_function(qa_out, func=function, num_col='age')
			responder.reply('Based on your query, the {function} is {value}')

		elif function not in ('avg','sum'):
			qa_out = qa.execute(size=300)

			## Default handling if no relevant entity found to filter on
			non_func_entities = [e for e in request.entities if e['type'] != 'function']
			if not non_func_entities:
				responder.reply("I'm not sure what you are looking for.")
				return

			responder.slots['value'] = _agg_function(qa_out, func=function)
			responder.reply('Based on your query, the {function} is {value}')

		else:
			responder.reply('What would you like to know the {function} of?')
			responder.frame['function']=func_entity
			responder.params.allowed_intents = ('general.get_aggregate', 'salary.get_salary_aggregate', 'date.get_date_range_aggregate', 'greeting.greet', 'greeting.exit', 'unsupported.unsupported')
			responder.listen()

	else:
		responder.reply('What statistic would you like to know?')
		responder.params.allowed_intents = ('general.get_aggregate', 'salary.get_salary_aggregate', 'date.get_date_range_aggregate', 'greeting.greet', 'greeting.exit', 'unsupported.unsupported')
		responder.listen()



@app.handle(intent='get_employees')
def get_employees(request, responder):
	"""
	When a user asks for a list of employees that satisfy certain criteria,
	this dialogue state filters the knowledge base on those criteria and returns
	the shortlisted list of names.
	"""
	
	# Finding age entities (indicators), if any
	age_entities = [e for e in request.entities if e['type'] == 'age']

	# Finding extreme entities (if any)
	try:
		extreme_entity = [e for e in request.entities if e['type'] == 'extreme'][0]
	except:
		extreme_entity = []

	action_entities = [e['value'][0]['cname'] for e in request.entities if e['type'] == 'employment_action']

	qa, size = _resolve_categorical_entities(request, responder)

	if action_entities:
		if action_entities[0] == 'fired':
			qa = qa.filter(field='dot', gt='1800-01-01')

	if age_entities or _find_additional_age_entities(request, responder):
		qa, size = _apply_age_filter(request, responder, qa, age_entities)

	if extreme_entity:
		qa, size = _resolve_extremes(request, responder, qa, extreme_entity, 'age')

	qa_out = qa.execute(size=size)
	responder.slots['emp_list'] = _get_names(qa_out)


	if len(qa_out)==0 or len([e for e in request.entities])==0:
		responder.reply("No such employees found")
		return

	if action_entities:
		responder.slots['action'] = action_entities[0]
		responder.reply("The {action} employees are based on your criteria are: {emp_list}")

	else:
		if qa_out and len(qa_out)==1:
			responder.reply("Here is the employee you are looking for: {emp_list}")
		else:
			responder.reply("Here are some employees that match your criteria: {emp_list}")




### Helper Functions ###


def _apply_age_filter(request, responder, qa, age_entities, num_entity=None):
	"""
	This function is used to filter any age related queries, that may include a 
	comparator, such as 'how many employees are more than 40 years old', 
	or an exact age 'employees who are 30 years of age'.
	"""

	if not num_entity:
		num_entity = [float(e['value'][0]['value']) for e in request.entities if e['type'] == 'sys_number']

		for i in request.text.split():
			try:
				num_entity.append(float(i))
			except:
				continue

	try:
		comparator_entity = [e for e in request.entities if e['type'] == 'comparator'][0]
	except:
		comparator_entity = []

	# The age entity can have either be accompanied by a comparator, extreme or no entity. 
	# These are mutually exclusive of others and hence can only be queried separately from
	# the knowledge base.

	if comparator_entity:
		comparator_canonical = comparator_entity['value'][0]['cname']

		if comparator_canonical == 'more than':
			gte_val = num_entity[0]
			lte_val = 100

		elif comparator_canonical == 'less than':
			lte_val = num_entity[0]
			gte_val = 0

		elif comparator_canonical == 'equals to':
			gte_val = num_entity[0]
			lte_val = num_entity[0]

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


def _find_additional_age_entities(request, responder):
	"""
	If the user has a query such as 'list all employees under 30', the notion of age is implicit
	rather than explicit in the form of an age entity. Hence, this function is beneficial in
	capturing such implicit entities.
	"""
	try:
		comparator_entity = [e for e in request.entities if e['type'] == 'comparator'][0]
		num_entity = [float(e['value'][0]['value']) for e in request.entities if e['type'] == 'sys_number']

		for i in request.text.split():
			try:
				num_entity.append(float(i))
			except:
				continue
	except:
		comparator_entity = []
		num_entity = []

	return True if comparator_entity and num_entity else False


def _resolve_categorical_entities(request, responder):
	"""
	This function retrieves all categorical entities as listed below and filters the knowledge base
	using these entities as filters. The final search object containing the shortlisted employee data
	is returned back to the calling function.
	"""

	# Finding all categorical entities
	categorical_entities = [e for e in request.entities if e['type'] in ('state', 'sex', 'maritaldesc','citizendesc',
		'racedesc','performance_score','employment_status','employee_source','position','department', 'reason_for_termination')]

	# Building custom search
	qa = app.question_answerer.build_search(index='employee_data')

	# Querying the knowledge base for all categorical filters
	if categorical_entities:
		try:
			for categorical_entity in categorical_entities:
				key = categorical_entity['type']

				if key == 'reason_for_termination':
					key = 'rft'

				val = categorical_entity['value'][0]['cname']
				kw = {key : val}
				qa = qa.filter(**kw)
		except:
			pass

	size = 300

	return qa, size


def _resolve_function_entity(responder, func_entity):
	"""
	Resolves the function entity to a form that is acceptable in the aggregate
	calculation function.
	"""

	# A dictionary to convert the canonical form of the function entity to one
	# that is accepted by the '_agg_function' for calculation of the aggregate value
	func_dic = {'percent':'pct', 'sum':'sum', 'average':'avg', 'count':'ct'}

	## mapping text entry's canonical entity form using the function dictionary
	key = func_entity['value'][0]['cname']
	function = func_dic[key]

	if key=='percent': key='percentage'
	responder.slots['function'] = key

	return function, responder


def _resolve_extremes(request, responder, qa, extreme_entity, field, num_entity=None):
	"""
	Resolves 'extreme' entities and sorts the search QA output according
	to the order required. Also returns a size back to the calling function. 
	This size is indicative of how many entries are need. For eg, if the user 
	query was '5 highest earners', this function will sort the search output 
	in a descending manner and return that along with the value 5. If no value
	is provided in the original query, this function returns 1 as size.
	"""

	if not num_entity:
		num_entity = [int(e['value'][0]['value']) for e in request.entities if e['type'] == 'sys_number']

		for i in request.text.split():
			try:
				num_entity.append(float(i))
			except:
				continue
		num_entity = [float(i) for i in num_entity]

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
	"""
	Function that does Sum, Average and Percent Calculations
	param qa_out (list) List of Json Objects Representing Users
	param func (str) - Function Type: 'avg','sum', 'ct', 'pct'
	param num_col (str) - Numerical Column Type : 'money', or 'age'
	returns result (float) - Resulting Value from function operation
	"""

	if qa_out:
		if(func=='avg'): return round(np.mean([emp[num_col] for emp in qa_out]),2)
		elif(func=='sum'): return np.sum([emp[num_col] for emp in qa_out])
		elif(func=='ct'): return len(qa_out)
		elif(func=='pct'): return round(len(qa_out)/3,2)

	else:
		return 0

def _get_names(qa_out):
	"""
	Get a List of Names from a QA Result
	param qa_out (list) Output of QA from a query
	"""

	names = [str(out['first_name']) + ' ' + str(out['last_name']) for out in qa_out]
	names = ', '.join(names)
	return names


def _get_person_info(request, responder, entity_type):
	"""
	This function is used to fetch employee names from either the previous turns' context
	or the current query. The latest occurence of a name entity is given preference.
	The name is then passed to the _fetch_from_kb function to obtain the desired information
	about the employee under consideration from the Knowledge Base.
	"""

	name = request.frame.get('name')

	# if the user has provided a new name, replace the existing name with it
	try:
		name_ent = [e for e in request.entities if e['type'] == 'name']
		name = name_ent[0]['value'][0]['cname']
	except:
		if name:
			pass
		else:
			return responder

	responder = _fetch_from_kb(responder, name, entity_type)
	return responder
	

def _fetch_from_kb(responder, name, entity_type):
	"""
	This function is used the fetch a particular information about the given employee
	from the knowledge base.
	"""

	employee = app.question_answerer.get(index='employee_data', emp_name=name)
	entity_option = employee[0][entity_type]

	responder.slots['name'] = name
	responder.slots[entity_type] = entity_option
	return responder


def _not_an_employee():
	return "Looks like that person does not work in this organisation."