.. _hr_assistant:

HR Assistant
==============

In this step-by-step walkthrough, you'll build a conversational application for a Human Resources assistant that can answer questions about employees at a company.

Working through this blueprint will teach you how to

   - handle a large number of domains and intents
   - use system entities such as amount-of-money, dates, and times
   - query and filter the knowledge base on multiple parameters

.. note::

   Please make sure to install and run all of the :ref:`pre-requisites <getting_started_virtualenv_setup>` for Workbench before continuing on with this blueprint tutorial.

1. The Use Case
^^^^^^^^^^^^^^^

This HR assistant would be used by an HR manager to ask questions about employees at an organization. They should be able to ask for information about a particular employee, for company-wide statistics, or for a group of employees that meet certain criteria.


2. Example Dialogue Interactions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The conversational flows for an HR assistant will primarily involve follow-up questions to natural language queries. Once the intent of the user is identified, multiple interactions may be necessary to get all of the information needed to complete the request.

Here are some examples of scripted dialogue interactions for conversational flows.

.. image:: /images/hr_assistant_interactions.png
    :width: 700px
    :align: center

.. _hr_assistant_model_hierarchy:

3. Domain-Intent-Entity Hierarchy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Here is the NLP model hierarchy for our HR assistant application.

.. image:: /images/hierarchy_hr_assistant.png

The HR assistant blueprint is organized into five domains: ``General``, ``Salary``, ``Dates``, ``Hierarchy``, and ``Unsupported``. The domains of the HR assistant blueprint correspond to the categories of questions that could be asked.

The full list of intents for all domains is illustrated below.

The ``General`` domain supports the following intents:

   - ``get_info`` — User wants specific information about an employee (eg. state, department, position, etc)
   - ``get_aggregate`` — User wants an average, total, or percentage of employees that meet certain criteria
   - ``get_employees`` — User wants a list of employees who meet certain criteria

The ``Salary`` domain supports the following intents:

   - ``get_salary`` — User wants the salary of a specific employee
   - ``get_salary_aggregate`` — User wants an average, total, or percentage specfically related to salary
   - ``get_salary_employees`` — User wants a list of employees who meet certain criteria that includes salary

The ``Date`` domain supports the following intents:

   - ``get_date`` — User wants the birth date, hiring date, or firing date of an employee
   - ``get_date_range_aggregate`` — User wants an average, total, or percentage filtered on a date range
   - ``get_date_range_employees`` — User wants a list of employees who meet certain criteria filtered on a date range

The ``Hierarchy`` domain supports the following intents:

   - ``get_hierarchy`` — User wants to know who an employee works for or who works for an employee

The ``Unsupported`` domain supports the following intents:

   - ``unsupported`` — User has provided a query outside the scope of the HR assistant

There are two types of entities in Workbench: :ref:`System Entities <system-entities>` and :doc:`Custom Entities <../userguide/entity_recognizer>`. System entities are pre-defined in Workbench. Examples include ``sys_temperature``, ``sys_time``, and ``sys_interval``. Custom entities are defined by the developers of each application. Within each entity folder, the file ``gazetteer.txt`` contains the full list of values for each custom entity.

