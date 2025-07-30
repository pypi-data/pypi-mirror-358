# %% [markdown]
# # NodeMapper tutorial
#
# Returning node ids based on similarity of text embeddings.
#
# Start by importing `NodeMapper`

# %%
# from hugger import *
from hugger.mapper import NodeMapper

# %% [markdown]
# Demo data for the tutorial

# %%
# An example dataframe
import pandas as pd

# generate data
ids = ["id1", "id2", "id3", "id4", "id5"]
texts = [
    "happy",
    "doughnut",
    "green",
    "sad",
    "foundation",
]
# to dataframe
df = pd.DataFrame({"id": ids, "text": texts})

# %% [markdown]
# Initializing `NodeMapper` will
# - load the given huggingface model
# - generate embeddings for the text column
# - creating a dictionary of the node ids : text embeddings

# %%
# init
mapper = NodeMapper(
    df=df,
    text_col="text",
    id_col="id",
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

# %% [markdown]
# Like `HuggingMapper` can simply get embeddings for given text

# %%
# generate embedding for a single text
embedding = mapper.embed_text("Good morning")
print(embedding.shape)

# generate embeddings for a list of texts
embeddings = mapper.embed_text(["Hello world", "Good evening", "Lunch time!"])
print(embeddings.shape)

# %% [markdown]
# But the main purpose of `NodeMapper` is to find similar texts and their corresponding ids

# %%
# retrieve those most similar to given text, above threshold
mapper.get_similar("concrete", threshold=0)  # threshold 0 returns all

# %%
# retrieve top match, above threshold
print(mapper.get_match("joyful", threshold=0.5), "\n")
print(mapper.get_match("concrete", threshold=0.5), "\n")
print(mapper.get_match("donut", threshold=0.5), "\n")
