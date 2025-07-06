"""Manages the knowledge base for intelligent help desk system"""
import os
import json
import re
from typing import List
import openai
import numpy as np
import faiss
from .models import KnowledgeItem
from .config import Config


class KnowledgeBaseManager:
    """Manages the knowledge base for intelligent help desk system"""

    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.knowledge_items: List[KnowledgeItem] = []
        self.vector_index = None
        self.categories = {}
        self.troubleshooting_steps = {}
        self.installation_guides = {}
        self.embedding_model = Config.OPENAI_EMBEDDING_MODEL
        self.embedding_dim = Config.OPENAI_EMBEDDING_DIMENSION
        self.index_path = os.path.join(
            Config.KNOWLEDGE_BASE_DIR, "knowledge_base_index.faiss"
        )
        self.items_path = os.path.join(
            Config.KNOWLEDGE_BASE_DIR, "knowledge_items.json"
        )

    def load_knowledge_base(self):
        """Load all knowledge base documents and create or load vector embeddings"""
        print("Loading knowledge base...")
        # Try to load saved index and items
        if os.path.exists(self.index_path) and os.path.exists(self.items_path):
            print("Loading saved FAISS index and knowledge items...")
            self.vector_index = faiss.read_index(self.index_path)
            with open(self.items_path, "r", encoding="utf-8") as f:
                items_data = json.load(f)
                self.knowledge_items = [
                    KnowledgeItem(**item) for item in items_data
                ]
            print(f"Loaded {len(self.knowledge_items)} items from disk.")
        else:
            # Load categories
            with open(Config.CATEGORIES_PATH, "r", encoding="utf-8") as f:
                self.categories = json.load(f)["categories"]

            # Load troubleshooting database
            with open(Config.TROUBLESHOOTING_PATH, "r", encoding="utf-8") as f:
                self.troubleshooting_steps = json.load(f)["troubleshooting_steps"]

            # Load installation guides
            with open(Config.INSTALLATION_GUIDES_PATH, "r", encoding="utf-8") as f:
                self.installation_guides = json.load(f)["software_guides"]

            # Process knowledge base markdown
            self._process_knowledge_base_md()

            # Process policies markdown
            self._process_policies_md()

            # Process troubleshooting steps
            self._process_troubleshooting_steps()

            # Process installation guides
            self._process_installation_guides()

            # Create vector embeddings
            self._create_vector_embeddings()

            # Save index and items
            faiss.write_index(self.vector_index, self.index_path)
            with open(self.items_path, "w", encoding="utf-8") as f:
                json.dump([item.dict() for item in self.knowledge_items], f)
            print(
                f"Knowledge base loaded and saved with {len(self.knowledge_items)} items."
            )

    def _process_knowledge_base_md(self):
        """Process the knowledge base markdown file"""
        with open(Config.KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        # Split into sections
        sections = re.split(r"^##\s+", content, flags=re.MULTILINE)

        for section in sections[1:]:  # Skip first empty section
            lines = section.strip().split("\n")
            title = lines[0].strip()
            content_lines = lines[1:]

            # Create knowledge items for each bullet point
            for line in content_lines:
                line = line.strip()
                if line.startswith("-") and len(line) > 1:
                    item_content = line[1:].strip()
                    if item_content:
                        self.knowledge_items.append(
                            KnowledgeItem(
                                content=item_content,
                                source=f"Knowledge Base - {title}",
                                relevance_score=0.0,
                                category=self._map_category_from_title(title),
                            )
                        )

    def _process_policies_md(self):
        """Process the company policies markdown file"""
        with open(Config.POLICIES_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        # Split into sections
        sections = re.split(r"^##\s+", content, flags=re.MULTILINE)

        for section in sections[1:]:
            lines = section.strip().split("\n")
            title = lines[0].strip()
            content_lines = lines[1:]

            # Create knowledge items for each bullet point
            for line in content_lines:
                line = line.strip()
                if line.startswith("-") and len(line) > 1:
                    item_content = line[1:].strip()
                    if item_content:
                        self.knowledge_items.append(
                            KnowledgeItem(
                                content=item_content,
                                source=f"Company Policies - {title}",
                                relevance_score=0.0,
                                category=self._map_category_from_title(title),
                            )
                        )

    def _process_troubleshooting_steps(self):
        """Process troubleshooting database"""
        for issue, data in self.troubleshooting_steps.items():
            # Add the main issue description
            self.knowledge_items.append(
                KnowledgeItem(
                    content=f"Troubleshooting steps for {issue}: {'; '.join(data['steps'])}",
                    source=f"Troubleshooting Database - {data['category']}",
                    relevance_score=0.0,
                    category=issue,
                )
            )

            # Add escalation information
            if "escalation_trigger" in data:
                self.knowledge_items.append(
                    KnowledgeItem(
                        content=f"Escalation trigger for {issue}: {data['escalation_trigger']}",
                        source=f"Troubleshooting Database - {data['category']}",
                        relevance_score=0.0,
                        category=issue,
                    )
                )

    def _process_installation_guides(self):
        """Process installation guides"""
        for software, guide in self.installation_guides.items():
            # Add installation steps
            steps_text = "; ".join(guide["steps"])
            self.knowledge_items.append(
                KnowledgeItem(
                    content=f"Installation steps for {software}: {steps_text}",
                    source=f"Installation Guide - {guide['title']}",
                    relevance_score=0.0,
                    category="software_installation",
                )
            )

            # Add common issues and solutions
            for issue in guide["common_issues"]:
                issue_text = issue['issue']
                solution_text = issue['solution']
                content = (
                    f"Common issue with {software}: {issue_text} - "
                    f"Solution: {solution_text}"
                )
                self.knowledge_items.append(
                    KnowledgeItem(
                        content=content,
                        source=f"Installation Guide - {guide['title']}",
                        relevance_score=0.0,
                        category="software_installation",
                    )
                )

    def _map_category_from_title(self, title: str) -> str:
        """Map section titles to categories"""
        title_lower = title.lower()
        if "password" in title_lower:
            return "password_reset"
        elif "software" in title_lower:
            return "software_installation"
        elif "hardware" in title_lower:
            return "hardware_failure"
        elif "network" in title_lower:
            return "network_connectivity"
        elif "email" in title_lower:
            return "email_configuration"
        elif "security" in title_lower:
            return "security_incident"
        elif "policy" in title_lower:
            return "policy_question"
        else:
            return "general"

    def _create_vector_embeddings(self):
        """Create vector embeddings for all knowledge items using OpenAI embeddings"""
        if not self.knowledge_items:
            return

        texts = [item.content for item in self.knowledge_items]
        embeddings = self._get_openai_embeddings(texts)
        embeddings = np.array(embeddings)

        # Create FAISS index
        dimension = embeddings.shape[1]
        self.vector_index = faiss.IndexFlatIP(dimension)
        self.vector_index.add(embeddings.astype("float32"))
        print(f"Created vector index with {len(embeddings)} embeddings")

    def _get_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get OpenAI embeddings for a list of texts (batched)"""
        # OpenAI API allows up to 2048 tokens per request, batch if needed
        batch_size = 50
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = self.client.embeddings.create(
                input=batch, model=self.embedding_model
            )
            batch_embeddings = [d.embedding for d in response.data]
            all_embeddings.extend(batch_embeddings)
        return all_embeddings

    def search_knowledge(
        self, query: str, category: str = None, top_k: int = None
    ) -> List[KnowledgeItem]:
        """Search knowledge base for relevant information using OpenAI embeddings"""
        if not self.vector_index or not self.knowledge_items:
            return []

        if top_k is None:
            top_k = int(Config.MAX_RETRIEVAL_RESULTS)
        else:
            top_k = int(top_k)

        # Add security context for security incidents
        if category == "security_incident":
            query = (
                query
                + "This is a security incident. Follow all necessary security policy. "
            )

        # Encode query using OpenAI
        query_embedding = self._get_openai_embeddings([query])[0]
        query_embedding = np.array(query_embedding).reshape(1, -1)

        # Search vector index
        scores, indices = self.vector_index.search(
            query_embedding.astype("float32"),
            min(top_k, len(self.knowledge_items)),
        )

        # Filter by category and similarity threshold
        results = []
        for _, (score, idx) in enumerate(zip(scores[0], indices[0])):
            item = self.knowledge_items[idx]
            print(item)

            # # Apply exact category filter
            # if category and item.category and category != item.category:
            #     continue
            # print("category passed")
            # Apply similarity threshold filter (ensure threshold is float)
            if float(score) < float(Config.SIMILARITY_THRESHOLD):
                continue

            item.relevance_score = float(score)
            results.append(item)

        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]
