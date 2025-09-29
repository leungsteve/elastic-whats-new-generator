#!/usr/bin/env python3
"""
Test script for validating storytelling integration without running the full server.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.models import Feature, Domain, Theme
from src.core.storytelling import StoryArcPlanner, TalkTrackGenerator, NarrativeFlowAnalyzer
from src.integrations.customer_story_research import CustomerStoryResearcher, BusinessValueCalculator

def test_storytelling_components():
    """Test that storytelling components can be imported and initialized."""
    print("🎭 Testing Storytelling Integration")
    print("=" * 50)

    try:
        # Test component initialization
        print("1. Initializing storytelling components...")
        story_arc_planner = StoryArcPlanner()
        talk_track_generator = TalkTrackGenerator()
        narrative_flow_analyzer = NarrativeFlowAnalyzer()
        customer_story_researcher = CustomerStoryResearcher()
        business_value_calculator = BusinessValueCalculator()
        print("✅ All components initialized successfully")

        # Test with sample feature
        print("\n2. Testing with sample feature...")
        test_feature = Feature(
            id="test-vector-search-1",
            name="Advanced Vector Search",
            description="Enhanced similarity search with 90% faster performance",
            benefits=["90% faster query performance", "Better relevance scoring"],
            domain=Domain.SEARCH,
            theme=Theme.OPTIMIZE
        )

        # Test story arc planning
        print("3. Testing story arc planning...")
        story_arc = story_arc_planner.create_story_arc(
            [test_feature],
            narrative_style='customer_journey',
            domain='search',
            audience='mixed'
        )
        print(f"✅ Generated story arc with {len(story_arc.positions)} positions")

        # Test talk track generation (simplified)
        print("4. Testing talk track generation...")
        from src.core.storytelling import StoryPosition
        talk_track = talk_track_generator.generate_talk_track(
            test_feature,
            StoryPosition.OPENING_HOOK,
            detail_level='standard',
            technical_depth='medium'
        )
        print(f"✅ Generated talk track with timing: {talk_track.estimated_duration} minutes")

        # Test business value calculation
        print("5. Testing business value calculation...")
        roi_projection = business_value_calculator.calculate_roi_projection(test_feature)
        print(f"✅ Calculated ROI projection: {roi_projection.total_annual_savings}")

        print("\n🎉 All storytelling integration tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_models():
    """Test that API models can handle storytelling parameters."""
    print("\n📊 Testing API Models")
    print("=" * 50)

    try:
        from src.api.main import PresentationGenerationRequest, UnifiedPresentationRequest

        # Test storytelling parameters in request model
        print("1. Testing PresentationGenerationRequest with storytelling params...")
        request = PresentationGenerationRequest(
            feature_ids=["test-1", "test-2"],
            domain="search",
            quarter="Q1-2024",
            audience="mixed",
            narrative_style="customer_journey",
            talk_track_detail="comprehensive",
            technical_depth="high",
            include_customer_stories=True,
            competitive_positioning=True,
            storytelling_enabled=True
        )
        print("✅ PresentationGenerationRequest model works with storytelling")

        # Test unified request model
        print("2. Testing UnifiedPresentationRequest...")
        unified_request = UnifiedPresentationRequest(
            feature_ids=["test-1"],
            quarter="Q1-2024",
            audience="business",
            narrative_style="innovation_showcase",
            storytelling_enabled=True
        )
        print("✅ UnifiedPresentationRequest model works with storytelling")

        print("🎉 API model tests passed!")
        return True

    except Exception as e:
        print(f"❌ API model test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Storytelling Integration")
    print("===================================\n")

    success1 = test_storytelling_components()
    success2 = test_api_models()

    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED!")
        print("The storytelling integration is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)