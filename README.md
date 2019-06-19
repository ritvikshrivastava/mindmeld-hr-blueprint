HR Assistant
============

In this step-by-step walkthrough, you'll build a conversational
application for a Human Resources assistant that can answer questions
about employees at a company.

Working through this blueprint will teach you how to

> -   handle a large number of domains and intents
> -   use system entities such as amount-of-money, dates, and times
> -   query the knowledge base on multiple parameters

> **note**
>
> Please make sure to install and run all of the
> pre-requisites \<getting\_started\_virtualenv\_setup\> for Workbench
> before continuing on with this blueprint tutorial.<br /> 

1. The Use Case
---------------

This HR assistant would be used by an HR manager to ask questions about
employees at an organization. They should be able to ask for information
about a particular employee, for company-wide statistics, or for a group
of employees that meet certain criteria.<br /> 

2. Example Dialogue Interactions
--------------------------------

The conversational flows for an HR assistant will primarily involve
follow-up questions to natural language queries. Once the intent of the
user is identified, multiple interactions may be necessary to get all of
the information needed to complete the request.

Here are some examples of scripted dialogue interactions for
conversational flows.

![image](custom_scripts/images/hr_assistant_interactions.png)
<br /> 

3. Domain-Intent-Entity Hierarchy
---------------------------------

Here is the NLP model hierarchy for our HR assistant application.

![image](custom_scripts/images/hierarchy_hr_assistant.png)

The HR assistant blueprint is organized into five domains: `General`,
`Salary`, `Dates`, `Hierarchy`, and `Unsupported`. The domains of the HR
assistant blueprint correspond to the categories of questions that could
be asked.

The full list of intents for all domains is illustrated below.

The `General` domain supports the following intents:

> -   `get_info` — User wants specific information about an employee
>     (eg. state, department, position, etc)
> -   `get_aggregate` — User wants an average, total, or percentage of
>     employees that meet certain criteria
> -   `get_employees` — User wants a list of employees who meet certain
>     criteria

The `Salary` domain supports the following intents:

> -   `get_salary` — User wants the salary of a specific employee
> -   `get_salary_aggregate` — User wants an average, total, or
>     percentage specfically related to salary
> -   `get_salary_employees` — User wants a list of employees who meet
>     certain criteria that includes salary

The `Date` domain supports the following intents:

> -   `get_date` — User wants the birth date, hiring date, or firing
>     date of an employee
> -   `get_date_range_aggregate` — User wants an average, total, or
>     percentage filtered on a date range
> -   `get_date_range_employees` — User wants a list of employees who
>     meet certain criteria filtered on a date range

The `Hierarchy` domain supports the following intents:

> -   `get_hierarchy` — User wants to know who an employee works for or
>     who works for an employee

The `Unsupported` domain supports the following intents:

> -   `unsupported` — User has provided a query outside the scope of the
>     HR assistant

The `greeting` domain supports the following intents:

> -   `greet` — Greet the user and inform them of the assistant's
>     functionality
> -   `exit` — Say bye to the user

There are two types of entities in Workbench:
System Entities \<system-entities\> and
Custom Entities \<../userguide/entity\_recognizer\>. System entities are
pre-defined in Workbench. Examples include `sys_temperature`,
`sys_time`, and `sys_interval`. Custom entities are defined by the
developers of each application. Within each entity folder, the file
`gazetteer.txt` contains the full list of values for each custom entity.

HR assistant defines and uses the following custom entities for each of
its domains, which are grouped by their purpose below:

> -   User Information: <br /> 
>         -   `state`: detects the state referred to, for example: "is
>             {mia|name} form {CA|state}?"<br /> 
>         -   `age`: detects whether the user is asking about the age of
>             an employee. For example: "tell me the {age of|age}
>             {mia|name}"<br /> 
>         -   `sex`: detects the gender of an employee. For example: "is
>             {Ivan|name} {male|sex}?"<br /> 
>         -   `maritaldesc`: detects the marital status of an employee.
>             For example: "is {Ivan|name} a {married|maritaldesc} man?"<br /> 
>         -   `citizendesc`: detects the citizenship status of an
>             employee. For example: "is {Nan|name} a {us
>             citizen|citizendesc}?"<br /> 
>         -   `racedesc`: detects the race of an employee. For example:
>             "is {Mia|name} {multiracial|racedesc}?"<br /> 
>         -   `reason_for_termination`: detects a reason for termination
>             for an employee. For example: "Did {Mia|name} leave
>             because of {medical issues|reason\_for\_termination}?"<br /> 
>         -   `department`: detects the department of an employee. For
>             example: "is {Nan|name} working in {sales|department}?"<br /> 
>         -   `position`: detects the position of an employee. For
>             example: "Is {Ivan|name} a {software engineer|position}?"<br /> 
>         -   `manager`: detects whether the user is asking for
>             hierarchy information. For example: "Who is the
>             {supervisor|manager} for {Mia|name}?"<br /> 
>         -   `employee_source`: detects how an employee heard about the
>             company. For example: "Did {mia|name} find out about us
>             from an {information session|racedesc}?"<br /> 
>         -   `performance_score`: detects the performance score of an
>             employee. For example: "Is {ivan|name} currently
>             {performing poorly|reason\_for\_termination} at the
>             company?"<br /> 
>         -   `money`: detects whether the user is referring to salary
>             information. For example: "What is {ivan|name}
>             {earning|money}"<br /> 
>         -   `dob`: detects whether the user is referring to date of
>             birth. For example: "When was {Nan|name} {born|dob}?"<br /> 
>         -   `employment_action`: detects whether the user is referring
>             to hiring or firing an employee. For example: "What was
>             {ivan|name}'s {date of termination|employment\_action}"
>
> -   Compare/Functions: <br /> 
>         -   `comparator`: detects comparison keywords (more than, less
>             than, equal to, between). For example: "is {mia|name}
>             {earning|money} {more than} {ivan|name}?"<br /> 
>         -   `extreme`: detects extreme keywords (highest, oldest,
>             lowest, youngest). For example: "who is the
>             {oldest|extreme} employee?"<br /> 
>         -   `date_compare`: detects date comparision key words (prior
>             to, after) For example: "Was {Ivan|name} {born|dob} {prior
>             to|date\_compare} {1990|sys\_time}?"<br /> 
>         -   `function`: detects a function type (percent, sum,
>             average, count) For example: "What {percent|function} of
>             employees are {women|sex}?"
>
> -   Custom Time Entities: <br /> 
>         -   `time_interval`: detects a decade (1980's, 80s, eighties)
>             For example: "{how many|function} employees were
>             {bron|dob} in the {eighties|time\_interval}?"<br /> 
>         -   `time_recur`: detects a recurring time interval (yearly,
>             monthly, weekly). For example: "what does {ivan|name}
>             {make|money} {monthly|time\_recur}?"<br /> 
>
>         time, amount of money, number,
>
HR assistant uses three system entities: `sys_time` (time),
`sys_amount-of-money` (money), `sys_number` (number). Some examples for
annotation with system entities: "{How many|function} employees were
{born|dob} in the {2009|sys\_time}?" and "what {fraction|function} of
employees {make|money} {less than|comparator} {69
grand|sys\_amount-of-money}?".

> **Exercise**

To train the different machine learning models in the NLP pipeline for
this app, we need labeled training data that covers all our intents and
entities. To download the data and code required to run this blueprint,
run the command below in a directory of your choice. (If you have
already completed the Quick Start for this blueprint, you should skip
this step.)

``` {.sourceCode .shell}
python -c "import mindmeld as mm; mm.blueprint('hr_assistant');"
```

This should create a Workbench project folder called `hr_assistant` in
your current directory with the following structure:

![image](custom_scripts/images/hr_assistant_directory.png)
<br /> 

4. Dialogue States
------------------

Dialogue state logic can be arbitrarily complex. Simple dialogue state
handlers just return a canned text response, while sophisticated ones
can call third party APIs, calculate state transitions, and return
complex responses.

Workbench supports three ways to organize dialogue states in the
Dialogue Manager:

1.  Define **one dialogue state for each intent**, as seen in the
    Kwik-E-Mart blueprint. This is the simplest approach, but can lead
    to duplicated code.
2.  Define **one dialogue state for multiple intents**. This requires
    more work up front, but helps you consolidate duplicated dialogue
    state logic. Example shown in the home assistant blueprint.
3.  Define **multiple dialogue states for multiple intents**. Based on
    the presence of entities, multiple dialogue states can handle a
    user's request. This is a good choice for when an intent can have a
    many possible dialogue states based on the presence of entities.

Which approach is best varies from one application to another. Figuring
that out always requires some trial and error. You can see an example of
the first two cases in the home assistant blueprint. The HR assistant
will use and discuss the third method.

Let's begin by looking at some of the dialogue states for the intents in
the `general` domain:

``` {.sourceCode .python}
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
```

Observe that the same intent has multiple dialogue states that specify a
`has_entity` field, except for the last case which serves as the default
case. In other words, Mindmeld will feed the request to the dialogue
state handler if there is a match between an entity found in the user
query and the entity that the dialogue state handler accepts. If none of
the entities are found, Mindmeld will default to the last case that does
not specify an entity. This is where the system can follow up with the
user and ask for any information needed to complete the query.

We can see this paradigm followed in the domain `salary` as well:

``` {.sourceCode .python}
@app.handle(intent='get_salary', has_entity='time_recur')
def get_salary_for_interval(request, responder):

    ...

@app.handle(intent='get_salary')
def get_salary(request, responder):

    ...
```

> **Exercise**
>
> Analyze the way the HR assistant blueprint uses this pattern
> **multiple dialogue states for multiple intents**. Why this pattern
> used instead of another?

Sometimes a dialogue state handler needs to be aware of the context from
a previous state. This happens in the **follow-up request pattern**.
Consider this conversational interaction:

``` {.sourceCode .bash}
User: Can you tell me about daniel?
App: What would you like to know about Daniel Davis?    # get_info_default
User: is he married
App: Daniel Davis is Single                             # get_info_maritaldesc
```

Observe that the first request leaves out some required information —
the type of user information to query. Therefore, in the response, the
application must ask the user for the missing information. Most
importantly, the app needs to "remember" context from the first request
(in this case the person that the user is referring to) to understand
the user's second request, in which the user specifies the information
that was missing.

Here is how the HR assistant blueprint implements this pattern:

1.  Define the `get_info` intent
2.  Define the `get_info` state (default that does not include a
    `has_entity`)

Here are the intents and states in the HR assistant blueprint, as
defined in the application dialogue handler modules in the blueprint
folder.

  -------------------------------------------------------------------------
  Intent                      Dialogue State    Dialogue State Function
                              Name              
  --------------------------- ----------------- ---------------------------
  `get_info`                  `get_info_age`    Get the age of an employee

  `get_info`                  `get_info_state`  Get the state of an
                                                employee

  `get_info`                  `get_info_marital Get the marital status of
                              desc`             an employee

  `get_info`                  `get_info_citizen Get the citizenship status
                              desc`             of an employee

  `get_info`                  `get_info_racedes Get the race of an employee
                              c`                

  `get_info`                  `get_info_perform Get the performance score
                              ance_score`       of an employee

  `get_info`                  `get_info_rft`    Get the reason for
                                                termination of an employee

  `get_info`                  `get_info_employe Get how an employee heard
                              e_source`         of the company

  `get_info`                  `get_info_positio Get the position of an
                              n`                employee

  `get_info`                  `get_info_employm Get the employment status
                              ent_status`       of an employee

  `get_info`                  `get_info_dept`   Get the department that an
                                                employee is in

  `get_info`                  `get_info_default Clarify the type of info
                              `                 requested of an employee

  `get_aggregate`             `get_aggregate`   Get aggregate information
                                                requested

  `get_employees`             `get_employees`   Get employees that meet a
                                                certain criteria

  `get_salary`                `get_salary`      Get the salary of an
                                                employee

  `get_salary_aggregate`      `get_salary_aggre Get aggregate salary
                              gate`             related information

  `get_salary_employees`      `get_salary_emplo Get employees that meet a
                              yees`             salary criteria

  `get_date`                  `get_date`        Get employees within a date
                                                range

  `get_date_range_aggregate`  `get_date_range_a Aggregate info of employees
                              ggregate`         within a date range

  `get_date_range_employees`  `get_date_range_e Get employees within a date
                              mployees`         range

  `get_hierarchy`             `get_hierarchy`   Get manager information of
                                                an employee

  `unsupported`               `unsupported`     Handle unsupported query by
                                                prompting user

  `greet`                     `greet`           Greet the user and describe
                                                functionality

  `exit`                      `exit`            Say bye to the user
  -------------------------------------------------------------------------
<br /> 

5. Knowledge Base
-----------------

The knowledge base for our HR assistant app leverages a publicly
available synthetic dataset from Kaggle
\<<https://www.kaggle.com/rhuebner/human-resources-data-set>\>\_. The knowledge base comprises one index in Elasticsearch
\<<https://www.elastic.co/products/elasticsearch>\>\_:

   - user\_data\` — information about employees

For example, here's the knowledge base entry in the `user_data` index
for the employee "Mia Brown":

``` {.sourceCode .javascript}
{
    "emp_name": "Brown, Mia",
    "id": 1103024456,
    "state": "MA",
    "dob": "1985-11-24",
    "age": 32,
    "sex": "Female",
    "maritaldesc": "Married",
    "citizendesc": "US Citizen",
    "racedesc": "Black or African American",
    "doh": "2008-10-27",
    "dot": "1800-01-01",
    "rft": "N/A - still employed",
    "employment_status": "Active",
    "department": "Admin Offices",
    "position": "Accountant I",
    "money": 28.5,
    "manager": "Brandon R. LeBlanc",
    "employee_source": "Diversity Job Fair",
    "performance_score": "Fully Meets",
    "first_name": "Mia",
    "last_name": "Brown"
}
```

Assuming that you have Elasticsearch installed, running the blueprint()
command described above should build the knowledge base for the HR
assistant app by creating the index and importing all the necessary
data. To verify that the knowledge base has been set up correctly, use
the Question Answerer \<../userguide/kb\> to query the indexes.

> **warning**
>
> Make sure that Elasticsearch is running in a separate shell before
> invoking the QuestionAnswerer. **For full functionality of the HR
> Assistant use Elasticsearch Version 5.5.3.**

``` {.sourceCode .python}
from mmworkbench.components.question_answerer import QuestionAnswerer
qa = QuestionAnswerer(app_path='user_data')
qa.get(index='user_data')[0]
```

``` {.sourceCode .console}
{
  'rft': 'N/A - still employed',
   'performance_score': 'N/A- too early to review',
   'citizendesc': 'US Citizen',
   'manager': 'Brandon R. LeBlanc',
   'sex': 'Female',
   'maritaldesc': 'Single',
   'emp_name': 'Singh, Nan ',
   'dot': '1800-01-01',
   'last_name': 'Singh',
   'racedesc': 'White',
   'money': 16.56,
   'dob': '1988-05-19',
   'employee_source': 'Website Banner Ads',
   'id': 1307059817,
   'state': 'MA',
   'employment_status': 'Active',
   'position': 'Administrative Assistant',
   'doh': '2015-05-01',
   'department': 'Admin Offices',
   'first_name': 'Nan',
   'age': 29
 }
```

> **Exercise**
>
> The blueprint comes with a pre-configured, pre-populated knowledge
> base to help you get up and running quickly. Read the User Guide
> section on Question Answerer \<../userguide/kb\> to learn how to
> create knowledge base indexes from scratch. Then, try creating one or
> more knowledge base indexes for your own data.
<br /> 

6. Training Data
----------------

The labeled data for training our NLP pipeline was created using a
combination of in-house data generation and crowdsourcing techniques.
This is a highly important multi-step process that is described in more
detail in
Step 6 \<../quickstart/06\_generate\_representative\_training\_data\> of
the Step-By-Step Guide. Be aware that at minimum, the following data
generation tasks are required:

+-------------------------------+--------------------------------------------+
| | Purpose |                   | | Question (for crowdsourced data          |
|                               | generators) | or instruction (for          |
|                               | annotators)                                |
+===============================+============================================+
| Exploratory data generation\  | "What kinds of questions would you ask a   |
| for guiding the app design    | smart HR assistant\                        |
|                               | that has access to an HR database?"        |
+-------------------------------+--------------------------------------------+
| Generate queries for          | `get_info` intent (`general` domain):\     |
| training\                     | "How would you ask for an employee's       |
| Domain and Intent Classifiers | information such as state,\                |
|                               | position, department, etc?"                |
|                               |                                            |
|                               | `get_salary` intent (`salary` domain):\    |
|                               | "How would you ask for the salary\         |
|                               | of an employee?"                           |
+-------------------------------+--------------------------------------------+
| Annotate queries\             | `get_info`: "Annotate all occurrences of\  |
| for training the Entity       | `name` and other user info entities in the |
| Recognizer                    | given query"                               |
+-------------------------------+--------------------------------------------+
| Annotate queries\             | HR Assistant does not use roles. For       |
| for training the Role         | examples please visit\                     |
| Classifier                    | the home assistant blueprint.              |
+-------------------------------+--------------------------------------------+
| Generation synonyms for       | `state` entity: "Enumerate a list of state |
| gazetteer generation\         | names"\                                    |
| to improve entity recognition | `department` entity: "What are some names  |
| accuracies                    | of\                                        |
|                               | departments at the company?"               |
+-------------------------------+--------------------------------------------+

In summary, the process is this:

1.  Start with an exploratory data generation process, collecting varied
    examples of how the end user would interact with the app.
2.  Cluster the data into different domains based on category. For
    example, the HR Assistant application has to answer questions
    regarding general information, salary, date filters, and hierarchy
    so we divide these areas into the following domains: `general`,
    `salary`, `date`, `hierarchy` (and `unsupported`).
3.  Once we establish a clear domain-intent-entity-role hierarchy,
    generate labeled data for each component in the hierarchy.

The `domains` directory contains the training data for intent
classification and entity recognition. The `entities` directory contains
the data for entity resolution. Directories are at root level in the
blueprint folder.

> **Exercise**
>
> -   Read
>     Step 6 \<../quickstart/06\_generate\_representative\_training\_data\>
>     of the Step-By-Step Guide for best practices around training data
>     generation and annotation for conversational apps. Following those
>     principles, create additional labeled data for all the intents in
>     this blueprint and use them as held-out validation data for
>     evaluating your app. You can read more about
>     NLP model evaluation and error analysis \<../userguide/nlp\> in
>     the user guide.
> -   To train NLP models for your own HR assistant application, you can
>     start by reusing the blueprint data for generic intents like
>     `get_info` and `get_salary`. If you have more information in your
>     HR database then you can create new intents and domains to include
>     the new functionality.

7. Training the NLP Classifiers
-------------------------------

Train a baseline NLP system for the blueprint app. The build() method of
the NaturalLanguageProcessor class, used as shown below, applies
Workbench's default machine learning settings.

``` {.sourceCode .python}
from mindmeld import configure_logs; configure_logs()
from mindmeld.components.nlp import NaturalLanguageProcessor
nlp = NaturalLanguageProcessor(app_path='./hr_assistant')
nlp.build()
```

``` {.sourceCode .console}
Fitting domain classifier
Loading raw queries from file hr_assistant/domains/date/get_date/train.txt
Loading raw queries from file hr_assistant/domains/date/get_date_range_aggregate/train.txt
Loading raw queries from file hr_assistant/domains/date/get_date_range_employees/train.txt
Loading raw queries from file hr_assistant/domains/general/get_aggregate/train.txt
.
.
.

 Fitting intent classifier: domain='general'
 Selecting hyperparameters using k-fold cross-validation with 5 splits
 Best accuracy: 99.51%, params: {'C': 1, 'class_weight': {0: 1.0998148148148148, 1: 0.9049019607843137, 2: 1.0234505862646566}, 'fit_intercept': True}
 Fitting entity recognizer: domain='general', intent='get_aggregate'
 No entity model configuration set. Using default.
 Selecting hyperparameters using k-fold cross-validation with 5 splits
 Best accuracy: 93.16%, params: {'C': 10000, 'penalty': 'l2'}
 .
 .
 .
```

> **tip**
>
> During active development, it helps to increase the
> Workbench logging level \<../userguide/getting\_started\> to better
> understand what is happening behind the scenes. All code snippets here
> assume that logging level is set to verbose.

To see how the trained NLP pipeline performs on a test query, use the
process method.

``` {.sourceCode .python}
nlp.process("is Mia brown in the sales department?")
```

``` {.sourceCode .console}
{'text': 'is Mia brown in the sales department?',
 'domain': 'general',
 'intent': 'get_info',
 'entities': [{'text': 'Mia brown',
   'type': 'name',
   'role': None,
   'value': [{'cname': 'Mia Brown',
     'score': 116.68605,
     'top_synonym': 'Mia Brown'},
    {'cname': 'Thelma Petrowsky',
     'score': 11.246895,
     'top_synonym': 'Petrowsky'},
    {'cname': 'Brooke Oliver', 'score': 11.212612, 'top_synonym': 'Brooke'},
    {'cname': 'Jeremiah Semizoglou',
     'score': 9.835518,
     'top_synonym': 'Jeremiah'}],
   'span': {'start': 3, 'end': 11}},
  {'text': 'sales',
   'type': 'department',
   'role': None,
   'value': [{'cname': 'sales', 'score': 33.45853, 'top_synonym': 'sales'}],
   'span': {'start': 20, 'end': 24}}]
}
```

### Inspect classifiers in baseline configuration

For the data distributed with this blueprint, the baseline performance
is already high. However, when extending the blueprint with your own
custom home assistant data, you may find that the default settings may
not be optimal and you can get better accuracy by individually
optimizing each of the NLP components.

Because the HR assistant app has five domains and over twenty intents,
the classifiers need a fair amount of fine-tuning.

Start by inspecting the baseline configurations that the different
classifiers use. The User Guide lists and describes the available
configuration options. As an example, the code below shows how to access
the model and feature extraction settings for the Intent Classifier.

``` {.sourceCode .python}
ic = nlp.domains['salary'].intent_classifier
ic.config.model_settings['classifier_type']
```

``` {.sourceCode .console}
'logreg'
```

``` {.sourceCode .python}
ic.config.features
```

``` {.sourceCode .console}
{'bag-of-words': {'lengths': [1, 2]},
 'edge-ngrams': {'lengths': [1, 2]},
 'exact': {'scaling': 10},
 'freq': {'bins': 5},
 'gaz-freq': {},
 'in-gaz': {}
}
```

You can experiment with different learning algorithms (model types),
features, hyperparameters, and cross-validation settings, by passing the
appropriate parameters to the classifier's fit method. Intent classifer
and role classifier examples follow.

### Experiment with the intent classifiers

We can change the feature extraction settings to use bag of trigrams in
addition to the default bag of words:

``` {.sourceCode .python}
ic.config.features['bag-of-words']['lengths'].append(3)
ic.fit()
```

``` {.sourceCode .console}
Fitting intent classifier: domain='salary'
Selecting hyperparameters using k-fold cross-validation with 5 splits
Best accuracy: 97.43%, params: {'C': 100, 'class_weight': {0: 0.8294469357249626, 1: 1.1142528735632182, 2: 1.1555555555555554}, 'fit_intercept': True}
```

We can also change the model for the intent classifier to Support Vector
Machine (SVM) classifier, which works well for some datasets:

``` {.sourceCode .python}
search_grid = {
   'C': [0.1, 0.5, 1, 5, 10, 50, 100, 1000, 5000],
   'kernel': ['linear', 'rbf', 'poly']
}

param_selection_settings = {
     'grid': search_grid,
     'type': 'k-fold',
     'k': 10
}

ic = nlp.domains['salary'].intent_classifier
ic.fit(model_settings={'classifier_type': 'svm'}, param_selection=param_selection_settings)
```

``` {.sourceCode .console}
Fitting intent classifier: domain='salary'
Selecting hyperparameters using k-fold cross-validation with 10 splits
Best accuracy: 96.64%, params: {'C': 1000, 'kernel': 'rbf'}
```

Similar options are available for inspecting and experimenting with the
Entity Recognizer and other NLP classifiers as well. Finding the optimal
machine learning settings is an iterative process involving several
rounds of parameter tuning, testing, and error analysis. Refer to the
NaturalLanguageProcessor \<../userguide/nlp\> in the user guide for more
about training, tuning, and evaluating the various Workbench
classifiers.

### Inspect the role classifiers

The HR assistant does not make use of the role classifiers. For an
examaple of inspecting the role classifiers please visit the home
assistant application blueprint.

### Inspect the configuration

The application configuration file, `config.py`, at the top level of the
home assistant folder, contains custom intent and domain classifier
model configurations. These are defined as dictionaries named
`DOMAIN_CLASSIFIER_CONFIG` and `INTENT_CLASSIFIER_CONFIG`, respectively;
other dictionaries include `ENTITY_RECOGNIZER_CONFIG` and
`ROLE_CLASSIFIER_CONFIG`. If no custom model configuration is added to
`config.py` file, Workbench uses its default classifier configurations
for training and evaluation. Here is an example of an intent
configuration:

``` {.sourceCode .python}
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
```

> **Exercise**
>
> Experiment with different models, features, and hyperparameter
> selection settings to see how they affect the classifier performance.
> Maintain a held-out validation set to evaluate your trained NLP models
> and analyze the misclassified test instances. Then use observations
> from the error analysis to inform your machine learning
> experimentation. For more on this topic, refer to the
> User Guide \<../userguide/nlp\>.
<br /> 

8. Parser Configuration
-----------------------

The relationships between entities in the HR assistant queries are
simple ones. For example, in the annotated query
`is {mia|name} {married|maritaldesc}?`, the `maritaldesc` entity is
self-sufficient, in that it is not described by any other entity.

If you extended the app to support queries with more complex entity
relationships, it would be necessary to specify *entity groups* and
configure the parser accordingly. For more about entity groups and
parser configurations, see the Language Parser \<../userguide/parser\>
chapter of the User Guide.

Since we do not have entity groups in the HR assistant app, we do not
need a parser configuration.
<br /> 

9. Using the Question Answerer
------------------------------

The Question Answerer \<../userguide/kb\> component in Workbench is
mainly used within dialogue state handlers for retrieving information
from the knowledge base. In the case of an HR assistant that
intelligently retrieves information from a knowledge base of employee
information a question answerer is essential. Other than the unsupported
intent, all of the intents in the HR Assistant make use of the Question
Answerer.

``` {.sourceCode .python}
from mindmeld.components import QuestionAnswerer
qa = QuestionAnswerer(app_path='hr_assistant')
users = qa.get(index='user_data')[0:3]
[user['emp_name'] for user in users]
```

``` {.sourceCode .console}
[
 "Singh, Nan",
 "Simard, Kramer",
 "Clayton, Rick"
]
```

Workbench would supports filtering the results (For example, we can
search for employees that are male, in the sales department, etc.) See
the User Guide \<../userguide/kb\> for an explanation of the retrieval
and ranking mechanisms that the Question Answerer offers.

In the case that we are trying to filter on multiple non-numeric
entities, we can do so by passing in a dictionary that contains a key
and value pair. An examaple of this is shown in the helper function for
the HR Assistant below.

``` {.sourceCode .python}
def _resolve_categorical_entities(request, responder):
  """
  This function retrieves all categorical entities as listed below and filters the knowledge base
  using these entities as filters. The final search object containing the shortlisted employee data
  is returned back to the calling function.
  """

  # Finding all categorical entities
  categorical_entities = [e for e in request.entities if e['type'] in ('state', 'sex', 'maritaldesc','citizendesc',
      'racedesc','performance_score','employment_status','employee_source','position','department')]

  # Building custom search
  qa = app.question_answerer.build_search(index='user_data')

  # Querying the knowledge base for all categorical filters
  if categorical_entities:
      try:
          for categorical_entity in categorical_entities:
              key = categorical_entity['type']
              val = categorical_entity['value'][0]['cname']
              kw = {key : val}
              qa = qa.filter(**kw) # Search is being filtered multiple times
      except:
          pass

  size = 300

  return qa, size
```

> **Exercise**
>
> -   Think of other important data that would be useful to have in the
>     knowledge base for an HR Assistant use case. Identify the ways
>     that data could be leveraged to provide a more intelligent user
>     experience.
> -   When customizing the blueprint for your own app, consider adding
>     additional employee information in the knowledge base.
<br /> 

10. Testing and Deployment
--------------------------

Once all the individual pieces (NLP, Dialogue State Handlers) have been
trained, configured or implemented, perform an end-to-end test of the
app using the Conversation class.

``` {.sourceCode .python}
from mindmeld.components.dialogue import Conversation
conv = Conversation(nlp=nlp, app_path='./hr_assistant')
conv.say('What is Elisa's marital status')
```

``` {.sourceCode .console}
['Elisa Bramante is Single']
```

The say method:

> -   packages the input text in a user request object
> -   passes the object to the Workbench Application Manager to a
>     simulate an external user interaction with the app, and
> -   outputs the textual part of the response sent by the dialogue
>     manager.

In the above example, we requested information about a particular
employee and the app responded, as expected, by identifying the employee
referenced by just the first name and the type of information requested
about the employee.

Try a multi-turn dialogue:

``` {.sourceCode .python}
>>> conv = Conversation(nlp=nlp, app_path='hr_assistant')
>>> conv.say('Tell me about Mia Brown')
['What information would you like to know about Elisa Bramante?', 'Listening...']
>>> conv.say("Who is her manager?")
["Brandon R. LeBlanc is Mia Brown's manager"]
```

If the user goes off track, or presents a query that is out of the scope
of the assistant, the app is able to recognize this and prompt the user
back to what is supported. Below is an example:

> \>\>\> conv.say("Can you give me a million dollars please?") ["Hmmm, I
> didn't quite understand. Would you like to know what you can ask me?",
> 'Listening...'] \>\>\> conv.say("Maybe.") ['Hmmm, did you mean yes or
> no?', 'Listening...'] \>\>\> conv.say("yes please") ["Great! You can
> ask me about an employee's individual information (eg. Is Ivan
> married?), some employee statistic (eg. average salary of females) or
> names of employees according to your criteria (eg. give me a list of
> all married employees)", 'Now, what would you like to know?',
> 'Listening...'] \>\>\> conv.say("What is nan singh's hourly salary?")
> ["Nan Singh's hourly salary is 16.56"]

Alternatively, enter conversation mode directly from the command-line.

``` {.sourceCode .console}
python -m hr_assistant converse
```

``` {.sourceCode .console}
You: Percent of employees earning less than 20 an hour?
App: The percent based on your query is 29.0
```

> **Exercise**
>
> Test the app and play around with different language patterns to
> discover edge cases that our classifiers are unable to handle. The
> more language patterns we can collect in our training data, the better
> our classifiers can handle in live usage with real users. Good luck
> and have fun - now you have your very own Jarvis!
