# -*- coding: utf-8 -*-
"""This module contains the Kwik-E-Mart workbench demo application"""
from __future__ import unicode_literals
from builtins import next

from mmworkbench import Application


app = Application(__name__)


@app.handle(intent='greet')
def welcome(context, slots, responder):
    try:
        slots['name'] = context['request']['session']['name']
        prefix = 'Hello, {name}. '
    except KeyError:
        prefix = 'Hello. '
    responder.prompt(prefix + 'I can help you find store hours '
                              'for your local Kwik-E-Mart. How can I help?')


@app.handle(intent='exit')
def say_goodbye(context, slots, responder):
    responder.reply(['Bye', 'Goodbye', 'Have a nice day.'])


@app.handle(intent='help')
def provide_help(context, slots, responder):
    prompts = ["I can help you find store hours for your local Kwik-E-Mart. For example, you can "
               "say 'Where's the nearest store?' or 'When does the Elm Street store open?'"]
    responder.prompt(prompts)


@app.handle(intent='get_store_hours')
def send_store_hours(context, slots, responder):
    active_store = None
    store_entity = next((e for e in context['entities'] if e['type'] == 'store_name'), None)
    if store_entity:
        try:
            stores = app.question_answerer.get(index='stores', id=store_entity['value']['id'])
        except TypeError:
            # failed to resolve entity

            stores = app.question_answerer.get(store_entity['text'], index='stores')
        try:
            active_store = stores[0]
            context['frame']['target_store'] = active_store
        except IndexError:
            # No active store... continue
            pass
    elif 'target_store' in context['frame']:
        active_store = context['frame']['target_store']

    if active_store:
        slots['store_name'] = active_store['store_name']
        slots['open_time'] = active_store['open_time']
        slots['close_time'] = active_store['close_time']
        responder.reply('The {store_name} Kwik-E-Mart opens at {open_time} and '
                        'closes at {close_time}.')
        return

    responder.prompt('Which store would you like to know about?')


@app.handle(intent='find_nearest_store')
def send_nearest_store(context, slots, responder):
    try:
        user_location = context['request']['session']['location']
    except KeyError:
        # request and session should always be here so assume location is the problem
        responder.reply("I'm not sure. You haven't told me where you are!")
        responder.suggest([{'type': 'location', 'text': 'Share your location'}])
        return

    stores = app.question_answerer.get(index='stores', sort='location', location=user_location)
    target_store = stores[0]
    slots['store_name'] = target_store['store_name']

    context['frame']['target_store'] = target_store
    responder.reply('Your nearest Kwik-E-Mart is located at {store_name}.')


@app.handle()
def default(context, slots, responder):
    prompts = ["Sorry, not sure what you meant there. I can help you find store hours "
               "for your local Kwik-E-Mart."]
    responder.prompt(prompts)


if __name__ == '__main__':
    app.cli()