# %% [markdown]
# # HuggingMapper tutorial
#
# Getting Embeddings.
#
# Start by importing `HuggingMapper`

# %%
# from hugger import *
from hugger.mapper import HuggingMapper

# %% [markdown]
# Initializing `HuggingMapper` will load the given huggingface model

# %%
# init
mapper = HuggingMapper(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

# %% [markdown]
# Get embeddings for given text

# %%
# generate embedding for a single text
embedding = mapper.embed_text("Good morning")
print(embedding.shape)

# generate embeddings for a list of texts
embeddings = mapper.embed_text(["Hello world", "Good evening", "Lunch time!"])
print(embeddings.shape)
