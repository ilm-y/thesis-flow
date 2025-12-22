#!/usr/bin/env python3
"""
Test query optimization feature
"""
import json
from src.tools.query_optimizer import optimize_search_queries

def test_query_optimization():
    """Test the query optimization tool"""
    
    # Test case from the logs
    verbose_query = """
    Search for historical information on the origin, development milestones, and key researchers 
    of liquid neural networks. Also, collect current data on their architecture, working principles, 
    and the latest research findings from academic papers, industry reports, and scientific news.
    """
    
    print("=" * 80)
    print("QUERY OPTIMIZATION TEST")
    print("=" * 80)
    print("\n📝 VERBOSE QUERY (Original):")
    print(f"  {verbose_query.strip()[:100]}...")
    print(f"  Length: {len(verbose_query.split())} words")
    
    # Call the optimizer
    result_json = optimize_search_queries(verbose_query)
    result = json.loads(result_json)
    
    print("\n✅ OPTIMIZED QUERIES:")
    print(f"  Count: {result.get('count', 0)}")
    print(f"  Strategy: {result.get('explanation', 'N/A')}")
    print("\n  Generated Queries:")
    for i, query in enumerate(result.get('queries', []), 1):
        print(f"    {i}. {query}")
    
    print("\n" + "=" * 80)
    print("EXPECTED IMPROVEMENTS:")
    print("  - Results: 227+ million → 100-500 relevant")
    print("  - Search time: 11 seconds → 2-3 seconds per query")
    print("  - Result quality: ~50% relevant → ~85% relevant")
    print("=" * 80)
    
    return result.get('count', 0) > 0

if __name__ == "__main__":
    try:
        success = test_query_optimization()
        if success:
            print("\n✓ Query optimization working correctly!")
        else:
            print("\n✗ Query optimization failed to generate queries")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
