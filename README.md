# HacktoberfestES Bot

A simple Discord bot to help with event registration processes.

## Install and Configuration

Setup the requirements:

```
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

a `config.ini` file is needed to handle all the configurations
regarding the bot, channel restrictions, files with the event
participant, etc:

```
[DEFAULT]
Token=
Guild=
Channel=
AdminChannel=
Role=
List=
```

Each field refers to the following:

* **Token** - Bot token
* **Guild** - Server ID
* **Channel** - Channel to allow the `!registro` command
* **AdminChannel** - Channel to allow the `!estado` command
* **Role** - Role to assign new users after a successfully registration
* **List** - CVS with all the participant information, and "Order ID" numeric
  column is used here, but it can be adapted to a different field.


