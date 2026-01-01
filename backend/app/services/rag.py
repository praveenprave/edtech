import os
from typing import List, Dict, Any
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.api_core.client_options import ClientOptions

class RAGService:
    """
    Service for retrieving content from Vertex AI Search (Discovery Engine).
    """
    def __init__(self, project_id: str, location: str = "global", data_store_id: str = None):
        self.project_id = project_id
        self.location = location
        # Use Env Var if not passed, else default
        self.data_store_id = data_store_id or os.getenv("DATA_STORE_ID", "textbooks-search")
        self.client = None
        
        # Initialize Client if credentials exist
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_CLOUD_PROJECT"):
            try:
                # Setup Client Options for the global location
                client_options = (
                    ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
                    if location != "global" else None
                )
                self.client = discoveryengine.SearchServiceClient(client_options=client_options)
            except Exception as e:
                print(f"⚠️ RAG Service Warning: Could not init Vertex AI Client: {e}")

    def search(self, query: str) -> str:
        """
        Searches the Vector DB for relevant textbook content.
        """
        print(f"🔍 RAG Search Query: {query}")
        
        # If client is not initialized (e.g. local dev without creds), return mock
        if not self.client:
           return self._mock_search_results(query)

        try:
            serving_config = self.client.serving_config_path(
                project=self.project_id,
                location=self.location,
                data_store=self.data_store_id,
                serving_config="default_config",
            )

            request = discoveryengine.SearchRequest(
                serving_config=serving_config,
                query=query,
                page_size=3,
                content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                    snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                        return_snippet=True
                    ),
                    summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                        summary_result_count=3,
                        include_citations=True,
                    ),
                ),
            )

            response = self.client.search(request)
            
            # combine summaries or snippets
            context = ""
            if response.summary and response.summary.summary_text:
                context += f"Summary: {response.summary.summary_text}\n\n"
            
            for result in response.results:
                data = result.document.derived_struct_data
                if "snippets" in data:
                     for snippet in data["snippets"]:
                         context += f"- {snippet.get('snippet', '')}\n"
            
            return context if context else "No relevant textbook content found."

        except Exception as e:
            print(f"❌ RAG Search Error: {e}")
            return self._mock_search_results(query)

    def _mock_search_results(self, query: str) -> str:
        """
        Fallback/Mock content for demo purposes.
        """
        print("⚠️ Using Mock RAG Results")
        if "photosynthesis" in query.lower():
            return """
            Textbook: Biology Std 10, Unit 2
            Page 45: Photosynthesis is the process by which green plants use sunlight to make their own food.
            Equation: 6CO2 + 6H2O + Light -> C6H12O6 + 6O2.
            Key Components: Chlorophyll (in Chloroplasts), Stomata (for gas exchange).
            Steps: 1. Light-dependent reaction (Thylakoids). 2. Calvin Cycle (Stroma).
            """
        elif "gravity" in query.lower():
             return """
             Textbook: Physics Std 9, Chapter 4
             Page 102: Universal Law of Gravitation. Every object in the universe attracts every other object.
             Formula: F = G * (m1 * m2) / r^2.
             G is the gravitational constant.
             """
        return f"Generic textbook definition for: {query}"
