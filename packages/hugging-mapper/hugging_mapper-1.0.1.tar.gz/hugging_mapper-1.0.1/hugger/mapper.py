import pandas as pd
import transformers
import torch
from sklearn.metrics.pairwise import cosine_similarity
import collections
import torch.nn.functional as F


# from pubmed_rag
def map_pooling(pooling: str):
    """
    Maps a string representing the pooling type to the corresponding pooling function.

    Parameters
    ----------
    pooling : str
        The type of pooling to be used. Must be one of 'mean_pooling' or 'attention_pooling'.

    Returns
    -------
    Callable
        The corresponding pooling function.

    Raises
    ------
    TypeError
        If the input is not a string.
    ValueError
        If the pooling type is not recognized.

    Examples
    --------
    >>> map_pooling('mean_pooling')
    <function mean_pooling at 0x...>
    >>> map_pooling('attention_pooling')
    <function attention_pooling at 0x...>
    """

    ## PRECONDITIONS
    # define options
    pooling_map = {"mean_pooling": mean_pooling, "attention_pooling": attention_pooling}
    if not isinstance(pooling, str):
        raise TypeError(f"pooling must be a str: {type(pooling)}")
    if pooling not in pooling_map:
        raise ValueError(f"pooling of {pooling} not an option in {pooling_map.keys()}")

    ## MAIN FUNCTION
    # retrieving pooling function
    pooling_function = pooling_map[pooling]
    return pooling_function


def mean_pooling(
    model_output: torch.Tensor, attention_mask: torch.Tensor
) -> torch.Tensor:
    """
    Computes the mean pooled sentence embedding from token embeddings and an attention mask.

    Given the output of a transformer model and the corresponding attention mask, this function
    calculates a single embedding vector for each sentence by averaging the token embeddings,
    taking into account only the tokens that are not masked (i.e., valid tokens).

    Parameters
    ----------
    model_output : torch.Tensor or tuple of torch.Tensor
        The output from a transformer model. The first element should contain the token embeddings
        with shape (batch_size, sequence_length, embedding_dim).
    attention_mask : torch.Tensor
        A mask indicating valid tokens (1 for valid, 0 for padding) with shape (batch_size, sequence_length).

    Returns
    -------
    torch.Tensor
        A tensor of shape (batch_size, embedding_dim) containing the mean pooled embeddings for each sentence.
    """
    token_embeddings = model_output[
        0
    ]  # First element of model_output contains all token embeddings
    input_mask_expanded = (
        attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    )
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )


def attention_pooling(
    model_output: torch.Tensor,
    attention_scores: torch.Tensor,
) -> torch.Tensor:
    """
    Applies attention-based pooling to aggregate token embeddings.
    This function computes a weighted sum of token embeddings using provided attention scores.
    The attention scores are normalized using softmax to obtain attention weights, which are
    then used to pool the token embeddings along the sequence dimension.

    Parameters
    ----------
    model_output : tuple or torch.Tensor
        The output from a model, where the first element (or the tensor itself) contains
        token embeddings of shape (batch_size, sequence_length, embedding_dim).
    attention_scores : torch.Tensor
        Attention scores for each token, of shape (batch_size, sequence_length).

    Returns
    -------
    torch.Tensor
        The pooled embeddings of shape (batch_size, embedding_dim), obtained by
        applying attention-based weighted sum over the token embeddings.
    """

    token_embeddings = model_output[0]
    # Ensure attention_scores are of type float
    attention_scores = attention_scores.float()
    attention_weights = F.softmax(attention_scores, dim=-1)
    return torch.sum(token_embeddings * attention_weights.unsqueeze(-1), dim=1)


