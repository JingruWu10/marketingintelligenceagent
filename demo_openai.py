import pandas as pd

from marketing_intelligence_agent import BusinessContext, KPIObservation, MarketingIntelligenceAgent
from marketing_intelligence_agent.llm.openai_provider import OpenAISynthesisProvider


def main():
    df = pd.read_csv("data/synthetic_kpis.csv")
    observations = [KPIObservation(**row) for row in df.to_dict(orient="records")]

    context = BusinessContext(
        objective="Understand why revenue growth is below target and identify the next decision-changing analysis.",
        customer_segment="all",
        constraints=["Do not infer causality from observational KPI movement alone."],
    )

    agent = MarketingIntelligenceAgent()
    provider = OpenAISynthesisProvider()
    result = agent.analyze_with_ai(context, observations, provider)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
