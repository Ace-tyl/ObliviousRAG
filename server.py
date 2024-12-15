import socketserver
import database
import web
import OT.sender as sender
import OT.compute as compute


port = 11451
vector_list_file = "test/vectors.pkl"
text_list_file = "test/texts.pkl"
db = database.Database(vector_list_file, text_list_file)


class TCPServer(socketserver.BaseRequestHandler):
    def handle(self):
        address = self.client_address[0]
        print(f"{address}: Established a connection.")
        embedding_vector, encrypted_vector, fm_slices, k = web.receive_chunk(self.request)
        print(f"{address}: Received a query, searching in database...")
        searched_ids = db.query(embedding_vector, fm_slices, 8 * k)
        texts = db.texts(searched_ids)
        n = len(texts)
        vectors = db.vectors(searched_ids)
        print(f"{address}: {n} results searched from database, calculating encrypted distances...")
        # Calculate encrypted distances
        calculated_distances = []
        for vector in vectors:
            encrypted_distance = 0
            for i in range(len(vector)):
                encrypted_distance += encrypted_vector[i] * float(vector[i])
            calculated_distances.append(encrypted_distance)
        print(f"{address}: Encrypted distances calculated, sending to client...")
        web.send_chunk(self.request, calculated_distances)
        print(f"{address}: Encrypted distances sent, starting OT process...")
        # Use OT to send texts
        text_converted = [compute.string_to_num(text) for text in texts]
        print(f"{address}: Preparing OT sender...")
        ot_sender = sender.Sender(text_converted, n)
        print(f"{address}: OT sender prepared.")
        web.send_chunk(self.request, (n, ot_sender.bulletin))
        received = web.receive_chunk(self.request)
        web.send_chunk(self.request, ot_sender.send(received))
        print(f"{address}: OT process completed. Session ends.")


if __name__ == "__main__":
    server = socketserver.ThreadingTCPServer(("localhost", port), TCPServer)
    server.serve_forever()
