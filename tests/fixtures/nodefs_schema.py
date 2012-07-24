# -*- coding: utf-8 -*-

from nodefs.lib.shortcuts import profile, absnode
from models import Thing, BoxOfThings

from nodefs.lib.selectors import StaticSelector
from django_nodefs.selectors import ModelSelector, ModelFileSelector, QuerySetSelector


schema = {
    'default': profile([

        absnode(StaticSelector('boxes_of_things'), [
            absnode(ModelSelector(projection='%(serial_number)s', model_class=BoxOfThings), [
                absnode(ModelSelector(projection='%(label)s', model_class=Thing), [
                    absnode(ModelFileSelector(projection='%(content_file)s', file_field_name='content_file', model_class=Thing), writable=True),
                ]),
            ]),
        ]),

        absnode(StaticSelector('simple_things'), [
            absnode(ModelSelector(projection='%(label)s', model_class=Thing)),
        ]),

        absnode(StaticSelector('nested_things'), [
            absnode(ModelSelector(projection='%(create_date.year)d', model_class=Thing), [
                absnode(ModelSelector(projection='%(create_date.month)d', model_class=Thing), [
                ]),
            ]),
        ]),

        absnode(StaticSelector('pre_filtered_things'), [
            absnode(StaticSelector('first_things'), [
                absnode(
                    QuerySetSelector('%(label)s', query_set=Thing.objects.filter(label__icontains='First')), [
                        absnode(ModelFileSelector(projection='%(content_file)s', file_field_name='content_file', model_class=Thing), writable=True),

                        absnode(ModelSelector('_%(serial_number)s', model_class=BoxOfThings), [
                            absnode(QuerySetSelector('%(label)s', query_set=Thing.objects.exclude(box__thing__label__icontains='First'), append=False), [
                            ]),
                        ]),
                    ]
                ),
            ]),

            absnode(StaticSelector('repeated_things'), [
                absnode(
                    QuerySetSelector('%(label)s', query_set=Thing.objects.filter(label__icontains='RepeatedThingLabel')), [
                        absnode(ModelFileSelector(projection='%(content_file)s', file_field_name='content_file', model_class=Thing), writable=True),
                    ]
                )
            ]),
        ])
    ]),
}

