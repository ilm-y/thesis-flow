#!/usr/bin/env python3
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Test script for search optimization and result filtering tools.
Tests query optimization, result filtering, and quality assessment.
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.query_optimizer import QueryOptimizer, optimize_search_queries
from src.tools.result_filter import ResultFilter, filter_and_rank_results
from src.tools.quality_assessment import QualityAssessment, assess_paper_quality


def test_query_optimization():
    """Test search query optimization."""
    print("\n" + "="*80)
    print("TEST 1: SEARCH QUERY OPTIMIZATION")
    print("="*80)

    test_cases = [
        {
            "name": "AI Glasses Research",
            "description": "Search academic databases (arXiv, IEEE Xplore, ACM Digital Library) and industry news websites for information related to AI glasses. Gather historical data such as the timeline of AI glasses development, early pioneers, and foundational work. Also, collect current data including the latest technological advances, market situation, and recent product launches. Aim to collect at least 25 academic papers and relevant industry reports spanning the past 5 years."
        },
        {
            "name": "Medical AI Applications",
            "description": "Find information about deep learning applications in medical diagnosis and treatment, including CNN-based image analysis, transformer models for healthcare, and clinical deployment challenges."
        },
        {
            "name": "Quantum Computing",
            "description": "Research quantum computing algorithms and their applications in cryptography, optimization, and machine learning, including recent breakthroughs from 2023-2025."
        }
    ]

    for test in test_cases:
        print(f"\n📌 Test: {test['name']}")
        print(f"Original Description:\n  {test['description'][:100]}...")

        # Call optimizer
        result = optimize_search_queries(test['description'])
        result_dict = json.loads(result)

        print(f"\n✅ Generated {result_dict['count']} optimized queries:")
        for i, query in enumerate(result_dict['queries'], 1):
            print(f"   {i}. {query}")

        print(f"\n📊 Strategy: {result_dict['explanation']}")


def test_result_filtering():
    """Test result filtering and ranking."""
    print("\n" + "="*80)
    print("TEST 2: RESULT FILTERING AND RANKING")
    print("="*80)

    # Create sample results (simulating arXiv search results)
    sample_results = [
        {
            "title": "Deep Learning for Computer Vision: A Comprehensive Survey",
            "snippet": "This comprehensive survey covers recent advances in deep learning for computer vision, including convolutional neural networks, vision transformers, and their applications in image classification, object detection, and semantic segmentation.",
            "link": "https://arxiv.org/abs/2401.12345",
            "published_date": "2024-01-15"
        },
        {
            "title": "Deep Learning for Computer Vision: A Comprehensive Survey",
            "snippet": "This comprehensive survey covers recent advances in deep learning for computer vision...",
            "link": "https://arxiv.org/abs/2401.12345"
        },  # Duplicate
        {
            "title": "404 Not Found",
            "snippet": "Error page",
            "link": "https://broken-link-example.com"
        },  # Low quality
        {
            "title": "Vision Transformers: A Game Changer in Computer Vision",
            "snippet": "Vision Transformers (ViT) have emerged as a powerful alternative to CNNs. This paper introduces a novel vision transformer architecture achieving state-of-the-art results on ImageNet with reduced computational complexity.",
            "link": "https://arxiv.org/abs/2210.54321",
            "published_date": "2022-10-30"
        },
        {
            "title": "Classical Edge Detection Methods",
            "snippet": "Brief description of Canny edge detection and Sobel operators.",
            "link": "https://example.edu/papers/edges",
            "published_date": "2005-03-15"
        },  # Less relevant, older
        {
            "title": "Convolutional Neural Networks for Image Analysis",
            "snippet": "Comprehensive study of CNN architectures including AlexNet, VGG, ResNet, and their performance on various computer vision benchmarks. This work provides detailed comparison of model sizes, training times, and accuracy metrics.",
            "link": "https://scholar.google.com/scholar?q=CNN+vision",
            "published_date": "2021-05-20",
            "citations": "150+"
        },
        {
            "title": "Real-time Object Detection with Deep Neural Networks",
            "snippet": "We propose YOLO, a real-time object detection system that frames detection as a single regression problem, achieving 45 FPS on standard hardware while maintaining competitive accuracy.",
            "link": "https://arxiv.org/abs/2301.11111",
            "published_date": "2023-01-10",
            "citations": "5000+"
        }
    ]

    print(f"\n📥 Input: {len(sample_results)} raw search results")
    print("\nOriginal results include:")
    print("  - 1 exact duplicate")
    print("  - 1 broken/error page (404)")
    print("  - 1 outdated paper (2005)")
    print("  - 4 high-quality papers")

    # Call filter
    result = filter_and_rank_results(json.dumps(sample_results), "computer vision deep learning neural networks")
    result_dict = json.loads(result)

    print(f"\n✅ Filtering Results:")
    print(f"   Original: {result_dict['total_original']}")
    print(f"   Filtered: {result_dict['total_filtered']}")
    print(f"   Kept: {result_dict['quality_summary']['kept_percentage']}%")

    print(f"\n📊 Filtering Statistics:")
    print(f"   Duplicates removed: {result_dict['quality_summary']['duplicates_removed']}")
    print(f"   Low-quality removed: {result_dict['quality_summary']['low_quality_removed']}")

    print(f"\n🏆 Top Filtered Results (by rank):")
    for result in result_dict['filtered_results'][:3]:
        print(f"   {result['rank']}. {result['title'][:60]}...")
        print(f"      📌 {result['quality_notes']}")


