from marketing_intelligence_agent import BusinessContext, KPIObservation, MarketingIntelligenceAgent


def test_detects_funnel_issue_when_traffic_stable_and_conversion_down():
    observations = [
        KPIObservation(metric="sessions", current=100, prior=100, segment="all"),
        KPIObservation(metric="purchase_conversion_rate", current=0.02, prior=0.03, segment="all"),
    ]
    result = MarketingIntelligenceAgent().analyze(
        BusinessContext(objective="Grow revenue"), observations
    )
    assert any("funnel progression" in h.statement.lower() for h in result.hypotheses)
