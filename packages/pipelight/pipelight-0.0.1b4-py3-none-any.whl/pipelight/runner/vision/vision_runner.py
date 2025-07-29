from typing import Callable, Optional, Tuple, Union, Sequence, Mapping, Dict, Sequence
import torch
from torch import nn
from ..model_runner import ModelRunner


class VisionRunner(ModelRunner):
    def __init__(
        self,
        model: nn.Module,
        target_data_getter: Callable[[torch.Tensor], torch.Tensor],
        source_data_getter: Optional[Callable[[torch.Tensor], torch.Tensor]] = None,
        data_getter: Optional[Callable[[torch.Tensor], Union[torch.Tensor, Tuple[torch.Tensor, ...]]]] = None,
        *args,
        metrics: Union[Callable[[torch.Tensor], torch.Tensor], Sequence[Callable[[torch.Tensor], torch.Tensor]], None] = None,
        global_metrics: Union[Callable[[torch.Tensor], torch.Tensor], Sequence[Callable[[torch.Tensor], torch.Tensor]], None] = None,
        features_extractor: Optional[Callable[[torch.Tensor], torch.Tensor]] = None,
        feature_metrics: Union[Callable[[torch.Tensor], torch.Tensor], Sequence[Callable[[torch.Tensor], torch.Tensor]], None] = None,
        **kwargs
    ):
        """
        Args:
            model (nn.Module): The model for the runner.
            target_data_getter (Callable[[torch.Tensor], torch.Tensor]):
                The target input data for the task.
            source_data_getter (Optional[Callable[[torch.Tensor], torch.Tensor]]):
                The source data that may be used to translate the source data into the target data.
                If ``None``, no translation task will be runned.
            data_getter (Optional[Callable[[torch.Tensor], Union[torch.Tensor, Tuple[torch.Tensor, ...]]]]):
                The data that is not regarding to the direct main task, but may be for guidance. If ``None``,
                no other data will be used.
            *args
            metrics (Union[Callable[[torch.Tensor], torch.Tensor], Sequence[Callable[[torch.Tensor], torch.Tensor]], None]):
                The metrics list that contains all metrics calculation function, used after each validation and test step.
            global_metrics (Union[Callable[[torch.Tensor], torch.Tensor], Sequence[Callable[[torch.Tensor], torch.Tensor]], None]):
                The metrics list that contains all metrics calculation function, used in the total collected results and ground
                truth. When it is not ``None`` or empty, generation collection will be automatically available to obtain.
            features_extractor (Optional[Callable[[torch.Tensor], torch.Tensor]]): The extractor that extracts
                the features from the ground truth and the generated results.
            feature_metrics (Union[Callable[[torch.Tensor], torch.Tensor], Sequence[Callable[[torch.Tensor], torch.Tensor]], None]):
                The metrics that are calculated from the extracted features in the end of the validation and test epoch.
            **kwargs
        
        """
        super().__init__(model, *args, **kwargs)
        self.__test_collection = self.__validation_collection = None
        self.__generation = self.__target = None
        self.__validation_generation_features = []
        self.__validation_target_features = []
        self.__test_generation_features = []
        self.__test_target_features = []
        
        self.target_data_getter = target_data_getter
        self.source_data_getter = source_data_getter
        self.data_getter = data_getter
        
        self.metrics = _to_sequence(metrics)
        self.global_metrics = _to_sequence(global_metrics)
        self.features_extractor = features_extractor
        self.feature_metrics = _to_sequence(feature_metrics)
    
    def get_target_data(self, batch: torch.Tensor) -> torch.Tensor:
        return self.target_data_getter(batch)
    
    def get_source_data(self, batch: torch.Tensor) -> Optional[torch.Tensor]:
        if self.source_data_getter is not None:
            return self.source_data_getter(batch)
    
    def get_additional_data(self, batch: torch.Tensor) -> Tuple[torch.Tensor, ...]:
        return _tuplize(self.data_getter, batch)
    
    def extract_features(self, batch: torch.Tensor) -> Optional[torch.Tensor]:
        if self.features_extractor is not None:
            return self.features_extractor(batch)
    
    def process_training_step_mean_metrics(self, loss):
        self.log('Loss', loss, prog_bar=True, logger=True, on_step=True, on_epoch=True, sync_dist=True)
    
    def generate(self, batch, batch_idx, source_input: Optional[torch.Tensor], data: Tuple[torch.Tensor, ...], target_input: Optional[torch.Tensor] = None) -> torch.Tensor:
        pass
    
    @torch.inference_mode()
    def __evaluation_step(self, batch, batch_idx, log_prefix: Optional[str] = None, sync_to_logger: bool = True, return_images: bool = False) -> Mapping[str, torch.Tensor]:
        """Evaluates the batch step.

        Args:
            batch: The output of your data iterable, normally a :class:`~torch.utils.data.DataLoader`.
            batch_idx: The index of this batch.
            log_prefix (Optional[str]): The string that tells the evaluation type, for example, 'val' or 'test'.
            sync_to_logger (bool): The flag whether sync the metrics to the logger.
            return_images (bool): The flag that controls whether adding the sampled and original images into
                the returned dictionary.

        Returns:
            Mapping: A dictionary that contains all metrics and the images if
                :param:`return_images` is ``True``.
        
        """
        target_input: torch.Tensor = self.get_target_data(batch)
        source: Optional[torch.Tensor] = self.get_source_data(batch)
        generation = self.generate(batch, batch_idx, source, self.get_additional_data(batch), target_input)
        metric_values = {_metric_name(metric) : metric(generation, target_input) for metric in self.metrics}
        features = self.extract_features(generation), self.extract_features(target_input)
        if log_prefix is None or log_prefix == '':
            collection_dict = metric_values
        else:
            collection_dict = {f'{log_prefix}-{key}' : value for key, value in metric_values.items()}
        if len(collection_dict) > 0:
            self.log_dict({key : value.mean() for key, value in collection_dict.items()}, logger=sync_to_logger, on_step=True, on_epoch=True, sync_dist=True)
        if return_images:
            return metric_values, features, generation.cpu(), target_input.cpu(), source.cpu()
        return metric_values, features
    
    @torch.no_grad()
    def validate_at_step(self, batch, batch_idx) -> Union[torch.Tensor, Tuple[torch.Tensor, ...]]:
        need_images = self.__validation_collection is not None or len(self.global_metrics) > 0
        evaluation = self.__evaluation_step(batch, batch_idx, log_prefix='Val', return_images=need_images)
        if need_images:
            if self.__validation_collection is None:
                self.need_validation_results()
            metric_values, features, generation, target, source = evaluation
            self.__validation_collection[0].append(generation)
            self.__validation_collection[1].append(target)
            self.__validation_collection[2].append(source)
        else:
            metric_values, features = evaluation
        generation_features, target_features = features
        if generation_features is not None:
            self.__validation_generation_features.append(generation_features)
        if target_features is not None:
            self.__validation_target_features.append(target_features)
        return metric_values
    
    @torch.no_grad()
    def end_for_validation_epoch(self, outputs: dict[str, torch.Tensor]):
        log = {f'Val-{key}' : value.mean() for key, value in outputs.items()}
        if len(self.__validation_generation_features) > 0 and len(self.__validation_target_features) > 0:
            generation_features = torch.concat(self.__validation_generation_features, dim=0)
            target_features = torch.concat(self.__validation_target_features, dim=0)
            self.__validation_generation_features.clear()
            self.__validation_target_features.clear()
            log.update({f'Val-{_metric_name(metric)}' : metric(generation_features.detach_(), target_features.detach_()).mean() for metric in self.feature_metrics})
        if len(self.global_metrics) > 0:
            generation, target, _ = self.__concat_collection(self.__validation_collection)
            log.update({f'Val-{_metric_name(metric)}' : metric(generation, target).mean() for metric in self.global_metrics})
        if len(log) > 0:
            self.log_dict(log, prog_bar=True, logger=True, on_step=False, on_epoch=True, sync_dist=True)
    
    @torch.no_grad()
    def test_at_step(self, batch, batch_idx) -> Union[torch.Tensor, Tuple[torch.Tensor, ...]]:
        need_images = self.__test_collection is not None or len(self.global_metrics) > 0
        evaluation = self.__evaluation_step(batch, batch_idx, log_prefix='Test', sync_to_logger=False, return_images=need_images)
        if need_images:
            if self.__test_collection is None:
                self.need_test_results()
            metric_values, features, generation, target, source = evaluation
            self.__test_collection[0].append(generation)
            self.__test_collection[1].append(target)
            self.__test_collection[2].append(source)
        else:
            metric_values, features = evaluation
        generation_features, target_features = features
        if generation_features is not None:
            self.__test_generation_features.append(generation_features)
        if target_features is not None:
            self.__test_target_features.append(target_features)
        return metric_values
    
    @torch.no_grad()
    def end_for_test_epoch(self, outputs: dict[str, torch.Tensor]):
        log = {key : value.mean() for key, value in outputs.items()}
        if len(self.__test_generation_features) > 0 and len(self.__test_target_features) > 0:
            generation_features = torch.concat(self.__test_generation_features, dim=0)
            target_features = torch.concat(self.__test_target_features, dim=0)
            self.__test_generation_features.clear()
            self.__test_target_features.clear()
            log.update({_metric_name(metric) : metric(generation_features.detach_(), target_features.detach_()).mean() for metric in self.feature_metrics})
        if len(self.global_metrics) > 0:
            generation, target, _ = self.__concat_collection(self.__test_collection)
            log.update({_metric_name(metric) : metric(generation, target).mean() for metric in self.global_metrics})
        if len(log) > 0:
            self.log_dict(log, prog_bar=True, logger=True, on_step=False, on_epoch=True, sync_dist=True)
    
    def __concat_collection(self, collection) -> Tuple[torch.Tensor, torch.Tensor, Optional[torch.Tensor]]:
        if self.__generation is None:
            generation, target, source = collection
            generation = torch.concat(generation, dim=0).permute(0, 2, 3, 1)
            target = torch.concat(target, dim=0).permute(0, 2, 3, 1)
            if source[0] is None:
                source = None
            else:
                source = torch.concat(source, dim=0).permute(0, 2, 3, 1)
            self.__generation = generation
            self.__target = target
            self.__source = source
        return self.__generation, self.__target, self.__source
        
    def __evaluation_results(self, results, collection) -> Union[torch.Tensor, Tuple[torch.Tensor, ...], Dict[str, torch.Tensor]]:
        if collection is not None:
            generation, target, source = self.__concat_collection(collection)
            error_map = torch.abs(generation - target)
            generation, target, error_map = generation.cpu(), target.cpu(), error_map.cpu()
            if isinstance(results, tuple):
                results = results + (generation, target, error_map)
                if source is not None:
                    results = results + (source.cpu(),)
            elif isinstance(results, dict):
                results.update({
                    'generation' : generation,
                    'target' : target,
                    'error' : error_map
                })
                if source is not None:
                    results.update({'source' : source.cpu()})
            else:
                results = results, generation, target, error_map
                if source is not None:
                    results = *results, source.cpu()
        return results
    
    def need_validation_results(self, need = True, need_images = True, *args, **kwargs):
        """Informs the runner to store the validation results, and collect them later by using
        :attr:`take_validation_results`.

        Args:
            need (bool): The flag that controls whether to use the validation results.
            need_images (bool) : The flag that controls whether to use the validation images.
        
        """
        super().need_validation_results(need, *args, **kwargs)
        if need_images:
            self.__generation = self.__target = self.__source = None
            self.__validation_collection = ([], [], [])
        else:
            self.__validation_collection = None
    
    @property
    def __validation_results__(self) -> Union[torch.Tensor, Tuple[torch.Tensor, ...], Dict[str, torch.Tensor]]:
        return self.__evaluation_results(super().__validation_results__, self.__validation_collection)
    
    def take_validation_results(self) -> Union[Tuple[torch.Tensor, ...], Tuple[Dict[str, torch.Tensor], torch.Tensor, torch.Tensor]]:
        result = super().take_validation_results()
        self.__generation = self.__target = self.__source = self.__validation_collection = None
        return result
    
    def need_test_results(self, need = True, need_images = True, *args, **kwargs):
        """Informs the runner to store the test results, and collect them later by using
        :attr:`take_test_results`.

        Args:
            need (bool): The flag that controls whether to use the test results.
            need_images (bool) : The flag that controls whether to use the test images.
        
        """
        super().need_test_results(need, *args, **kwargs)
        if need_images:
            self.__generation = self.__target = self.__source = None
            self.__test_collection = ([], [], [])
        else:
            self.__test_collection = None
    
    @property
    def __test_results__(self) -> Union[torch.Tensor, Tuple[torch.Tensor, ...], Dict[str, torch.Tensor]]:
        return self.__evaluation_results(super().__test_results__, self.__test_collection)
    
    def take_test_results(self) -> Union[Tuple[torch.Tensor, ...], Tuple[Dict[str, torch.Tensor], torch.Tensor, torch.Tensor]]:
        result = super().take_test_results()
        self.__generation = self.__target = self.__source = self.__test_collection = None
        return result


def _tuplize(func, batch):
    if func is None:
        return tuple()
    else:
        data = func(batch)
        if not isinstance(data, tuple):
            data = (data,)
        return data


def _to_sequence(values):
    if values is None:
        return []
    elif isinstance(values, Sequence):
        return values
    else:
        return [values]


def _metric_name(metric):
    if hasattr(metric, '__name__'):
        return metric.__name__
    else:
        return type(metric).__name__