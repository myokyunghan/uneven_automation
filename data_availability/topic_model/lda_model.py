import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation as LDA
from preprocess import Preprocessor


def load_lda_model_from_config(model_config):
    """

    Args:
        model_config: a dict

    Returns:
        a LDATopicModel instance
    """
    n_components = model_config['n_components']
    max_df = model_config['max_df']
    min_df = model_config['min_df']
    attach_suffix = model_config['attach_suffix']
    to_return = LDATopicModel(n_components, max_df, min_df, attach_suffix)
    return to_return


class LDATopicModel:
    def __init__(self, n_components, max_df=0.8, min_df=10,
                 attach_suffix=False):
        self.preprocessor = Preprocessor()
        self.vectorizer = CountVectorizer(
            stop_words='english', max_df=max_df, min_df=min_df,
        )
        self.topic_model = LDA(n_components=n_components, verbose=10)
        self.attach_suffix = attach_suffix
        self.vectorized = None
        self.transformed = None
        self.topic_info = None

    def __call__(self, list_):
        """

        Args:
            list_: a list of dict

        Returns:
            a transformed array
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
        suffix_needed = self.attach_suffix
        to_return = self.preprocessor.prep_lda_model_input(
            list_, suffix_needed
        )
        return to_return

    def get_topic_info(self):
        """

        Returns:
            a list of dict
        """
        if self.topic_info is not None:
            return self.topic_info
        else:
            rep_words = self.get_representative_words_of_each_topic()
            topics = list(range(0, len(rep_words)))
            counts = np.array([0.0]*len(topics))
            for i in range(len(self.transformed)):
                counts += self.transformed[i]
            to_return = [{"Topic": int(i), "Count": int(counts[i]),
                          "Representation": rep_words[i]}
                         for i in np.argsort(-counts)]
            self.topic_info = to_return
            return to_return

    def run_model(self, list_):
        """

        Args:
            list_: a list of dict

        Returns:
            a transformed array
        """
        to_vectorize = self._preprocess(list_)
        model_input = self.vectorizer.fit_transform(to_vectorize)
        to_return = self.topic_model.fit_transform(model_input)
        return to_return

    def run_model_and_get_output_list(self, list_, fit_list=None):
        """

        Args:
            list_: a list of dict

        Returns:
            a list of dict, where each dict has additional key "topic_info"
        """
        if "lemmatized" in list_[0]:
            print("[LDATopicModel] using lemmatized data")
            to_vectorize = [dict_["lemmatized"] for dict_ in list_]
        else:
            print("[LDATopicModel] lemmatizing")
            to_vectorize = self._preprocess(list_)
        model_input = self.vectorizer.fit_transform(to_vectorize)
        if fit_list is not None:
            print(f"fit and transform seperately; fitting with len {len(fit_list)}")
            print(f"after that, transform would be done on len {model_input.shape[0]}")
            print("[LDATopicModel] lemmatizing")
            to_vectorize_for_fit = self._preprocess(fit_list)
            model_input_for_fit = self.vectorizer.transform(to_vectorize_for_fit)
            self.topic_model = self.topic_model.fit(model_input_for_fit)
            model_output = self.topic_model.transform(model_input)
        else:
            model_output = self.topic_model.fit_transform(model_input)
        self.vectorized = model_input
        self.transformed = model_output
        for idx, dict_ in enumerate(list_):
            dict_["lemmatized"] = to_vectorize[idx]
            dict_["topic_info"] = model_output[idx].tolist()
        return list_

    def from_preprocessed_run_model_and_get_scores(self, list_):
        """

        Args:
            list_: a preprocessed list of dict

        Returns:
            a tuple (perplexity, cohesiveness)
        """
        to_vectorize = [dict_["lemmatized"] for dict_ in list_]
        model_input = self.vectorizer.fit_transform(to_vectorize)
        self.topic_model.fit(model_input)
        to_return = self.topic_model.perplexity(model_input)
        return to_return

    def get_representative_words_of_each_topic(self, top_n=10):
        """

        Returns:
            a list of dict
        """
        to_return = []
        feature_names = self.vectorizer.get_feature_names_out()
        for topic in self.topic_model.components_:
            topic_words_idx = topic.argsort()[::-1]
            top_n_idx = topic_words_idx[:top_n]
            to_append = {
                str(feature_names[i]): round(topic[i]) for i in top_n_idx
            }
            to_return.append(to_append)
        return to_return