HR assistant defines and uses the following custom entities for each of its domains, which are grouped by their purpose below:

   - User Information
       - ``state``: detects the state referred to, for example: "is {mia|name} form {CA|state}?"
       - ``age``: detects whether the user is asking about the age of an employee. For example: "tell me the {age of|age} {mia|name}"
       - ``sex``: detects the gender of an employee. For example: "is {Ivan|name} {male|sex}?"
       - ``maritaldesc``: detects the marital status of an employee. For example: "is {Ivan|name} a {married|maritaldesc} man?"
       - ``citizendesc``: detects the citizenship status of an employee. For example: "is {Nan|name} a {us citizen|citizendesc}?"
       - ``racedesc``: detects the race of an employee. For example: "is {Mia|name} {multiracial|racedesc}?"
       - ``reason_for_termination``: detects a reason for termination for an employee. For example: "Did {Mia|name} leave because of {medical issues|reason_for_termination}?"
       - ``department``: detects the department of an employee. For example: "is {Nan|name} working in {sales|department}?"
       - ``position``: detects the position of an employee. For example: "Is {Ivan|name} a {software engineer|position}?"
       - ``manager``: detects whether the user is asking for hierarchy information. For example: "Who is the {supervisor|manager} for {Mia|name}?"
       - ``employee_source``: detects how an employee heard about the company. For example: "Did {mia|name} find out about us from an {information session|racedesc}?"
       - ``performance_score``: detects the performance score of an employee. For example: "Is {ivan|name} currently {performing poorly|reason_for_termination} at the company?"
       - ``money``: detects whether the user is referring to salary information. For example: "What is {ivan|name} {earning|money}"
       - ``dob``: detects whether the user is referring to date of birth. For example: "When was {Nan|name} {born|dob}?"
       - ``employment_action``: detects whether the user is referring to hiring or firing an employee. For example: "What was {ivan|name}'s {date of termination|employment_action}"


   - Compare/Functions
       - ``comparator``: detects comparison keywords (more than, less than, equal to, between). For example: "is {mia|name} {earning|money} {more than} {ivan|name}?"
       - ``extreme``: detects extreme keywords (highest, oldest, lowest, youngest). For example: "who is the {oldest|extreme} employee?"
       - ``date_compare``: detects date comparision key words (prior to, after) For example: "Was {Ivan|name} {born|dob} {prior to|date_compare} {1990|sys_time}?"
       - ``function``: detects a function type (percent, sum, average, count) For example: "What {percent|function} of employees are {women|sex}?"

   - Custom Time Entities
       - ``time_interval``: detects a decade (1980's, 80s, eighties) For example: "{how many|function} employees were {bron|dob} in the {eighties|time_interval}?"
       - ``time_recur``: detects a recurring time interval (yearly, monthly, weekly). For example: "what does {ivan|name} {make|money} {monthly|time_recur}?"

       time, amount of money, number,

HR assistant uses three system entities: ``sys_time`` (time), ``sys_amount-of-money`` (money), ``sys_number`` (number). Some examples for annotation with system entities: "{How many|function} employees were {born|dob} in the {2009|sys_time}?" and "what {fraction|function} of employees {make|money} {less than|comparator} {69 grand|sys_amount-of-money}?".

.. admonition:: Exercise

To train the different machine learning models in the NLP pipeline for this app, we need labeled training data that covers all our intents and entities. To download the data and code required to run this blueprint, run the command below in a directory of your choice. (If you have already completed the Quick Start for this blueprint, you should skip this step.)

.. code-block:: shell

    python -c "import mmworkbench as wb; wb.blueprint('hr_assistant');"

This should create a Workbench project folder called ``hr_assistant`` in your current directory with the following structure:

.. image:: /images/hr_assistant_directory.png
    :width: 250px
    :align: center


4. Dialogue States
^^^^^^^^^^^^^^^^^^

Dialogue state logic can be arbitrarily complex. Simple dialogue state handlers just return a canned text response, while sophisticated ones can call third party APIs, calculate state transitions, and return complex responses.

Workbench supports three ways to organize dialogue states in the Dialogue Manager:

#. Define **one dialogue state for each intent**, as seen in the Kwik-E-Mart blueprint. This is the simplest approach, but can lead to duplicated code.
#. Define **one dialogue state for multiple intents**. This requires more work up front, but helps you consolidate duplicated dialogue state logic. Example shown in the home assistant blueprint.
#. Define **multiple dialogue states for multiple intents**. Based on the presence of entities, multiple dialogue states can handle a user's request. This is a good choice for when each intent can have a many possible dialogue states.

Which approach is best varies from one application to another. Figuring that out always requires some trial and error. You can see an example of the first two cases in the home assistant blueprint. The HR assistant will use and discuss the third method.

Let's begin by looking at some of the dialogue states for the intents in the ``general`` domain:

.. code:: python

      @app.handle(intent='get_info', has_entity='age')
      def get_info_age(request, responder):

      ...

      @app.handle(intent='get_info', has_entity='state')
      def get_info_state(request, responder):

      ...

      @app.handle(intent='get_info', has_entity='position')
      def get_info_position(request, responder):

      ...

      @app.handle(intent='get_info')
      def get_info_default(request, responder):

      ...

Observe that the same intent has multiple dialogue states that specify a ``has_entity`` field, except for the last case which serves as the default case. In other words, Mindmeld will feed the request to the dialogue state handler if there is a match between an entity found in the user query and the entity that the dialogue state handler accepts. If none of the entities are found, Mindmeld will default to the last case that does not specify an entity. This is where the system can follow up with the user and ask for any information needed to complete the query.



We can see this paradigm followed in the domain ``salary`` as well:

.. code:: python

      @app.handle(intent='get_salary', has_entity='time_recur')
      def get_salary_for_interval(request, responder):

      ...

      @app.handle(intent='get_salary')
      def get_salary(request, responder):

      ...


.. admonition:: Exercise

   Analyze the way the HR assistant blueprint uses this pattern **multiple dialogue states for multiple intents** Why this pattern used instead of another?


Sometimes a dialogue state handler needs to be aware of the context from a previous state. This happens in the **follow-up request pattern**. Consider this conversational interaction:

.. code:: bash

  User: Turn on the lights.
  App: Sure. Which lights?
  User: In the kitchen

Observe that the first request leaves out some required information — the location of the light to turn on. Therefore, in the response, the application must prompt the user for the missing information. Most importantly, the app needs to "remember" context from the first request to understand the user's second request, in which the user specifies the information that was missing.

Here is how the home assistant blueprint implements this pattern:

#. Define the ``specify_location`` intent
#. Define the ``specify_location`` state
#. Since multiple states (``close/open door``, ``lock/unlock door``, ``turn on/off lights``, ``turn on/off appliance``, ``check door/light``) can lead to the ``specify location`` state, pass the previous state/action information in the request object, as ``request.frame['desired_action']``

The code for ``specify_location`` looks like this:

.. code:: python

   @app.handle(intent='specify_location')
   def specify_location(request, responder):
       selected_all = False
       selected_location = _get_location(request)

       if selected_location:
           try:
               if request.frame['desired_action'] == 'Close Door':
                   reply = _handle_door_open_close_reply(selected_all, selected_location, request,
                                                         desired_state="closed")
               elif request.frame['desired_action'] == 'Open Door':
                   reply = _handle_door_open_close_reply(selected_all, selected_location, request,
                                                         desired_state="opened")
               elif request.frame['desired_action'] == 'Lock Door':
                   reply = _handle_door_lock_unlock_reply(selected_all, selected_location, request,
                                                          desired_state="locked")
               elif request.frame['desired_action'] == 'Unlock Door':
                   reply = _handle_door_lock_unlock_reply(selected_all, selected_location, request,
                                                          desired_state="unlocked")
               elif request.frame['desired_action'] == 'Check Door':
                   reply = _handle_check_door_reply(selected_location, responder)
               elif request.frame['desired_action'] == 'Turn On Lights':
                   color = _get_color(request) or request.frame.get('desired_color')
                   reply = _handle_lights_reply(selected_all, selected_location, responder,
                                                desired_state="on", color=color)
               elif request.frame['desired_action'] == 'Turn Off Lights':
                   reply = _handle_lights_reply(selected_all, selected_location, responder,
                                                desired_state="off")
               elif request.frame['desired_action'] == 'Check Lights':
                   reply = _handle_check_lights_reply(selected_location, responder)
               elif request.frame['desired_action'] == 'Turn On Appliance':
                   selected_appliance = request.frame['appliance']
                   reply = _handle_appliance_reply(selected_all, selected_location, selected_appliance,
                                                   desired_state="on")
               elif request.frame['desired_action'] == 'Turn Off Appliance':
                   selected_appliance = request.frame['appliance']
                   reply = _handle_appliance_reply(selected_all, selected_location, selected_appliance,
                                                   desired_state="off")
           except KeyError:
               reply = "Please specify an action to go along with that location."

           responder.reply(reply)
       else:
           reply = "I'm sorry, I wasn't able to recognize that location, could you try again?"
           responder.reply(reply)


Here are the intents and states in the home assistant blueprint, as defined in the application dialogue handler modules in the blueprint folder.

+---------------------------------------------------+--------------------------------+---------------------------------------------------+
|  Intent                                           |  Dialogue State Name           | Dialogue State Function                           |
+===================================================+================================+===================================================+
| ``greet``                                         | ``greet``                      | Begin an interaction and welcome the user         |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``check_weather``                                 | ``check_weather``              | Check the weather                                 |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``check_door``                                    | ``check_door``                 | Check the door                                    |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``close_door``                                    | ``close_door``                 | Close the door                                    |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``open_door``                                     | ``open_door``                  | To open the door                                  |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``lock_door``                                     | ``lock_door``                  | To lock the door                                  |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``unlock_door``                                   | ``unlock_door``                | Unlock the door                                   |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``turn_appliance_on``                             | ``turn_appliance_on``          | Turn the appliance on                             |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``turn_appliance_off``                            | ``turn_appliance_off``         | Turn the appliance off                            |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``check_lights``                                  | ``check_lights``               | Check the lights                                  |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``turn_lights_on``                                | ``turn_lights_on``             | Turn the lights on                                |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``turn_lights_off``                               | ``turn_lights_off``            | Turn the lights off                               |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``check_thermostat``                              | ``check_thermostat``           | Check the thermostat                              |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``set_thermostat``                                | ``set_thermostat``             | Set the thermostat                                |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``turn_up_thermostat``,  ``turn_down_thermostat`` | ``change_thermostat``          | Change the thermostat                             |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``change_alarm``                                  | ``change_alarm``               | Change the alarm                                  |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``check_alarm``                                   | ``check_alarm``                | Check the alarm                                   |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``remove_alarm``                                  | ``remove_alarm``               | Remove the alarm                                  |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``set_alarm``                                     | ``set_alarm``                  | Set the alarm                                     |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``start_timer``                                   | ``start_timer``                | Start the timer                                   |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``stop_timer``                                    | ``stop_timer``                 | Stop the timer                                    |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``specify_location``                              | ``specify_location``           | Specify locations in the house                    |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``specify_time``                                  | ``specify_time``               | Specify the time in the follow up questions       |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``exit``                                          | ``exit``                       | End the current interaction                       |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+
| ``unknown``                                       | ``unknown``                    | Prompt a user who has gone off-topic              |
|                                                   |                                | to get back to food ordering                      |
+---------------------------------------------------+--------------------------------+---------------------------------------------------+

5. Knowledge Base
^^^^^^^^^^^^^^^^^

Since the home assistant is a straightforward command-and-control application, it has no product catalog, and therefore does not need a knowledge base.

6. Training Data
^^^^^^^^^^^^^^^^

The labeled data for training our NLP pipeline was created using a combination of in-house data generation and crowdsourcing techniques. This is a highly important multi-step process that is described in more detail in :doc:`Step 6 <../quickstart/06_generate_representative_training_data>` of the Step-By-Step Guide. Be aware that at minimum, the following data generation tasks are required:

+--------------------------------------------------+--------------------------------------------------------------------------+
| | Purpose                                        | | Question (for crowdsourced data generators)                            |
| |                                                | | or instruction (for annotators)                                        |
+==================================================+==========================================================================+
| | Exploratory data generation                    | | "What kinds of questions would you ask a smart HR assistant            |
| | for guiding the app design                     | | that has access to an HR database?"                                    |
+--------------------------------------------------+--------------------------------------------------------------------------+
| | Generate queries for training                  | | ``get_info`` intent (``general`` domain):                              |
| | Domain and Intent Classifiers                  | | "How would you ask for an employee's information such as state,        |
| |                                                | | position, department, etc?"                                            |
| |                                                | |                                                                        |
| |                                                | | ``get_salary`` intent (``salary`` domain):                             |
| |                                                | | "How would you ask for the salary                                      |
| |                                                | | of an employee?"                                                       |
+--------------------------------------------------+--------------------------------------------------------------------------+
| | Annotate queries                               | | ``get_info``: "Annotate all occurrences of                             |
| | for training the Entity Recognizer             | | ``name`` and other user info entities in the given query"              |
+--------------------------------------------------+--------------------------------------------------------------------------+
| | Annotate queries                               | | HR Assistant does not use roles. For examples please visit             |
| | for training the Role Classifier               | | the home assistant blueprint.                                          |
+--------------------------------------------------+--------------------------------------------------------------------------+
| | Generation synonyms for gazetteer generation   | | ``state`` entity: "Enumerate a list of state names"                    |
| | to improve entity recognition accuracies       | | ``department`` entity: "What are some names of                         |
| |                                                | | departments at the company?"                                           |
+--------------------------------------------------+--------------------------------------------------------------------------+

In summary, the process is this:

#. Start with an exploratory data generation process, collecting varied examples of how the end user would interact with the app.
#. Cluster the data into different domains based on category. For example, the HR Assistant application has to answer questions regarding general information, salary, date filters, and hierarchy so we divide these areas into the following domains: ``general``, ``salary``, ``date``, ``hierarchy`` (and ``unsupported``).
#. Once we establish a clear domain-intent-entity-role hierarchy, generate labeled data for each component in the hierarchy.

The ``domains`` directory contains the training data for intent classification and entity recognition. The ``entities`` directory contains the data for entity resolution. Directories are at root level in the blueprint folder.

.. admonition:: Exercise

   - Read :doc:`Step 6 <../quickstart/06_generate_representative_training_data>` of the Step-By-Step Guide for best practices around training data generation and annotation for conversational apps. Following those principles, create additional labeled data for all the intents in this blueprint and use them as held-out validation data for evaluating your app. You can read more about :doc:`NLP model evaluation and error analysis <../userguide/nlp>` in the user guide.

   - To train NLP models for your own HR assistant application, you can start by reusing the blueprint data for generic intents like ``get_info`` and ``get_salary``. If you have more information in your HR database then you can create new intents and domains to include the new functionality.


7. Training the NLP Classifiers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Train a baseline NLP system for the blueprint app. The :meth:`build()` method of the :class:`NaturalLanguageProcessor` class, used as shown below, applies Workbench's default machine learning settings.

.. code:: python

   from mmworkbench.components.nlp import NaturalLanguageProcessor
   import mmworkbench as wb
   wb.configure_logs()
   nlp = NaturalLanguageProcessor(app_path='home_assistant')
   nlp.build()

.. code-block:: console

   Fitting domain classifier
   Loading queries from file weather/check_weather/train.txt
   Loading queries from file times_and_dates/remove_alarm/train.txt
   Loading queries from file times_and_dates/start_timer/train.txt
   Loading queries from file times_and_dates/change_alarm/train.txt
   .
   .
   .
   Fitting intent classifier: domain='greeting'
   Selecting hyperparameters using k-fold cross validation with 5 splits
   Best accuracy: 99.31%, params: {'fit_intercept': False, 'C': 1, 'class_weight': {0: 1.5304182509505702, 1: 0.88306789606035196}}
   Fitting entity recognizer: domain='greeting', intent='exit'
   No entity model configuration set. Using default.
   Fitting entity recognizer: domain='greeting', intent='greet'
   No entity model configuration set. Using default.
   Fitting entity recognizer: domain='unknown', intent='unknown'
   No entity model configuration set. Using default.
   Fitting intent classifier: domain='smart_home'
   Selecting hyperparameters using k-fold cross validation with 5 splits
   Best accuracy: 98.43%, params: {'fit_intercept': True, 'C': 100, 'class_weight': {0: 0.99365079365079367, 1: 1.5915662650602409, 2: 1.3434782608695652, 3: 1.5222222222222221, 4: 0.91637426900584784, 5: 0.74743589743589745, 6: 1.9758620689655173, 7: 1.4254901960784312, 8: 1.0794871794871794, 9: 1.0645320197044335, 10: 1.1043715846994535, 11: 1.2563909774436088, 12: 1.3016260162601625, 13: 1.0775510204081633, 14: 1.8384615384615384}}

.. tip::

  During active development, it helps to increase the :doc:`Workbench logging level <../userguide/getting_started>` to better understand what is happening behind the scenes. All code snippets here assume that logging level is set to verbose.

To see how the trained NLP pipeline performs on a test query, use the :meth:`process` method.

.. code:: python

   nlp.process("please set my alarm to 8am for tomorrow")

.. code-block:: console

       { 'domain': 'times_and_dates',
         'entities': [ { 'role': None,
                         'span': {'end': 38, 'start': 23},
                         'text': '8am for tomorrow',
                         'type': 'sys_time',
                         'value': [ { 'grain': 'hour',
                                      'value': '2019-02-16T08:00:00.000-08:00'}]}],
         'intent': 'set_alarm',
         'text': 'please set my alarm to 8am for tomorrow'
       }

Inspect classifiers in baseline configuration
"""""""""""""""""""""""""""""""""""""""""""""

For the data distributed with this blueprint, the baseline performance is already high. However, when extending the blueprint with your own custom home assistant data, you may find that the default settings may not be optimal and you can get better accuracy by individually optimizing each of the NLP components.

Because the home assistant app has five domains and over twenty intents, the classifiers need a fair amount of fine-tuning.

Start by inspecting the baseline configurations that the different classifiers use. The User Guide lists and describes the available configuration options. As an example, the code below shows how to access the model and feature extraction settings for the Intent Classifier.

.. code:: python

   ic = nlp.domains['smart_home'].intent_classifier
   ic.config.model_settings['classifier_type']

.. code-block:: console

   'logreg'

.. code-block:: python

   ic.config.features

.. code-block:: console

   {'bag-of-words': {'lengths': [1, 2]},
    'edge-ngrams': {'lengths': [1, 2]},
    'exact': {'scaling': 10},
    'freq': {'bins': 5},
    'gaz-freq': {},
    'in-gaz': {}
   }

You can experiment with different learning algorithms (model types), features, hyperparameters, and cross-validation settings, by passing the appropriate parameters to the classifier's :meth:`fit` method. Intent classifer and role classifier examples follow.

Experiment with the intent classifiers
""""""""""""""""""""""""""""""""""""""

We can change the feature extraction settings to use bag of trigrams in addition to the default bag of words:

.. code:: python

   ic.config.features['bag-of-words']['lengths'].append(3)
   ic.fit()

.. code-block:: console

   Fitting intent classifier: domain='smart_home'
   Selecting hyperparameters using k-fold cross-validation with 5 splits
   Best accuracy: 97.95%, params: {'C': 100, 'class_weight': {0: 2.1058169934640523, 1: 2.1058169934640523, 2: 0.9449346405228759, 3: 2.2581148121899366, 4: 1.7132480818414322, 5: 2.1058169934640523, 6: 0.7752149982800138, 7: 0.4041150092323926, 8: 2.234803921568627, 9: 1.4608823529411765, 10: 1.1334539969834088, 11: 1.100608519269777, 12: 1.1785055643879174, 13: 1.521981424148607, 14: 1.6213295074127212, 15: 1.129201680672269, 16: 2.8003619909502264}, 'fit_intercept': True}

We can also change the model for the intent classifier to Support Vector Machine (SVM) classifier, which works well for some datasets:

.. code:: python

   search_grid = {
      'C': [0.1, 0.5, 1, 5, 10, 50, 100, 1000, 5000],
      'kernel': ['linear', 'rbf', 'poly']
   }

   param_selection_settings = {
        'grid': search_grid,
        'type': 'k-fold',
        'k': 10
   }

   ic = nlp.domains['smart_home'].intent_classifier
   ic.fit(model_settings={'classifier_type': 'svm'}, param_selection=param_selection_settings)

.. code-block:: console

   Fitting intent classifier: domain='smart_home'
   Loading queries from file smart_home/check_lights/train.txt
   Loading queries from file smart_home/specify_location/train.txt
   Loading queries from file smart_home/turn_appliance_off/train.txt
   Loading queries from file smart_home/check_thermostat/train.txt
   Loading queries from file smart_home/set_thermostat/train.txt
   Loading queries from file smart_home/turn_up_thermostat/train.txt
   Loading queries from file smart_home/turn_lights_on/train.txt
   Loading queries from file smart_home/unlock_door/train.txt
   Loading queries from file smart_home/turn_on_thermostat/train.txt
   Loading queries from file smart_home/lock_door/train.txt
   Loading queries from file smart_home/turn_down_thermostat/train.txt
   Unable to load query: Unable to resolve system entity of type 'sys_time' for '12pm'.
   Loading queries from file smart_home/close_door/train.txt
   Loading queries from file smart_home/turn_lights_off/train.txt
   Loading queries from file smart_home/open_door/train.txt
   Loading queries from file smart_home/turn_off_thermostat/train.txt
   Loading queries from file smart_home/turn_appliance_on/train.txt
   Selecting hyperparameters using k-fold cross-validation with 10 splits
   Best accuracy: 98.27%, params: {'C': 5000, 'kernel': 'rbf'}

Similar options are available for inspecting and experimenting with the Entity Recognizer and other NLP classifiers as well. Finding the optimal machine learning settings is an iterative process involving several rounds of parameter tuning, testing, and error analysis. Refer to the :doc:`NaturalLanguageProcessor <../userguide/nlp>` in the user guide for more about training, tuning, and evaluating the various Workbench classifiers.

Inspect the role classifiers
""""""""""""""""""""""""""""

The home assistant application has role classifiers to distinguish between different role labels. For example, the annotated data in the ``times_and_dates`` domain and ``check_alarm`` intent has two types of roles: ``old_time`` and ``new_time``. The role classifier detects these roles for the ``sys_time`` entity:

.. code:: python

   nlp.domains["times_and_dates"].intents["change_alarm"].load()
   nlp.domains["times_and_dates"].intents["change_alarm"].entities["sys_time"].role_classifier.fit()
   nlp.domains["times_and_dates"].intents["change_alarm"].entities["sys_time"].role_classifier.evaluate()

.. code-block:: console

   <StandardModelEvaluation score: 100.00%, 21 of 21 examples correct>

In the above case, the role classifier was able to correctly distinguish between ``new_time`` and ``old_time`` for all test cases.

Inspect the configuration
"""""""""""""""""""""""""

The application configuration file, ``config.py``, at the top level of the home assistant folder, contains custom intent and domain classifier model configurations. These are defined as dictionaries named ``DOMAIN_CLASSIFIER_CONFIG`` and ``INTENT_CLASSIFIER_CONFIG``, respectively; other dictionaries include ``ENTITY_RECOGNIZER_CONFIG`` and ``ROLE_CLASSIFIER_CONFIG``. If no custom model configuration is added to ``config.py`` file, Workbench uses its default classifier configurations for training and evaluation. Here is an example of an intent configuration:

.. code:: python

   INTENT_CLASSIFIER_CONFIG = {
       'model_type': 'text',
       'model_settings': {
           'classifier_type': 'logreg'
       },
       'param_selection': {
           'type': 'k-fold',
           'k': 5,
           'grid': {
               'fit_intercept': [True, False],
               'C': [0.01, 1, 10, 100],
               'class_bias': [0.7, 0.3, 0]
           }
       },
       'features': {
           "bag-of-words": {
               "lengths": [1, 2]
           },
           "edge-ngrams": {"lengths": [1, 2]},
           "in-gaz": {},
           "exact": {"scaling": 10},
           "gaz-freq": {},
           "freq": {"bins": 5}
       }
   }

.. admonition:: Exercise

   Experiment with different models, features, and hyperparameter selection settings to see how they affect the classifier performance. Maintain a held-out validation set to evaluate your trained NLP models and analyze the misclassified test instances. Then use observations from the error analysis to inform your machine learning experimentation. For more on this topic, refer to the :doc:`User Guide <../userguide/nlp>`.


8. Parser Configuration
^^^^^^^^^^^^^^^^^^^^^^^

The relationships between entities in the home assistant queries are simple ones. For example, in the annotated query ``is the {back|location} door closed or open``, the ``location`` entity is self-sufficient, in that it is not described by any other entity.

If you extended the app to support queries with more complex entity relationships, it would be necessary to specify *entity groups* and configure the parser accordingly. For example, in the query ``is the {green|color} {back|location} door closed or open``, we would need to relate the ``color`` entity to the ``location`` entity, because one entity describes the other. The related entities would form an entity group. For more about entity groups and parser configurations, see the :doc:`Language Parser <../userguide/parser>` chapter of the User Guide.

Since we do not have entity groups in the home assistant app, we do not need a parser configuration.

9. Using the Question Answerer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :doc:`Question Answerer <../userguide/kb>` component in Workbench is mainly used within dialogue state handlers for retrieving information from the knowledge base. Since the home assistant app has no knowledge base, no question answerer is not needed.


10. Testing and Deployment
^^^^^^^^^^^^^^^^^^^^^^^^^^

Once all the individual pieces (NLP, Dialogue State Handlers) have been trained, configured or implemented, perform an end-to-end test of the app using the :class:`Conversation` class.

.. code:: python

   from mmworkbench.components.dialogue import Conversation
   conv = Conversation(nlp=nlp, app_path='home_assistant')
   conv.say('set alarm for 6am')

.. code-block:: console

   ['Ok, I have set your alarm for 06:00:00.']

The :meth:`say` method:

 - packages the input text in a user request object
 - passes the object to the Workbench Application Manager to a simulate an external user interaction with the app, and
 - outputs the textual part of the response sent by the dialogue manager.

In the above example, we requested to set an alarm for 6 AM and the app responded, as expected, by confirming that the alarm was set.

Try a multi-turn dialogues:

.. code:: python

   >>> conv = Conversation(nlp=nlp, app_path='home_assistant')
   >>> conv.say('Hi there!')
   ['Hi, I am your home assistant. I can help you to check weather, set temperature and control the lights and other appliances.]
   >>> conv.say("close the front door")
   ['Ok. The front door has been closed.']
   >>> conv.say("set the thermostat for 60 degrees")
   ['The thermostat temperature in the home is now 60 degrees F.']
   >>> conv.say("decrease the thermostat by 5 degrees")
   ['The thermostat temperature in the home is now 55 degrees F.']
   >>> conv.say("open the front door")
   ['Ok. The front door has been opened.']
   >>> conv.say("Thank you!")
   ['Bye!']


Alternatively, enter conversation mode directly from the command-line.

.. code:: console

       python -m home_assistant converse


.. code-block:: console

   You: What's the weather today in San Francisco?
   App: The weather forecast in San Francisco is clouds with a min of 62.6 F and a max of 89.6 F

.. admonition:: Exercise

   Test the app and play around with different language patterns to discover edge cases that our classifiers are unable to handle. The more language patterns we can collect in our training data, the better our classifiers can handle in live usage with real users. Good luck and have fun - now you have your very own Jarvis!