def get_tokens(
    tokenizer: transformers.AutoTokenizer,
    input: list,
    tokenizer_kwargs: dict = dict(
        padding=True, truncation=True, return_tensors="pt", max_length=512
    ),
) -> transformers.BatchEncoding:
    """
    Encodes a list of sentences using a Hugging Face tokenizer.

    Parameters
    ----------
    tokenizer : transformers.AutoTokenizer
        The tokenizer instance from Hugging Face's `transformers` library.
    input : list or str
        A list of sentences to be tokenized.
    tokenizer_kwargs : dict
        Additional keyword arguments to pass to the tokenizer (default is
        ``{'padding': True, 'truncation': True, 'return_tensors': 'pt', 'max_length': 512}``).

    Returns
    -------
    transformers.BatchEncoding
        The encoded inputs as a `BatchEncoding` object, suitable for model input.

    Raises
    ------
    AssertionError
        If `input` is not a list of strings or if `tokenizer_kwargs` is not a dictionary.

    Examples
    --------
    >>> from transformers import AutoTokenizer
    >>> tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L12-v2')
    >>> sentences = ["dogs are happy", "cats are cute"]
    >>> encoded = get_tokens(tokenizer, sentences)
    """

    # PRECONDITION CHECKS
    if not isinstance(input, collections.abc.Iterable):
        raise TypeError(f"input must be a list of strings {input}")
    if not isinstance(tokenizer_kwargs, dict):
        raise TypeError(f"tokenizer_kwargs must be a dict: {tokenizer_kwargs}")

    # MAIN FUNCTION
    # get tokens
    encoded_input = tokenizer(input, **tokenizer_kwargs)

    return encoded_input


def get_embeddings(
    model: transformers.AutoModel,
    encoded_input: transformers.BatchEncoding,
    pooling_function=attention_pooling,
) -> torch.Tensor:
    """
    Generates sentence embeddings using a Hugging Face model and a specified pooling function.

    This function takes a pre-trained Hugging Face model and a batch of encoded sentences,
    computes their embeddings, applies a pooling function to obtain sentence-level representations,
    and normalizes the resulting embeddings.

    Parameters
    ----------
    model : transformers.AutoModel
        The Hugging Face model used to generate token embeddings.
    encoded_input : transformers.BatchEncoding
        The batch of tokenized sentences to embed.
    pooling_function : Callable
        The pooling function to aggregate token embeddings into sentence embeddings.
        Defaults to `attention_pooling`.

    Returns
    -------
    torch.Tensor
        The normalized sentence embeddings as a tensor.

    Raises
    ------
    AssertionError
        If `encoded_input` is not an instance of `transformers.BatchEncoding`.

    Examples
    --------
    >>> from transformers import AutoTokenizer, AutoModel
    >>> huggingface_model_name = 'sentence-transformers/all-MiniLM-L6-v2'
    >>> tokenizer = AutoTokenizer.from_pretrained(huggingface_model_name)
    >>> model = AutoModel.from_pretrained(huggingface_model_name)
    >>> sentences = ["dogs are happy", "cats are cute"]
    >>> encoded = get_tokens(tokenizer, sentences)
    >>> embeddings = get_embeddings(model, encoded)
    """

    # PRECONDITION CHECKS

    # MAIN FUNCTION

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)

    # Perform pooling
    sentence_embeddings = pooling_function(
        model_output, encoded_input["attention_mask"]
    )

    # Normalize embeddings
    sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

    return sentence_embeddings


