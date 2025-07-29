from collections import defaultdict
from typing import Any, DefaultDict, cast

try:
    import networkx as nx
except ImportError:
    nx = None

from django.apps import apps
from django.core.management.base import BaseCommand, CommandParser
from django.db import models

from django_data_purger.enums import DataPurgerAction
from django_data_purger.services import get_tables_with_data_purging_enabled


class Collector:
    def __init__(self, *, source_model: type[models.Model]) -> None:
        if nx is None:
            raise RuntimeError(
                "Please install networkx before using the model dependency collector."
            )

        self.source_model = source_model

        self.seen_models: set[type[models.Model]] = set()
        self.dependencies: DefaultDict[type[models.Model], set[type[models.Model]]] = (
            defaultdict(set)
        )

    def add_dependency(
        self, *, model: type[models.Model], dependency: type[models.Model]
    ) -> None:
        self.dependencies[model].add(dependency)

    def collect(self, *, model: type[models.Model]) -> None:
        child_relations = (
            rel
            for rel in model._meta.get_fields(include_hidden=True)
            if rel.auto_created
            and not rel.concrete
            and (rel.one_to_one or rel.one_to_many)
        )

        for rel in child_relations:
            related_model = cast(type[models.Model], rel.related_model)

            if model == related_model:
                continue

            if not related_model:
                continue

            self.add_dependency(model=model, dependency=related_model)

            if related_model not in self.seen_models:
                self.seen_models.add(related_model)
                self.collect(model=related_model)

    def calculate_affected_models(self) -> int:
        affected_models: set[type[models.Model]] = set()

        for dependencies in self.dependencies.values():
            affected_models |= dependencies

        return len(affected_models)

    def calculate_dependency_ordering(self) -> list[list[type[models.Model]]]:  # noqa
        # Grab a copy of the dependencies, we remove items from it while
        # calculate the depencency ordering.
        dependencies = self.dependencies.copy()

        delete_batches: list[list[type[models.Model]]] = []

        while dependencies:
            models_to_delete: set[type[models.Model]] = set()
            current_batch: set[type[models.Model]] = set()

            for parent, model_dependencies in dependencies.items():
                all_models = {parent, *list(model_dependencies)}

                for model in all_models:
                    # We can't delete the model if it exists as a key in
                    # the dependencies mapping.
                    if model in dependencies.keys():
                        continue

                    # It's safe to add the model to the current batch of models that
                    # can be deleted independently of each other.
                    current_batch.add(model)

                    # Remove the model from the dependency tree.
                    for deps in dependencies.values():
                        try:
                            deps.remove(model)
                        except KeyError:
                            pass

                    # Models without any dependencies left can be deleted from
                    # the dependency tree.
                    for model_to_delete, deps in dependencies.items():
                        if not deps:
                            models_to_delete.add(model_to_delete)

                    # Circular dependencies where only models form the circle exists
                    # as dependencies has to be removed.
                    edges = [[k, v] for k, items in dependencies.items() for v in items]
                    graph = nx.DiGraph(edges)
                    cycles = nx.simple_cycles(graph)

                    for cycle in cycles:
                        cycle_set = set(cycle)
                        for _model, _dependencies in dependencies.items():
                            if _model in cycle and _dependencies.issubset(cycle_set):
                                models_to_delete.add(_model)

            # Add the current batch of models to the result.
            delete_batches.append(list(current_batch))

            # Remove the models without any dependences left from the dependency tree
            # before calculating the next batch.
            for model in models_to_delete:
                del dependencies[model]

        return delete_batches

    def print_dependency_results(self) -> None:
        def get_model_name(model: type[models.Model]) -> str:
            return f"{model._meta.app_label}.{model._meta.object_name}"

        for model, dependencies in self.dependencies.items():
            print(f"The following models depend on {get_model_name(model)}:")
            for dependency in dependencies:
                print(f"- {get_model_name(dependency)}")
            print()

        print()
        print("==============")
        print()

        print(
            f"{self.calculate_affected_models()} models depend "
            f"on {get_model_name(self.source_model)}."
        )

        print()
        print("==============")
        print()

        print(
            f"The models have to be deleted in the following order "
            f"before you can delete {get_model_name(self.source_model)}:"
        )
        print("(Models from each batch can be deleted in an arbitrary order.)")
        print()

        batches = self.calculate_dependency_ordering()
        tables_with_purging = get_tables_with_data_purging_enabled(
            action=DataPurgerAction.DELETE
        )

        for i, batch in enumerate(batches):
            print(f"Batch {i + 1}:")
            for model in batch:
                model_name = get_model_name(model)
                print(
                    "- "
                    + ("✅" if model_name in tables_with_purging else "🛑")
                    + f"  {model_name}"
                )

            print()


class Command(BaseCommand):
    help = "List models depending on the input model"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--model", required=True)

    def handle(self, *args: Any, **options: Any) -> None:
        model_full_name = options["model"]
        app_label, model_name = model_full_name.split(".")

        model = apps.get_model(app_label=app_label, model_name=model_name)

        collector = Collector(source_model=model)
        collector.collect(model=model)
        collector.print_dependency_results()
