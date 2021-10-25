import copy
from joblib import Parallel
import numpy as np
from sklearn import clone
from sklearn.pipeline import Pipeline
from sklearn.model_selection import check_cv
from sklearn.model_selection._validation import _fit_and_score, _insert_error_scores, _aggregate_score_dicts, _normalize_score_results
from sklearn.utils.validation import indexable
from sklearn.metrics import check_scoring
from sklearn.metrics._scorer import _check_multimetric_scoring
from sklearn.base import is_classifier
from sklearn.utils.fixes import delayed

def _transform_except_last_estimator(transformer, X_src, X_train):
    """パイプラインのとき、最終学習器以外のtransformを適用"""
    if transformer is not None:
        transformer.fit(X_train)
        X_dst = transformer.transform(X_src)
        return X_dst
    else:
        return X_src

def _eval_set_selection(eval_set_selection, transformer,
                        fit_params, train, test):
    """eval_setの中から学習データ or テストデータのみを抽出"""
    fit_params_modified = copy.deepcopy(fit_params)
    # eval_setが存在しなければ、そのままfit_paramsを返す
    eval_sets = [v for v in fit_params.keys() if 'eval_set' in v]
    if len(eval_sets) == 0:
        return fit_params_modified
    eval_set_name = eval_sets[0]  # eval_setの列名(pipelineでは列名が変わるため)
    # 元のeval_setからX, yを取得
    X_fit = fit_params[eval_set_name][0][0]
    y_fit = fit_params[eval_set_name][0][1]
    # eval_setに該当データを入力し直す
    if eval_set_selection == 'train':
        fit_params_modified[eval_set_name] = [(_transform_except_last_estimator(transformer, X_fit[train], X_fit[train])\
                                              , y_fit[train])]
    elif eval_set_selection == 'test':
        fit_params_modified[eval_set_name] = [(_transform_except_last_estimator(transformer, X_fit[test], X_fit[train])\
                                              , y_fit[test])]
    else:
        fit_params_modified[eval_set_name] = [(_transform_except_last_estimator(transformer, X_fit, X_fit[train])\
                                              , y_fit)]
    return fit_params_modified

def _fit_and_score_eval_set(eval_set_selection, transformer,
                            estimator, X, y, scorer, train, test, verbose,
                            parameters, fit_params, return_train_score=False,
                            return_parameters=False, return_n_test_samples=False,
                            return_times=False, return_estimator=False,
                            split_progress=None, candidate_progress=None,
                            error_score=np.nan):

    """Fit estimator and compute scores for a given dataset split."""
    # eval_setの中から学習データ or テストデータのみを抽出
    fit_params_modified = _eval_set_selection(eval_set_selection, transformer,
                                              fit_params, train, test)
    result = _fit_and_score(estimator, X, y, scorer, train, test, verbose, parameters,
                            fit_params_modified,
                            return_train_score=return_train_score,
                            return_parameters=return_parameters, return_n_test_samples=return_n_test_samples,
                            return_times=return_times, return_estimator=return_estimator,
                            split_progress=split_progress, candidate_progress=candidate_progress,
                            error_score=error_score)
    return result

def _make_transformer(eval_set_selection, estimator):
    """estimatorがパイプラインのとき、最終学習器以外の変換器(前処理クラスのリスト)を作成"""
    if isinstance(estimator, Pipeline) and eval_set_selection != 'original':
        transformer = Pipeline([step for i, step in enumerate(estimator.steps) if i < len(estimator) - 1])
        return transformer
    else:
        return None

