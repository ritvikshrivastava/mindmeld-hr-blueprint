# -*- coding: utf-8 -*-
"""This module contains the MindMeld HR assistant blueprint application"""

from hr_assistant_categories.root import app

import hr_assistant_categories.salary
import hr_assistant_categories.general
import hr_assistant_categories.date
import hr_assistant_categories.heirarchy

__all__ = ['app']
