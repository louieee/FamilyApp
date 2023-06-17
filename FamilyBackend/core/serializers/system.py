from rest_framework import serializers


class CustomCharField(serializers.CharField):
	def __init__(self, case=None, **kwargs):
		self.case = case
		super().__init__(**kwargs)

	def to_internal_value(self, data):
		if isinstance(data, str):
			if self.case == 'lower':
				data = data.lower()
			elif self.case == 'upper':
				data = data.upper()
			elif self.case == 'title':
				data = data.title()
		return super().to_internal_value(data)


class CustomEmailField(serializers.EmailField):
	def to_internal_value(self, data):
		data = data.lower()
		return super().to_internal_value(data)
