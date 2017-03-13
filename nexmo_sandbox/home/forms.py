from urllib import parse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.urls import reverse
from django.utils.translation import ugettext as _
import nexmo
from nexmo_config import NexmoConfig

# region [ Choices ]
LANG_CHOICES = (
    ('cy-GB', 'cy-GB'),
    ('da-DK', 'da-DK'),
    ('de-DE', 'de-DE'),
    ('en-AU', 'en-AU'),
    ('en-GB', 'en-GB'),
    ('en-IN', 'en-IN'),
    ('en-US', 'en-US'),
    ('es-ES', 'es-ES'),
    ('es-US', 'es-US'),
    ('fr-CA', 'fr-CA'),
    ('fr-FR', 'fr-FR'),
    ('is-IS', 'is-IS'),
    ('it-IT', 'it-IT'),
    ('nb-NO', 'nb-NO'),
    ('nl-NL', 'nl-NL'),
    ('pl-PL', 'pl-PL'),
    ('pt-BR', 'pt-BR'),
    ('pt-PT', 'pt-PT'),
    ('ro-RO', 'ro-RO'),
    ('ru-RU', 'ru-RU'),
    ('sv-SE', 'sv-SE'),
    ('tr-TR', 'tr-TR'),
)
VOICE_CHOICES = (
    ('Salli', 'Salli - en-US female'),
    ('Joey', 'Joey - en-US male'),
    ('Naja', 'Naja - da-DK femaleMads - da-DK male'),
    ('Marlene', 'Marlene - de-DE female'),
    ('Hans', 'Hans - de-DE male'),
    ('Nicole', 'Nicole - en-AU female'),
    ('Russell', 'Russell - en-AU male'),
    ('Amy', 'Amy - en-GB female'),
    ('Brian', 'Brian - en-GB male'),
    ('Emma', 'Emma - en-GB female'),
    ('Gwyneth', 'Gwyneth - en-GB-WLS female'),
    ('Geraint', 'Geraint - en-GB-WLS male'),
    ('Gwyneth', 'Gwyneth - cy-GB-WLS female'),
    ('Geraint', 'Geraint - cy-GB-WLS male'),
    ('Raveena', 'Raveena - en-IN female'),
    ('Chipmunk', 'Chipmunk - en-US male'),
    ('Eric', 'Eric - en-US male'),
    ('Ivy', 'Ivy - en-US female'),
    ('Jennifer', 'Jennifer - en-US female'),
    ('Justin', 'Justin - en-US male'),
    ('Kendra', 'Kendra - en-US female'),
    ('Kimberly', 'Kimberly - en-US female'),
    ('Conchita', 'Conchita - es-ES female'),
    ('Enrique', 'Enrique - es-ES male'),
    ('Penelope', 'Penelope - es-US female'),
    ('Miguel', 'Miguel - es-US male'),
    ('Chantal', 'Chantal - fr-CA female'),
    ('Celine', 'Celine - fr-FR female'),
    ('Mathieu', 'Mathieu - fr-FR male'),
    ('Dora', 'Dora - is-IS female'),
    ('Karl', 'Karl - is-IS male'),
    ('Carla', 'Carla - it-IT female'),
    ('Giorgio', 'Giorgio - it-IT male'),
    ('Liv', 'Liv - nb-NO female'),
    ('Lotte', 'Lotte - nl-NL female'),
    ('Ruben', 'Ruben - nl-NL male'),
    ('Agnieszka', 'Agnieszka - pl-PL female'),
    ('Jacek', 'Jacek - pl-PL male'),
    ('Ewa', 'Ewa - pl-PL female'),
    ('Jan', 'Jan - pl-PL male'),
    ('Maja', 'Maja - pl-PL female'),
    ('Vitoria', 'Vitoria - pt-BR female'),
    ('Ricardo', 'Ricardo - pt-BR male'),
    ('Cristiano', 'Cristiano - pt-PT male'),
    ('Ines', 'Ines - pt-PT female'),
    ('Carmen', 'Carmen - ro-RO female'),
    ('Maxim', 'Maxim - ru-RU male'),
    ('Tatyana', 'Tatyana - ru-RU female'),
    ('Astrid', 'Astrid - sv-SE female'),
    ('Filiz', 'Filiz - tr-TR female'),
)
# endregion


class VoiceCallForm(forms.Form):
    phone_number = forms.CharField(label=_('Phone Number'), required=True)
    voice = forms.ChoiceField(label=_('Voice'), required=True, choices=VOICE_CHOICES, initial='Joey')
    message = forms.CharField(label=_('Message'), required=True, widget=forms.Textarea)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        h = FormHelper()
        h.form_method = 'POST'
        h.form_action = reverse('make_call')
        h.add_input(Submit('submit', _('Send')))
        self.helper = h

    def p(self, o, name='', indent=1):
        if indent == 1:
            print('{} => '.format(name))
        gap = '  '
        space = gap * indent

        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, dict):
                    print('{}{}: -> {{'.format(space, k))
                    self.p(v, name, indent+1)
                    print('{}}}'.format(space))
                    continue

                if isinstance(v, list):
                    print('{}{}: ->'.format(space, k))
                    self.p(v, name, indent + 1)
                    continue

                print('{}{}:  {}'.format(space, k, v))
        elif isinstance(o, list) or isinstance(o, tuple):
            print('{}['.format(space))
            indented = gap * (indent + 1)
            for itm in o:
                print('{}{},'.format(indented, itm))
            print('{}]'.format(space))
        else:
            print('{}{}'.format(space, o))

        if indent == 1:
            print('::\n')

    def submit(self):
        data = self.cleaned_data
        phone_number = data['phone_number']

        url_param = {
            'message': data['message'],
            'voice': data['voice'],
        }
        answer_url = '{url}/?{params}'.format(
            url=self.request.build_absolute_uri(reverse('outgoing_call')),
            params=parse.urlencode(url_param)
        )

        # print(answer_url)
        # this for txt
        # client = nexmo.Client(key=NexmoConfig.api_key, secret=NexmoConfig.api_secret)

        # this require voice api, therefore need new JWT auth (need app + private key)
        client = nexmo.Client(key=NexmoConfig.api_key, secret=NexmoConfig.api_secret,
                              application_id=NexmoConfig.application_id, private_key=NexmoConfig.private_key)

        # sms_result = client.send_message({'from': NexmoConfig.from_phone, 'to': phone_number, 'text': data['message']})
        # print(sms_result)

        call_params = {
            'from': {'type': 'phone', 'number': NexmoConfig.from_phone},
            'to': [{'type': 'phone', 'number': phone_number}],
            'answer_url': [answer_url],

            'answer_method': 'POST',              # default 'GET'
            # 'machine_detection': 'hangup',        # default
            'length_timer': 60,                  # hangup after 5min, default 7200min => 2h
            'ringing_timer': 30,                  # wait 60s while ringing, default 60s
        }
        # self.p(call_params, 'Call Params')
        result = client.create_call(call_params)
        # self.p(result, 'Call Result')

        result = client.get_application(application_id=NexmoConfig.application_id)
        # self.p(result)

        return 'Voice sent!'