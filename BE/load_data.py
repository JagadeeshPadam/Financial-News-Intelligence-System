"""
Load mock news data into the system
"""
import json
import sys
from datetime import datetime
from graph.langgraph_pipeline import news_pipeline

def load_mock_data():
    """Load mock news articles from JSON file"""
    print("🔄 Loading mock news data...")
    
    # Load JSON file
    with open('data/mock_news.json', 'r') as f:
        articles = json.load(f)
    
    print(f"📰 Found {len(articles)} articles to process")
    
    # Process each article
    processed_count = 0
    duplicate_count = 0
    error_count = 0
    
    for i, article in enumerate(articles, 1):
        try:
            print(f"\n[{i}/{len(articles)}] Processing: {article['headline'][:60]}...")
            
            result = news_pipeline.process_article(article)
            
            if result.get('error'):
                print(f"  ❌ Error: {result['error']}")
                error_count += 1
            elif result.get('is_duplicate'):
                print(f"  🔄 Duplicate detected (parent: {result.get('parent_article_id', 'unknown')[:8]}...)")
                duplicate_count += 1
            else:
                processed_count += 1
                entities = result.get('entities', {})
                stocks = result.get('impacted_stocks', [])
                print(f"  ✅ Processed successfully")
                print(f"     Entities: {sum(len(v) for v in entities.values())} extracted")
                print(f"     Stocks: {len(stocks)} impacted")
        
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            error_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("📊 Summary:")
    print(f"  ✅ Successfully processed: {processed_count}")
    print(f"  🔄 Duplicates detected: {duplicate_count}")
    print(f"  ❌ Errors: {error_count}")
    print(f"  📈 Total articles: {len(articles)}")
    print("="*60)
    
    if processed_count > 0:
        print("\n✨ Mock data loaded successfully!")
        print("🚀 You can now query the system via the API or frontend.")
    else:
        print("\n⚠️  Warning: No articles were successfully processed.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(load_mock_data())
