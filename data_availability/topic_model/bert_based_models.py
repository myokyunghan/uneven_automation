import pandas as pd
from torch import cuda
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bertopic import BERTopic
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from transformers.pipelines import pipeline
from preprocess import Preprocessor
from sentence_transformers import SentenceTransformer




def get_components_from_config(model_config):
    """

    Args:
        model_config: a dict

    Returns:
        a tuple of (nr_topics, vectorizer, clustering)
    """
    nr_topics = model_config["nr_topics"]

    if model_config["clustering"] is None:
        clustering = None
    else:
        if model_config["clustering"]["name"] == "kmeans":
            clustering = KMeans(
                n_clusters=model_config["clustering"]["n_clusters"]
            )
        else:
            raise ValueError(f'Clustering algorithm not supported:'
                             f' {model_config["clustering"]["name"]}')

    if model_config["vectorizer"] is None:
        vectorizer = None
    elif model_config["vectorizer"] == "CountVectorizer":
        vectorizer = CountVectorizer(stop_words='english')
    else:
        raise ValueError(f'Vectorizer not supported: '
                         f'{model_config["vectorizer"]}')
    
    if model_config["embedding_model"] is None:
        embedding_model = None
    elif model_config["embedding_model"] == 'all-MiniLM-L6-v2':
        embedding_model = SentenceTransformer(model_config["embedding_model"])
    else:
        raise ValueError(f'embedding_model not supported: '
                         f'{model_config["embedding_model"]}')

    return nr_topics, vectorizer, clustering, embedding_model


def load_bert_based_model_from_config(model_config):
    """

    Args:
        model_config: a dict

    Returns:
        a Bert-based topic model instance
    """
    nr_topics, vectorizer, clustering, embedding_model = get_components_from_config(
        model_config)
    if model_config["model_type"] == "text":
        to_return = TextBERTopicModel(
            nr_topics=nr_topics,
            vectorizer=vectorizer,
            clustering=clustering,
            embedding_model=embedding_model
        )
    elif model_config["model_type"] == "code":
        if cuda.is_available():
            device = "cuda:0"
        else:
            device = None
        to_return = CodeBERTopicModel(
            nr_topics=nr_topics,
            vectorizer=vectorizer,
            clustering=clustering,
            device=device
        )
    else:
        raise ValueError("Model type not supported")
    return to_return


class TextBERTopicModel:
    def __init__(self, nr_topics=None, vectorizer=None, clustering=None, embedding_model=None):
        self.preprocessor = Preprocessor()
        self.topic_model = BERTopic(verbose=True,
                                    nr_topics=nr_topics,
                                    vectorizer_model=vectorizer,
                                    hdbscan_model=clustering,
                                    embedding_model = embedding_model)

    def __call__(self, list_):
        """

        Args:
            list_: a list of dict

        Returns:
            a pandas DataFrame
        """
        to_return = self.run_model(list_)
        return to_return

    def _preprocess(self, list_):
        """

        Args:
            list_: a list of dict

        Returns:
            a list of str
        """
        to_return = self.preprocessor.prep_text_model_input(list_)
        return to_return

    def get_topic_info(self):
        """

        Returns:
            a list of dict
        """
        to_return = self.topic_model.get_topic_info()
        to_return = to_return.to_dict(orient="records")
        return to_return

    def _get_document_info(self, docs, df=None, metadata=None):
        """

        Args:
            docs: a list of str
            df: a pandas DataFrame
            metadata: a dict

        Returns:
            a pandas DataFrame
        """
        return self.topic_model.get_document_info(docs, df, metadata)

    def run_model(self, list_):
        """

        Args:
            list_: a list of dict

        Returns:
            tuple of list of topics and their probabilities
        """
        model_input = self._preprocess(list_)
        to_return = self.topic_model.fit_transform(model_input)
        return to_return

    def run_model_and_get_output_list(self, list_, fit_list=None):
        """

        Args:
            list_: a list of dict
            fit_list: a list of dict, optional

        Returns:
            a list of dict
        """
        model_input = self._preprocess(list_)
        if fit_list is not None:
            print(f"fit and transform seperately; fitting with len {len(fit_list)}")
            print(f"after that, transform would be done on len {len(model_input)}")
            model_input_for_fit = self._preprocess(fit_list)
            self.topic_model.fit(model_input_for_fit)
            topic_prediction, _ = self.topic_model.transform(model_input)
            to_return = pd.DataFrame(list_)
            to_return["Document"] = model_input
            to_return["Topic"] = topic_prediction
        else:

            self.topic_model.fit_transform(model_input)
            to_return = self._get_document_info(docs=model_input,
                                                df=pd.DataFrame(list_))
        to_return = to_return[["id", "creationdate", "title", "tags", "body",
                               "Document", "Topic"]]
        to_return = to_return.to_dict(orient="records")
        return to_return


class CodeBERTopicModel:
    def __init__(
            self,
            nr_topics=None,
            vectorizer=None,
            clustering=None,
            device=None
    ):
        self.preprocessor = Preprocessor()
        self.embedding_model = pipeline(task="feature-extraction",
                                        model="microsoft/codebert-base",
                                        device=device)
        self.topic_model = BERTopic(verbose=True,
                                    nr_topics=nr_topics,
                                    vectorizer_model=vectorizer,
                                    hdbscan_model=clustering,
                                    embedding_model=self.embedding_model)

    def __call__(self, list_):
        """

        Args:
            list_: a list of dict

        Returns:
            a pandas DataFrame
        """
        to_return = self.run_model(list_)
        return to_return

    def _preprocess(self, list_):
        """

        Args:
            list_: a list of dict

        Returns:
            a list of str
        """
        to_return = self.preprocessor.prep_code_model_input(list_)
        return to_return

    def get_topic_info(self, id_=None):
        """

        Args:
            id_: an int or None

        Returns:
            a list of dict
        """
        to_return = self.topic_model.get_topic_info(id_)
        to_return = to_return.to_dict(orient="records")
        return to_return

    def _get_document_info(self, docs, df=None, metadata=None):
        """

        Args:
            docs: a list of str
            df: a pandas DataFrame
            metadata: a dict

        Returns:
            a pandas DataFrame
        """
        return self.topic_model.get_document_info(docs, df, metadata)

    def run_model(self, list_):
        """

        Args:
            list_: a list of dict

        Returns:
            a tuple of list of topics and their probabilities
        """
        model_input, _ = self._preprocess(list_)
        to_return = self.topic_model.fit_transform(model_input)
        return to_return

    def run_model_and_get_output_list(self, list_):
        """

        Args:
            list_: a list of dict

        Returns:
            a list of dict
        """
        model_input, source_list = self._preprocess(list_)
        self.topic_model.fit_transform(model_input)
        to_return = self._get_document_info(docs=model_input,
                                            df=pd.DataFrame(source_list))
        to_return = to_return[["id", "creationdate", "title", "tags", "body",
                               "Document", "Topic"]]
        to_return = to_return.to_dict(orient="records")
        self.topic_model.visualize_topics()
        return to_return