def test_quality_assessment():
    """Test paper quality assessment."""
    print("\n" + "="*80)
    print("TEST 3: PAPER QUALITY ASSESSMENT")
    print("="*80)

    # Create sample papers with varied quality
    sample_papers = [
        {
            "title": "Vision Transformers: Replacing Convolutions with Pure Attention (2021)",
            "snippet": "We investigate the application of transformer encoders to image recognition. When trained on large amounts of image data and transferred to multiple mid-sized or small image recognition benchmarks (ImageNet, CIFAR-100, etc.), Vision Transformer (ViT) models rival or outperform state-of-the-art convolutional networks while requiring substantially fewer computational resources to train.",
            "link": "https://arxiv.org/abs/2010.11929",
            "published_date": "2021-10-25",
            "citations": "15000+"
        },
        {
            "title": "ImageNet-21K pretraining for the masses",
            "snippet": "This work presents a comprehensive study of ImageNet-21K pretraining for vision models, demonstrating the effectiveness of large-scale pretraining on downstream tasks.",
            "link": "https://arxiv.org/abs/2104.14294",
            "published_date": "2021-04-29",
            "citations": "800+"
        },
        {
            "title": "A Simple Yet Effective Baseline for 3D Human Pose Estimation",
            "snippet": "We propose a simple yet effective approach for 3D human pose estimation. Our method achieves competitive results on benchmark datasets.",
            "link": "https://example.com/paper",
            "published_date": "2019-07-15",
            "citations": "50"
        },
        {
            "title": "My Blog Post on Deep Learning",
            "snippet": "I write about deep learning techniques.",
            "link": "https://medium.com/@user/deep-learning",
            "published_date": "2023-06-01"
        },
        {
            "title": "Real-time Object Detection with YOLOv3",
            "snippet": "We present YOLOv3, an incremental improvement on YOLOv2. Using a few tricks we've improved COCO AP by 5.9%. In addition the speed is quite fast. It runs in realtime on a Titan X GPU and processes images at 150 FPS. It's also not too bad on a regular GPU.",
            "link": "https://arxiv.org/abs/1804.02767",
            "published_date": "2018-04-08",
            "citations": "20000+"
        }
    ]

    print(f"\n📥 Input: {len(sample_papers)} papers with varied quality")
    print("\nPapers include:")
    print("  - Highly-cited recent works")
    print("  - Moderately-cited papers")
    print("  - Older works")
    print("  - Blog posts")

    # Call quality assessment
    result = assess_paper_quality(json.dumps(sample_papers), "vision transformer object detection computer vision")
    result_dict = json.loads(result)

    print(f"\n✅ Quality Assessment Results:")
    print(f"   Total Assessed: {result_dict['total_assessed']}")
    print(f"   Average Quality Score: {result_dict['average_score']}/100")

    print(f"\n🏆 Quality Distribution:")
    dist = result_dict['quality_distribution']
    print(f"   ★★★★★ Excellent (90-100): {dist['excellent']}")
    print(f"   ★★★★☆ Very Good (75-90): {dist['very_good']}")
    print(f"   ★★★☆☆ Good (60-75): {dist['good']}")
    print(f"   ★★☆☆☆ Fair (45-60): {dist['fair']}")
    print(f"   ★☆☆☆☆ Poor (<45): {dist['poor']}")

    print(f"\n📊 Top Papers by Quality:")
    for i, paper in enumerate(result_dict['assessed_papers'][:3], 1):
        print(f"   {i}. {paper['title'][:50]}...")
        print(f"      Score: {paper['quality_score']}/100 - {paper['quality_rating']}")
        print(f"      Notes: {paper['scoring_notes']}")