def cross_validate_eval_set(eval_set_selection,
                            estimator, X, y=None, groups=None, scoring=None, cv=None,
                            n_jobs=None, verbose=0, fit_params=None,
                            pre_dispatch='2*n_jobs', return_train_score=False,
                            return_estimator=False, error_score=np.nan):
    """
    Evaluate a scores by cross-validation with `eval_set` argument in fit_params

    This method is suitable for calculating cross validation scores with `early_stopping_round` in XGBoost or LightGBM.

    Parameters
    ----------
    eval_set_selection : {'all', 'train', 'test', 'original', 'original_transformed'}
        Select data passed to `eval_set` in `fit_params`. Available only if "estimator" is LightGBM or XGBoost.
            
        If "all", use all data in `X` and `y`.

        If "train", select train data from `X` and `y` using cv.split().

        If "test", select test data from `X` and `y` using cv.split().

        If "original", use raw `eval_set`.

        If "original_transformed", use `eval_set` transformed by fit_transform() of pipeline if `estimater` is pipeline.

    estimator : estimator object implementing 'fit'
        The object to use to fit the data.

    X : array-like of shape (n_samples, n_features)
        The data to fit. Can be for example a list, or an array.

    y : array-like of shape (n_samples,) or (n_samples, n_outputs), \
            default=None
        The target variable to try to predict in the case of
        supervised learning.

    groups : array-like of shape (n_samples,), default=None
        Group labels for the samples used while splitting the dataset into
        train/test set. Only used in conjunction with a "Group" :term:`cv`
        instance (e.g., :class:`GroupKFold`).

    scoring : str, callable, list, tuple, or dict, default=None
        Strategy to evaluate the performance of the cross-validated model on
        the test set.

        If `scoring` represents a single score, one can use:

        - a single string (see :ref:`scoring_parameter`);
        - a callable (see :ref:`scoring`) that returns a single value.

        If `scoring` represents multiple scores, one can use:

        - a list or tuple of unique strings;
        - a callable returning a dictionary where the keys are the metric
          names and the values are the metric scores;
        - a dictionary with metric names as keys and callables a values.

        See :ref:`multimetric_grid_search` for an example.

    cv : int, cross-validation generator or an iterable, default=None
        Determines the cross-validation splitting strategy.
        Possible inputs for cv are:

        - None, to use the default 5-fold cross validation,
        - int, to specify the number of folds in a `(Stratified)KFold`,
        - :term:`CV splitter`,
        - An iterable yielding (train, test) splits as arrays of indices.

        For int/None inputs, if the estimator is a classifier and ``y`` is
        either binary or multiclass, :class:`StratifiedKFold` is used. In all
        other cases, :class:`.Fold` is used. These splitters are instantiated
        with `shuffle=False` so the splits will be the same across calls.

        Refer :ref:`User Guide <cross_validation>` for the various
        cross-validation strategies that can be used here.

        .. versionchanged:: 0.22
            ``cv`` default value if None changed from 3-fold to 5-fold.

    n_jobs : int, default=None
        Number of jobs to run in parallel. Training the estimator and computing
        the score are parallelized over the cross-validation splits.
        ``None`` means 1 unless in a :obj:`joblib.parallel_backend` context.
        ``-1`` means using all processors. See :term:`Glossary <n_jobs>`
        for more details.

    verbose : int, default=0
        The verbosity level.

    fit_params : dict, default=None
        Parameters to pass to the fit method of the estimator.

    pre_dispatch : int or str, default='2*n_jobs'
        Controls the number of jobs that get dispatched during parallel
        execution. Reducing this number can be useful to avoid an
        explosion of memory consumption when more jobs get dispatched
        than CPUs can process. This parameter can be:

            - None, in which case all the jobs are immediately
              created and spawned. Use this for lightweight and
              fast-running jobs, to avoid delays due to on-demand
              spawning of the jobs

            - An int, giving the exact number of total jobs that are
              spawned

            - A str, giving an expression as a function of n_jobs,
              as in '2*n_jobs'

    return_train_score : bool, default=False
        Whether to include train scores.
        Computing training scores is used to get insights on how different
        parameter settings impact the overfitting/underfitting trade-off.
        However computing the scores on the training set can be computationally
        expensive and is not strictly required to select the parameters that
        yield the best generalization performance.

        .. versionadded:: 0.19

        .. versionchanged:: 0.21
            Default value was changed from ``True`` to ``False``

    return_estimator : bool, default=False
        Whether to return the estimators fitted on each split.

        .. versionadded:: 0.20

    error_score : 'raise' or numeric, default=np.nan
        Value to assign to the score if an error occurs in estimator fitting.
        If set to 'raise', the error is raised.
        If a numeric value is given, FitFailedWarning is raised.

        .. versionadded:: 0.20
    """

    X, y, groups = indexable(X, y, groups)

    cv = check_cv(cv, y, classifier=is_classifier(estimator))

    if callable(scoring):
        scorers = scoring
    elif scoring is None or isinstance(scoring, str):
        scorers = check_scoring(estimator, scoring)
    else:
        scorers = _check_multimetric_scoring(estimator, scoring)

    # 最終学習器以外の前処理変換器作成
    transformer = _make_transformer(eval_set_selection, estimator)

    # We clone the estimator to make sure that all the folds are
    # independent, and that it is pickle-able.
    parallel = Parallel(n_jobs=n_jobs, verbose=verbose,
                        pre_dispatch=pre_dispatch)
    results = parallel(
        delayed(_fit_and_score_eval_set)(
            eval_set_selection, transformer,
            clone(estimator), X, y, scorers, train, test, verbose, None,
            fit_params, return_train_score=return_train_score,
            return_times=True, return_estimator=return_estimator,
            error_score=error_score)
        for train, test in cv.split(X, y, groups))

    # For callabe scoring, the return type is only know after calling. If the
    # return type is a dictionary, the error scores can now be inserted with
    # the correct key.
    if callable(scoring):
        _insert_error_scores(results, error_score)

    results = _aggregate_score_dicts(results)

    ret = {}
    ret['fit_time'] = results["fit_time"]
    ret['score_time'] = results["score_time"]

    if return_estimator:
        ret['estimator'] = results["estimator"]

    test_scores_dict = _normalize_score_results(results["test_scores"])
    if return_train_score:
        train_scores_dict = _normalize_score_results(results["train_scores"])

    for name in test_scores_dict:
        ret['test_%s' % name] = test_scores_dict[name]
        if return_train_score:
            key = 'train_%s' % name
            ret[key] = train_scores_dict[name]

    return ret

