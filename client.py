import socket
from transformers import AutoModel, AutoTokenizer
import phe
import web
import torch
import numpy as npy
import OT.receiver as receiver
import OT.compute as compute

encoder = AutoModel.from_pretrained("sentence-transformers/gtr-t5-base").encoder
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/gtr-t5-base")


def get_embeddings(text_list):
    inputs = tokenizer(text_list, padding="max_length", truncation=True, return_tensors="pt", max_length=128)
    with torch.no_grad():
        model_output = encoder(**inputs)
        hidden_state = model_output.last_hidden_state
        embeddings = hidden_state.mean(dim=1)
    return embeddings


def perturb(v, sigma):
    noise = npy.random.normal(0, sigma, len(v))
    noised = v + noise
    return noised / npy.linalg.norm(noised)


address = "localhost"  # Can be modified
port = 11451  # Can be modified
query = input("Input your query: ")
query_embedding = get_embeddings([query])[0].numpy()  # Get the embeddings of the query
query_embedding /= npy.linalg.norm(query_embedding)
perturbed_query_embedding = perturb(query_embedding, 1e-2)

fm_slices = [range(i * 192, (i + 1) * 192) for i in range(4)]
k = 5
public_key, private_key = phe.generate_paillier_keypair()
encrypted_query_embedding = [public_key.encrypt(float(query_embedding[i])) for i in range(len(query_embedding))]
equivalence_query_embedding = perturbed_query_embedding[:]

for i in range(len(query_embedding)):
    for sl in fm_slices:
        if query_embedding[i] in sl:
            query_embedding[i] = -query_embedding[i]
            break

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((address, port))

print("Query prepared. Send to server...")
web.send_chunk(client_socket, (perturbed_query_embedding, encrypted_query_embedding, fm_slices, k))
encrypted_distances = web.receive_chunk(client_socket)
print("Received encrypted distance.")
distances = torch.tensor([private_key.decrypt(encrypted) for encrypted in encrypted_distances])
indices = torch.topk(distances, k).indices
print(f"Selected indices: {indices}")

print("Receiving chunks via OT...")
print("Receiving bulletin from server...")
n, sender_bulletin = web.receive_chunk(client_socket)
ot_receiver = receiver.Receiver(n, k, indices, sender_bulletin)
print("Sending information to server in step1...")
web.send_chunk(client_socket, ot_receiver.sent)
print("Receiving information from server in step2...")
c, received = web.receive_chunk(client_socket)
print("Decrypting data...")
result = ot_receiver.receive(c, received)
decrypted_result = [compute.num_to_string(item) for item in result]

print("Received.")
print(decrypted_result)
