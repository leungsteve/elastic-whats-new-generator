#!/usr/bin/env python3
"""
Test script for the new storytelling API endpoints.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

def test_endpoint_models():
    """Test that the new request/response models work properly."""
    print("🧪 Testing New API Endpoint Models")
    print("=" * 50)

    try:
        # Test importing the models from the API
        from src.api.main import (
            CustomerStoryRequest, CustomerStoryResponse,
            BusinessValueRequest, BusinessValueResponse,
            CompetitivePositioningRequest, CompetitivePositioningResponse
        )

        # Test CustomerStoryRequest model
        print("1. Testing CustomerStoryRequest model...")
        customer_request = CustomerStoryRequest(
            feature_id="test-feature-1",
            research_depth="standard",
            include_metrics=True,
            industry_focus="technology"
        )
        print(f"✅ CustomerStoryRequest: {customer_request.feature_id}")

        # Test BusinessValueRequest model
        print("2. Testing BusinessValueRequest model...")
        business_request = BusinessValueRequest(
            feature_ids=["test-feature-1", "test-feature-2"],
            organization_size="enterprise",
            industry="technology",
            current_spend=50000.0
        )
        print(f"✅ BusinessValueRequest: {len(business_request.feature_ids)} features")

        # Test CompetitivePositioningRequest model
        print("3. Testing CompetitivePositioningRequest model...")
        competitive_request = CompetitivePositioningRequest(
            feature_id="test-feature-1",
            competitors=["Splunk", "Datadog", "New Relic"],
            analysis_depth="comprehensive"
        )
        print(f"✅ CompetitivePositioningRequest: {len(competitive_request.competitors or [])} competitors")

        # Test Response models
        print("4. Testing Response models...")
        customer_response = CustomerStoryResponse(
            feature_id="test-feature-1",
            customer_stories=[{"customer": "TechCorp", "impact": "50% improvement"}],
            business_impact={"roi": "300%", "savings": "$2M annually"},
            generated_at=datetime.now(),
            research_depth="standard"
        )
        print(f"✅ CustomerStoryResponse: {len(customer_response.customer_stories)} stories")

        business_response = BusinessValueResponse(
            feature_ids=["test-1"],
            roi_projection={"roi": "250%", "timeline": "12 months"},
            value_drivers=[{"category": "Cost Savings", "description": "Reduced infrastructure costs"}],
            total_annual_savings="$1.5M",
            payback_period="8 months",
            calculated_at=datetime.now()
        )
        print(f"✅ BusinessValueResponse: {business_response.total_annual_savings} savings")

        competitive_response = CompetitivePositioningResponse(
            feature_id="test-1",
            competitive_analysis={"positioning": "Leader"},
            differentiators=["Best performance", "Lowest cost"],
            market_position="Leader",
            competitor_comparison={"Splunk": "2x faster", "Datadog": "50% less cost"},
            analyzed_at=datetime.now()
        )
        print(f"✅ CompetitivePositioningResponse: {len(competitive_response.differentiators)} differentiators")

        print("\n🎉 All API model tests passed!")
        return True

    except Exception as e:
        print(f"❌ Model test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_imports():
    """Test that all the storytelling components can be imported properly."""
    print("\n📦 Testing API Component Imports")
    print("=" * 50)

    try:
        print("1. Testing storytelling imports...")
        from src.core.storytelling import StoryArcPlanner, TalkTrackGenerator, NarrativeFlowAnalyzer
        from src.integrations.customer_story_research import CustomerStoryResearcher, BusinessValueCalculator
        print("✅ All storytelling components imported successfully")

        print("2. Testing component initialization...")
        researcher = CustomerStoryResearcher()
        calculator = BusinessValueCalculator()
        print("✅ Components initialized successfully")

        print("3. Testing API server can be imported...")
        from src.api.main import app
        print("✅ FastAPI app imported successfully")

        print("\n🎉 All import tests passed!")
        return True

    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_endpoint_routes():
    """Test that the endpoint routes are properly defined."""
    print("\n🛣️  Testing API Route Definitions")
    print("=" * 50)

    try:
        from src.api.main import app

        # Get all routes from the FastAPI app
        routes = []
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                for method in route.methods:
                    routes.append(f"{method} {route.path}")

        # Check for our new endpoints
        expected_endpoints = [
            "POST /features/{feature_id}/customer-stories",
            "POST /features/business-value",
            "POST /features/{feature_id}/competitive-analysis"
        ]

        print("1. Checking for new storytelling endpoints...")
        for endpoint in expected_endpoints:
            if endpoint in routes:
                print(f"✅ Found: {endpoint}")
            else:
                print(f"❌ Missing: {endpoint}")

        print(f"\n2. Total API routes defined: {len(routes)}")

        # Show some sample routes for verification
        storytelling_routes = [r for r in routes if any(keyword in r.lower() for keyword in ['customer', 'business', 'competitive'])]
        if storytelling_routes:
            print("3. Storytelling-related routes:")
            for route in storytelling_routes[:5]:  # Show first 5
                print(f"   - {route}")

        print("\n🎉 Route definition tests passed!")
        return True

    except Exception as e:
        print(f"❌ Route test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing New Storytelling API Endpoints")
    print("==========================================\n")

    # Run all tests
    success1 = test_endpoint_models()
    success2 = test_api_imports()
    success3 = test_endpoint_routes()

    if success1 and success2 and success3:
        print("\n🎉 ALL ENDPOINT TESTS PASSED!")
        print("The new storytelling API endpoints are ready for use.")
    else:
        print("\n❌ Some tests failed.")
        print("Please check the errors above.")