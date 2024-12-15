import pickle


def receive_chunk(request):
    length = request.recv(4)
    length_value = length[0] + 256 * (length[1] + 256 * (length[2] + 256 * (length[3])))
    content = b''
    for i in range(0, length_value, 4096):
        content += request.recv(min(4096, length_value - i))
    return pickle.loads(content)


def send_chunk(request, data):
    content = pickle.dumps(data)
    length = []
    content_length = len(content)
    for i in range(4):
        length.append(content_length % 256)
        content_length //= 256
    request.send(bytes(length))
    for i in range(0, len(content), 4096):
        request.send(content[i:i + 4096])
