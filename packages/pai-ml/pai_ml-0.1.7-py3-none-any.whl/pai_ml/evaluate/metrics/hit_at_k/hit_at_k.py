import warnings
from typing import List, Dict, Union, Optional, Any, Set

import datasets
import evaluate

_DESCRIPTION = """\
Hit@K (also known as Success@K or Binary Recall@K) measures whether 
at least one relevant item is successfully retrieved in the top-K results. 
It answers the question: "Was the retrieval successful in finding at least 
one relevant item in the top-K results?"

Hit@K = 1 if (at least one relevant item in top-K) else 0

This is a binary metric (0 or 1) that focuses on retrieval success rather 
than the proportion of relevant items found. It's particularly useful when 
users typically only examine the top-K results and consider the search 
successful if they find at least one relevant item.

This implementation supports:
- Multiple K values in a single computation
- Binary relevance judgments  
- Batch processing for multiple queries
- String-based item identifiers
- Different averaging methods across queries

Based on IR evaluation standards from TREC and CBIR literature.

This metric is particularly useful for:
- Content-Based Image Retrieval (CBIR)
- Information Retrieval systems
- Recommendation systems
- Any ranking/retrieval evaluation where binary success matters
"""

_KWARGS_DESCRIPTION = """\
Args:
    predictions (list of lists): A list where each inner list contains the string IDs of retrieved items,
        sorted by relevance, for a single query.
    references (list of lists/sets): A list where each inner list/set contains the string IDs of
        the true relevant items for the corresponding query.
    k_values (list of int, optional): A list of k values for which to compute Hit@k.
        Defaults to [1, 5, 10, 20, 50].
    compute_per_NR (bool, optional): If True, computes Hit@NR for each query, where NR is the
        number of relevant items for that query. The result will be under 'hit_at_NR'.
        Defaults to False.
    average (str, optional): How to average results across queries. Options:
        - 'macro': Average hit rates across queries (each query weighted equally)
        - 'micro': Pool all queries together (same as macro for binary metrics)
        - None: Return per-query results without averaging
        Defaults to 'macro'.
    relevance_threshold (float, optional): This parameter is kept for compatibility but
        has no effect since only binary relevance is supported. Defaults to 1.0.
    ignore_missing (bool, optional): Whether to ignore queries with no relevant items.
        Defaults to True.

Returns:
    (dict): A dictionary with keys like 'hit_at_K' for each k in k_values.
    When average='macro' or 'micro', returns mean values. When average=None, returns lists of per-query scores.
    Also includes 'hit_at_NR' if compute_per_NR is True.
"""

_CITATION = """\
@article{muller2001performance,
    title={Performance evaluation in content-based image retrieval: overview and proposals},
    author={M{\"u}ller, Henning and M{\"u}ller, Wolfgang and Squire, David McG and Marchand-Maillet, St{\'e}phane and Pun, Thierry},
    journal={Pattern Recognition Letters},
    volume={22},
    number={5},
    pages={593--601},
    year={2001},
    publisher={Elsevier}
}
"""


def hit_at_k(retrieved_items: List[Any], relevant_items: Union[List[Any], Set[Any]], k: int) -> float:
	"""
	Calculates Hit at K (Hit@k).

	Hit@k = 1 if (at least one relevant item in the top k retrieved items) else 0

	This is a binary success metric that returns 1.0 if at least one relevant item
	is found in the top-k results, and 0.0 otherwise.

	Args:
		retrieved_items: A list of item IDs retrieved by the system, in ranked order.
		relevant_items: A list or set of item IDs that are truly relevant for the query.
		k: The cut-off for the number of retrieved items to consider.

	Returns:
		The hit at k, either 0.0 or 1.0.

	Raises:
		ValueError: If k is not a positive integer.
		TypeError: If inputs are not of the correct type.
	"""
	if not isinstance(k, int) or k <= 0:
		raise ValueError("k must be a positive integer.")
	if not isinstance(retrieved_items, list):
		raise TypeError("retrieved_items must be a list.")
	if not isinstance(relevant_items, (list, set)):
		raise TypeError("relevant_items must be a list or set.")

	# Ensure relevant_items is a set for efficient lookup
	relevant_set = set(relevant_items)

	# If no relevant items exist, hit is undefined (we return 0.0)
	if not relevant_set:
		return 0.0

	# If no items were retrieved, hit is 0.
	if not retrieved_items:
		return 0.0

	# Consider only the first k retrieved items
	top_k_retrieved = retrieved_items[:k]

	# Check if any item in top k is relevant
	for item_id in top_k_retrieved:
		if item_id in relevant_set:
			return 1.0  # Found at least one relevant item

	return 0.0  # No relevant items found in top k


def _parse_predictions(predictions: List[Any]) -> List[Any]:
	"""Parse prediction list to get ranked items."""
	if not predictions:
		return []

	# Since we only support string sequences now, predictions are already ranked items
	return predictions


def _parse_references(references: Union[List[Any], Set[Any]], threshold: float = 1.0) -> Set[Any]:
	"""Parse reference list/set to extract relevant items."""
	relevant_items = set()

	# Convert to list if it's a set
	if isinstance(references, set):
		references = list(references)

	# Since we only support string sequences now, all items in references are relevant
	for item in references:
		relevant_items.add(item)

	return relevant_items


