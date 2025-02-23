from rixmsg.example.OtherMessage import OtherMessage
from rixmsg.example.ExampleMessage import ExampleMessage

def print_other(msg):
    print('number:', msg.number)
    print('flag:', msg.flag)

def print_example(msg):
    print('number:', msg.number)
    print('word:', msg.word)
    print('flag:', msg.flag)
    print('object:')
    print_other(msg.object)
    print('array:', msg.array)
    print('static_array:', msg.static_array)
    print('array_of_words:', msg.array_of_words)
    print('static_array_of_words:', msg.static_array_of_words)
    print('array_of_objects:', msg.array_of_objects)
    print('static_array_of_objects:', msg.static_array_of_objects)

other = OtherMessage()
other.number = 1234
other.flag = True

example = ExampleMessage()
example.number = 1234
example.word = 'Hello, world!'
example.flag = True
example.object = other
example.array.append(1)
example.array.append(2)
example.array.append(3)
example.static_array[0] = 4
example.static_array[1] = 5
example.static_array[2] = 6
example.array_of_words.append('one')
example.array_of_words.append('two')
example.array_of_words.append('three')
example.static_array_of_words[0] = 'four'
example.static_array_of_words[1] = 'five'
example.static_array_of_words[2] = 'six'
example.array_of_objects.append(other)
example.array_of_objects.append(other)
example.array_of_objects.append(other)
example.static_array_of_objects[0].number = 7
example.static_array_of_objects[0].flag = False
example.static_array_of_objects[1].number = 8
example.static_array_of_objects[1].flag = True
example.static_array_of_objects[2].number = 9
example.static_array_of_objects[2].flag = False

print("Original: ")
print_example(example)

encoded = bytearray()
example.serialize(encoded)

print("\nEncoded: ")
print(encoded)

context = {'offset': 0}
decoded = ExampleMessage()
decoded.deserialize(encoded, context)

print("\nDecoded: ")
print_example(decoded)

assert example.number == decoded.number
assert example.word == decoded.word
assert example.flag == decoded.flag
assert example.object.number == decoded.object.number
assert example.object.flag == decoded.object.flag
assert example.array == decoded.array
assert example.static_array == decoded.static_array
assert example.array_of_words == decoded.array_of_words
assert example.static_array_of_words == decoded.static_array_of_words
assert len(example.array_of_objects) == len(decoded.array_of_objects)
assert len(example.static_array_of_objects) == len(decoded.static_array_of_objects)
for i in range(len(example.array_of_objects)):
    assert example.array_of_objects[i].number == decoded.array_of_objects[i].number
    assert example.array_of_objects[i].flag == decoded.array_of_objects[i].flag
for i in range(len(example.static_array_of_objects)):
    assert example.static_array_of_objects[i].number == decoded.static_array_of_objects[i].number
    assert example.static_array_of_objects[i].flag == decoded.static_array_of_objects[i].flag
print("Success!")