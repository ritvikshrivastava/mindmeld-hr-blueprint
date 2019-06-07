# -*- coding: utf-8 -*-
"""This module contains the dialogue states for the 'salary' domain in 
the MindMeld HR assistant blueprint application
"""
from .root import app


@app.handle(intent='get_hierarchy')
def heirarchy(request, responder):
    replies = ["The manager for {name} is {name}"]
    responder.reply(replies)