class HuggingMapper:
    """
    A class for mapping text to embeddings using a Hugging Face model.
    This class provides methods to load a pre-trained model and tokenizer, embed text,
    and configure pooling methods for generating embeddings.

    Parameters
    ----------
    model_name : str
        The name of the pre-trained model to be used for generating embeddings (default is "cambridgeltl/SapBERT-from-PubMedBERT-fulltext").
    tokenizer_kwargs : dict
        Additional keyword arguments to be passed to the tokenizer (default is
        `{'padding': True, 'truncation': True, 'return_tensors': 'pt', 'max_length': 512}`).
    pooling : str
        The pooling method to be used for generating embeddings (default is "mean_pooling").

    Attributes
    ----------
    model_name : str
        The name of the pre-trained model.
    tokenizer_kwargs : dict
        The keyword arguments used for tokenization.
    pooling : str
        The pooling method used for generating embeddings.
    tokenizer : transformers.AutoTokenizer
        The pre-trained tokenizer instance.
    model : transformers.AutoModel
        The pre-trained model instance.

    Methods
    -------
    embed_text(text_input: str) -> torch.Tensor
        Embeds a given text using the pre-trained model and pooling function.
    """

    def __init__(
        self,
        model_name: str = "cambridgeltl/SapBERT-from-PubMedBERT-fulltext",
        tokenizer_kwargs: dict = dict(
            padding=True, truncation=True, return_tensors="pt", max_length=512
        ),
        pooling: str = "mean_pooling",
    ):
        # attributes
        self.model_name = model_name
        self.tokenizer_kwargs = tokenizer_kwargs
        self.pooling = pooling

        # load tokenizer and model
        print(f"Loading tokenizer for model: {self.model_name}")
        self._tokenizer = transformers.AutoTokenizer.from_pretrained(self.model_name)
        print(f"Loading model: {self.model_name}")
        self._model = transformers.AutoModel.from_pretrained(self.model_name)

    @property
    def tokenizer_kwargs(self) -> dict:
        """
        Returns the tokenizer keyword arguments used for tokenization.

        Returns
        -------
        dict
            The tokenizer keyword arguments.
        """
        return self._tokenizer_kwargs

    @tokenizer_kwargs.setter
    def tokenizer_kwargs(self, value: dict):
        """
        Sets the tokenizer keyword arguments used for tokenization.

        Parameters
        ----------
        value : dict
            The tokenizer keyword arguments to set.
        """
        if not isinstance(value, dict):
            raise TypeError(f"tokenizer_kwargs must be a dict: {type(value)}")
        self._tokenizer_kwargs = value

    @property
    def pooling(self) -> str:
        """
        Returns the pooling method used for generating embeddings.

        Returns
        -------
        str
            The pooling method.
        """
        return self._pooling

    @pooling.setter
    def pooling(self, value: str):
        """
        Sets the pooling method used for generating embeddings.

        Parameters
        ----------
        value : str
            The pooling method to set. Must be one of 'mean_pooling' or 'attention_pooling'.

        Raises
        ------
        ValueError
            If the provided pooling method is not recognized.
        """
        if value not in ["mean_pooling", "attention_pooling"]:
            raise ValueError(
                f"pooling must be 'mean_pooling' or 'attention_pooling': {value}"
            )
        self._pooling = value

    # immutable class properties
    @property
    def tokenizer(self) -> transformers.AutoTokenizer:
        """
        Returns the pre-trained tokenizer instance.

        Returns
        -------
        transformers.AutoTokenizer
            The loaded tokenizer instance.
        """
        return self._tokenizer

    @property
    def model(self) -> transformers.AutoModel:
        """
        Returns the pre-trained model instance.

        Returns
        -------
        transformers.AutoModel
            The loaded model instance.
        """
        return self._model

    def embed_text(self, text_input: str) -> torch.Tensor:
        """
        Embeds a given text using the pre-trained model and pooling function.

        Parameters
        ----------
        text : str
            The text to be embedded.

        Returns
        -------
        torch.Tensor
            The normalized embedding of the input text.
        """

        # tokenize the input text
        tokenized_input = self._tokenizer(text_input, **self.tokenizer_kwargs)

        # gen embedding
        embedding = get_embeddings(
            self._model, tokenized_input, pooling_function=map_pooling(self.pooling)
        )

        return embedding


