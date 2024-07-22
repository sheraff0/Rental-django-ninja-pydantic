from box import Box
import json

RECOMMENDED_PRODUCT_FORMATS = (
    (100000, 'личная работа, наставничество'),
    #(100000, 'личная работа, наставничество, консультации и т.д.'),
    (10000, 'курс, мастермайнд, интенсив'),
    (0, 'воркбук, гайд, марафон, вебинар'),
    #(0, 'воркбук, гайд, марафон, вебинар, мастер-класс, подписка на клуб'),
)


def get_recommended_format(average_ticket):
    return next(text for threshold, text in RECOMMENDED_PRODUCT_FORMATS if average_ticket > threshold)


def is_box(data):
    return Box in [data.__class__, *data.__class__.__bases__]


def exclude_key(k):
    return k.startswith("__") or k in ["VERSION", "DEFAULTS"]


class EvalBox(Box):
    def _eval(self, data):
        if is_box(data):
            locals().update(self)
            if data != self:
                locals().update(data)
            for k in data:
                if k.startswith("__"):
                    value = data[k]
                    try:
                        value = eval(value)
                    except:
                        value = None
                    data[k] = value
                    locals()[k] = value
                else:
                    self._eval(data[k])

    def eval(self):
        self._eval(self)
        return self

    def _blank(self, data, exclude=True, clear=True):
        for k in [*data.keys()]:
            if exclude_key(k):
                if exclude:
                    data.pop(k)
            else:
                if is_box(data[k]):
                    self._blank(data[k], exclude=exclude, clear=clear)
                elif clear:
                    data[k] = None
        for k in [*data.keys()]:
            if data[k] == {}:
                data.pop(k)

    def blank(self, exclude=True, clear=True):
        self._blank(self, exclude=exclude, clear=clear)
        return self

    def _fill(self, data, form_data):
        for k in form_data.keys():
            if (k in data) and not exclude_key(k):
                if is_box(form_data[k]):
                    self._fill(data[k], form_data[k])
                else:
                    data[k] = form_data[k]

    def fill(self, form_data: Box):
        self._fill(self, form_data)
        return self


class EvalMixin:
    @property
    def result(self) -> dict:
        try:
            #assert self.finalized
            schema = EvalBox(json.loads(self.schema))
            data = Box(json.loads(self.data))
            schema.blank(exclude=False)
            # if self.project.user.is_verified:
            if True:
                schema.fill(data)
            schema.eval()
            return schema.to_dict()
        except:
            return {}
