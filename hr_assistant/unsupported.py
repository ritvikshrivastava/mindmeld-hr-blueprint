# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'unsupported' domain in 
the MindMeld HR assistant blueprint application
"""

from .root import app
from hr_assistant.general import _resolve_categorical_entities, _resolve_function_entity, _resolve_extremes, _agg_function, _get_names, _get_person_info, _fetch_from_kb
import re



@app.handle(intent='unsupported')
def unsupported(request, responder):

	if request.frame.get('visited'):

		no_list = ['no', 'nah', 'nope', 'nada', 'nay', 'nu', 'none', 'null', 'stop', 'cancel', 'dismiss', 'exit', 'end', 'bye', 'tata']
		yes_list = ['yes', 'ya', 'yup', 'yo', 'hm', 'hmm', 'hmmm', 'mm-hmm', 'mm hmm', 'okay', 'sure', 'all right', 'k', 'kk', 'kay', 'ok', 'okie-dokie', 'okie dokie', 'why not', 'alright', 'for sure', 'definitely']

		text = request.text.lower()
		text = re.sub('[^A-Za-z0-9]+', ' ', text)
		text = text.split()

		if any(x in text for x in no_list):
			replies = ['Alright, goodbye!', 'Alright, have a nice day!', 'Sure, see you later!', 'Ok, happy to help!']
			responder.reply(replies)
			responder.frame['visited']=False

		elif any(x in text for x in yes_list):
			responder.reply(["Great! You can ask me about an employee's individual information (eg. Is Ivan married?), \
				some employee statistic (eg. average salary of females) \
				or names of employees according to your criteria (eg. give me a list of all married employees)"])

			responder.reply("Now, what would you like to know?")
			responder.frame['visited']=False
			responder.listen()

		else:
			responder.reply("Hmmm, did you mean yes or no?")
			responder.frame['visited'] = False
			responder.listen()

	else:
		responder.reply("Hmmm, I didn't quite understand. Would you like to know what you can ask me?")
		responder.frame['visited'] = True
		responder.target_dialogue_state = 'unsupported'
		responder.listen()