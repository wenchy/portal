import collections

# NOTE: Variable Injection
#
# An variable which is a dict can be injected into form "options"
# or "datalist", and it will be dynamically evaluated.
# Injection pattern: "$VAR_NAME"
FRUIT_DICT = collections.OrderedDict()
FRUIT_DICT[1] = "apple"
FRUIT_DICT[2] = "banana"
FRUIT_DICT[3] = "watermelon"


# NOTE: Function Injection
#
# A function which returns dict can be injected into form "options"
# or "datalist", and it will be dynamically evaluated.
# Injection pattern: "$FUNC_NAME"
def gen_pet_dict():
    servers = collections.OrderedDict()
    servers[10] = "cat"
    servers[20] = "dog"
    servers[30] = "pig"
    return servers