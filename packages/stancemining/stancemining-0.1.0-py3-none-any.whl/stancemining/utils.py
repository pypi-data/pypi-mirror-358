import logging

from cuml import DBSCAN
from nltk.corpus import stopwords
import numpy as np
import polars as pl
import sklearn.preprocessing

def deduplicate_target_embeddings(embeddings):
    normalized_embeddings = sklearn.preprocessing.normalize(embeddings, axis=1, norm='l2')
    max_distance = 0.2
    embed_clusters = DBSCAN(eps=max_distance, metric='euclidean', algorithm='rbc', min_samples=2).fit_predict(normalized_embeddings)
    return embed_clusters

def get_similar_target_mapper(embeddings: np.ndarray, target_df: pl.DataFrame):
    assert 'count' in target_df.columns, "target_df must contain 'count' column"
    assert 'Target' in target_df.columns, "target_df must contain 'Target' column"
    assert embeddings.shape[0] == target_df.shape[0], "embeddings must match the number of targets in target_df"

    embed_clusters = deduplicate_target_embeddings(embeddings)
    target_df = target_df.with_columns(pl.Series(name='cluster', values=embed_clusters))
    primary_target_df = target_df.sort('count', descending=True).unique('cluster', keep='first').rename({'Target': 'top_target', 'count': 'top_count'})
    target_df = target_df.filter(pl.col('cluster') != -1).join(primary_target_df, on='cluster', how='inner').filter(pl.col('top_target') != pl.col('Target'))
    return {k: v for k, v in target_df.select(['Target', 'top_target']).rows()}

def remove_bad_targets(target_df: pl.DataFrame):
    phrases = [
        'the primary stance target of the piece of text is',
        'the primary stance target of this text is',
        'the primary stance target in the given text is',
        'the primary stance target of the text is',
        'the primary stance target is the noun phrase', 
        'the primary stance target of the given text is',
        'the primary stance target is',
        'stance target: 1.',
        'stance target:',
        'stance target',
        'target1',
        'target2'
    ]
    for phrase in phrases:
        target_df = target_df.with_columns(pl.col('Target').str.replace(phrase, ''))
    exclude_phrases = ['', 'url', 'rt', 'rt @', '@rt']
    target_df = target_df.with_columns(pl.col('Target').str.strip_chars('"').str.strip_chars(':').str.strip_chars())
    target_df = target_df.filter(~(pl.col('Target').str.contains('rt @\w+'))\
                              .or_(pl.col('Target').str.contains('rt \w+'))\
                              .or_(pl.col('Target').str.contains(r'^[\U0001F000-\U0001FFFF\u2600-\u26FF\u2700-\u27BF]+$'))\
                              .or_(pl.col('Target').is_in(stopwords.words('english') + stopwords.words('french')))\
                              .or_(pl.col('Target').str.to_lowercase().is_in(exclude_phrases)))
    return target_df

def get_var_and_max_var_target(documents_df: pl.DataFrame, target_info_df: pl.DataFrame) -> pl.DataFrame:
    if 'topic_id' in target_info_df.columns:
        target_info_df = target_info_df.group_by('noun_phrase')\
            .agg(pl.col('topic_id'), pl.col('polarity'))
    else:
        target_info_df = target_info_df.group_by('noun_phrase')\
            .agg(pl.col('polarity'))
    target_info_df = target_info_df.with_columns([
        pl.col('polarity').list.mean().alias('mean'),
        pl.when(pl.col('polarity').list.len() > 1)\
            .then(pl.col('polarity').list.var())\
            .otherwise(0)
            .alias('var')
    ])

    documents_df = documents_df.join(
        documents_df.explode('Targets')\
            .join(target_info_df, left_on='Targets', right_on='noun_phrase', how='left')\
            .group_by('ID')\
            .agg(pl.all().sort_by('var').last())\
            .with_columns(pl.col('Targets').alias('Target'))\
            .select(['ID', 'Target']),
        on='ID',
        how='left',
        maintain_order='left'
    )
    return documents_df, target_info_df


def filter_stance_targets(all_targets: pl.Series) -> pl.Series:
    # lower case all results
    all_targets = all_targets.list.eval(
        pl.element().str.to_lowercase().str.strip_chars().str.replace('stance target: ', '').str.replace('1. ', '').str.strip_chars().str.strip_chars('"').str.strip_chars("'")
    )
    # remove exact duplicates
    all_targets = all_targets.list.unique()
    return all_targets

def filter_phrases(target_embeds, similarity_threshold=0.9):
    # Compute cosine similarity matrix for current sublist
    embeddings = target_embeds.struct.field('embeddings').to_numpy()
    phrases_list = target_embeds.struct.field('Targets').to_list()
    norms = np.linalg.norm(embeddings, axis=1)
    similarity = np.dot(embeddings, embeddings.T) / np.outer(norms, norms)
    
    # Get upper triangular part to avoid duplicate comparisons
    similarity = np.triu(similarity, k=1)
    
    # Find indices of similar phrases within this sublist
    similar_indices = set(int(i) for i in np.where(similarity > similarity_threshold)[0])
    
    if not similar_indices:
        return phrases_list

    # Filter current sublist
    filtered_sublist = [
        phrase for j, phrase in enumerate(phrases_list)
        if j not in similar_indices
    ]
    return filtered_sublist

