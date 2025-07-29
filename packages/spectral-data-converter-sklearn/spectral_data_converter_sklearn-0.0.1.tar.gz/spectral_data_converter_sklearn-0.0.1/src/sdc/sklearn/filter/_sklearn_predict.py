import argparse
import pickle
from typing import List

from wai.logging import LOGGING_WARNING

from sdc.api import flatten_list, make_list, Filter, Spectrum2D, safe_deepcopy
from sklearn.base import BaseEstimator


class SklearnPredict(Filter):
    """
    Loads a pickled model and generates predictions on the incoming data, adding it to the sample data.
    """

    def __init__(self, model_file: str = None, target: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the plugin.

        :param model_file: the pickled model to load
        :type model_file: str
        :param target: the sample data field to store the predictions under
        :type target: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.model_file = model_file
        self.target = target
        self._model = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "sklearn-predict"

    def description(self) -> str:
        """
        Returns a description of the filter.

        :return: the description
        :rtype: str
        """
        return "Loads a pickled scikit-learn model and generates predictions on the incoming data, adding it to the sample data."

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [Spectrum2D]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [Spectrum2D]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-m", "--model_file", type=str, help="The pickled scikit-learn model to load and use.", default=None, required=True)
        parser.add_argument("-t", "--target", type=str, help="The sample data field to store the predictions under.", default=None, required=True)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.model_file = ns.model_file
        self.target = ns.target

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.model_file is None:
            raise Exception("No model file supplied!")
        if self.target is None:
            raise Exception("No sample data field specified for predictions!")

    def _do_process(self, data):
        """
        Processes the data record(s).

        :param data: the record(s) to process
        :return: the potentially updated record(s)
        """
        result = []

        # load model
        if self._model is None:
            path = self.session.expand_placeholders(self.model_file)
            self.logger().info("Loading model from: %s" % path)
            try:
                with open(path, "rb") as fp:
                    self._model = pickle.load(fp)
            except:
                self.logger().error("Failed to load model from: %s" % path, exc_info=True)
                return data

        # is it a sklearn model?
        if not isinstance(self._model, BaseEstimator):
            self.logger().error("Model is not derived from sklearn.base.BaseEstimator: %s" % str(type(self._model)))
            return data

        # make predictions
        for item in make_list(data):
            item = safe_deepcopy(item)

            try:
                pred = self._model.predict([item.spectrum.amplitudes])
                item.spectrum.sample_data[self.target] = pred[0]
            except:
                self.logger().error("Failed to generate prediction for: %s" % item.spectrum.id, exc_info=True)

            result.append(item)

        return flatten_list(result)
