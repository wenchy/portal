OPCODE_MIN = 0
OPCODE_READ_START = 0
OPCODE_UPDATE_START = 100
OPCODE_DELETE_START = 200
OPCODE_MAX = 300  # exclusive

# Define a range that is left-inclusive and right-exclusive
ALL = (OPCODE_MIN, OPCODE_MAX)
READ = (OPCODE_READ_START, OPCODE_UPDATE_START)
UPDATE = (OPCODE_UPDATE_START, OPCODE_DELETE_START)
DELETE = (OPCODE_DELETE_START, OPCODE_MAX)


def is_read(opcode: int) -> bool:
    min, max = READ
    return min <= opcode < max


def is_update(opcode: int) -> bool:
    min, max = UPDATE
    return min <= opcode < max


def is_delete(opcode: int) -> bool:
    min, max = DELETE
    return min <= opcode < max
