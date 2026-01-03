from formtools.wizard.views import SessionWizardView

POS = {
    'ADJ': 'adjective',
    'NN': 'noun',
    'NNS': 'plural noun',
    'VB': 'verb',
    'VBD': 'verb, past tense',
    'VBG': 'verb, gerund or present participle'
}

def get_context_data(self, *args, **kwargs):
    kwargs['pk'] = self.get_object().pk
    return super().get_context_data(**kwargs)

class CommonWizard(SessionWizardView):
    many = None
    def get_template_names(self):
        return [self.templates[int(self.steps.current)]]
    def done(self, form_list, form_dict, **kwargs):
        data = do_dict(form_list)
        if self.many is not None:
            many_things = data.pop(self.many)
        thing = self.model(**data)
        thing.save()
        if self.many is not None:
            thing.quadranyms.add(*many_things)
            thing.save()
        return redirect(f'/{thing.whois()}/{thing.pk}')

class QuadrasetWizard(CommonWizard):
    templates = ['add/wiz.html', 'add/wiz.html']
    model = Quadraset
    many = 'quadranyms'
    form_list = [QuadrasetForm1, QuadrasetForm2]

def qontext_vu(request):
    quads, q1 = Quadranym.data.picks(request, 'q1_id')
    quads, q2 = Quadranym.data.picks(request, 'q2_id')
    quads, q3 = Quadranym.data.picks(request, 'q3_id')
    return render(request, 'compare/qontext.html', dict(quads=quads, q1=q1, q2=q2, q3=q3))
