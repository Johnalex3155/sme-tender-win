import sys
from src.utils.scraper import TenderScraper
from src.agents.tender_agent import TenderAgent

def main():
    print("--- SME Tender-Win Agent ---")
    
    # Initialize
    scraper = TenderScraper()
    agent = TenderAgent("data/sme_profile.json")
    
    # 1. Search
    query = "AI Logistics government tenders Egypt"
    results = scraper.search_tenders(query)
    
    if not results:
        print("Error: No tenders found or Firecrawl unreachable.")
        return
    else:
        # Extract the first promising result
        url = results[0].get('url', 'http://example.com')
        tender_text = scraper.get_tender_details(url)
        
    if not tender_text:
        print("Error: Could not extract content from the tender.")
        return

    # 2. Analyze
    analysis = agent.analyze_win_probability(tender_text)
    print(f"\n[Analysis] Win Probability: {analysis['probability']}")
    print(f"Justification: {analysis['justification']}")
    
    # 3. Draft
    proposal = agent.generate_proposal_draft(tender_text)
    print(f"\n[Proposal Draft]\n{proposal['technical_approach']}")
    print(f"\n[Checklist]\n{'- '.join(proposal['checklist'])}")

if __name__ == '__main__':
    main()