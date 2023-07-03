from django.db.models import Q
from rest_framework import serializers

from core.models import TimeTable, Item, Row, Column, RowTypes
from core.serializers.system import CustomCharField


class TimeTableSerializer(serializers.ModelSerializer):
	title = CustomCharField(case="title")

	class Meta:
		model = TimeTable
		exclude = ("creator",)

	def validate(self, attrs):
		family = attrs.get("family")
		family = self.instance.family if not family and self.instance else family
		if "title" in attrs and family:
			timetable = TimeTable.objects.filter(title__iexact=attrs.get("title"), family=family)
			timetable = timetable.exclude(id=self.instance.id) if self.instance else timetable
			if timetable.exists():
				raise serializers.ValidationError("A timetable with this title exists already")
		return attrs


class RowSerializer(serializers.ModelSerializer):
	class Meta:
		model = Row
		fields = "__all__"

	def validate(self, attrs):
		timetable = attrs.get("timetable")
		timetable = self.instance.timetable if not timetable and self.instance else timetable
		if "title" in attrs and timetable:
			row = Row.objects.filter(title__iexact=attrs.get("title"), timetable=timetable)
			row = row.exclude(id=self.instance.id) if self.instance else row
			if row.exists():
				raise serializers.ValidationError("A row with this title exists already")
		return attrs


class ColumnSerializer(serializers.ModelSerializer):
	class Meta:
		model = Column
		fields = "__all__"

	def validate(self, attrs):
		timetable = attrs.get("timetable")
		timetable = self.instance.timetable if not timetable and self.instance else timetable
		if "title" in attrs and timetable:
			column = Column.objects.filter(title__iexact=attrs.get("title"), timetable=timetable)
			column = column.exclude(id=self.instance.id) if self.instance else column
			if column.exists():
				raise serializers.ValidationError("A column with this title exists already")
		if "start_time" in attrs:
			column = Column.objects.filter(Q(start_time=attrs.get("start_time")) |
			                               Q(start_time__lte=attrs.get("start_time"),
			                                 end_time__gt=attrs.get("start_time")))
			column = column.exclude(id=self.instance.id) if self.instance else column
			if column.exists():
				raise serializers.ValidationError("The start time clashes with other columns")
		if "end_time" in attrs:
			column = Column.objects.filter(Q(end_time=attrs.get("end_time")) |
			                               Q(start_time__lt=attrs.get("end_time"), end_time__gte=attrs.get("end_time")))
			column = column.exclude(id=self.instance.id) if self.instance else column
			if column.exists():
				raise serializers.ValidationError("The end time clashes with other columns")
		end_time = attrs.get("end_time")
		end_time = self.instance.end_time if not end_time and self.instance else end_time
		start_time = attrs.get("start_time")
		start_time = self.instance.start_time if not start_time and self.instance else start_time
		least_start_time = Column.objects.filter(timetable__timed_column=True, timetable=timetable)
		least_start_time = least_start_time.exclude(id=self.instance) if self.instance else least_start_time
		least_start_time = least_start_time.order_by("start_time").first()
		if least_start_time and end_time:
			duration = end_time - least_start_time
		elif start_time and end_time:
			duration = end_time - start_time
		else:
			duration = None
		if duration:
			if duration.min > 1440 and timetable.row_type == RowTypes.DAY:
				raise serializers.ValidationError("The end date has exceeded one day")
			elif duration.days > 7 and timetable.row_type == RowTypes.WEEK:
				raise serializers.ValidationError("The end date has exceeded one week")
			elif duration.days > 31 and timetable.row_type == RowTypes.MONTH:
				raise serializers.ValidationError("The end date has exceeded one month")
			elif duration.days > 366 and timetable.row_type == RowTypes.YEAR:
				raise serializers.ValidationError("The end date has exceeded one year")
		return attrs


class ItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = Item
		fields = "__all__"

