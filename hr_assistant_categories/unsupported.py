# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'unsupported' domain in 
the MindMeld HR assistant blueprint application
"""

from .root import app

@app.handle(intent='unsupported')
def unsupported(request, responder):
	responder.reply("Hello! What information are you looking for? You can ask for an employee's individual information (eg. Is Ivan married?), \
some statistic about the employees (eg. average salary of females) \
or get a list of employees according to your criteria (eg. )")
	responder.listen()