def cross_val_score_eval_set(eval_set_selection,
                             estimator, X, y=None, groups=None, scoring=None,
                             cv=None, n_jobs=None, verbose=0, fit_params=None,
                             pre_dispatch='2*n_jobs', error_score=np.nan):
    """
    Evaluate a score by cross-validation with `eval_set` argument in fit_params

    This method is suitable for calculating cross validation score with `early_stopping_round` in XGBoost or LightGBM.

    Parameters
    ----------
    eval_set_selection : {'all', 'train', 'test'}
        Select data passed to `eval_set`.
        
        If "all", using all data in former "eval_set"

        If "train", select train data in former "eval_set" using cv.split()

        If "test", select test data in former "eval_set" using cv.split()
    
    estimator : estimator object implementing 'fit'
        The object to use to fit the data.

    X : array-like of shape (n_samples, n_features)
        The data to fit. Can be for example a list, or an array.

    y : array-like of shape (n_samples,) or (n_samples, n_outputs), \
            default=None
        The target variable to try to predict in the case of
        supervised learning.

    groups : array-like of shape (n_samples,), default=None
        Group labels for the samples used while splitting the dataset into
        train/test set. Only used in conjunction with a "Group" :term:`cv`
        instance (e.g., :class:`GroupKFold`).

    scoring : str or callable, default=None
        A str (see model evaluation documentation) or
        a scorer callable object / function with signature
        ``scorer(estimator, X, y)`` which should return only
        a single value.

        Similar to :func:`cross_validate`
        but only a single metric is permitted.

        If None, the estimator's default scorer (if available) is used.

    cv : int, cross-validation generator or an iterable, default=None
        Determines the cross-validation splitting strategy.
        Possible inputs for cv are:

        - None, to use the default 5-fold cross validation,
        - int, to specify the number of folds in a `(Stratified)KFold`,
        - :term:`CV splitter`,
        - An iterable yielding (train, test) splits as arrays of indices.

        For int/None inputs, if the estimator is a classifier and ``y`` is
        either binary or multiclass, :class:`StratifiedKFold` is used. In all
        other cases, :class:`KFold` is used. These splitters are instantiated
        with `shuffle=False` so the splits will be the same across calls.

        Refer :ref:`User Guide <cross_validation>` for the various
        cross-validation strategies that can be used here.

        .. versionchanged:: 0.22
            ``cv`` default value if None changed from 3-fold to 5-fold.

    n_jobs : int, default=None
        Number of jobs to run in parallel. Training the estimator and computing
        the score are parallelized over the cross-validation splits.
        ``None`` means 1 unless in a :obj:`joblib.parallel_backend` context.
        ``-1`` means using all processors. See :term:`Glossary <n_jobs>`
        for more details.

    verbose : int, default=0
        The verbosity level.

    fit_params : dict, default=None
        Parameters to pass to the fit method of the estimator.

    pre_dispatch : int or str, default='2*n_jobs'
        Controls the number of jobs that get dispatched during parallel
        execution. Reducing this number can be useful to avoid an
        explosion of memory consumption when more jobs get dispatched
        than CPUs can process. This parameter can be:

            - None, in which case all the jobs are immediately
              created and spawned. Use this for lightweight and
              fast-running jobs, to avoid delays due to on-demand
              spawning of the jobs

            - An int, giving the exact number of total jobs that are
              spawned

            - A str, giving an expression as a function of n_jobs,
              as in '2*n_jobs'

    error_score : 'raise' or numeric, default=np.nan
        Value to assign to the score if an error occurs in estimator fitting.
        If set to 'raise', the error is raised.
        If a numeric value is given, FitFailedWarning is raised.

        .. versionadded:: 0.20
    """
    # To ensure multimetric format is not supported
    scorer = check_scoring(estimator, scoring=scoring)

    cv_results = cross_validate_eval_set(eval_set_selection=eval_set_selection,
                                         estimator=estimator, X=X, y=y, groups=groups,
                                         scoring={'score': scorer}, cv=cv,
                                         n_jobs=n_jobs, verbose=verbose,
                                         fit_params=fit_params,
                                         pre_dispatch=pre_dispatch,
                                         error_score=error_score)
    return cv_results['test_score']