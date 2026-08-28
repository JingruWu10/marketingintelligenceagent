from marketing_intelligence_agent import AISynthesis, BusinessContext, KPIObservation, MarketingIntelligenceAgent


class FakeProvider:
    def synthesize(self, context, analysis):
        assert context.objective == "Grow revenue"
        assert analysis.hypotheses
        return AISynthesis(
            executive_summary="Conversion weakened while traffic was stable.",
            observed=analysis.what_changed,
            inferred=[analysis.hypotheses[0].statement],
            unknown=["Which funnel step explains the decline"],
            recommended=["Diagnose the leaking step before changing media investment"],
            next_analysis=analysis.what_to_check_next,
            confidence="high",
        )


def test_ai_layer_keeps_deterministic_output_separate():
    observations = [
        KPIObservation(metric="sessions", current=100, prior=100, segment="all"),
        KPIObservation(metric="purchase_conversion_rate", current=0.02, prior=0.03, segment="all"),
    ]
    result = MarketingIntelligenceAgent().analyze_with_ai(
        BusinessContext(objective="Grow revenue"),
        observations,
        FakeProvider(),
    )
    assert result.deterministic.hypotheses
    assert result.ai_synthesis.confidence == "high"
    assert "Diagnose" in result.ai_synthesis.recommended[0]
