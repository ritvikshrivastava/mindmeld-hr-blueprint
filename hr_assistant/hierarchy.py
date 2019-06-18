# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'salary' domain in 
the MindMeld HR assistant blueprint application
"""
from .root import app
from hr_assistant.general import _resolve_categorical_entities, _resolve_function_entity, _resolve_extremes, _agg_function, _get_names, _get_person_info, _fetch_from_kb



@app.handle(intent='get_hierarchy', has_entity='name')
def heirarchy(request, responder):
	"""
	If a user asks about any employees manager or whether they are some other employee's 
	manager, this function captures all the names in the query and returns the employee-manager
	mapping for each one of them.
	"""

	try:
		name_ent = [e['value'][0]['cname'] for e in request.entities if e['type'] == 'name']
		manager_dict = {}

		for name in name_ent:
			responder = _fetch_from_kb(responder, name, 'manager')
			manager_dict = {responder.slots['name'], responder.slots['manager']}
			reply = ["{manager} is {name}'s manager"]
			responder.reply(reply)

	except:
		responder.reply("Who's manager would you like to know?")