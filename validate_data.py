#!/usr/bin/env python3
"""
Data Quality Validator for WAF Training Data
Checks diversity, distribution, and readiness for training
"""

import json
from collections import Counter
import sys

def validate_data(jsonl_path="data/tokenized/benign_sequences.jsonl"):
    print("=" * 60)
    print("WAF TRAINING DATA VALIDATION")
    print("=" * 60)
    print()
    
    # Load sequences
    sequences = []
    try:
        with open(jsonl_path) as f:
            for line in f:
                sequences.append(json.loads(line)['tokens'])
    except FileNotFoundError:
        print(f"❌ ERROR: File not found: {jsonl_path}")
        print("   Run tokenize_requests.py first!")
        sys.exit(1)
    
    if not sequences:
        print("❌ ERROR: No sequences found!")
        sys.exit(1)
    
    # Basic stats
    total_sequences = len(sequences)
    unique_sequences = len(set(tuple(s) for s in sequences))
    diversity_ratio = (unique_sequences / total_sequences) * 100
    
    print(f"📊 BASIC STATISTICS")
    print(f"  Total sequences: {total_sequences:,}")
    print(f"  Unique patterns: {unique_sequences:,}")
    print(f"  Diversity ratio: {diversity_ratio:.2f}%")
    print()
    
    # Quality check
    if total_sequences < 10000:
        print(f"⚠️  WARNING: Only {total_sequences:,} sequences")
        print("   Recommended minimum: 10,000")
        print()
    
    if diversity_ratio < 10:
        print(f"❌ CRITICAL: Diversity too low ({diversity_ratio:.2f}%)")
        print("   Need at least 10% unique patterns")
        print("   → Run traffic generation longer or fix scripts")
        print()
        status = "FAILED"
    elif diversity_ratio < 20:
        print(f"⚠️  WARNING: Diversity acceptable but low ({diversity_ratio:.2f}%)")
        print("   Recommended: 20%+ for best results")
        print()
        status = "ACCEPTABLE"
    else:
        print(f"✅ GOOD: Diversity is strong ({diversity_ratio:.2f}%)")
        print()
        status = "GOOD"
    
    # Length distribution
    lengths = [len(s) for s in sequences]
    print(f"📏 SEQUENCE LENGTH")
    print(f"  Min: {min(lengths)}, Max: {max(lengths)}, Avg: {sum(lengths)/len(lengths):.2f}")
    print()
    
    # Token analysis
    all_tokens = [t for seq in sequences for t in seq]
    token_counts = Counter(all_tokens)
    
    print(f"🔤 TOKEN STATISTICS")
    print(f"  Total tokens: {len(all_tokens):,}")
    print(f"  Unique tokens: {len(token_counts):,}")
    print()
    
    print(f"  Top 15 tokens:")
    for token, count in token_counts.most_common(15):
        percentage = (count / len(all_tokens)) * 100
        print(f"    {token:40s} {count:6,} ({percentage:5.2f}%)")
    print()
    
    # App distribution
    app_tokens = [seq[0] for seq in sequences if seq and seq[0].startswith('APP_')]
    app_counts = Counter(app_tokens)
    
    print(f"🌐 APPLICATION DISTRIBUTION")
    for app, count in sorted(app_counts.items()):
        percentage = (count / len(app_tokens)) * 100
        print(f"  {app:20s} {count:6,} ({percentage:5.2f}%)")
    print()
    
    # Check balance
    app_percentages = [(count / len(app_tokens)) * 100 for count in app_counts.values()]
    if max(app_percentages) > 60:
        print(f"⚠️  WARNING: Imbalanced app distribution")
        print(f"   One app dominates with {max(app_percentages):.1f}%")
        print()
    else:
        print(f"✅ GOOD: Apps are reasonably balanced")
        print()
    
    # Method distribution
    method_tokens = [t for seq in sequences for t in seq if t.startswith('METHOD_')]
    method_counts = Counter(method_tokens)
    
    print(f"📨 HTTP METHOD DISTRIBUTION")
    for method, count in sorted(method_counts.items(), key=lambda x: -x[1]):
        percentage = (count / len(method_tokens)) * 100
        print(f"  {method:20s} {count:6,} ({percentage:5.2f}%)")
    print()
    
    # Check for POST presence
    post_percentage = (method_counts.get('METHOD_POST', 0) / len(method_tokens)) * 100
    if post_percentage < 10:
        print(f"⚠️  WARNING: Very few POST requests ({post_percentage:.2f}%)")
        print("   Real traffic usually has 15-30% POST")
        print()
    else:
        print(f"✅ GOOD: POST requests present ({post_percentage:.2f}%)")
        print()
    
    # Status code distribution
    status_tokens = [t for seq in sequences for t in seq if t.startswith('STATUS_')]
    status_counts = Counter(status_tokens)
    
    print(f"📊 STATUS CODE DISTRIBUTION")
    for status, count in sorted(status_counts.items()):
        percentage = (count / len(status_tokens)) * 100
        print(f"  {status:20s} {count:6,} ({percentage:5.2f}%)")
    print()
    
    # Final verdict
    print("=" * 60)
    print(f"FINAL VERDICT: {status}")
    print("=" * 60)
    print()
    
    if status == "FAILED":
        print("❌ DATA NOT READY FOR TRAINING")
        print("   → Generate more diverse traffic")
        print("   → Ensure all apps are running")
        print("   → Check Locust scripts are using enhanced versions")
        sys.exit(1)
    elif status == "ACCEPTABLE":
        print("⚠️  DATA ACCEPTABLE BUT NOT OPTIMAL")
        print("   You can proceed with training, but:")
        print("   → Consider running traffic generation longer")
        print("   → Model performance may be limited")
        print()
        print("Proceed? (y/n): ", end="")
        sys.exit(0)
    else:
        print("✅ DATA READY FOR TRAINING!")
        print("   → High diversity: Good generalization expected")
        print("   → Balanced distribution: Fair representation")
        print("   → Sufficient volume: Adequate for learning")
        print()
        print("Next step: Run training script")
        sys.exit(0)

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "data/tokenized/benign_sequences.jsonl"
    validate_data(path)
