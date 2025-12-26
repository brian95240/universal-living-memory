"""
$0-Cost Optimizer - Intelligent Cost Minimization
Vertex Genesis v1.3.0

Decision engine that always chooses the best $0-cost option.
Tracks costs, suggests optimizations, and prevents expensive choices.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CostTier(Enum):
    """Cost tiers for model selection."""
    FREE = 0  # $0 cost
    CHEAP = 1  # < $0.001 per 1k tokens
    MODERATE = 2  # < $0.01 per 1k tokens
    EXPENSIVE = 3  # >= $0.01 per 1k tokens


@dataclass
class CostDecision:
    """Cost decision result."""
    chosen_option: str
    cost_per_1k_tokens: float
    cost_tier: CostTier
    reasoning: str
    alternatives: List[Dict[str, Any]]
    savings: float  # Compared to most expensive option


class CostOptimizer:
    """
    $0-cost optimizer with intelligent decision making.
    Always prioritizes free options, suggests optimizations.
    """
    
    def __init__(self):
        self.total_cost = 0.0
        self.decision_history: List[CostDecision] = []
        self.free_options_used = 0
        self.paid_options_avoided = 0
        
        logger.info("💰 Cost Optimizer initialized (Target: $0)")
    
    def _classify_cost(self, cost_per_1k: float) -> CostTier:
        """Classify cost into tier."""
        if cost_per_1k == 0.0:
            return CostTier.FREE
        elif cost_per_1k < 0.001:
            return CostTier.CHEAP
        elif cost_per_1k < 0.01:
            return CostTier.MODERATE
        else:
            return CostTier.EXPENSIVE
    
    def evaluate_options(
        self,
        options: List[Dict[str, Any]],
        context: str = "",
        quality_threshold: float = 0.7
    ) -> CostDecision:
        """
        Evaluate options and choose best $0-cost option.
        
        Args:
            options: List of option dictionaries with 'cost_per_1k_tokens', 'quality_score', etc.
            context: Context for decision making
            quality_threshold: Minimum acceptable quality score (0-1)
        
        Returns:
            CostDecision with chosen option and reasoning
        """
        if not options:
            raise ValueError("No options provided")
        
        # Filter by quality threshold
        quality_options = [
            opt for opt in options
            if opt.get('quality_score', 1.0) >= quality_threshold
        ]
        
        if not quality_options:
            logger.warning(f"⚠️ No options meet quality threshold {quality_threshold}, using all options")
            quality_options = options
        
        # Separate free and paid options
        free_options = [
            opt for opt in quality_options
            if opt.get('cost_per_1k_tokens', 0.0) == 0.0
        ]
        
        paid_options = [
            opt for opt in quality_options
            if opt.get('cost_per_1k_tokens', 0.0) > 0.0
        ]
        
        # ALWAYS prefer free options
        if free_options:
            # Sort free options by quality score (descending)
            free_options.sort(
                key=lambda x: (
                    x.get('quality_score', 0.5),
                    -x.get('params_millions', 999999),  # Prefer smaller models
                    x.get('downloads', 0)  # Prefer popular models
                ),
                reverse=True
            )
            
            chosen = free_options[0]
            
            # Calculate savings
            if paid_options:
                most_expensive = max(paid_options, key=lambda x: x.get('cost_per_1k_tokens', 0.0))
                savings = most_expensive.get('cost_per_1k_tokens', 0.0)
            else:
                savings = 0.0
            
            # Build reasoning
            reasoning = f"Selected FREE option: {chosen.get('model_id', 'unknown')} "
            reasoning += f"(quality: {chosen.get('quality_score', 0.5):.2f}, "
            reasoning += f"params: {chosen.get('params_millions', 0)}M). "
            reasoning += f"Avoided {len(paid_options)} paid options. "
            if savings > 0:
                reasoning += f"Saved ${savings:.4f} per 1k tokens."
            
            decision = CostDecision(
                chosen_option=chosen.get('model_id', 'unknown'),
                cost_per_1k_tokens=0.0,
                cost_tier=CostTier.FREE,
                reasoning=reasoning,
                alternatives=[
                    {
                        'model_id': opt.get('model_id'),
                        'cost': opt.get('cost_per_1k_tokens'),
                        'quality': opt.get('quality_score')
                    }
                    for opt in free_options[1:4]  # Top 3 alternatives
                ],
                savings=savings
            )
            
            self.free_options_used += 1
            self.paid_options_avoided += len(paid_options)
            
            logger.info(f"✅ {reasoning}")
            
            self.decision_history.append(decision)
            return decision
        
        # No free options available - this is a problem!
        logger.error("❌ NO FREE OPTIONS AVAILABLE - This violates $0-cost principle!")
        
        # Find cheapest paid option as fallback
        paid_options.sort(key=lambda x: x.get('cost_per_1k_tokens', 999999))
        chosen = paid_options[0]
        cost = chosen.get('cost_per_1k_tokens', 0.0)
        
        reasoning = f"⚠️ FALLBACK: No free options available. "
        reasoning += f"Selected cheapest paid option: {chosen.get('model_id', 'unknown')} "
        reasoning += f"at ${cost:.4f} per 1k tokens. "
        reasoning += "RECOMMENDATION: Index more free models to avoid costs!"
        
        decision = CostDecision(
            chosen_option=chosen.get('model_id', 'unknown'),
            cost_per_1k_tokens=cost,
            cost_tier=self._classify_cost(cost),
            reasoning=reasoning,
            alternatives=[],
            savings=0.0
        )
        
        logger.warning(reasoning)
        
        self.decision_history.append(decision)
        return decision
    
    def track_usage(self, tokens_used: int, cost_per_1k: float):
        """
        Track token usage and cost.
        
        Args:
            tokens_used: Number of tokens used
            cost_per_1k: Cost per 1k tokens
        """
        cost = (tokens_used / 1000) * cost_per_1k
        self.total_cost += cost
        
        if cost > 0:
            logger.warning(f"💸 Cost incurred: ${cost:.6f} ({tokens_used} tokens @ ${cost_per_1k:.4f}/1k)")
        else:
            logger.info(f"✅ Free usage: {tokens_used} tokens")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cost optimization statistics.
        
        Returns:
            Statistics dictionary
        """
        total_decisions = len(self.decision_history)
        total_savings = sum(d.savings for d in self.decision_history)
        
        return {
            'total_cost': self.total_cost,
            'total_decisions': total_decisions,
            'free_options_used': self.free_options_used,
            'paid_options_avoided': self.paid_options_avoided,
            'total_savings': total_savings,
            'average_savings_per_decision': total_savings / total_decisions if total_decisions > 0 else 0.0,
            'cost_efficiency': (self.free_options_used / total_decisions * 100) if total_decisions > 0 else 0.0
        }
    
    def suggest_optimizations(self) -> List[str]:
        """
        Suggest cost optimizations based on decision history.
        
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        stats = self.get_statistics()
        
        # Check if we're meeting $0-cost target
        if stats['total_cost'] > 0:
            suggestions.append(
                f"⚠️ Total cost is ${stats['total_cost']:.4f}, not $0. "
                "Consider indexing more free models."
            )
        
        # Check cost efficiency
        if stats['cost_efficiency'] < 100:
            suggestions.append(
                f"💡 Cost efficiency is {stats['cost_efficiency']:.1f}%. "
                "Aim for 100% by using only free models."
            )
        
        # Check for repeated paid options
        paid_decisions = [d for d in self.decision_history if d.cost_per_1k_tokens > 0]
        if paid_decisions:
            paid_models = {}
            for d in paid_decisions:
                paid_models[d.chosen_option] = paid_models.get(d.chosen_option, 0) + 1
            
            for model, count in paid_models.items():
                suggestions.append(
                    f"🔍 Model '{model}' was used {count} times with cost. "
                    "Find a free alternative and add to index."
                )
        
        # Check for missing use cases
        if stats['total_decisions'] > 10:
            free_rate = stats['free_options_used'] / stats['total_decisions']
            if free_rate < 0.9:
                suggestions.append(
                    "📚 Consider bulk indexing more free models from HuggingFace "
                    "to increase free option availability."
                )
        
        if not suggestions:
            suggestions.append("✅ Cost optimization is perfect! Maintaining $0 cost.")
        
        return suggestions
    
    def reset_statistics(self):
        """Reset all statistics."""
        self.total_cost = 0.0
        self.decision_history = []
        self.free_options_used = 0
        self.paid_options_avoided = 0
        logger.info("📊 Cost statistics reset")


# Global optimizer instance
_global_optimizer: Optional[CostOptimizer] = None


def get_optimizer() -> CostOptimizer:
    """Get or create global cost optimizer instance."""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = CostOptimizer()
    return _global_optimizer


# Convenience function for quick decisions
def choose_best_free_option(
    options: List[Dict[str, Any]],
    context: str = ""
) -> Tuple[Dict[str, Any], str]:
    """
    Choose best free option from list.
    
    Args:
        options: List of option dictionaries
        context: Context for decision
    
    Returns:
        Tuple of (chosen_option, reasoning)
    """
    optimizer = get_optimizer()
    decision = optimizer.evaluate_options(options, context)
    
    # Find the chosen option in original list
    chosen = next(
        (opt for opt in options if opt.get('model_id') == decision.chosen_option),
        options[0]
    )
    
    return chosen, decision.reasoning


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    optimizer = CostOptimizer()
    
    # Test: Free vs paid options
    options1 = [
        {'model_id': 'free-model-1', 'cost_per_1k_tokens': 0.0, 'quality_score': 0.85, 'params_millions': 3000},
        {'model_id': 'free-model-2', 'cost_per_1k_tokens': 0.0, 'quality_score': 0.80, 'params_millions': 7000},
        {'model_id': 'paid-model-1', 'cost_per_1k_tokens': 0.002, 'quality_score': 0.95, 'params_millions': 70000},
        {'model_id': 'paid-model-2', 'cost_per_1k_tokens': 0.01, 'quality_score': 0.98, 'params_millions': 175000}
    ]
    
    decision1 = optimizer.evaluate_options(options1, context="text generation")
    print(f"Decision 1: {decision1.chosen_option} - {decision1.reasoning}")
    
    # Test: Only free options
    options2 = [
        {'model_id': 'free-model-3', 'cost_per_1k_tokens': 0.0, 'quality_score': 0.75, 'params_millions': 1000},
        {'model_id': 'free-model-4', 'cost_per_1k_tokens': 0.0, 'quality_score': 0.90, 'params_millions': 5000}
    ]
    
    decision2 = optimizer.evaluate_options(options2, context="translation")
    print(f"Decision 2: {decision2.chosen_option} - {decision2.reasoning}")
    
    # Get statistics
    stats = optimizer.get_statistics()
    print(f"Statistics: {stats}")
    
    # Get suggestions
    suggestions = optimizer.suggest_optimizations()
    print("Suggestions:")
    for s in suggestions:
        print(f"  - {s}")
