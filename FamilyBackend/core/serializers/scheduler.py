from rest_framework import serializers

from core.models import Pipeline, Stage, Task
from core.serializers.system import CustomCharField
from core.serializers.user import UserSerializer


class PipelineSerializer(serializers.ModelSerializer):
	title = CustomCharField(case="title")

	class Meta:
		model = Pipeline
		fields = "__all__"

	def validate(self, attrs):
		pipeline = Pipeline.objects.filter(family=attrs.get('family'), title__iexact=attrs.get("title"))
		pipeline = pipeline.exclude(id=self.instance.id) if self.instance else pipeline
		if pipeline.exists():
			raise serializers.ValidationError("A pipeline with this title exists already")
		return attrs


class StageSerializer(serializers.ModelSerializer):
	title = CustomCharField(case="title")

	class Meta:
		model = Stage
		fields = "__all__"

	def validate(self, attrs):
		pipeline = attrs.get("pipeline")
		pipeline = self.instance.pipeline if self.instance and not pipeline else pipeline
		if pipeline and "title" in attrs:
			stage = Stage.objects.filter(pipeline=pipeline, title__iexact=attrs.get("title"))
			stage = stage.exclude(id=self.instance.id) if self.instance else stage
			if stage.exists():
				raise serializers.ValidationError("A stage with this title exists already")
		return attrs


class CreateTaskSerializer(serializers.ModelSerializer):
	title = CustomCharField(case="title")
	auto_move = serializers.BooleanField(required=False)
	auto_done = serializers.BooleanField(required=False)
	done = serializers.BooleanField(required=False)
	repeat = serializers.BooleanField(required=False)

	class Meta:
		model = Task
		exclude = ("creator",)

	def validate(self, attrs):
		attrs['creator'] = self.context.get("user")
		stage = attrs.get("stage")
		stage = self.instance.stage if self.instance and not stage else stage
		if "title" in attrs and stage:
			task = Task.objects.filter(stage=stage, title__iexact=attrs.get("title"))
			task = task.exclude(id=self.instance) if self.instance else task
			if task.exists():
				raise serializers.ValidationError("A task with this title already exists")
		auto_move = attrs.get("auto_move")
		auto_move = self.instance.auto_move if self.instance and not auto_move else auto_move
		repeat = attrs.get("repeat")
		repeat = self.instance.repeat if self.instance and not repeat else repeat
		if auto_move and repeat and auto_move is True and repeat is True:
			raise serializers.ValidationError("A task can either be on repeat or auto move but not both")
		return attrs


class TaskSerializer(serializers.ModelSerializer):
	creator = UserSerializer(read_only=True)
	assignees = UserSerializer(read_only=True, many=True)
	stage = StageSerializer(read_only=True)

	class Meta:
		model = Task
		fields = "__all__"
