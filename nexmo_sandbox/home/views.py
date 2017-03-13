import json
from django.http import HttpResponse
from urllib import parse
from django.urls import reverse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from nexmo import ncco
import nexmo
from nexmo.ncco import d
import time
from nexmo_config import NexmoConfig
from nexmo_sandbox.home.forms import VoiceCallForm


@csrf_exempt
def view_home(request):
    test_data = {
        'phone_number': '+16475004789',
        'message': 'Sensor Point Six_B5228098_1, went out of range on 2017-02-16 9:50am eastern, in cooler, at Vaughan '
                   'valley. with alarm escalation level 1. the current Reading is 20.9°C. '
                   'Please press 1 to acknowledge, press 7 to repeat',
    }

    if request.POST:
        print(request.POST)

    form = VoiceCallForm(request, initial=test_data)
    context = {
        'form': form,
    }
    return render(request, 'home.html', context=context)


@csrf_exempt
def make_call(request):
    display_message = ''
    form = VoiceCallForm(request)

    if request.POST:
        form = VoiceCallForm(request, data=request.POST)
        if form.is_valid():
            try:
                display_message = form.submit()
            except Exception as ex:
                display_message = 'Error: %s' % ex
                raise

    context = {
        'message': display_message,
        'form': form,
    }
    return render(request, 'home.html', context)


@csrf_exempt
def outgoing_call(request):
    # response = []
    # voice = request.GET.get('voice', 'Amy')
    # message = parse.unquote_plus(request.GET.get('message', 'Hello'))
    # talk = {
    #     'action': 'talk',
    #     'text': message,
    #     'voiceName': voice,
    # }
    # response.append(talk)
    # response_json = json.dumps(response, indent=4)
    #
    # return HttpResponse(response_json, content_type='application/json')
    return synthesize_message(request)


def synthesize_message(request):
    voice = request.GET.get('voice', 'Joey')
    message = parse.unquote_plus(request.GET.get('message', ''))

    req = ncco.Request(pretty=True, sort_keys=True)
    talk = ncco.Talk(message, barge_in=True, voice_name=voice)
    req.add_action(talk)
    gather_input_url = '{url}/?{params}'.format(url=request.build_absolute_uri(reverse(gather_input)),
                                                params=parse.urlencode(request.GET.dict()))
    event_url = [gather_input_url]
    input = ncco.Input(event_url, max_digits=1, time_out=15)
    req.add_action(input)
    return req.render()


@csrf_exempt
def gather_input(request):
    rsp = ncco.Response(request.body)
    assert isinstance(rsp, ncco.Response)
    d(rsp.dict())

    dtmf = rsp.dtmf
    if dtmf == '7':
        return synthesize_message(request)

    voice_name = request.GET.get('voice', 'Joey')
    req = ncco.Request(pretty=True, sort_keys=True)

    if rsp.timed_out:
        talk = ncco.Talk('We will call back in 5 minutes. Thank you, and good bye!', barge_in=False, voice_name=voice_name)
        req.add_action(talk)
        return req.render()

    if dtmf == '1':
        talk = ncco.Talk('Thank you, and good bye!', barge_in=False, voice_name=voice_name)
        req.add_action(talk)
        return req.render()

    invalid_input = ncco.Talk('Please press 1 to acknowledge, press 7 to repeat', barge_in=True, voice_name=voice_name)
    req.add_action(invalid_input)

    event_url = [request.build_absolute_uri()]
    input = ncco.Input(event_url, max_digits=1, time_out=15)
    req.add_action(input)

    return req.render()




