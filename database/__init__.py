import torch
import numpy as npy
import pickle


class Database(object):
    """
    A database class that stores embedding vectors and texts.
    """
    def __init__(self, vector_list_file, text_list_file, dtype=torch.float16, dtype_cpu=torch.float32, device='cuda'):
        """
        Initializes the database with given file
        :param vector_list_file: A pickle file containing a list of embedding vectors. Torch or numpy tensors are allowed.
        :param text_list_file: A pickle file containing a list of texts, must be list of str
        :param dtype: The type of elements in embedding vectors
        :param dtype_cpu: The type of elements in embedding vectors in CPU
        :param device: The device where the database is stored
        """
        with open(vector_list_file, 'rb') as f:
            self.database = pickle.load(f)
            # The type of database is a numpy array
            # Convert to torch tensor
            if type(self.database) is npy.ndarray:
                self.database = torch.from_numpy(self.database).type(dtype)
            # The type of database is a list
            # Convert to torch tensor
            if type(self.database) is list:
                self.database = torch.tensor(npy.array(self.database), dtype=dtype)
            # If the type of tensor does not match dtype
            # Convert the type of tensor
            if self.database.dtype != dtype:
                self.database = self.database.type(dtype)

        with open(text_list_file, 'rb') as f:
            self.text_list = pickle.load(f)

        if len(self.database) != len(self.text_list):
            raise ValueError("The length of embedding vectors list and text list do not match")

        self.m = len(self.database)
        self.database = self.database.to(device).T.contiguous()
        self.dtype = dtype
        self.dtype_cpu = dtype_cpu
        self.device = device
        self.dim = len(self.database)

    def query(self, query_vector, fm_slices, kp, candidate=4096):
        """
        Make the query on the database. Returns the IDs of the result.
        :param query_vector: The vector to query
        :param fm_slices: The slices of dimensions in the Flipping Method
        :param kp: The number of results returned for each vector in the equivalence class
        :param candidate: The number of candidates after the first stage
        :return: The list of IDs of the result
        """
        query = torch.tensor(query_vector, dtype=self.dtype, device=self.device)
        temp_results = []
        results = torch.zeros(self.m, dtype=self.dtype, device=self.device)

        # Stage 1
        for sl in fm_slices:
            current_result = query[sl] @ self.database[sl]
            temp_results.append(current_result)
            results += torch.abs(current_result)
        result = results.topk(candidate).indices

        # Stage 2
        # This stage is performed on CPU
        for i in range(len(temp_results)):
            temp_results[i] = temp_results[i][result].type(self.dtype_cpu).cpu()
        distance = torch.zeros(candidate, dtype=self.dtype_cpu)
        for i in range(len(temp_results)):
            distance += temp_results[i]
        result = result.cpu()
        num = 0
        returned_result = list(result[distance.topk(kp).indices].numpy())
        for i in range(1, 2**len(fm_slices)):
            operate_bit = ((i & -i) - 1).bit_count()
            if num & (1 << operate_bit):
                distance += temp_results[operate_bit] * 2
            else:
                distance -= temp_results[operate_bit] * 2
            num ^= (1 << operate_bit)
            returned_result += list(result[distance.topk(kp).indices].numpy())
        return list(set(returned_result))

    def vectors(self, ids):
        """
        Return the list of vectors corresponding to the ids
        :param ids: The IDs of the vectors
        :return: The list of vectors, returned in torch.tensor
        """
        return self.database.T[ids].type(self.dtype_cpu).cpu()

    def texts(self, ids):
        """
        Return the list of texts corresponding to the ids
        :param ids: The IDs of the texts
        :return: The list of texts
        """
        result = []
        for i in ids:
            result.append(self.text_list[i])
        return result
