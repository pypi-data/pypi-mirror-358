import argparse
import json
import pickle
from typing import List

from wai.logging import LOGGING_WARNING

from seppl import get_class
from sdc.api import Spectrum2D, BatchWriter
from sklearn.base import BaseEstimator


class SklearnFit(BatchWriter):

    def __init__(self, model: str = None, model_params: str = None, template: str = None,
                 target: str = None, output_file: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the plugin.

        :param model: the classname of the model to build
        :type model: str
        :param model_params: the parameters of the model as JSON string
        :type model_params: str
        :param template: the pickled model file to load and train instead of using classname/params
        :type template: str
        :param target: the sample data field to use as output variable
        :type target: str
        :param output_file: where to pickle the model to
        :type output_file: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.model = model
        self.model_params = model_params
        self.template = template
        self.target = target
        self.output_file = output_file

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "sklearn-fit"

    def description(self) -> str:
        """
        Returns a description of the writer.

        :return: the description
        :rtype: str
        """
        return "Builds a scikit-learn model on the incoming data and saves it."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-m", "--model", type=str, help="The classname of the model to build.", required=False, default=None)
        parser.add_argument("-p", "--model_params", metavar="JSON", type=str, help="The parameters of the model as JSON string.", required=False, default=None)
        parser.add_argument("-T", "--template", metavar="FILE", type=str, help="The path to the pickled model template to load and train instead of classname/parameters.", required=False, default=None)
        parser.add_argument("-t", "--target", type=str, help="The name of the sample data field to use as output variable.", required=True, default=None)
        parser.add_argument("-o", "--output_file", metavar="FILE", type=str, help="The file to save the model to.", required=True, default=None)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.model = ns.model
        self.model_params = ns.model_params
        self.template = ns.template
        self.target = ns.target
        self.output_file = ns.output_file

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [Spectrum2D]

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if (self.model is None) and (self.template is None):
            raise Exception("Neither model classname nor model template specified!")
        if self.target is None:
            raise Exception("No sample data field specified!")

    def write_batch(self, data):
        """
        Saves the data in one go.

        :param data: the data to write
        :type data: Iterable
        """
        if len(data) == 0:
            raise Exception("No data for training!")

        # collate data
        x = []
        y = []
        for sp in data:
            x.append(sp.spectrum.amplitudes)
            if self.target in sp.spectrum.sample_data:
                y.append(float(sp.spectrum.sample_data[self.target]))
            else:
                self.logger().warning("Missing '%s' for spectrum: %s" % (self.target, sp.spectrum.id))
                y.append(None)

        # instantiate model
        if self.template is not None:
            try:
                path = self.session.expand_placeholders(self.template)
                self.logger().info("Loading model template: %s" % path)
                with open(path, "rb") as fp:
                    model = pickle.load(fp)
            except:
                self.logger().error("Failed to load model template: %s" % self.template, exc_info=True)
                return
        else:
            try:
                if (self.model_params is not None) and (self.model_params.startswith("{")):
                    model_params = json.loads(self.model_params)
                    model = get_class(self.model)(**model_params)
                else:
                    model = get_class(self.model)()
            except:
                self.logger().error("Failed to instantiate class '%s' with parameters: %s" % (self.model, str(self.model_params)), exc_info=True)
                return

        # is it a sklearn model?
        if not isinstance(model, BaseEstimator):
            self.logger().error("Model is not derived from sklearn.base.BaseEstimator: %s" % str(type(model)))
            return

        # train model
        try:
            model.fit(x, y)
        except:
            self.logger().error("Failed to train model!", exc_info=True)
            return

        # save model
        path = self.session.expand_placeholders(self.output_file)
        self.logger().info("Saving model to: %s" % path)
        with open(path, "wb") as fp:
            pickle.dump(model, fp)