class NodeMapper(HuggingMapper):
    """
    A class for mapping nodes to their corresponding text embeddings using a Hugging Face model.
    This class extends the HuggingMapper class to handle a DataFrame containing node IDs and their associated text.
    It provides methods to generate embeddings for each node and find similar nodes based on a given input text.

    Parameters
    ----------
    df : pandas.DataFrame
        A DataFrame containing the node IDs and their corresponding text.
    text_col : str
        The name of the column in the DataFrame that contains the text to be embedded.
    id_col : str
        The name of the column in the DataFrame that contains the node IDs (default is "id").
    model_name : str
        The name of the pre-trained model to be used for generating embeddings (default is "cambridgeltl/SapBERT-from-PubMedBERT-fulltext").
    tokenizer_kwargs : dict
        Additional keyword arguments to be passed to the tokenizer (default is
        `{'padding': True, 'truncation': True, 'return_tensors': 'pt', 'max_length': 512}`).
    pooling : str
        The pooling method to be used for generating embeddings (default is "mean_pooling").

    Attributes
    ----------
    df : pandas.DataFrame
        The DataFrame containing the node IDs and their corresponding text.
    text_col : str
        The name of the column in the DataFrame that contains the text to be embedded.
    id_col : str
        The name of the column in the DataFrame that contains the node IDs.
    mapping : dict
        A dictionary mapping node IDs to their corresponding text.
    mapping_embeddings : dict
        A dictionary mapping node IDs to their corresponding embeddings.

    Methods
    -------
    get_similar(input_text: str, threshold: float = 0.8, metric: str = "cosine") -> dict
        Finds similar items in the mapping based on a similarity threshold.
    get_match(input_text: str, threshold: float = 0.8, metric: str = "cosine") -> tuple
        Finds the best match for the input text from the mapping based on a similarity threshold.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        text_col: str,
        id_col: str = "id",
        model_name: str = "cambridgeltl/SapBERT-from-PubMedBERT-fulltext",
        tokenizer_kwargs: dict = dict(
            padding=True, truncation=True, return_tensors="pt", max_length=512
        ),
        pooling: str = "mean_pooling",
    ):
        # initialize the parent class
        super().__init__(
            model_name,
            tokenizer_kwargs,
            pooling,
        )
        # attributes
        self.df = df
        self.text_col = text_col
        self.id_col = id_col
        # for cache, not hidden
        self._mapping = self.__get_mapping()
        print(f"Generating embeddings for {len(self.mapping)} nodes ...")
        self._mapping_embeddings = self.__embed_mapping()

    @property
    def mapping(self) -> dict:
        """
        Returns the mapping of node IDs to their corresponding text.

        Returns
        -------
        dict
            A dictionary where keys are node IDs and values are the corresponding text.
        """
        return self._mapping

    @property
    def mapping_embeddings(self) -> dict:
        """
        Returns the mapping of node IDs to their corresponding embeddings.

        Returns
        -------
        dict
            A dictionary where keys are node IDs and values are the corresponding embeddings.
        """
        return self._mapping_embeddings

    # Helper methods
    def __get_mapping(self) -> dict:
        """
        Creates a mapping of node IDs to their corresponding text.

        Returns
        -------
        dict
            A dictionary where keys are node IDs and values are the corresponding text.
        """
        if self.id_col not in self.df.columns or self.text_col not in self.df.columns:
            raise ValueError(
                f"DataFrame must contain columns: {self.id_col}, {self.text_col}"
            )

        return dict(zip(self.df[self.id_col], self.df[self.text_col]))

    def __embed_mapping(self) -> dict:
        """
        Generates a dictionary mapping node IDs to their corresponding embeddings.

        This method processes each entry in `self.mapping`, tokenizes the associated text using the loaded tokenizer,
        and computes embeddings using the specified model and pooling function. The resulting embeddings are stored
        in a dictionary keyed by node IDs.

        Returns
        -------
        dict
            A dictionary where each key is a node ID and each value is the corresponding embedding vector.

        Notes
        -----
        - The tokenizer and model are loaded using internal methods.
        - Embeddings are generated using the `get_embeddings` function with a configurable pooling strategy.
        """

        return {k: self.embed_text(v) for k, v in self.mapping.items()}

        # # init
        # mapped_embeddings = {}

        # print(f"Embedding mapping: {len(self.mapping)} inputs ...")
        # for key, value in self.mapping.items():
        #     # tokenize the text
        #     tokenized = tokenizer(value, **self.tokenizer_kwargs)
        #     # embbed
        #     embeddings = get_embeddings(
        #         model,
        #         tokenized,
        #         pooling_function=map_pooling(self.pooling)
        #     )
        #     # add to the dictionary
        #     mapped_embeddings[key] = embeddings

        # return mapped_embeddings

    # Public methods
    def get_similar(
        self, input_text: str, threshold: float = 0.8, metric: str = "cosine"
    ) -> list:
        """
        Finds similar items in the mapping based on a similarity threshold.

        Parameters
        ----------
        input_text : str
            The input text to find similar items for.
        threshold : float
            The minimum similarity score required to consider an item similar (default is 0.8).
        metric : str
            The similarity metric to use for comparison (default is "cosine").

        Returns
        -------
        dict
            A dictionary containing the IDs of similar items as keys and their corresponding metadata
            (text and similarity score) as values. The dictionary is sorted in descending order by score.

        Raises
        ------
        TypeError
            If `input_text` is not a string or if `metric` is not a string.
        ValueError
            If `metric` is not one of the supported similarity metrics ("cosine" or "jaccard").

        Examples
        --------
        >>> import pandas as pd
        >>> df = pd.DataFrame({"id": ["n1", "n2"], "text": ["hello", "world"]})
        >>> mapper = NodeMapper(df, text_col='text', id_col='id')
        Loading tokenizer for model: cambridgeltl/SapBERT-from-PubMedBERT-fulltext
        Loading model: cambridgeltl/SapBERT-from-PubMedBERT-fulltext
        Generating embeddings for 2 nodes ...
        >>> similar_items = mapper.get_similar("planet", threshold=0.8, metric="cosine")
        """

        if not isinstance(metric, str):
            raise TypeError(f"metric must be a string: {type(metric)}")
        # cleaning
        metric = metric.lower().strip()
        if metric not in ["cosine", "jaccard"]:
            raise ValueError(f"metric must be 'cosine' or 'todo': {metric}")

        if metric == "cosine":
            similarity_func = cosine_similarity
        else:
            raise ValueError(f"Unsupported metric: {metric}")

        # get embedding for input text
        input_embedding = self.embed_text(input_text)

        # filter mapping dict based on similarity threshold
        matches = {
            key: {
                "text": self.mapping[key],
                "score": similarity_func(input_embedding, value).item(),
            }
            for key, value in self.mapping_embeddings.items()
            if similarity_func(input_embedding, value) >= threshold
        }
        # desc sort matches by score
        return dict(
            sorted(matches.items(), key=lambda item: item[1]["score"], reverse=True)
        )

    def get_match(
        self, input_text: str, threshold: float = 0.8, metric: str = "cosine"
    ) -> list:
        """
        Finds the best match for the input text from the mapping based on a similarity threshold.

        Parameters
        ----------
        input_text : str
            The input text to find a match for.
        threshold : float
            The minimum similarity score required to consider a match valid (default is 0.8).
        metric : str
            The similarity metric to use for comparison (default is "cosine").

        Returns
        -------
        tuple
            A tuple containing the ID of the best match and its corresponding metadata.
            The metadata includes the text of the match and its similarity score.
            If no match is found above the threshold, returns (None, None).

        Raises
        ------
        TypeError
            If `input_text` is not a string or if `metric` is not a string.
        ValueError
            If `metric` is not one of the supported similarity metrics ("cosine" or "jaccard").

        Examples
        --------
        >>> import pandas as pd
        >>> df = pd.DataFrame({"id": ["n1", "n2"], "text": ["hello", "world"]})
        >>> mapper = NodeMapper(df, text_col='text', id_col='id')
        Loading tokenizer for model: cambridgeltl/SapBERT-from-PubMedBERT-fulltext
        Loading model: cambridgeltl/SapBERT-from-PubMedBERT-fulltext
        Generating embeddings for 2 nodes ...
        >>> best_match_id, metadata = mapper.get_match("earth", threshold=0.8, metric="cosine")
        """

        # get similar items
        matches = self.get_similar(input_text, threshold, metric)

        # check if matches is empty
        if not matches:
            return None, None
        else:
            # return top match only
            top_key = list(matches.keys())[0]
            return top_key, matches[top_key]