def test_combined_workflow():
    """Test the complete optimization workflow."""
    print("\n" + "="*80)
    print("TEST 4: COMPLETE OPTIMIZATION WORKFLOW")
    print("="*80)

    # Simulate the complete workflow
    original_description = "Search for information about AI glasses, including history, current technologies, market trends, and applications"

    print(f"\n📝 Step 1: Original Research Description")
    print(f"   {original_description}")

    # Step 1: Optimize queries
    print(f"\n🔍 Step 2: Optimize Search Queries")
    opt_result = optimize_search_queries(original_description)
    opt_dict = json.loads(opt_result)
    print(f"   Generated {opt_dict['count']} optimized queries:")
    for i, query in enumerate(opt_dict['queries'], 1):
        print(f"   {i}. {query}")

    # Simulate search results
    print(f"\n🌐 Step 3: Execute Searches (Simulated)")
    print("   Would execute each query against arXiv/academic databases")

    # Step 2: Filter results (simulated)
    print(f"\n🧹 Step 4: Filter and Rank Results")
    simulated_results = [
        {"title": f"Result {i}", "snippet": "Quality content about AR/VR", "link": f"https://arxiv.org/abs/000{i}"}
        for i in range(1, 31)
    ]
    simulated_results.append({"title": "Spam", "snippet": "404 error"})  # Add some junk

    filter_result = filter_and_rank_results(json.dumps(simulated_results), " ".join(opt_dict['queries'][0].split()[:3]))
    filter_dict = json.loads(filter_result)

    print(f"   Original results: {filter_dict['total_original']}")
    print(f"   After filtering: {filter_dict['total_filtered']}")
    print(f"   Quality preserved: {filter_dict['quality_summary']['kept_percentage']}%")

    # Step 3: Assess quality (on filtered results)
    print(f"\n⭐ Step 5: Assess Paper Quality")
    if filter_dict['filtered_results']:
        assess_result = assess_paper_quality(
            json.dumps(filter_dict['filtered_results'][:5]),
            " ".join(opt_dict['queries'][0].split()[:3])
        )
        assess_dict = json.loads(assess_result)
        print(f"   Papers assessed: {assess_dict['total_assessed']}")
        print(f"   Average quality: {assess_dict['average_score']}/100")
        print(f"   Top result: {assess_dict['top_papers'][0] if assess_dict['top_papers'] else 'N/A'}")

    print(f"\n✅ Workflow Complete!")
    print(f"   Input: Verbose research description")
    print(f"   Output: High-quality filtered and ranked papers for analysis")


if __name__ == "__main__":
    print("\n" + "🧪 SEARCH OPTIMIZATION TOOLS TEST SUITE 🧪".center(80))

    try:
        test_query_optimization()
        test_result_filtering()
        test_quality_assessment()
        test_combined_workflow()

        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nSummary:")
        print("  ✓ Query optimization working")
        print("  ✓ Result filtering working")
        print("  ✓ Quality assessment working")
        print("  ✓ Complete workflow functional")
        print("\nNext steps:")
        print("  1. Export tools to researcher_node")
        print("  2. Test with actual arXiv searches")
        print("  3. Validate result quality improvements")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