@evaluate.utils.file_utils.add_start_docstrings("""\n""")
class HitAtK(evaluate.Metric):

	def _info(self):
		return evaluate.MetricInfo(
			description=_DESCRIPTION,
			citation=_CITATION,
			inputs_description=_KWARGS_DESCRIPTION,
			features=datasets.Features({
				"predictions": datasets.Sequence(datasets.Value("string")),
				"references": datasets.Sequence(datasets.Value("string")),
			}),
			reference_urls=["https://www.sciencedirect.com/science/article/abs/pii/S0167865500001185"]
		)

	# noinspection PyMethodOverriding
	def _compute(
			self,
			predictions: List[List[Any]],
			references: List[Union[List[Any], Set[Any]]],
			k_values: Optional[List[int]] = None,
			compute_per_NR: bool = False,  # noqa
			average: Optional[str] = "macro",
			relevance_threshold: float = 1.0,
			ignore_missing: bool = True,
			**kwargs
	) -> Dict[str, Any]:
		if not predictions or not references:
			raise ValueError("Empty predictions and references provided")

		if len(predictions) != len(references):
			raise ValueError(
				f"Mismatch in the number of predictions ({len(predictions)}) and references ({len(references)})"
			)

		if k_values is None:
			k_values = [1, 5, 10, 20, 50]

		# Validate k_values
		for k in k_values:
			if not isinstance(k, int) or k <= 0:
				raise ValueError(f"All k values must be positive integers, got: {k}")

		# Validate averaging method
		if average not in ["macro", "micro", None]:
			raise ValueError("average must be 'macro', 'micro', or None")

		# Initialize results storage
		per_query_scores = {f"hit_at_{k_val}": [] for k_val in k_values}
		if compute_per_NR:
			per_query_scores["hit_at_NR"] = []

		valid_queries = 0
		total_hits = {k: 0 for k in k_values}
		total_hits_NR = 0  # noqa

		for pred_items, ref_items in zip(predictions, references):
			# Parse references to extract relevant items
			try:
				relevant_set = _parse_references(ref_items, relevance_threshold)
			except Exception as e:
				raise ValueError(f"Error parsing references: {e}")

			# Handle queries with no relevant items
			if not relevant_set:
				if ignore_missing:
					continue
				else:
					# Add zero scores for queries with no relevant items
					for k_val in k_values:
						per_query_scores[f"hit_at_{k_val}"].append(0.0)
					if compute_per_NR:
						per_query_scores["hit_at_NR"].append(0.0)
					valid_queries += 1
					continue

			valid_queries += 1

			# Parse predictions to get ranked items
			try:
				ranked_items = _parse_predictions(pred_items)
			except Exception as e:
				raise ValueError(f"Error parsing predictions: {e}")

			# Compute hit@k for each k value
			for k_val in k_values:
				score = hit_at_k(ranked_items, relevant_set, k_val)
				per_query_scores[f"hit_at_{k_val}"].append(score)

				# For micro/macro averaging - count hits
				total_hits[k_val] += score

			# Compute Hit@NR if requested
			if compute_per_NR:
				NR = len(relevant_set)
				score_nr = hit_at_k(ranked_items, relevant_set, NR)
				per_query_scores["hit_at_NR"].append(score_nr)

				# For averaging
				total_hits_NR += score_nr

		if valid_queries == 0:
			warnings.warn("No valid queries found for evaluation")
			results = {}
			for k_val in k_values:
				key_name = f"hit_at_{k_val}"
				results[key_name] = 0.0 if average is not None else []
			if compute_per_NR:
				results["hit_at_NR"] = 0.0 if average is not None else []
			return results

		# Compute final scores based on averaging method
		results = {}

		if average in ["macro", "micro"]:
			# For binary metrics like Hit@K, macro and micro averaging are equivalent
			# Both compute the proportion of successful queries
			for k_val in k_values:
				results[f"hit_at_{k_val}"] = total_hits[k_val] / valid_queries

			if compute_per_NR:
				results["hit_at_NR"] = total_hits_NR / valid_queries

		else:  # average is None
			# Return per-query results
			for k_val in k_values:
				key = f"hit_at_{k_val}"
				results[f"hit_at_{k_val}"] = per_query_scores[key]

			if compute_per_NR:
				results["hit_at_NR"] = per_query_scores["hit_at_NR"]

		# Add summary statistics
		if average is not None:
			results["total_queries"] = valid_queries
			if valid_queries > 0:
				avg_relevant = sum(len(_parse_references(ref_items)) for _, ref_items in zip(predictions, references)
								   if _parse_references(ref_items)) / valid_queries
				results["avg_relevant_per_query"] = avg_relevant

		return results


# Convenience function for standalone usage
def compute_hit_at_k(
		predictions: List[List[str]],
		references: List[List[str]],
		k_values: Optional[List[int]] = None,
		**kwargs
) -> Dict[str, float]:
	"""
	Convenience function to compute Hit@K without using the evaluate framework.

	Args:
		predictions: List of prediction lists (ranked item IDs)
		references: List of reference lists (relevant item IDs)
		k_values: List of K values to compute
		**kwargs: Additional arguments passed to the metric

	Returns:
		Dictionary of Hit@K scores
	"""
	if k_values is None:
		k_values = [1, 5, 10, 20, 50]

	metric = HitAtK()
	return metric.compute(
		predictions=predictions,
		references=references,
		k_values=k_values,
		**kwargs
	)
