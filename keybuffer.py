from ordered_set import OrderedSet

class KeyBuffer:
    def __init__(self, maxsize=10):
        self._key_buffer = []
        self._maxsize = maxsize

    def push(self, value):
        while len(self._key_buffer) >= self._maxsize:
            del self._key_buffer[0]
        self._key_buffer.append(value)

    def shift(self):
        if len(self._key_buffer) == 0:
            return
        del self._key_buffer[0]

    def get_pressed_key(self):
        kind = OrderedSet(self._key_buffer)
        if -1 in kind:
            kind.remove(-1)
            if len(kind) > 0:
                return kind[-1]
            else:
                return -1
        else:
            if len(kind) > 0:
                return kind[-1]
            else:
                return None