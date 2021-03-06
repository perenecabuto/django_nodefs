from nodefs.lib.shortcuts import profile, absnode
from nodefs.lib.selectors import StaticSelector
from selectors import ModelSelector, ModelFileSelector
from models import Thing, BoxOfThings


schema = {
    'default': profile([
        absnode(StaticSelector('simple_things'), [
            absnode(ModelSelector(projection='%(label)s', model_class=Thing)),
        ]),

        absnode(StaticSelector('nested_things'), [
            absnode(ModelSelector(projection='%(create_date.year)d', model_class=Thing), [
                absnode(ModelSelector(projection='%(create_date.month)d', model_class=Thing), [
                ]),
            ]),
        ]),

        absnode(StaticSelector('boxes_of_things'), [
            absnode(ModelSelector(projection='%(serial_number)s', model_class=BoxOfThings), [
                absnode(ModelSelector(projection='%(label)s', model_class=Thing), [
                    absnode(ModelFileSelector(projection='%(content_file)s', file_field_name='content_file', model_class=Thing)),
                ]),
            ])
        ]),
    ])
}
