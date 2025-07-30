from typing import Optional, List
import numpy as np
from ..strategy import Strategy
from ..spaces import SMBOSpace


class SMBOSearch(Strategy):
    def __init__(
        self,
        real: Optional[dict] = None,
        integer: Optional[dict] = None,
        categorical: Optional[dict] = None,
        search_config: dict = {
            "base_estimator": "GP",
            "acq_function": "gp_hedge",
            "n_initial_points": 5,
        },
        maximize_objective: bool = False,
        fixed_params: Optional[dict] = None,
        reload_path: Optional[str] = None,
        reload_list: Optional[list] = None,
        seed_id: int = 42,
        sort_key = None,
        verbose: bool = False,
    ):
        """Sequential Model-Based Optimization Search Strategy.
        Wraps around https://github.com/scikit-optimize/scikit-optimize
        Reference: https://tinyurl.com/bdxawcsb

        Args:
            real (Optional[dict], optional):
                Dictionary of real-valued search variables & their priors.
                E.g. {"lrate": {"begin": 0.1, "end": 0.5, "prior": "log-uniform"}}
                Defaults to None.
            integer (Optional[dict], optional):
                Dictionary of integer-valued search variables & their priors.
                E.g. {"batch_size": {"begin": 1, "end": 5, "bins": "uniform"}}
                Defaults to None.
            categorical (Optional[dict], optional):
                Dictionary of categorical-valued search variables.
                E.g. {"arch": ["mlp", "cnn"]}
                Defaults to None.
            search_config (dict, optional): SMBO search hyperparameters.
                Defaults to {"base_estimator": "GP",
                             "acq_function": "gp_hedge",
                             "n_initial_points": 5}.
            maximize_objective (bool, optional): Whether to maximize objective.
                Defaults to False.
            fixed_params (Optional[dict], optional):
                Fixed parameters that will be added to all configurations.
                Defaults to None.
            reload_path (Optional[str], optional):
                Path to load previous search log from. Defaults to None.
            reload_list (Optional[list], optional):
                List of previous results to reload. Defaults to None.
            seed_id (int, optional):
                Random seed for reproducibility. Defaults to 42.
            verbose (bool, optional):
                Option to print intermediate results. Defaults to False.
        """
        self.search_name = "SMBO"
        self.space = SMBOSpace(real, integer, categorical)
        Strategy.__init__(
            self,
            real,
            integer,
            categorical,
            search_config,
            maximize_objective,
            fixed_params,
            reload_path,
            reload_list,
            seed_id,
            sort_key,
            verbose,
        )
        self.init_optimizer()

        # Add start-up message printing the search space
        if self.verbose:
            self.print_hello()

    def init_optimizer(self) -> None:
        """Initialize the surrogate model/hyperparam config proposer."""
        try:
            from skopt import Optimizer
        except ImportError:
            raise ImportError(
                "You need to install `scikit-optimize` & `scikit-learn==0.24.2`"
                " to use the SMBO search strategy."
            )
        self.hyper_optimizer = Optimizer(
            dimensions=self.space.dimensions,
            random_state=self.seed_id,
            base_estimator=self.search_config["base_estimator"],
            acq_func=self.search_config["acq_function"],
            n_initial_points=self.search_config["n_initial_points"],
        )

    def ask_search(self, batch_size: int) -> List[dict]:
        """Get proposals to eval next (in batches) - SMBO Search.

        Args:
            batch_size (int): Number of desired configurations

        Returns:
            List[dict]: List of configuration dictionaries
        """
        param_batch = []
        proposals = self.hyper_optimizer.ask(n_points=batch_size)
        # Generate list of dictionaries with different hyperparams to evaluate
        for prop in proposals:
            proposal_params = {}
            for i, p_name in enumerate(self.space.param_range.keys()):
                if type(prop[i]) == np.int64:
                    proposal_params[p_name] = int(prop[i])
                else:
                    proposal_params[p_name] = prop[i]
            param_batch.append(proposal_params)
        return param_batch

    def tell_search(
        self,
        batch_proposals: list,
        perf_measures: list,
        ckpt_paths: Optional[List[str]] = None,
    ) -> None:
        """Perform post-iteration clean-up by updating surrogate model.

        Args:
            batch_proposals (list): List of evaluated configurations
            perf_measures (list): List of corresponding performances
            ckpt_paths (Optional[List[str]], optional):
                List of corresponding model ckpts to store. Defaults to None.
        """
        x = []
        for i, prop in enumerate(batch_proposals):
            prop_conf = dict(prop)
            if self.fixed_params is not None:
                for k in self.fixed_params.keys():
                    if k in prop_conf.keys():
                        del prop_conf[k]
            x.append(list(prop_conf.values()))

        # Negate function values for maximization
        if not self.maximize_objective:
            self.hyper_optimizer.tell(x, perf_measures)
        else:
            self.hyper_optimizer.tell(x, [-1 * p for p in perf_measures])

    def update_search(self) -> None:
        """Refine search space boundaries after set of search iterations."""
        if self.refine_after is not None:
            # Check whether there are still refinements open
            # And whether we have already passed last refinement point
            if len(self.refine_after) > self.refine_counter:
                exact = (
                    self.eval_counter == self.refine_after[self.refine_counter]
                )
                skip = (
                    self.eval_counter > self.refine_after[self.refine_counter]
                    and self.last_refined
                    != self.refine_after[self.refine_counter]
                )
                if exact or skip:
                    self.refine(self.refine_top_k)
                    self.last_refined = self.refine_after[self.refine_counter]
                    self.refine_counter += 1

    def setup_search(self) -> None:
        """Initialize search settings at startup."""
        # Set up search space refinement - random, SMBO, nevergrad
        if self.search_config is not None:
            if "refine_top_k" in self.search_config.keys():
                self.refine_counter = 0
                assert self.search_config["refine_top_k"] > 1
                self.refine_after = self.search_config["refine_after"]
                # Make sure that refine iteration is list
                if type(self.refine_after) == int:
                    self.refine_after = [self.refine_after]
                self.refine_top_k = self.search_config["refine_top_k"]
                self.last_refined = 0
            else:
                self.refine_after = None
        else:
            self.refine_after = None

    def refine_space(
        self,
        real: Optional[dict] = None,
        integer: Optional[dict] = None,
        categorical: Optional[dict] = None,
    ) -> None:
        """Update the SMBO search space based on refined dictionaries.

        Args:
            real (Optional[dict], optional):
                Dictionary of real-valued search variables & their priors.
                E.g. {"lrate": {"begin": 0.1, "end": 0.5, "prior": "log-uniform"}}
                Defaults to None.
            integer (Optional[dict], optional):
                Dictionary of integer-valued search variables & their priors.
                E.g. {"batch_size": {"begin": 1, "end": 5, "bins": "uniform"}}
                Defaults to None.
            categorical (Optional[dict], optional):
                Dictionary of categorical-valued search variables.
                E.g. {"arch": ["mlp", "cnn"]}
                Defaults to None.
        """
        self.space.update(real, integer, categorical)
        # Reinitialize the optimizer and provide data from previous updates
        self.init_optimizer()
        for iter in self.log:
            self.tell_search([iter["params"]], [iter["objective"]])
